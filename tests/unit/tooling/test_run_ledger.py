from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[3] / ".agents" / "skills" / "_tooling" / "run_ledger.py"


def run_script(*args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_record_appends_a_jsonl_event_and_generates_run_id(tmp_path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    env = os.environ.copy()
    env["BEEMBHAI_RUN_LEDGER_PATH"] = str(ledger_path)

    result = run_script(
        "record",
        "--event",
        "started",
        "--story-key",
        "BEEM-16",
        "--skill-name",
        "story-implement",
        "--branch",
        "feat/BEEM-16-bootstrap",
        "--step",
        "story-design",
        "--changed-file",
        "docs/product/epics/BEEM-3/stories/BEEM-16/story-design.md",
        "--external-action",
        "jira:transition:In Progress",
        "--field",
        "source=direct",
        env=env,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["ledger_path"] == str(ledger_path)
    assert output["run_id"]
    assert output["entry"]["event"] == "started"
    assert output["entry"]["story_key"] == "BEEM-16"
    assert output["entry"]["skill_name"] == "story-implement"
    assert output["entry"]["changed_files"] == [
        "docs/product/epics/BEEM-3/stories/BEEM-16/story-design.md"
    ]
    assert output["entry"]["external_actions"] == ["jira:transition:In Progress"]
    assert output["entry"]["metadata"] == {"source": "direct"}

    stored_lines = ledger_path.read_text(encoding="utf-8").splitlines()
    assert len(stored_lines) == 1
    stored_entry = json.loads(stored_lines[0])
    assert stored_entry["run_id"] == output["run_id"]
    assert stored_entry["event"] == "started"
    assert stored_entry["story_key"] == "BEEM-16"


def test_latest_finds_the_most_recent_matching_run(tmp_path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    env = os.environ.copy()
    env["BEEMBHAI_RUN_LEDGER_PATH"] = str(ledger_path)

    first = run_script(
        "record",
        "--event",
        "started",
        "--story-key",
        "BEEM-16",
        "--skill-name",
        "story-design",
        "--branch",
        "feat/BEEM-16-a",
        env=env,
    )
    second = run_script(
        "record",
        "--event",
        "started",
        "--story-key",
        "BEEM-16",
        "--skill-name",
        "story-design",
        "--branch",
        "feat/BEEM-16-b",
        env=env,
    )
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr

    result = run_script("latest", "--story-key", "BEEM-16", env=env)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip()

    latest_run_id = result.stdout.strip()
    assert latest_run_id != ""
    assert latest_run_id in ledger_path.read_text(encoding="utf-8")
    assert latest_run_id == json.loads(second.stdout)["run_id"]


def test_preview_summarises_changed_files_commits_and_actions(tmp_path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    env = os.environ.copy()
    env["BEEMBHAI_RUN_LEDGER_PATH"] = str(ledger_path)

    start = run_script(
        "record",
        "--event",
        "started",
        "--story-key",
        "BEEM-16",
        "--skill-name",
        "implement",
        "--branch",
        "feat/BEEM-16-bootstrap",
        "--changed-file",
        "app/auth/router.py",
        "--changed-file",
        "app/main.py",
        env=env,
    )
    run_id = json.loads(start.stdout)["run_id"]

    finish = run_script(
        "record",
        "--run-id",
        run_id,
        "--event",
        "completed",
        "--story-key",
        "BEEM-16",
        "--skill-name",
        "implement",
        "--branch",
        "feat/BEEM-16-bootstrap",
        "--commit",
        "abc1234",
        "--external-action",
        "git:commit",
        "--notes",
        "seeded bootstrap admin",
        env=env,
    )
    assert finish.returncode == 0, finish.stderr

    preview = run_script("preview", "--run-id", run_id, env=env)
    assert preview.returncode == 0, preview.stderr
    stdout = preview.stdout
    assert f"Target run: {run_id}" in stdout
    assert "Changed files:" in stdout
    assert "- app/auth/router.py" in stdout
    assert "- app/main.py" in stdout
    assert "Commits:" in stdout
    assert "- abc1234" in stdout
    assert "External actions:" in stdout
    assert "- git:commit" in stdout
    assert "seeded bootstrap admin" in stdout


def test_hook_appends_a_post_tool_use_event_from_stdin(tmp_path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    env = os.environ.copy()
    env["BEEMBHAI_RUN_LEDGER_PATH"] = str(ledger_path)

    payload = {
        "session_id": "session-123",
        "turn_id": "turn-456",
        "cwd": "/workspace/bheembhai",
        "hook_event_name": "PostToolUse",
        "permission_mode": "default",
        "tool_name": "Bash",
        "tool_use_id": "tool-789",
        "tool_input": {"command": "echo hello"},
        "tool_response": {"stdout": "hello"},
        "last_assistant_message": "Completed the command.",
    }

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "hook"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
        input=json.dumps(payload),
    )

    assert result.returncode == 0, result.stderr
    stored_lines = ledger_path.read_text(encoding="utf-8").splitlines()
    assert len(stored_lines) == 1
    stored_entry = json.loads(stored_lines[0])
    assert stored_entry["run_id"] == "turn-456"
    assert stored_entry["session_id"] == "session-123"
    assert stored_entry["turn_id"] == "turn-456"
    assert stored_entry["event"] == "posttooluse"
    assert stored_entry["step"] == "Bash"
    assert stored_entry["metadata"]["tool_name"] == "Bash"
    assert stored_entry["metadata"]["tool_use_id"] == "tool-789"
    assert stored_entry["metadata"]["tool_input"] == {"command": "echo hello"}
    assert stored_entry["metadata"]["tool_response"] == {"stdout": "hello"}
