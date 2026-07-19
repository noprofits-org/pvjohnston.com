#!/usr/bin/env bash
set -euo pipefail

# OAuth/keychain authentication is deliberately allowed, so this cannot use
# Claude Code's --bare mode. Safe mode removes user/project customizations;
# the remaining flags remove tools, MCP, slash commands, persistence, and
# automatic model fallback for a fresh one-shot model-system invocation.
claude \
  --print \
  --output-format text \
  --model claude-fable-5 \
  --effort high \
  --safe-mode \
  --disable-slash-commands \
  --tools "" \
  --strict-mcp-config \
  --mcp-config '{"mcpServers":{}}' \
  --no-session-persistence
