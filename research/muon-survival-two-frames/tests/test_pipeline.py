from __future__ import annotations

import copy
import json
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
from analyze import AnalysisSpec, build_analysis_result, write_or_check_result  # noqa: E402
from bundle import (  # noqa: E402
    RunExecutionError,
    RunSpec,
    create_new_run_directory,
    execute_and_seal,
    generate_lifetimes,
    save_array_exclusive,
    validate_run_bundle,
)
from contract import ContractError, authorize_run_request, run_namespaces, validate_recorded_run_authorization  # noqa: E402
from render_figure import HEIGHT_PX, WIDTH_PX, render_png_bytes, write_or_check_png  # noqa: E402


class PipelineContractTests(unittest.TestCase):
    def workflow_event(self, *, decision: str, from_state: str, event_id: str = "event-1") -> dict:
        return {
            "sequence": 1,
            "event_id": event_id,
            "type": "review",
            "from": from_state,
            "to": "execute",
            "decision": decision,
        }

    def write_ledger(self, path: Path, event: dict) -> None:
        path.write_text(f"{json.dumps(event, separators=(',', ':'))}\n", encoding="utf-8")

    def toy_spec(self) -> RunSpec:
        return RunSpec(
            experiment="muon-survival-two-frames",
            purpose="setup-toy",
            run_id="toy-run",
            command="setup-only toy runner",
            seed=0,
            draw_count=16,
            scale_s=1e-6,
            lineage={"fixture": {"path": "setup-toy/input", "sha256": "0" * 64}},
            authorization={"kind": "setup-toy"},
            platform={"environment": "setup-toy"},
            path_prefix="setup-toy/toy-run",
        )

    def test_only_graph_authorized_normal_and_retry_run_ids_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            base = Path(temporary)
            ledger = base / "setup-toy-workflow.jsonl"
            runs = base / "setup-toy-runs"
            self.write_ledger(ledger, self.workflow_event(decision="approve", from_state="setup_review"))
            normal = authorize_run_request("run-001", workflow_path=ledger, runs_dir=runs)
            self.assertEqual(normal["kind"], "normal")
            validate_recorded_run_authorization("run-001", normal, workflow_path=ledger)
            with self.assertRaises(ContractError):
                authorize_run_request("run-002", workflow_path=ledger, runs_dir=runs)
            with self.assertRaises(ContractError):
                authorize_run_request("run-003", workflow_path=ledger, runs_dir=runs)

            prior = runs / "run-001"
            prior.mkdir(parents=True)
            self.write_ledger(ledger, self.workflow_event(decision="registered_retry", from_state="run_review", event_id="retry-1"))
            retry = authorize_run_request("run-002", workflow_path=ledger, runs_dir=runs)
            self.assertEqual(retry["kind"], "registered_retry")
            validate_recorded_run_authorization("run-002", retry, workflow_path=ledger)
            (prior / "COMPLETE.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "complete run-001"):
                authorize_run_request("run-002", workflow_path=ledger, runs_dir=runs)

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
            self.assertTrue(validate_run_bundle(run_dir, spec)["valid"])
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
            analysis_admission={"event_id": "setup-toy", "sequence": 1, "decision": "approve", "event_sha256": "4" * 64},
        )
        return build_analysis_result(sample, spec)

    def test_analysis_result_png_and_metrics_regenerate_and_check_on_synthetic_fixture(self) -> None:
        result = self.synthetic_result()
        self.assertEqual(result["outcome_kind"], "understanding-observations-no-verdict")
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            base = Path(temporary)
            summary = base / "setup-toy-summary.json"
            figure = base / "setup-toy-figure.png"
            metrics = base / "setup-toy-metrics.json"
            write_or_check_result(summary, result, check=False)
            write_or_check_result(summary, result, check=True)
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
                write_or_check_result(summary, result, check=True)


if __name__ == "__main__":
    unittest.main()
