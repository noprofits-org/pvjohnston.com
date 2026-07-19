#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf '%s\n' \
    'Scheduled:  run-model.sh --task analysis|identification --case CASE-XXXX --model LABEL --run 01|02|03' \
    'Diagnostic: run-model.sh --task analysis|identification --case CASE-XXXX --model LABEL --diagnostic NN' \
    '' \
    'The frozen run matrix selects the only permitted model adapter.'
}

task=''
case_id=''
model_label=''
run_number=''
diagnostic_number=''

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task) task="${2:-}"; shift 2 ;;
    --case) case_id="${2:-}"; shift 2 ;;
    --model) model_label="${2:-}"; shift 2 ;;
    --run) run_number="${2:-}"; shift 2 ;;
    --diagnostic) diagnostic_number="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

if [[ "$task" != 'analysis' && "$task" != 'identification' ]]; then
  printf 'Invalid --task. Use analysis or identification.\n' >&2
  exit 2
fi
if [[ ! "$case_id" =~ ^CASE-[A-Z0-9]{4}$ ]]; then
  printf 'Invalid --case. Expected CASE- followed by four uppercase letters/digits.\n' >&2
  exit 2
fi
if [[ ! "$model_label" =~ ^[a-z0-9][a-z0-9._-]*$ ]]; then
  printf 'Invalid --model label.\n' >&2
  exit 2
fi
if [[ -n "$run_number" && -n "$diagnostic_number" ]]; then
  printf 'Choose either --run or --diagnostic, not both.\n' >&2
  exit 2
fi
if [[ -n "$run_number" ]]; then
  if [[ ! "$run_number" =~ ^0[1-3]$ ]]; then
    printf 'Invalid --run. Scheduled pilot runs are 01, 02, or 03.\n' >&2
    exit 2
  fi
  run_kind='scheduled'
  run_id="$run_number"
elif [[ -n "$diagnostic_number" ]]; then
  if [[ ! "$diagnostic_number" =~ ^[0-9]{2}$ ]]; then
    printf 'Invalid --diagnostic. Use a two-digit diagnostic identifier.\n' >&2
    exit 2
  fi
  run_kind='diagnostic'
  run_id="$diagnostic_number"
else
  printf 'Missing --run or --diagnostic.\n' >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
experiment_dir="$(cd "$script_dir/.." && pwd)"
manifest="$experiment_dir/data/manifest.json"
matrix="$experiment_dir/run-matrix.json"
lock_file="$experiment_dir/collection-lock.json"

node "$script_dir/verify-collection-lock.mjs" "$experiment_dir" >/dev/null

