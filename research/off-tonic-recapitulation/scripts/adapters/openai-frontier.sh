#!/usr/bin/env bash
set -euo pipefail

# This adapter intentionally tests the Codex CLI model system, not a bare API
# model. The frozen stage directory contains only the prompt assembled by the
# runner. Tool-bearing features are disabled where the CLI exposes a switch;
# the read-only sandbox is a second boundary.
response_file="$(mktemp "${TMPDIR:-/tmp}/off-tonic-codex-response.XXXXXX")"
cleanup() {
  rm -f "$response_file"
}
trap cleanup EXIT

codex exec \
  --model gpt-5.6-sol \
  --ephemeral \
  --ignore-user-config \
  --ignore-rules \
  --skip-git-repo-check \
  --strict-config \
  --sandbox read-only \
  --color never \
  --disable apps \
  --disable browser_use \
  --disable code_mode \
  --disable code_mode_host \
  --disable code_mode_only \
  --disable computer_use \
  --disable deferred_executor \
  --disable hooks \
  --disable image_generation \
  --disable in_app_browser \
  --disable multi_agent \
  --disable shell_tool \
  --disable tool_suggest \
  --disable unified_exec \
  --disable workspace_dependencies \
  -c 'approval_policy="never"' \
  -c 'model_reasoning_effort="high"' \
  -c 'model_verbosity="low"' \
  -c 'web_search="disabled"' \
  --output-last-message "$response_file" \
  - >/dev/null

cat "$response_file"
