"""Complete, visibly synthetic workflow ledgers for setup-only replay tests."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


EXPERIMENT = "muon-survival-two-frames"
GRAPH_SHA256 = "e50f12475131efe1fa9313fd2a7e9c04c049355356b26a69362afe52a418d404"


class WorkflowFixture:
    def __init__(self, temporary_root: Path, source_experiment_dir: Path) -> None:
        self.repository_root = temporary_root / "setup-toy-repository"
        self.experiment_dir = self.repository_root / "research" / EXPERIMENT
        self.experiment_dir.mkdir(parents=True)
        shutil.copytree(source_experiment_dir / "workflow", self.experiment_dir / "workflow")
        shutil.copy2(source_experiment_dir / "workflow.jsonl", self.experiment_dir / "workflow.jsonl")
        self.workflow_path = self.experiment_dir / "workflow.jsonl"
        self.sequence = len(self.workflow_path.read_text(encoding="utf-8").splitlines())
        self.submission_sequence: int | None = None

    @staticmethod
    def event_id(sequence: int) -> str:
        return f"00000000-0000-4000-8000-{sequence:012d}"

    @staticmethod
    def journal_id(sequence: int) -> str:
        return f"10000000-0000-4000-8000-{sequence:012d}"

    def _artifact(self, sequence: int, event_id: str, stem: str, content: str) -> dict:
        source_relative = f"research/{EXPERIMENT}/workflow/{stem}.md"
        snapshot_relative = f"research/{EXPERIMENT}/workflow/evidence/{sequence:04d}-01-{event_id}-{stem}.md"
        payload = content.encode("utf-8")
        (self.repository_root / source_relative).write_bytes(payload)
        (self.repository_root / snapshot_relative).write_bytes(payload)
        return {
            "source_path": source_relative,
            "snapshot_path": snapshot_relative,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
        }

    def _common(self, sequence: int, event_id: str, event_type: str, actor: str, role: str, from_state: str, to_state: str) -> dict:
        return {
            "schema": 1,
            "graph_version": 1,
            "graph_sha256": GRAPH_SHA256,
            "event_id": event_id,
            "timestamp": f"2000-01-01T00:00:{sequence:02d}.000Z",
            "experiment": EXPERIMENT,
            "sequence": sequence,
            "type": event_type,
            "actor": actor,
            "role": role,
            "from": from_state,
            "to": to_state,
            "context": {"branch": f"post/{EXPERIMENT}", "parent_commit": "0" * 40},
        }

    def _append(self, event: dict) -> dict:
        with self.workflow_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, separators=(",", ":")) + "\n")
        self.sequence = event["sequence"]
        return event

    def submit(self, *, from_state: str, to_state: str, role: str, actor: str, stem: str, content: str) -> dict:
        sequence = self.sequence + 1
        event_id = self.event_id(sequence)
        event = self._common(sequence, event_id, "submit", actor, role, from_state, to_state)
        event.update({
            "artifacts": [self._artifact(sequence, event_id, stem, content)],
            "journal_checkpoint_event_id": self.journal_id(sequence),
            "note": "Complete setup-toy graph fixture; no production execution.",
        })
        self.submission_sequence = sequence
        return self._append(event)

    def review(self, *, from_state: str, to_state: str, decision: str, actor: str, stem: str, content: str) -> dict:
        if self.submission_sequence is None:
            raise AssertionError("review fixture requires a pending submission")
        sequence = self.sequence + 1
        event_id = self.event_id(sequence)
        event = self._common(sequence, event_id, "review", actor, "independent_reviewer", from_state, to_state)
        event.update({
            "decision": decision,
            "submission_sequence": self.submission_sequence,
            "artifacts": [self._artifact(sequence, event_id, stem, content)],
            "journal_checkpoint_event_id": self.journal_id(sequence),
            "note": "Independent setup-toy review fixture; no production execution.",
        })
        self.submission_sequence = None
        return self._append(event)

    def approve_setup(self) -> dict:
        self.submit(
            from_state="setup", to_state="setup_review", role="experiment_engineer",
            actor="setup-toy-engineer", stem="setup-toy-v3", content="# Complete setup-toy handoff\n",
        )
        return self.review(
            from_state="setup_review", to_state="execute", decision="approve",
            actor="setup-toy-reviewer", stem="setup-toy-review-v3", content="# Approved complete setup-toy handoff\n",
        )

    def approve_run(self, run_id: str = "run-001") -> dict:
        self.submit(
            from_state="execute", to_state="run_review", role="run_operator",
            actor="setup-toy-run-operator", stem="run-toy-v1", content=f"# Complete setup-toy run receipt\n\n{run_id}\n",
        )
        return self.review(
            from_state="run_review", to_state="analyze", decision="approve",
            actor="setup-toy-run-reviewer", stem="run-toy-review-v1", content=f"# Approved immutable setup-toy run\n\n{run_id}\n",
        )

    def submit_analysis(self) -> dict:
        return self.submit(
            from_state="analyze", to_state="analysis_review", role="analyst",
            actor="setup-toy-analyst", stem="analysis-toy-v1", content="# Complete setup-toy analysis handoff\n",
        )

    def register_retry(self) -> dict:
        self.submit(
            from_state="execute", to_state="run_review", role="run_operator",
            actor="setup-toy-run-operator", stem="run-toy-incomplete-v1", content="# Incomplete setup-toy run-001 receipt\n",
        )
        return self.review(
            from_state="run_review", to_state="execute", decision="registered_retry",
            actor="setup-toy-retry-reviewer", stem="run-toy-retry-review-v1", content="# Registered setup-toy retry of run-001\n",
        )