dataset_version="$(node -e 'const m=require(process.argv[1]); process.stdout.write(m.dataset_version)' "$manifest")"
if [[ ! "$dataset_version" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  printf 'Unsafe dataset version in manifest.\n' >&2
  exit 3
fi
if ! node -e 'const m=require(process.argv[1]); if (!m.models[process.argv[2]]) process.exit(1)' "$matrix" "$model_label"; then
  printf 'Model label is absent from the frozen run matrix: %s\n' "$model_label" >&2
  exit 3
fi

condition="$(node -e 'const m=require(process.argv[1]); process.stdout.write(m.evidence_condition)' "$manifest")"
case_file="$(node -e '
  const fs=require("fs"), path=require("path");
  const root=process.argv[1], wanted=process.argv[2], m=require(path.join(root,"data/manifest.json"));
  for (const entry of m.cases) {
    const full=path.join(root,"data",entry.file), item=JSON.parse(fs.readFileSync(full,"utf8"));
    if (entry.case_id===wanted && item.case_id===wanted) { process.stdout.write(full); process.exit(0); }
  }
  process.exit(1);
' "$experiment_dir" "$case_id")" || {
  printf 'Case is absent from the frozen manifest: %s\n' "$case_id" >&2
  exit 3
}

prompt_relative="$(node -e 'const m=require(process.argv[1]); process.stdout.write(m.tasks[process.argv[2]].prompt)' "$matrix" "$task")"
adapter_relative="$(node -e 'const m=require(process.argv[1]); process.stdout.write(m.models[process.argv[2]].adapter)' "$matrix" "$model_label")"
prompt_file="$experiment_dir/$prompt_relative"
adapter_file="$experiment_dir/$adapter_relative"
if [[ ! -x "$adapter_file" ]]; then
  printf 'Frozen adapter is not executable: %s\n' "$adapter_relative" >&2
  exit 3
fi

output_dir="$experiment_dir/outputs/$dataset_version/$run_kind/$task"
if [[ "$run_kind" == 'scheduled' ]]; then
  output_base="${model_label}__${condition}__${case_id}__run-${run_id}"
else
  output_base="${model_label}__${condition}__${case_id}__diagnostic-${run_id}"
fi
output_file="$output_dir/${output_base}.md"
invalid_file="$output_dir/${output_base}.invalid.md"
metadata_file="$output_dir/${output_base}.run.json"
stderr_file="$output_dir/${output_base}.stderr.txt"
marker_file="$output_dir/${output_base}.complete.json"
lock_dir="$output_dir/.${output_base}.lock"

mkdir -p "$output_dir"
if ! mkdir "$lock_dir" 2>/dev/null; then
  printf 'Another process owns this run slot: %s\n' "$output_base" >&2
  exit 4
fi

stage_dir="$(mktemp -d "${TMPDIR:-/tmp}/off-tonic-model.XXXXXX")"
cleanup() {
  rm -rf "$stage_dir"
  rmdir "$lock_dir" 2>/dev/null || true
}
trap cleanup EXIT

if [[ -e "$output_file" || -e "$invalid_file" || -e "$metadata_file" || -e "$marker_file" ]]; then
  printf 'Refusing to overwrite existing run: %s\n' "$output_base" >&2
  exit 4
fi

node "$script_dir/build-prompt.mjs" "$experiment_dir" "$task" "$case_id" > "$stage_dir/prompt.md"
started_at="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

set +e
(
  cd "$stage_dir"
  "$adapter_file" < prompt.md
) > "$stage_dir/response.md" 2> "$stage_dir/stderr.txt"
command_status=$?
set -e
ended_at="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

validation_status='not_run'
validation_error=''
if [[ $command_status -eq 0 ]]; then
  set +e
  node "$script_dir/validate-output.mjs" "$task" "$case_id" "$case_file" "$stage_dir/response.md" \
    > "$stage_dir/validation.stdout" 2> "$stage_dir/validation.stderr"
  validation_exit=$?
  set -e
  if [[ $validation_exit -eq 0 ]]; then
    validation_status='valid'
  else
    validation_status='invalid'
    validation_error="$(tr '\n' ' ' < "$stage_dir/validation.stderr" | cut -c1-1000)"
  fi
else
  validation_status='command_failed'
fi

if [[ "$validation_status" == 'valid' ]]; then
  staged_response="$stage_dir/${output_base}.md"
  final_response="$output_file"
else
  staged_response="$stage_dir/${output_base}.invalid.md"
  final_response="$invalid_file"
fi
mv "$stage_dir/response.md" "$staged_response"
staged_stderr="$stage_dir/${output_base}.stderr.txt"
mv "$stage_dir/stderr.txt" "$staged_stderr"
staged_metadata="$stage_dir/${output_base}.run.json"

node "$script_dir/write-run-metadata.mjs" \
  "$staged_metadata" "$matrix" "$manifest" "$lock_file" "$prompt_file" "$stage_dir/prompt.md" \
  "$case_file" "$staged_response" "$staged_stderr" "$adapter_file" \
  "$task" "$case_id" "$model_label" "$run_kind" "$run_id" "$started_at" "$ended_at" \
  "$command_status" "$validation_status" "$validation_error"

chmod 0444 "$staged_response" "$staged_metadata" "$staged_stderr"
mv "$staged_response" "$final_response"
mv "$staged_stderr" "$stderr_file"
mv "$staged_metadata" "$metadata_file"
node "$script_dir/write-completion-marker.mjs" "$marker_file" "$metadata_file" "$final_response" "$stderr_file"
chmod 0444 "$marker_file"

if [[ "$validation_status" != 'valid' ]]; then
  printf 'Run retained as %s (%s).\n' "$final_response" "$validation_status" >&2
  exit 5
fi
printf '%s\n' "$output_file"
