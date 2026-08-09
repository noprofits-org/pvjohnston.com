from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

import numpy as np
from PIL import Image


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENT_DIR / "src"))

import contract  # noqa: E402
import reconstruct  # noqa: E402
from analyze import (  # noqa: E402
    AnalysisSpec,
    analysis_admission,
    build_analysis_result,
    validate_analysis_result,
    write_or_check_result,
)
from bundle import (  # noqa: E402
    RunExecutionError,
    RunSpec,
    create_new_run_directory,
    execute_and_seal,
    generate_lifetimes,
    save_array_exclusive,
    validate_run_bundle,
)
from contract import (  # noqa: E402
    WORKFLOW_CLI_PATH,
    WORKFLOW_GRAPH_PATH,
    ContractError,
    authorize_run_request,
    canonical_json_bytes,
    run_namespaces,
    validate_recorded_run_authorization,
)
from render_figure import HEIGHT_PX, WIDTH_PX, render_png_bytes, write_or_check_png  # noqa: E402
from workflow_fixture import WorkflowFixture  # noqa: E402


class PipelineContractTests(unittest.TestCase):
    @staticmethod
    def digest_record_at(repository_root: Path, path: Path) -> dict:
        payload = path.read_bytes()
        return {
            "path": path.relative_to(repository_root).as_posix(),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }

    def stage_validated_result(self, repository_root: Path, result: dict) -> dict:
        """Give a synthetic result complete, resolvable provenance in a temp root."""

        staged = copy.deepcopy(result)
        staged_experiment = repository_root / "research/muon-survival-two-frames"
        for relative in (
            "src/analyze.py",
            "schemas/analysis-result.schema.json",
            "inputs.json",
            "constants.json",
        ):
            destination = staged_experiment / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(EXPERIMENT_DIR / relative, destination)
        source_files = {
            "manifest": repository_root / "setup-toy/run-manifest.json",
            "sample": repository_root / "setup-toy/sample.npy",
            "completion": repository_root / "setup-toy/COMPLETE.json",
        }
        for label, path in source_files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(f"setup-toy-{label}\n".encode("ascii"))
            staged["source_run"][label] = self.digest_record_at(repository_root, path)
        generator = staged_experiment / "src/analyze.py"
        schema = staged_experiment / "schemas/analysis-result.schema.json"
        inputs = staged_experiment / "inputs.json"
        constants = staged_experiment / "constants.json"
        staged["provenance"] = {
            "generator": self.digest_record_at(repository_root, generator),
            "schema": self.digest_record_at(repository_root, schema),
            "inputs": [
                staged["source_run"]["manifest"],
                staged["source_run"]["sample"],
                staged["source_run"]["completion"],
                self.digest_record_at(repository_root, inputs),
                self.digest_record_at(repository_root, constants),
            ],
        }
        return staged

    def toy_spec(self) -> RunSpec:
        lineage = {
            name: {"path": f"setup-toy/{name}", "sha256": "0" * 64}
            for name in (
                "protocol", "setup_manifest", "inputs", "constants", "sources",
                "environment", "requirements", "workflow_graph", "workflow_cli",
            )
        }
        return RunSpec(
            experiment="muon-survival-two-frames",
            purpose="setup-toy",
            run_id="toy-run",
            command="setup-only toy runner",
            seed=0,
            draw_count=16,
            scale_s=1e-6,
            lineage=lineage,
            authorization={
                "kind": "setup-toy",
                "workflow_path": "setup-toy/workflow.jsonl",
                "event_id": "00000000-0000-4000-8000-000000000001",
                "sequence": 1,
                "submission_sequence": 1,
                "decision": "setup-toy",
                "graph_version": 1,
                "graph_sha256": "0" * 64,
                "event_sha256": "0" * 64,
            },
            platform={
                "os": "setup-toy", "release": "setup-toy", "architecture": "setup-toy",
                "python_implementation": "setup-toy", "python_version": "setup-toy",
                "numpy_version": "setup-toy", "matplotlib_version": "setup-toy",
                "pip_version": "setup-toy", "node_version": "setup-toy",
            },
            path_prefix="setup-toy/toy-run",
        )

    def test_only_graph_authorized_normal_and_retry_run_ids_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            base = Path(temporary)
            fixture = WorkflowFixture(base, EXPERIMENT_DIR)
            fixture.approve_setup()
            ledger = fixture.workflow_path
            runs = base / "setup-toy-runs"
            verifier = {
                "workflow_path": ledger,
                "runs_dir": runs,
                "graph_path": WORKFLOW_GRAPH_PATH,
                "repository_root": fixture.repository_root,
                "workflow_cli_path": WORKFLOW_CLI_PATH,
            }
            normal = authorize_run_request("run-001", **verifier)
            self.assertEqual(normal["kind"], "normal")
            validate_recorded_run_authorization("run-001", normal, **{key: value for key, value in verifier.items() if key != "runs_dir"})
            with self.assertRaises(ContractError):
                authorize_run_request("run-002", **verifier)
            with self.assertRaises(ContractError):
                authorize_run_request("run-003", **verifier)

            prior = runs / "run-001"
            prior.mkdir(parents=True)
            fixture.register_retry()
            retry = authorize_run_request("run-002", **verifier)
            self.assertEqual(retry["kind"], "registered_retry")
            recorded_verifier = {key: value for key, value in verifier.items() if key != "runs_dir"}
            validate_recorded_run_authorization("run-002", retry, **recorded_verifier)
            validate_recorded_run_authorization("run-001", normal, **recorded_verifier)
            (prior / "COMPLETE.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "complete run-001"):
                authorize_run_request("run-002", **verifier)

    def test_underspecified_event_is_rejected_by_full_graph_replay(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            fixture = WorkflowFixture(Path(temporary), EXPERIMENT_DIR)
            fixture.workflow_path.write_text(
                '{"sequence":1,"event_id":"event-1","type":"review","from":"setup_review","to":"execute","decision":"approve"}\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ContractError, "graph replay"):
                authorize_run_request(
                    "run-001",
                    workflow_path=fixture.workflow_path,
                    runs_dir=Path(temporary) / "setup-toy-runs",
                    graph_path=WORKFLOW_GRAPH_PATH,
                    repository_root=fixture.repository_root,
                    workflow_cli_path=WORKFLOW_CLI_PATH,
                )

    def test_authorization_consumes_the_exact_replayed_ledger_bytes(self) -> None:
        real_run = subprocess.run
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            base = Path(temporary)

            normal_fixture = WorkflowFixture(base / "normal", EXPERIMENT_DIR)
            normal_event = normal_fixture.approve_setup()
            normal_runs = base / "normal-runs"

            def replace_normal_after_replay(*args, **kwargs):
                completed = real_run(*args, **kwargs)
                normal_fixture.workflow_path.write_text('{"sequence":1,"replacement":"unverified"}\n', encoding="utf-8")
                return completed

            with mock.patch("contract.subprocess.run", side_effect=replace_normal_after_replay):
                normal = authorize_run_request(
                    "run-001",
                    workflow_path=normal_fixture.workflow_path,
                    runs_dir=normal_runs,
                    graph_path=WORKFLOW_GRAPH_PATH,
                    repository_root=normal_fixture.repository_root,
                    workflow_cli_path=WORKFLOW_CLI_PATH,
                )
            self.assertEqual(normal["event_id"], normal_event["event_id"])

            recorded_fixture = WorkflowFixture(base / "recorded", EXPERIMENT_DIR)
            recorded_fixture.approve_setup()
            recorded_kwargs = {
                "workflow_path": recorded_fixture.workflow_path,
                "graph_path": WORKFLOW_GRAPH_PATH,
                "repository_root": recorded_fixture.repository_root,
                "workflow_cli_path": WORKFLOW_CLI_PATH,
            }
            recorded = authorize_run_request("run-001", runs_dir=base / "recorded-runs", **recorded_kwargs)

            def replace_recorded_after_replay(*args, **kwargs):
                completed = real_run(*args, **kwargs)
                recorded_fixture.workflow_path.write_text('{"sequence":1,"replacement":"unverified"}\n', encoding="utf-8")
                return completed

            with mock.patch("contract.subprocess.run", side_effect=replace_recorded_after_replay):
                validate_recorded_run_authorization("run-001", recorded, **recorded_kwargs)

            retry_fixture = WorkflowFixture(base / "retry", EXPERIMENT_DIR)
            retry_fixture.approve_setup()
            retry_event = retry_fixture.register_retry()
            retry_runs = base / "retry-runs"
            (retry_runs / "run-001").mkdir(parents=True)

            def replace_retry_after_replay(*args, **kwargs):
                completed = real_run(*args, **kwargs)
                retry_fixture.workflow_path.write_text('{"sequence":1,"replacement":"unverified"}\n', encoding="utf-8")
                return completed

            with mock.patch("contract.subprocess.run", side_effect=replace_retry_after_replay):
                retry = authorize_run_request(
                    "run-002",
                    workflow_path=retry_fixture.workflow_path,
                    runs_dir=retry_runs,
                    graph_path=WORKFLOW_GRAPH_PATH,
                    repository_root=retry_fixture.repository_root,
                    workflow_cli_path=WORKFLOW_CLI_PATH,
                )
            self.assertEqual(retry["event_id"], retry_event["event_id"])

    def test_historical_run_approval_remains_valid_after_analysis_submission(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            fixture = WorkflowFixture(Path(temporary), EXPERIMENT_DIR)
            fixture.approve_setup()
            approval = fixture.approve_run("run-001")
            fixture.submit_analysis()
            admission = analysis_admission(
                approval["event_id"],
                "run-001",
                workflow_path=fixture.workflow_path,
                graph_path=WORKFLOW_GRAPH_PATH,
                repository_root=fixture.repository_root,
                workflow_cli_path=WORKFLOW_CLI_PATH,
            )
            self.assertEqual(admission["sequence"], approval["sequence"])
            self.assertLess(admission["sequence"], fixture.sequence)
            self.assertEqual(admission["event_sha256"], hashlib.sha256(
                (json.dumps(approval, separators=(",", ":")) + "\n").encode("utf-8")
            ).hexdigest())

    def test_historical_admission_consumes_bound_ledger_and_snapshot_bytes(self) -> None:
        real_run = subprocess.run
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            fixture = WorkflowFixture(Path(temporary), EXPERIMENT_DIR)
            fixture.approve_setup()
            approval = fixture.approve_run("run-001")
            fixture.submit_analysis()
            snapshot = fixture.repository_root / approval["artifacts"][0]["snapshot_path"]

            def replace_paths_after_replay(*args, **kwargs):
                completed = real_run(*args, **kwargs)
                fixture.workflow_path.write_text('{"sequence":1,"replacement":"unverified"}\n', encoding="utf-8")
                snapshot.write_text("replacement omits requested run identity\n", encoding="utf-8")
                return completed

            with mock.patch("contract.subprocess.run", side_effect=replace_paths_after_replay):
                admission = analysis_admission(
                    approval["event_id"],
                    "run-001",
                    workflow_path=fixture.workflow_path,
                    graph_path=WORKFLOW_GRAPH_PATH,
                    repository_root=fixture.repository_root,
                    workflow_cli_path=WORKFLOW_CLI_PATH,
                )
            self.assertEqual(admission["event_id"], approval["event_id"])
            self.assertNotIn("run-001", snapshot.read_text(encoding="utf-8"))

    def test_production_absence_detects_every_namespace(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            runs = Path(temporary) / "runs"
            runs.mkdir()
            (runs / "run-002").mkdir()
            self.assertEqual(run_namespaces(runs), ["run-002"])
        with mock.patch("contract.verify_setup_manifest", return_value={"artifacts": []}), mock.patch("contract.run_namespaces", return_value=["run-002"]):
            with self.assertRaisesRegex(ContractError, "run-002"):
                contract.setup_validation()

    def test_raw_sample_publication_is_atomically_exclusive_under_race(self) -> None:
        sample = generate_lifetimes(self.toy_spec())
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            target = Path(temporary) / "setup-toy-sample.npy"
            barrier = threading.Barrier(2)

            def contender():
                barrier.wait()
                try:
                    save_array_exclusive(target, sample)
                    return "won"
                except ContractError:
                    return "rejected"

            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(contender) for _ in range(2)]
                outcomes = sorted(future.result() for future in futures)
            self.assertEqual(outcomes, ["rejected", "won"])
            np.testing.assert_array_equal(np.load(target, allow_pickle=False), sample)

    def test_success_logs_are_actual_process_streams_and_hash_bound(self) -> None:
        spec = self.toy_spec()
        sample = generate_lifetimes(spec)
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            run_dir = create_new_run_directory(Path(temporary) / "setup-toy-runs", "toy-run")

            def draw(_spec):
                print("draw-stdout-sentinel")
                print("draw-stderr-sentinel", file=sys.stderr)
                return sample

            execute_and_seal(
                run_dir,
                spec,
                started_at="2000-01-01T00:00:00Z",
                completed_at="2000-01-01T00:00:01Z",
                draw=draw,
            )
            self.assertIn("draw-stdout-sentinel", (run_dir / "stdout.log").read_text(encoding="utf-8"))
            self.assertIn("draw-stderr-sentinel", (run_dir / "stderr.log").read_text(encoding="utf-8"))
            integrity = validate_run_bundle(run_dir, spec)
            self.assertTrue(integrity["valid"])
            self.assertTrue(all(integrity[name] for name in ("schema_valid", "manifest_valid", "provenance_valid", "hashes_valid")))
            (run_dir / "stdout.log").write_text("tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "checksum mismatch"):
                validate_run_bundle(run_dir, spec)

    def test_failure_traceback_is_in_actual_stderr_and_namespace_is_incomplete(self) -> None:
        spec = self.toy_spec()
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            run_dir = create_new_run_directory(Path(temporary) / "setup-toy-runs", "toy-run")

            def fail(_spec):
                print("failure-stdout-sentinel")
                print("failure-stderr-sentinel", file=sys.stderr)
                raise OSError("synthetic setup failure")

            with self.assertRaises(RunExecutionError):
                execute_and_seal(
                    run_dir,
                    spec,
                    started_at="2000-01-01T00:00:00Z",
                    completed_at="2000-01-01T00:00:01Z",
                    draw=fail,
                )
            self.assertIn("failure-stdout-sentinel", (run_dir / "stdout.log").read_text(encoding="utf-8"))
            stderr = (run_dir / "stderr.log").read_text(encoding="utf-8")
            self.assertIn("failure-stderr-sentinel", stderr)
            self.assertIn("OSError: synthetic setup failure", stderr)
            self.assertFalse((run_dir / "COMPLETE.json").exists())

    def synthetic_result(self) -> dict:
        paths = np.asarray([0.0, np.log(2.0), np.log(4.0)], dtype=np.float64)
        primitives = {
            "momentum_mev_c": 1.0,
            "mass_energy_mev": 1.0,
            "tau0_s": 1.0,
            "c_m_s": 1.0,
            "units": dict(reconstruct.PRIMITIVE_UNITS),
        }
        sample = np.linspace(0.0, 3.0, 16, dtype=np.float64)
        spec = AnalysisSpec(
            paths_m=paths,
            primitives=primitives,
            focal_index=1,
            frame_relative_tolerance=1e-12,
            standard_error_multiplier=4.0,
            maximum_grid_discrepancy=0.5,
            source_run={
                "run_id": "setup-toy-run",
                "manifest": {"path": "setup-toy/run-manifest.json", "bytes": 1, "sha256": "1" * 64},
                "sample": {"path": "setup-toy/sample.npy", "bytes": 1, "sha256": "2" * 64},
                "completion": {"path": "setup-toy/COMPLETE.json", "bytes": 1, "sha256": "3" * 64},
            },
            integrity_flags={"schema": True, "manifest": True, "provenance": True, "hashes": True, "run_bundle": True, "run_admission": True},
            generated_at="2000-01-01T00:00:00Z",
            analysis_admission={
                "event_id": "00000000-0000-4000-8000-000000000001",
                "sequence": 2,
                "submission_sequence": 1,
                "decision": "approve",
                "graph_version": 1,
                "graph_sha256": "e50f12475131efe1fa9313fd2a7e9c04c049355356b26a69362afe52a418d404",
                "workflow_path": "research/muon-survival-two-frames/workflow.jsonl",
                "event_sha256": "4" * 64,
            },
        )
        return build_analysis_result(sample, spec)

    def test_analysis_result_png_and_metrics_regenerate_and_check_on_synthetic_fixture(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            base = Path(temporary)
            result = self.stage_validated_result(base, self.synthetic_result())
            self.assertEqual(result["outcome_kind"], "understanding-observations-no-verdict")
            summary = base / "setup-toy-summary.json"
            figure = base / "setup-toy-figure.png"
            metrics = base / "setup-toy-metrics.json"
            write_or_check_result(summary, result, check=False, verify_provenance=True, enforce_frozen_inputs=False, repository_root=base)
            write_or_check_result(summary, result, check=True, verify_provenance=True, enforce_frozen_inputs=False, repository_root=base)
            png_first = render_png_bytes(result)
            png_second = render_png_bytes(copy.deepcopy(result))
            self.assertEqual(png_first, png_second)
            write_or_check_png(figure, png_first, check=False)
            write_or_check_png(figure, png_second, check=True)
            with Image.open(figure) as image:
                self.assertEqual(image.size, (WIDTH_PX, HEIGHT_PX))
            command = [
                "node",
                str(EXPERIMENT_DIR / "generate-metrics.mjs"),
                "--setup-fixture",
                str(summary),
                "--output",
                str(metrics),
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            subprocess.run([*command, "--check"], check=True, capture_output=True, text=True)
            projection = json.loads(metrics.read_text(encoding="utf-8"))
            self.assertIn("detector_elapsed_time_s", projection["metrics"])
            self.assertIn("muon_contracted_distance_m", projection["metrics"])
            self.assertIn("counterfactual_survival", projection["metrics"])
            self.assertIn("pass_numeric_shapes_dtypes_units_valid", projection["metrics"])
            summary.write_text("{}\n", encoding="utf-8")
            with self.assertRaises(ContractError):
                write_or_check_result(summary, result, check=True, verify_provenance=True, enforce_frozen_inputs=False, repository_root=base)

    def test_metrics_write_and_check_reject_full_result_contract_tampering(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            base = Path(temporary)
            result = self.stage_validated_result(base, self.synthetic_result())
            summary = base / "setup-toy-summary.json"
            metrics = base / "setup-toy-metrics.json"
            summary.write_bytes(canonical_json_bytes(result))
            command = [
                "node", str(EXPERIMENT_DIR / "generate-metrics.mjs"),
                "--setup-fixture", str(summary), "--output", str(metrics),
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            mutations = {
                "schema": lambda value: value.pop("muon_frame"),
                "cross_field": lambda value: value["detector_frame"]["elapsed_time_s"].__setitem__(1, 99.0),
                "digest_provenance": lambda value: value["provenance"]["generator"].__setitem__("sha256", "0" * 64),
                "integrity_details": lambda value: value["checks"]["details"].pop("grid_valid"),
            }
            for name, mutate in mutations.items():
                with self.subTest(mode="write", mutation=name):
                    changed = copy.deepcopy(result)
                    mutate(changed)
                    summary.write_bytes(canonical_json_bytes(changed))
                    candidate = base / f"setup-toy-{name}-metrics.json"
                    rejected = subprocess.run(
                        [*command[:-1], str(candidate)],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertNotEqual(rejected.returncode, 0)
                    self.assertFalse(candidate.exists())
                with self.subTest(mode="check", mutation=name):
                    rejected = subprocess.run([*command, "--check"], check=False, capture_output=True, text=True)
                    self.assertNotEqual(rejected.returncode, 0)
            summary.write_bytes(canonical_json_bytes(result))
            subprocess.run([*command, "--check"], check=True, capture_output=True, text=True)

    def test_result_schema_and_cross_field_validation_reject_stale_content(self) -> None:
        result = self.synthetic_result()
        self.assertTrue(validate_analysis_result(result, verify_provenance=False, enforce_frozen_inputs=False))
        mutations = [
            lambda value: value.pop("muon_frame"),
            lambda value: value["detector_frame"].__setitem__("beta", "not-a-number"),
            lambda value: value["grid_m"].append(99.0),
            lambda value: value["focal"].__setitem__("empirical_count", -1),
            lambda value: value["provenance"]["generator"].__setitem__("sha256", "bad"),
            lambda value: value["checks"].__setitem__("all_passed", not value["checks"]["all_passed"]),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                changed = copy.deepcopy(result)
                mutate(changed)
                with self.assertRaises(ContractError):
                    validate_analysis_result(changed, verify_provenance=False, enforce_frozen_inputs=False)


if __name__ == "__main__":
    unittest.main()
