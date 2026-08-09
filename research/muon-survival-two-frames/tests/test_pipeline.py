from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Mapping
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
    main as analyze_main,
    build_analysis_result,
    parse_admitted_run_evidence,
    registered_analysis_spec,
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
    derived_stage_path,
    install_derived_bytes_atomic,
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

    def stage_validated_result(self, temporary_root: Path, result: dict) -> tuple[Path, dict]:
        """Give a synthetic result complete, resolvable provenance in a temp root."""

        fixture = WorkflowFixture(temporary_root)
        repository_root = fixture.repository_root
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
        graph = repository_root / "research/workflow.graph.v1.json"
        graph.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(WORKFLOW_GRAPH_PATH, graph)
        workflow_cli = repository_root / "scripts/research-workflow.mjs"
        workflow_cli.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(WORKFLOW_CLI_PATH, workflow_cli)

        fixture.approve_setup()
        approval = fixture.approve_run("toy-run")
        fixture.submit_analysis()
        staged["analysis_admission"] = analysis_admission(
            approval["event_id"],
            "toy-run",
            workflow_path=fixture.workflow_path,
            graph_path=graph,
            repository_root=repository_root,
            workflow_cli_path=workflow_cli,
            allowed_run_ids=frozenset({"toy-run"}),
        )

        run_dir = create_new_run_directory(repository_root / "setup-toy", "toy-run")
        sample = self.synthetic_sample()
        execute_and_seal(
            run_dir,
            self.toy_spec(),
            started_at="2000-01-01T00:00:00Z",
            completed_at="2000-01-01T00:00:01Z",
            draw=lambda _spec: sample,
        )
        source_files = {
            "manifest": run_dir / "run-manifest.json",
            "sample": run_dir / "proper_lifetimes_s.npy",
            "completion": run_dir / "COMPLETE.json",
        }
        staged["source_run"] = {
            "run_id": "toy-run",
            **{
                label: self.digest_record_at(repository_root, path)
                for label, path in source_files.items()
            },
        }
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
        return repository_root, staged

    @staticmethod
    def synthetic_sample() -> np.ndarray:
        return np.linspace(0.0, 3.0, 16, dtype=np.float64)

    def toy_spec(
        self,
        run_id: str = "toy-run",
        path_prefix: str = "setup-toy/toy-run",
        scale_s: float = 1e-6,
    ) -> RunSpec:
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
            run_id=run_id,
            command="setup-only toy runner",
            seed=0,
            draw_count=16,
            scale_s=scale_s,
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
            path_prefix=path_prefix,
        )

    def test_admitted_run_marker_requires_one_exact_structured_field(self) -> None:
        valid = (
            b"Both run-001 and run-002 are discussed incidentally.\n"
            b"- **Admitted run:** `run-001`\n"
        )
        self.assertEqual(parse_admitted_run_evidence([valid]), "run-001")

        invalid = {
            "missing": [b"Incidental run-001 and run-002 only.\n"],
            "duplicate": [
                b"- **Admitted run:** `run-001`\n",
                b"- **Admitted run:** `run-001`\n",
            ],
            "conflicting_artifacts": [
                b"- **Admitted run:** `run-001`\n",
                b"- **Admitted run:** `run-002`\n",
            ],
            "malformed": [b"- **Admitted run:** run-001\n"],
            "both_ids_in_one_field": [
                b"- **Admitted run:** `run-001` and `run-002`\n",
            ],
            "both_ids_as_fields": [
                b"- **Admitted run:** `run-001`\n- **Admitted run:** `run-002`\n",
            ],
            "unregistered": [b"- **Admitted run:** `run-003`\n"],
            "leading_space": [b" - **Admitted run:** `run-001`\n"],
            "trailing_text": [b"- **Admitted run:** `run-001` approved\n"],
        }
        for name, payloads in invalid.items():
            with self.subTest(case=name), self.assertRaises(ContractError):
                parse_admitted_run_evidence(payloads)

    def test_workflow_fixture_has_a_stable_programmatic_setup_prefix(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            with mock.patch.object(Path, "read_text", side_effect=AssertionError(
                "workflow fixture must not read a mutable live ledger"
            )):
                fixture = WorkflowFixture(Path(temporary))
            records = [json.loads(line) for line in fixture.workflow_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([record["sequence"] for record in records], [1, 2, 3])
            self.assertEqual([record["type"] for record in records], ["init", "submit", "review"])
            self.assertEqual(
                [(record["from"], record["to"]) for record in records],
                [(None, "brainstorm"), ("brainstorm", "question_review"), ("question_review", "setup")],
            )
            self.assertEqual(records[2]["decision"], "approve")
            self.assertEqual(records[2]["submission_sequence"], 2)
            self.assertEqual(fixture.sequence, 3)
            self.assertIsNone(fixture.submission_sequence)
            snapshots = list((fixture.experiment_dir / "workflow/evidence").iterdir())
            self.assertEqual(len(snapshots), 2)

    def test_registered_analysis_entrypoint_uses_real_integrity_plumbing_for_both_runs(self) -> None:
        cases = (("run-001", False, False), ("run-002", True, True))
        for run_id, register_retry, check_mode in cases:
            with self.subTest(run_id=run_id), tempfile.TemporaryDirectory(
                prefix="muon-setup-nonproduction-"
            ) as temporary:
                fixture = WorkflowFixture(Path(temporary))
                repository_root = fixture.repository_root
                graph = repository_root / "research/workflow.graph.v1.json"
                graph.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(WORKFLOW_GRAPH_PATH, graph)
                workflow_cli = repository_root / "scripts/research-workflow.mjs"
                workflow_cli.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(WORKFLOW_CLI_PATH, workflow_cli)

                fixture.approve_setup()
                if register_retry:
                    fixture.register_retry()
                approval = fixture.approve_run(run_id)
                other_run_id = "run-002" if run_id == "run-001" else "run-001"
                with self.assertRaisesRegex(ContractError, "differs from the requested"):
                    analysis_admission(
                        approval["event_id"],
                        other_run_id,
                        workflow_path=fixture.workflow_path,
                        graph_path=graph,
                        repository_root=repository_root,
                        workflow_cli_path=workflow_cli,
                    )

                runs_dir = repository_root / "setup-toy-analysis-runs"
                run_dir = create_new_run_directory(runs_dir, run_id)
                path_prefix = run_dir.relative_to(repository_root).as_posix()
                run_spec = self.toy_spec(run_id=run_id, path_prefix=path_prefix, scale_s=1.0)
                sample = self.synthetic_sample()
                execute_and_seal(
                    run_dir,
                    run_spec,
                    started_at="2000-01-01T00:00:00Z",
                    completed_at="2000-01-01T00:00:01Z",
                    draw=lambda _spec: sample,
                )
                toy_inputs = {
                    "production": {
                        "momentum_mev_c": 1.0,
                        "laboratory_grid": {
                            "index_start": 0,
                            "index_stop_inclusive": 2,
                            "step_m": float(np.log(2.0)),
                        },
                        "focal_index": 1,
                    },
                    "checks": {
                        "frame_relative_tolerance": 1e-12,
                        "focal_monte_carlo_standard_error_multiplier": 4.0,
                        "maximum_grid_absolute_discrepancy": 0.5,
                    },
                }
                toy_constants = {
                    "constants": {
                        "muon_mass_energy_mev": {"value": 1.0},
                        "muon_proper_mean_lifetime_s": {"value": 1.0},
                        "speed_of_light_m_s": {"value": 1.0},
                    },
                }
                builder_calls: list[tuple[str, Mapping[str, Any] | None]] = []

                def run_spec_builder(selected_run_id: str, *, recorded_authorization=None):
                    builder_calls.append((selected_run_id, recorded_authorization))
                    return run_spec

                def spec_loader(selected_run_id: str, event_id: str, generated_at: str):
                    return registered_analysis_spec(
                        selected_run_id,
                        event_id,
                        generated_at,
                        runs_dir=runs_dir,
                        repository_root=repository_root,
                        workflow_path=fixture.workflow_path,
                        graph_path=graph,
                        workflow_cli_path=workflow_cli,
                        run_spec_builder=run_spec_builder,
                        inputs_loader=lambda: toy_inputs,
                        constants_loader=lambda: toy_constants,
                    )

                output = repository_root / f"setup-toy-analysis-{run_id}.json"
                generated_at = "2000-01-01T00:00:09Z"
                if check_mode:
                    output.write_text(json.dumps({"generated_at": generated_at}) + "\n", encoding="utf-8")
                writer_calls: list[tuple[Path, dict, bool]] = []

                def result_writer(path: Path, result: dict, *, check: bool) -> None:
                    writer_calls.append((path, result, check))

                arguments = ["--run-id", run_id, "--run-review-event", approval["event_id"]]
                if check_mode:
                    arguments.append("--check")
                self.assertEqual(analyze_main(
                    arguments,
                    output_path=output,
                    spec_loader=spec_loader,
                    result_writer=result_writer,
                    now=lambda: generated_at,
                    environment_setter=lambda: None,
                ), 0)
                self.assertEqual(builder_calls, [(run_id, run_spec.authorization)])
                self.assertEqual(len(writer_calls), 1)
                written_path, result, observed_check = writer_calls[0]
                self.assertEqual(written_path, output)
                self.assertEqual(observed_check, check_mode)
                self.assertEqual(result["source_run"]["run_id"], run_id)
                self.assertTrue(all(result["checks"][name] for name in (
                    "frame_agreement",
                    "focal_monte_carlo_within_four_standard_errors",
                    "maximum_grid_discrepancy_at_most_threshold",
                    "counts_valid_and_monotonic",
                    "numeric_shapes_dtypes_units_valid",
                    "schema_manifest_provenance_and_hashes_valid",
                    "all_passed",
                )))
                expected_command = (
                    "research/muon-survival-two-frames/.venv/bin/python "
                    "research/muon-survival-two-frames/src/analyze.py "
                    f"--run-id {run_id} --run-review-event <approved-event-id>"
                    + (" --check" if check_mode else "")
                )
                self.assertEqual(contract.analysis_command(run_id, check=check_mode), expected_command)

    def test_only_graph_authorized_normal_and_retry_run_ids_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            base = Path(temporary)
            fixture = WorkflowFixture(base)
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
            fixture = WorkflowFixture(Path(temporary))
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

            normal_fixture = WorkflowFixture(base / "normal")
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

            recorded_fixture = WorkflowFixture(base / "recorded")
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

            retry_fixture = WorkflowFixture(base / "retry")
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

    def test_authorization_executes_captured_graph_and_verifier_bytes(self) -> None:
        real_run = subprocess.run
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            base = Path(temporary)
            fixture = WorkflowFixture(base)
            approved = fixture.approve_setup()
            graph = base / "setup-toy-approved-graph.json"
            workflow_cli = base / "setup-toy-approved-workflow.mjs"
            shutil.copy2(WORKFLOW_GRAPH_PATH, graph)
            shutil.copy2(WORKFLOW_CLI_PATH, workflow_cli)

            def replace_original_tools_before_subprocess_open(*args, **kwargs):
                graph.write_text('{"replacement":"unapproved graph"}\n', encoding="utf-8")
                workflow_cli.write_text("throw new Error('unapproved verifier');\n", encoding="utf-8")
                return real_run(*args, **kwargs)

            with mock.patch("contract.subprocess.run", side_effect=replace_original_tools_before_subprocess_open):
                authorization = authorize_run_request(
                    "run-001",
                    workflow_path=fixture.workflow_path,
                    runs_dir=base / "setup-toy-runs",
                    graph_path=graph,
                    repository_root=fixture.repository_root,
                    workflow_cli_path=workflow_cli,
                )
            self.assertEqual(authorization["event_id"], approved["event_id"])
            self.assertIn("unapproved graph", graph.read_text(encoding="utf-8"))
            self.assertIn("unapproved verifier", workflow_cli.read_text(encoding="utf-8"))

    def test_historical_run_approval_remains_valid_after_analysis_submission(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            fixture = WorkflowFixture(Path(temporary))
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
            fixture = WorkflowFixture(Path(temporary))
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

    def test_derived_publication_recovers_stages_and_rejects_existing_finals(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            base = Path(temporary)
            for suffix in ("json", "png"):
                with self.subTest(suffix=suffix):
                    target = base / f"setup-toy-derived.{suffix}"
                    payload = f"complete-{suffix}-payload".encode("ascii")
                    digest = hashlib.sha256(payload).hexdigest()
                    partial = derived_stage_path(target, digest, "1" * 32, "tmp")
                    mismatched = derived_stage_path(target, digest, "2" * 32, "ready")
                    partial.write_bytes(payload[:5])
                    mismatched.write_bytes(b"mismatched-ready")
                    quarantined = install_derived_bytes_atomic(
                        target,
                        payload,
                        nonce_factory=lambda: "3" * 32,
                    )
                    self.assertEqual(target.read_bytes(), payload)
                    self.assertFalse(partial.exists())
                    self.assertFalse(mismatched.exists())
                    self.assertEqual(len(quarantined), 2)
                    self.assertEqual(
                        {path.read_bytes() for path in quarantined},
                        {payload[:5], b"mismatched-ready"},
                    )
                    self.assertFalse(list(base.glob(f".{target.name}.publish-*")))
                    with self.assertRaisesRegex(ContractError, "refusing to overwrite"):
                        install_derived_bytes_atomic(target, b"replacement")
                    self.assertEqual(target.read_bytes(), payload)

            recovered_target = base / "setup-toy-recovered.json"
            recovered_payload = b"complete-recoverable-ready"
            recovered_digest = hashlib.sha256(recovered_payload).hexdigest()
            recovered_ready = derived_stage_path(
                recovered_target,
                recovered_digest,
                "4" * 32,
                "ready",
            )
            recovered_ready.write_bytes(recovered_payload)
            self.assertEqual(
                install_derived_bytes_atomic(recovered_target, recovered_payload),
                [],
            )
            self.assertEqual(recovered_target.read_bytes(), recovered_payload)
            self.assertFalse(recovered_ready.exists())

    def test_derived_publication_race_never_exposes_a_partial_final(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            target = Path(temporary) / "setup-toy-race.json"
            payloads = (b"A" * (256 * 1024), b"B" * (256 * 1024))
            first_ready = threading.Event()
            second_ready = threading.Event()
            release = threading.Event()
            stop_observer = threading.Event()
            observations: list[bytes] = []

            def observe() -> None:
                while not stop_observer.wait(0.0005):
                    if os.path.lexists(target):
                        try:
                            observations.append(target.read_bytes())
                        except FileNotFoundError:
                            pass

            def contender(payload: bytes, nonce: str, ready_event: threading.Event) -> str:
                def before_install(_ready_path: Path) -> None:
                    ready_event.set()
                    self.assertTrue(release.wait(timeout=5.0))

                try:
                    install_derived_bytes_atomic(
                        target,
                        payload,
                        nonce_factory=lambda: nonce,
                        before_install=before_install,
                    )
                    return "won"
                except (ContractError, OSError):
                    return "rejected"

            observer = threading.Thread(target=observe)
            observer.start()
            with ThreadPoolExecutor(max_workers=2) as pool:
                first = pool.submit(contender, payloads[0], "5" * 32, first_ready)
                self.assertTrue(first_ready.wait(timeout=5.0))
                self.assertFalse(os.path.lexists(target))
                second = pool.submit(contender, payloads[1], "6" * 32, second_ready)
                self.assertTrue(second_ready.wait(timeout=5.0))
                self.assertFalse(os.path.lexists(target))
                release.set()
                outcomes = sorted((first.result(), second.result()))
            observations.append(target.read_bytes())
            stop_observer.set()
            observer.join(timeout=5.0)
            self.assertEqual(outcomes, ["rejected", "won"])
            self.assertIn(target.read_bytes(), payloads)
            self.assertTrue(observations)
            self.assertTrue(all(observed in payloads for observed in observations))
            self.assertFalse(list(target.parent.glob(f".{target.name}.publish-*")))

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
        sample = self.synthetic_sample()
        spec = AnalysisSpec(
            paths_m=paths,
            primitives=primitives,
            focal_index=1,
            frame_relative_tolerance=1e-12,
            standard_error_multiplier=4.0,
            maximum_grid_discrepancy=0.5,
            source_run={
                "run_id": "toy-run",
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
            repository_root, result = self.stage_validated_result(Path(temporary), self.synthetic_result())
            self.assertEqual(result["outcome_kind"], "understanding-observations-no-verdict")
            summary = repository_root / "setup-toy-summary.json"
            figure = repository_root / "setup-toy-figure.png"
            metrics = repository_root / "setup-toy-metrics.json"
            write_or_check_result(summary, result, check=False, enforce_frozen_inputs=False, repository_root=repository_root)
            write_or_check_result(summary, result, check=True, enforce_frozen_inputs=False, repository_root=repository_root)
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
                write_or_check_result(summary, result, check=True, enforce_frozen_inputs=False, repository_root=repository_root)

    def test_node_metrics_publication_recovers_quarantines_and_races_atomically(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            repository_root, result = self.stage_validated_result(Path(temporary), self.synthetic_result())
            summary = repository_root / "setup-toy-summary.json"
            summary.write_bytes(canonical_json_bytes(result))

            def command(output: Path) -> list[str]:
                return [
                    "node",
                    str(EXPERIMENT_DIR / "generate-metrics.mjs"),
                    "--setup-fixture",
                    str(summary),
                    "--output",
                    str(output),
                ]

            baseline = repository_root / "setup-toy-node-baseline-metrics.json"
            subprocess.run(command(baseline), check=True, capture_output=True, text=True)
            expected = baseline.read_bytes()
            rejected = subprocess.run(command(baseline), check=False, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(baseline.read_bytes(), expected)
            subprocess.run([*command(baseline), "--check"], check=True, capture_output=True, text=True)

            digest = hashlib.sha256(expected).hexdigest()
            partial_target = repository_root / "setup-toy-node-partial-metrics.json"
            partial_stage = derived_stage_path(partial_target, digest, "7" * 32, "tmp")
            partial_stage.write_bytes(expected[:17])
            subprocess.run(command(partial_target), check=True, capture_output=True, text=True)
            self.assertEqual(partial_target.read_bytes(), expected)
            self.assertFalse(partial_stage.exists())
            partial_quarantine = list(repository_root.glob(f".{partial_target.name}.quarantine-*.stage"))
            self.assertEqual(len(partial_quarantine), 1)
            self.assertEqual(partial_quarantine[0].read_bytes(), expected[:17])

            ready_target = repository_root / "setup-toy-node-ready-metrics.json"
            ready_stage = derived_stage_path(ready_target, digest, "8" * 32, "ready")
            ready_stage.write_bytes(expected)
            subprocess.run(command(ready_target), check=True, capture_output=True, text=True)
            self.assertEqual(ready_target.read_bytes(), expected)
            self.assertFalse(ready_stage.exists())

            mismatch_target = repository_root / "setup-toy-node-mismatch-metrics.json"
            mismatch_stage = derived_stage_path(mismatch_target, digest, "9" * 32, "ready")
            mismatch_stage.write_bytes(b"mismatched-ready")
            subprocess.run(command(mismatch_target), check=True, capture_output=True, text=True)
            self.assertEqual(mismatch_target.read_bytes(), expected)
            mismatch_quarantine = list(repository_root.glob(f".{mismatch_target.name}.quarantine-*.stage"))
            self.assertEqual(len(mismatch_quarantine), 1)
            self.assertEqual(mismatch_quarantine[0].read_bytes(), b"mismatched-ready")

            race_target = repository_root / "setup-toy-node-race-metrics.json"
            launch = threading.Barrier(2)
            stop_observer = threading.Event()
            observations: list[bytes] = []

            def observe() -> None:
                while not stop_observer.wait(0.0005):
                    if os.path.lexists(race_target):
                        try:
                            observations.append(race_target.read_bytes())
                        except FileNotFoundError:
                            pass

            def contender() -> int:
                launch.wait()
                return subprocess.run(
                    command(race_target),
                    check=False,
                    capture_output=True,
                    text=True,
                ).returncode

            observer = threading.Thread(target=observe)
            observer.start()
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(contender) for _ in range(2)]
                outcomes = sorted(future.result() for future in futures)
            observations.append(race_target.read_bytes())
            stop_observer.set()
            observer.join(timeout=5.0)
            self.assertEqual(outcomes[0], 0)
            self.assertNotEqual(outcomes[1], 0)
            self.assertTrue(observations)
            self.assertTrue(all(observed == expected for observed in observations))
            self.assertFalse(list(repository_root.glob(f".{race_target.name}.publish-*")))

    def test_metrics_write_and_check_reject_full_result_contract_tampering(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            repository_root, result = self.stage_validated_result(Path(temporary), self.synthetic_result())
            summary = repository_root / "setup-toy-summary.json"
            metrics = repository_root / "setup-toy-metrics.json"
            summary.write_bytes(canonical_json_bytes(result))
            command = [
                "node", str(EXPERIMENT_DIR / "generate-metrics.mjs"),
                "--setup-fixture", str(summary), "--output", str(metrics),
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)

            def mutate_detail_and_pass(value):
                value["checks"]["details"]["grid_valid"] = False
                value["checks"]["numeric_shapes_dtypes_units_valid"] = False
                value["checks"]["all_passed"] = False

            def mutate_pass_and_all(value):
                value["checks"]["frame_agreement"] = False
                value["checks"]["all_passed"] = False

            def mutate_raw_derived_empirical(value):
                value["empirical"]["counts"][1] -= 1
                value["empirical"]["survival_probability"][1] = value["empirical"]["counts"][1] / 16
                value["focal"]["empirical_count"] = value["empirical"]["counts"][1]
                value["focal"]["empirical_survival_probability"] = value["empirical"]["survival_probability"][1]

            mutations = {
                "schema": lambda value: value.pop("muon_frame"),
                "cross_field": lambda value: value["detector_frame"]["elapsed_time_s"].__setitem__(1, 99.0),
                "diagnostic_value": lambda value: value["checks"]["diagnostics"].__setitem__(
                    "focal_binomial_standard_error",
                    value["checks"]["diagnostics"]["focal_binomial_standard_error"] + 0.125,
                ),
                "detail_value": mutate_detail_and_pass,
                "pass_and_all": mutate_pass_and_all,
                "admission_identity": lambda value: value["analysis_admission"].__setitem__("event_sha256", "0" * 64),
                "source_run_id": lambda value: value["source_run"].__setitem__("run_id", "other-toy-run"),
                "associated_provenance": lambda value: value["provenance"]["inputs"].__setitem__(
                    0, copy.deepcopy(value["provenance"]["inputs"][1])
                ),
                "raw_derived_empirical": mutate_raw_derived_empirical,
            }
            for name, mutate in mutations.items():
                with self.subTest(mode="write", mutation=name):
                    changed = copy.deepcopy(result)
                    mutate(changed)
                    summary.write_bytes(canonical_json_bytes(changed))
                    candidate = repository_root / f"setup-toy-{name}-metrics.json"
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
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            repository_root, result = self.stage_validated_result(Path(temporary), self.synthetic_result())
            self.assertTrue(validate_analysis_result(
                result,
                enforce_frozen_inputs=False,
                repository_root=repository_root,
            ))
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
                        validate_analysis_result(
                            changed,
                            enforce_frozen_inputs=False,
                            repository_root=repository_root,
                        )


if __name__ == "__main__":
    unittest.main()
