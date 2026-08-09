#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import { createHash, randomUUID } from 'node:crypto';
import {
  closeSync,
  constants as fsConstants,
  existsSync,
  fstatSync,
  fsyncSync,
  lstatSync,
  mkdirSync,
  openSync,
  readFileSync,
  readSync,
  readdirSync,
  realpathSync,
  renameSync,
  unlinkSync,
  writeFileSync,
  writeSync,
} from 'node:fs';
import { hostname } from 'node:os';
import { basename, dirname, isAbsolute, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const schemaVersion = 1;
const maxRecordBytes = 256 * 1024;
const maxEvidenceBytes = 1024 * 1024;
const maxEvidenceTotalBytes = 4 * 1024 * 1024;
const maxWorkflowLogBytes = 64 * 1024 * 1024;
const maxJournalBytes = 64 * 1024 * 1024;
const maxNoteCharacters = 10_000;
const workflowRecoveryReserveBytes = maxRecordBytes;
const maxNormalWorkflowLogBytes = maxWorkflowLogBytes - workflowRecoveryReserveBytes;
const maxArtifacts = 16;
const experimentPattern = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const postBranchPattern = /^post\/[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const identifierPattern = /^[A-Za-z0-9][A-Za-z0-9._:@-]{0,127}$/;
const statePattern = /^[a-z][a-z0-9_]*$/;
const sha256Pattern = /^[a-f0-9]{64}$/;
const uuidPattern = /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const defaultRoot = resolve(scriptDirectory, '..');
const defaultGraphPath = resolve(scriptDirectory, '../research/workflow.graph.v1.json');
const noFollow = fsConstants.O_NOFOLLOW ?? 0;

class CliError extends Error {}

function fail(message) {
  throw new CliError(message);
}

function usage() {
  console.log(`Usage:
  node scripts/research-workflow.mjs graph [--format mermaid|json]
  node scripts/research-workflow.mjs init --experiment <slug> --post-type <type> \\
    --question <text> --journal <session> --actor <id> [--shelf-entry <heading>]
  node scripts/research-workflow.mjs status --experiment <slug> [--json]
  node scripts/research-workflow.mjs submit --experiment <slug> --actor <id> \\
    --artifact <workflow-receipt> [--artifact <path> ...] [--note <text>]
  node scripts/research-workflow.mjs review --experiment <slug> --actor <id> \\
    --decision <allowed-decision> --artifact <workflow-review> [--note <text>]
  node scripts/research-workflow.mjs verify (--experiment <slug> | --all)
  node scripts/research-workflow.mjs repair --experiment <slug> [--unlock-stale]

The CLI records and verifies handoffs. It never runs an experiment.`);
}

function parseOptions(args) {
  const options = {};
  const booleanOptions = new Set(['all', 'json', 'unlock-stale']);
  for (let index = 0; index < args.length; index += 1) {
    const token = args[index];
    if (!token.startsWith('--') || token.length === 2) fail(`unexpected argument: ${token}`);
    const key = token.slice(2);
    if (booleanOptions.has(key)) {
      if (Object.hasOwn(options, key)) fail(`duplicate option: --${key}`);
      options[key] = true;
      continue;
    }
    const value = args[index + 1];
    if (value === undefined || value.startsWith('--')) fail(`--${key} requires a value`);
    index += 1;
    if (key === 'artifact') {
      options.artifact ??= [];
      options.artifact.push(value);
    } else {
      if (Object.hasOwn(options, key)) fail(`duplicate option: --${key}`);
      options[key] = value;
    }
  }
  return options;
}

function requireOnly(options, allowed) {
  for (const key of Object.keys(options)) {
    if (!allowed.has(key)) fail(`unknown option: --${key}`);
  }
}

function required(options, key) {
  const value = options[key];
  if (typeof value !== 'string' || !value.trim()) fail(`--${key} is required`);
  return value.trim();
}

function optional(options, key) {
  const value = options[key];
  return typeof value === 'string' && value.trim() ? value.trim() : undefined;
}

function optionalNote(options) {
  const note = optional(options, 'note');
  if (note && note.length > maxNoteCharacters) {
    fail(`--note is too long; maximum ${maxNoteCharacters} characters`);
  }
  return note;
}

function validateIdentifier(value, label) {
  if (!identifierPattern.test(value)) fail(`${label} must be a stable ID using letters, digits, and ._:@-`);
  return value;
}

function validateExperiment(value) {
  if (!experimentPattern.test(value)) {
    fail('experiment must begin with a lowercase letter and use lowercase letters, digits, and single hyphens');
  }
  return value;
}

function repositoryRoot() {
  const requested = process.env.RESEARCH_WORKFLOW_ROOT
    ? resolve(process.env.RESEARCH_WORKFLOW_ROOT)
    : defaultRoot;
  if (!existsSync(requested)) fail(`repository root does not exist: ${requested}`);
  return realpathSync(requested);
}

function pathIsInside(parent, child) {
  const difference = relative(parent, child);
  return difference !== ''
    && difference !== '..'
    && !difference.startsWith(`..${sep}`)
    && !isAbsolute(difference);
}

function repoPath(root, path) {
  return relative(root, path).split(sep).join('/');
}

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function exactKeys(value, allowed, label) {
  if (!isPlainObject(value)) fail(`${label} must be an object`);
  const unexpected = Object.keys(value).filter((key) => !allowed.has(key));
  if (unexpected.length) fail(`${label} has unexpected field ${unexpected[0]}`);
}

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function graphPathForVersion(version) {
  if (process.env.RESEARCH_WORKFLOW_GRAPH) return resolve(process.env.RESEARCH_WORKFLOW_GRAPH);
  return resolve(scriptDirectory, `../research/workflow.graph.v${version}.json`);
}

function loadGraph(path = process.env.RESEARCH_WORKFLOW_GRAPH
  ? resolve(process.env.RESEARCH_WORKFLOW_GRAPH)
  : defaultGraphPath) {
  let raw;
  let graph;
  try {
    raw = readFileSync(path);
    graph = JSON.parse(raw.toString('utf8'));
  } catch (error) {
    fail(`cannot read workflow graph ${path}: ${error.message}`);
  }
  if (!isPlainObject(graph) || graph.schema_version !== schemaVersion
    || !Number.isInteger(graph.graph_version) || graph.graph_version < 1) {
    fail('workflow graph has an unsupported schema or graph version');
  }
  if (!isPlainObject(graph.states)) fail('workflow graph states must be an object');
  if (!statePattern.test(graph.initial_state) || !Object.hasOwn(graph.states, graph.initial_state)) {
    fail('workflow graph initial_state is missing or invalid');
  }
  if (!isPlainObject(graph.states[graph.initial_state])
    || graph.states[graph.initial_state].kind !== 'work') {
    fail('workflow graph initial_state must be a work state');
  }
  if (!Array.isArray(graph.terminal_states) || !graph.terminal_states.length
    || new Set(graph.terminal_states).size !== graph.terminal_states.length) {
    fail('workflow graph must declare at least one unique terminal state');
  }
  const terminals = new Set(graph.terminal_states);
  const reverse = new Map(Object.keys(graph.states).map((name) => [name, []]));
  const reviewSubmitters = new Map(Object.keys(graph.states).map((name) => [name, []]));
  for (const [name, state] of Object.entries(graph.states)) {
    if (!statePattern.test(name) || !isPlainObject(state)) fail(`workflow state ${name} is invalid`);
    if (!['work', 'review', 'terminal'].includes(state.kind)) fail(`workflow state ${name} has invalid kind`);
    if (!identifierPattern.test(state.role || '') || typeof state.label !== 'string' || !state.label.trim()
      || typeof state.description !== 'string' || !state.description.trim()) {
      fail(`workflow state ${name} is missing valid role, label, or description`);
    }
    if (state.kind !== 'terminal'
      && (typeof state.artifact_contract !== 'string' || !state.artifact_contract.trim())) {
      fail(`workflow state ${name} is missing an artifact contract`);
    }
    if (state.kind === 'work') {
      if (!Number.isFinite(state.lineage_order) || state.lineage_order <= 0) {
        fail(`workflow work state ${name} needs a positive lineage_order`);
      }
      if (!statePattern.test(state.submit_to || '') || !Object.hasOwn(graph.states, state.submit_to)
        || graph.states[state.submit_to]?.kind !== 'review') {
        fail(`workflow work state ${name} must submit to a review state`);
      }
      reverse.get(state.submit_to).push(name);
      reviewSubmitters.get(state.submit_to).push(name);
    } else if (state.kind === 'review') {
      if (!isPlainObject(state.decisions) || !Object.keys(state.decisions).length) {
        fail(`workflow review state ${name} has no decisions`);
      }
      if (!Object.hasOwn(state.decisions, 'approve')) {
        fail(`workflow review state ${name} must declare an approve decision`);
      }
      for (const [decision, target] of Object.entries(state.decisions)) {
        if (!statePattern.test(decision) || !statePattern.test(target)
          || !Object.hasOwn(graph.states, target)) {
          fail(`workflow review state ${name} has invalid decision ${decision}`);
        }
        if (!['work', 'terminal'].includes(graph.states[target]?.kind)) {
          fail(`workflow review state ${name} cannot target review state ${target}; decisions must target work or terminal`);
        }
        reverse.get(target).push(name);
      }
    } else {
      if (!terminals.has(name)) fail(`workflow terminal state ${name} is absent from terminal_states`);
      if (!['success', 'parked'].includes(state.terminal_outcome)) {
        fail(`workflow terminal state ${name} has invalid terminal_outcome`);
      }
    }
  }
  for (const terminal of terminals) {
    if (!statePattern.test(terminal) || graph.states[terminal]?.kind !== 'terminal') {
      fail(`workflow terminal_states contains nonterminal ${terminal}`);
    }
  }
  const successfulTerminals = [...terminals]
    .filter((name) => graph.states[name].terminal_outcome === 'success');
  if (successfulTerminals.length !== 1) {
    fail('workflow graph must declare exactly one successful terminal');
  }
  for (const [name, state] of Object.entries(graph.states)) {
    if (state.kind !== 'review') continue;
    const submitters = reviewSubmitters.get(name);
    if (submitters.length !== 1) {
      fail(`workflow review state ${name} must have exactly one submitting work state`);
    }
    const approveTarget = graph.states[state.decisions.approve];
    const submitter = graph.states[submitters[0]];
    if (approveTarget.kind === 'terminal' && approveTarget.terminal_outcome !== 'success') {
      fail(`workflow review state ${name} approve decision cannot target a non-success terminal`);
    }
    if (approveTarget.kind !== 'terminal'
      && approveTarget.lineage_order <= submitter.lineage_order) {
      fail(`workflow review state ${name} approve decision must advance lineage`);
    }
    for (const [decision, targetName] of Object.entries(state.decisions)) {
      if (decision === 'approve') continue;
      const target = graph.states[targetName];
      if (target.kind === 'terminal' && target.terminal_outcome === 'success') {
        fail(`workflow review state ${name} non-approve decision ${decision} cannot target the successful terminal`);
      }
      if (target.kind === 'work' && target.lineage_order > submitter.lineage_order) {
        fail(`workflow review state ${name} non-approve decision ${decision} cannot advance lineage`);
      }
    }
  }

  const reached = new Set([graph.initial_state]);
  const queue = [graph.initial_state];
  while (queue.length) {
    const name = queue.shift();
    const state = graph.states[name];
    const targets = state.kind === 'work'
      ? [state.submit_to]
      : state.kind === 'review' ? Object.values(state.decisions) : [];
    for (const target of targets) {
      if (!reached.has(target)) {
        reached.add(target);
        queue.push(target);
      }
    }
  }
  const unreachable = Object.keys(graph.states).filter((name) => !reached.has(name));
  if (unreachable.length) fail(`workflow graph has unreachable states: ${unreachable.join(', ')}`);

  const reachesTerminal = new Set(terminals);
  const reverseQueue = [...terminals];
  while (reverseQueue.length) {
    const name = reverseQueue.shift();
    for (const predecessor of reverse.get(name)) {
      if (!reachesTerminal.has(predecessor)) {
        reachesTerminal.add(predecessor);
        reverseQueue.push(predecessor);
      }
    }
  }
  const trapped = Object.keys(graph.states).filter((name) => !reachesTerminal.has(name));
  if (trapped.length) fail(`workflow graph has states that cannot reach a terminal: ${trapped.join(', ')}`);

  Object.defineProperties(graph, {
    _sha256: { value: sha256(raw), enumerable: false },
    _path: { value: path, enumerable: false },
  });
  return graph;
}

function gitOutput(root, args) {
  return execFileSync('git', args, {
    cwd: root,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'ignore'],
  }).trim();
}

function repositoryContext(root) {
  try {
    return {
      branch: gitOutput(root, ['branch', '--show-current']) || null,
      parent_commit: gitOutput(root, ['rev-parse', 'HEAD']),
    };
  } catch {
    return { branch: null, parent_commit: null };
  }
}

function requireOwningPostWorktree(root, action, expectedBranch = undefined) {
  let branch;
  let topLevel;
  let gitDirectory;
  let commonDirectory;
  try {
    branch = gitOutput(root, ['branch', '--show-current']);
    topLevel = realpathSync(gitOutput(root, [
      'rev-parse', '--path-format=absolute', '--show-toplevel',
    ]));
    gitDirectory = realpathSync(gitOutput(root, [
      'rev-parse', '--path-format=absolute', '--git-dir',
    ]));
    commonDirectory = realpathSync(gitOutput(root, [
      'rev-parse', '--path-format=absolute', '--git-common-dir',
    ]));
  } catch {
    fail(`${action} requires an owning post/<slug> branch in a linked non-primary worktree`);
  }
  if (!postBranchPattern.test(branch) || topLevel !== root
    || topLevel === dirname(commonDirectory) || gitDirectory === commonDirectory) {
    fail(`${action} requires an owning post/<slug> branch in a linked non-primary worktree`);
  }
  if (expectedBranch && branch !== expectedBranch) {
    fail(`${action} belongs to ${expectedBranch}; current worktree is on ${branch}`);
  }
  return branch;
}

function experimentDirectory(root, experiment) {
  const directory = resolve(root, 'research', experiment);
  if (!pathIsInside(root, directory)) fail('experiment path escapes the repository');
  if (!existsSync(directory)) {
    fail(`missing research/${experiment}; copy research/_TEMPLATE there before initializing the workflow`);
  }
  const info = lstatSync(directory);
  if (!info.isDirectory() || info.isSymbolicLink()) {
    fail(`research/${experiment} must be a real directory, not a link`);
  }
  const realDirectory = realpathSync(directory);
  if (!pathIsInside(root, realDirectory)) fail('experiment directory resolves outside the repository');
  return realDirectory;
}

function syncDirectory(directory) {
  let descriptor;
  try {
    descriptor = openSync(directory, fsConstants.O_RDONLY | noFollow);
    const info = fstatSync(descriptor);
    if (!info.isDirectory()) fail(`managed path is not a directory: ${directory}`);
    fsyncSync(descriptor);
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
  }
}

function ensureRealChildDirectory(parent, name, { create = false } = {}) {
  const candidate = resolve(parent, name);
  if (!pathIsInside(parent, candidate) || dirname(candidate) !== parent) fail(`unsafe managed directory: ${name}`);
  if (!existsSync(candidate)) {
    if (!create) fail(`missing managed directory: ${candidate}`);
    mkdirSync(candidate, { mode: 0o755 });
    syncDirectory(parent);
  }
  const info = lstatSync(candidate);
  if (!info.isDirectory() || info.isSymbolicLink()) {
    fail(`managed directory ${candidate} must be a real directory, not a symlink`);
  }
  const real = realpathSync(candidate);
  if (!pathIsInside(parent, real)) fail(`managed directory resolves outside its parent: ${candidate}`);
  return real;
}

function managedPaths(experimentDir, { create = false } = {}) {
  const workflowDir = ensureRealChildDirectory(experimentDir, 'workflow', { create });
  const evidenceDir = ensureRealChildDirectory(workflowDir, 'evidence', { create });
  return {
    workflowDir,
    evidenceDir,
    logPath: resolve(experimentDir, 'workflow.jsonl'),
    lockPath: resolve(workflowDir, '.transition.lock'),
  };
}

function validateExistingLog(path, experimentDir) {
  if (!existsSync(path)) fail(`workflow is not initialized for ${repoPath(dirname(dirname(experimentDir)), experimentDir)}`);
  const info = lstatSync(path);
  if (!info.isFile() || info.isSymbolicLink()) fail(`workflow log must be a regular file, not a symlink: ${path}`);
  const real = realpathSync(path);
  if (dirname(real) !== experimentDir) fail('workflow log resolves outside the experiment directory');
}

function openRegular(path, flags, label, mode = 0o644) {
  let descriptor;
  try {
    descriptor = openSync(path, flags | noFollow, mode);
    if (!fstatSync(descriptor).isFile()) fail(`${label} is not a regular file`);
    return descriptor;
  } catch (error) {
    if (descriptor !== undefined) closeSync(descriptor);
    if (error instanceof CliError) throw error;
    fail(`cannot open ${label}: ${error.message}`);
  }
}

function validateOpenedManagedFile(descriptor, path, parent, label) {
  const opened = fstatSync(descriptor, { bigint: true });
  const linked = lstatSync(path, { bigint: true });
  const real = realpathSync(path);
  if (!opened.isFile() || opened.nlink !== 1n
    || !linked.isFile() || linked.isSymbolicLink() || linked.nlink !== 1n
    || linked.dev !== opened.dev || linked.ino !== opened.ino
    || !pathIsInside(parent, real)) {
    fail(`${label} changed, is linked, or resolves outside its managed directory`);
  }
  return opened;
}

function linuxBootId() {
  const path = '/proc/sys/kernel/random/boot_id';
  if (!existsSync(path)) return null;
  try {
    const value = readFileSync(path, 'utf8').trim();
    return uuidPattern.test(value) ? value.toLowerCase() : null;
  } catch {
    return null;
  }
}

function linuxProcessStartTicks(pid) {
  const path = `/proc/${pid}/stat`;
  if (!existsSync(path)) return null;
  try {
    const value = readFileSync(path, 'utf8');
    const endOfCommand = value.lastIndexOf(') ');
    if (endOfCommand < 0) return null;
    const fieldsFromState = value.slice(endOfCommand + 2).trim().split(/\s+/);
    const startTicks = fieldsFromState[19];
    return /^\d+$/.test(startTicks || '') ? startTicks : null;
  } catch {
    return null;
  }
}

function acquireLock(paths) {
  let descriptor;
  try {
    descriptor = openSync(
      paths.lockPath,
      fsConstants.O_WRONLY | fsConstants.O_CREAT | fsConstants.O_EXCL | noFollow,
      0o600,
    );
  } catch (error) {
    if (error.code === 'EEXIST' || error.code === 'ELOOP') {
      fail(`workflow transition is locked; inspect ${paths.lockPath}, then use repair --unlock-stale only if its process is gone`);
    }
    throw error;
  }
  const identity = fstatSync(descriptor);
  let acquisitionError;
  try {
    validateOpenedManagedFile(descriptor, paths.lockPath, paths.workflowDir, 'workflow transition lock');
    writeFileSync(descriptor, `${JSON.stringify({
      pid: process.pid,
      hostname: hostname(),
      timestamp: new Date().toISOString(),
      lock_id: randomUUID(),
      boot_id: linuxBootId(),
      process_start_ticks: linuxProcessStartTicks(process.pid),
    })}\n`);
    fsyncSync(descriptor);
  } catch (error) {
    acquisitionError = error;
  } finally {
    closeSync(descriptor);
  }
  if (acquisitionError) {
    const current = lstatSync(paths.lockPath);
    if (current.isFile() && !current.isSymbolicLink()
      && current.dev === identity.dev && current.ino === identity.ino) {
      unlinkSync(paths.lockPath);
    }
    throw acquisitionError;
  }
  syncDirectory(paths.workflowDir);
  return () => {
    if (!existsSync(paths.lockPath)) fail('workflow transition lock disappeared while held');
    const current = lstatSync(paths.lockPath);
    if (!current.isFile() || current.isSymbolicLink()
      || current.dev !== identity.dev || current.ino !== identity.ino) {
      fail('workflow transition lock was replaced while held; refusing to remove it');
    }
    unlinkSync(paths.lockPath);
    syncDirectory(paths.workflowDir);
  };
}

function assertUnlocked(paths, allowLock) {
  if (!existsSync(paths.lockPath)) return;
  const info = lstatSync(paths.lockPath);
  if (!info.isFile() || info.isSymbolicLink()) fail('workflow transition lock is not a regular file');
  if (!allowLock) fail(`workflow transition is locked; retry after the active transition finishes`);
}

function clearStaleLock(paths) {
  let listed;
  try {
    listed = lstatSync(paths.lockPath);
  } catch (error) {
    if (error.code === 'ENOENT') return false;
    throw error;
  }
  if (!listed.isFile() || listed.isSymbolicLink()) {
    fail('workflow transition lock is not a regular file; refusing stale-lock removal');
  }
  const descriptor = openRegular(paths.lockPath, fsConstants.O_RDONLY, 'workflow transition lock', 0o600);
  const identity = fstatSync(descriptor);
  let content;
  try {
    if (identity.size < 2 || identity.size > 4096) fail('workflow transition lock has an invalid size');
    content = readFileSync(descriptor, 'utf8');
  } finally {
    closeSync(descriptor);
  }
  let lock;
  try {
    lock = JSON.parse(content);
  } catch (error) {
    fail(`workflow transition lock is malformed; refusing stale-lock removal: ${error.message}`);
  }
  exactKeys(lock, new Set([
    'pid', 'hostname', 'timestamp', 'lock_id', 'boot_id', 'process_start_ticks',
  ]), 'workflow transition lock');
  if (!Number.isInteger(lock.pid) || lock.pid < 1
    || typeof lock.hostname !== 'string' || !lock.hostname
    || typeof lock.timestamp !== 'string' || Number.isNaN(Date.parse(lock.timestamp))
    || !uuidPattern.test(lock.lock_id || '')
    || (lock.boot_id !== null && !uuidPattern.test(lock.boot_id || ''))
    || (lock.process_start_ticks !== null && !/^\d+$/.test(lock.process_start_ticks || ''))) {
    fail('workflow transition lock has invalid ownership metadata; refusing stale-lock removal');
  }
  if (lock.hostname !== hostname()) {
    fail(`workflow transition lock belongs to host ${lock.hostname}; refusing cross-host stale-lock removal`);
  }
  const currentBootId = linuxBootId();
  let ownerGone = Boolean(lock.boot_id && currentBootId && lock.boot_id !== currentBootId);
  if (!ownerGone) {
    try {
      process.kill(lock.pid, 0);
      const currentStartTicks = linuxProcessStartTicks(lock.pid);
      if (lock.process_start_ticks && currentStartTicks
        && lock.process_start_ticks !== currentStartTicks) {
        ownerGone = true;
      } else {
        fail(`workflow transition lock owner PID ${lock.pid} is still alive`);
      }
    } catch (error) {
      if (error instanceof CliError) throw error;
      if (error.code === 'ESRCH') ownerGone = true;
      else {
        fail(`cannot prove workflow transition lock owner PID ${lock.pid} is gone: ${error.message}`);
      }
    }
  }
  if (!ownerGone) fail('cannot prove workflow transition lock owner is gone');
  const current = lstatSync(paths.lockPath);
  if (!current.isFile() || current.isSymbolicLink()
    || current.dev !== identity.dev || current.ino !== identity.ino) {
    fail('workflow transition lock changed during stale-lock inspection; refusing removal');
  }
  unlinkSync(paths.lockPath);
  syncDirectory(paths.workflowDir);
  return true;
}

function journalDirectory(root) {
  if (process.env.RESEARCH_LOG_DIR) return resolve(process.env.RESEARCH_LOG_DIR);
  let common;
  try {
    common = gitOutput(root, ['rev-parse', '--path-format=absolute', '--git-common-dir']);
  } catch {
    fail('cannot locate the Git common directory for the research journal');
  }
  return resolve(common, 'research-journal');
}

function requireJournal(root, session) {
  validateIdentifier(session, 'journal session');
  const directory = journalDirectory(root);
  if (!existsSync(directory)) fail(`journal session does not exist: ${session}; run research-log.mjs start first`);
  const directoryInfo = lstatSync(directory);
  if (!directoryInfo.isDirectory() || directoryInfo.isSymbolicLink()) {
    fail('research journal directory must be a real directory');
  }
  const realDirectory = realpathSync(directory);
  const path = resolve(realDirectory, `${session}.jsonl`);
  if (!existsSync(path)) fail(`journal session does not exist: ${session}; run research-log.mjs start first`);
  const content = readBoundedRegular(path, {
    parent: realDirectory,
    label: `journal session ${session}`,
    maxBytes: maxJournalBytes,
  }).bytes.toString('utf8');
  if (!content.endsWith('\n')) fail(`journal session ${session} has an incomplete final record; repair it first`);
  const lines = content.split('\n').slice(0, -1);
  if (!lines.length || lines.some((line) => !line.trim())) fail(`journal session ${session} has invalid blank records`);
  let events;
  try {
    events = lines.map((line, index) => {
      try {
        return JSON.parse(line);
      } catch (error) {
        throw new Error(`invalid JSON at line ${index + 1}: ${error.message}`);
      }
    });
  } catch (error) {
    fail(`journal session ${session} is invalid: ${error.message}`);
  }
  const allowedTypes = new Set([
    'start', 'note', 'source', 'decision', 'checkpoint', 'close', 'resume', 'recovery',
  ]);
  const requiredTextByType = {
    start: ['title'],
    note: ['message'],
    source: ['source', 'finding'],
    decision: ['decision'],
    checkpoint: ['summary'],
    close: ['summary'],
    resume: ['message'],
    recovery: ['message'],
  };
  const eventIds = new Set();
  let state = null;
  for (const [index, event] of events.entries()) {
    if (!isPlainObject(event) || event.schema !== 1 || event.session !== session
      || !allowedTypes.has(event.type)
      || !uuidPattern.test(event.event_id || '') || eventIds.has(event.event_id)
      || typeof event.timestamp !== 'string' || Number.isNaN(Date.parse(event.timestamp))
      || new Date(event.timestamp).toISOString() !== event.timestamp
      || !isPlainObject(event.context)) {
      fail(`journal session ${session} has mixed-session or malformed common fields at record ${index + 1}`);
    }
    eventIds.add(event.event_id);
    for (const field of requiredTextByType[event.type]) {
      if (typeof event[field] !== 'string' || !event[field].trim()) {
        fail(`journal session ${session} ${event.type} record ${index + 1} is missing ${field}`);
      }
    }
    if (event.type === 'start') {
      if (index !== 0 || state !== null) fail(`journal session ${session} has a second or misplaced start record`);
      state = 'open';
    } else if (event.type === 'close') {
      if (state !== 'open') fail(`journal session ${session} closes while it is not open`);
      state = 'closed';
    } else if (event.type === 'resume') {
      if (state !== 'closed') fail(`journal session ${session} resumes while it is not closed`);
      state = 'open';
    } else if (event.type !== 'recovery' && state !== 'open') {
      fail(`journal session ${session} records ${event.type} while it is not open`);
    }
    if (event.type === 'recovery'
      && (!Number.isInteger(event.discarded_bytes) || event.discarded_bytes < 1)) {
      fail(`journal session ${session} recovery record ${index + 1} is invalid`);
    }
  }
  if (events[0]?.type !== 'start') fail(`journal session ${session} has no valid start record`);
  if (state !== 'open') fail(`journal session is closed: ${session}; run research-log.mjs resume first`);
  return events;
}

function requireFreshJournalCheckpoint(root, loaded) {
  const session = loaded.metadata.journal_session;
  const journalEvents = requireJournal(root, session);
  let lastBoundEventId = loaded.metadata.journal_anchor_event_id;
  for (const event of loaded.events) {
    if (event.type === 'submit' || event.type === 'review') {
      lastBoundEventId = event.journal_checkpoint_event_id;
    }
  }
  const lastBoundIndex = journalEvents.findIndex(({ event_id: eventId }) => eventId === lastBoundEventId);
  if (lastBoundIndex < 0) {
    fail(`journal session ${session} no longer contains its last workflow-bound event`);
  }
  const checkpoint = journalEvents.at(-1);
  if (journalEvents.length - 1 <= lastBoundIndex || checkpoint.type !== 'checkpoint'
    || typeof checkpoint.next !== 'string' || !checkpoint.next.trim()) {
    fail(`journal session ${session} requires a fresh checkpoint with --next immediately before this handoff`);
  }
  return checkpoint.event_id;
}

function requireReadyShelfEntry(root, heading) {
  const path = resolve(root, 'notes/questions.md');
  if (!existsSync(path)) fail('notes/questions.md is missing; cannot verify the Research shelf entry');
  const lines = readFileSync(path, 'utf8').split('\n');
  const start = lines.findIndex((line) => line.trim() === `## ${heading}`);
  if (start < 0) fail(`Research shelf entry not found: ${heading}`);
  let end = lines.length;
  for (let index = start + 1; index < lines.length; index += 1) {
    if (lines[index].startsWith('## ')) {
      end = index;
      break;
    }
  }
  if (!lines.slice(start + 1, end).some((line) => /^-\s+\*\*Status:\*\*\s+ready\b/i.test(line.trim()))) {
    fail(`Research shelf entry is not ready: ${heading}`);
  }
}

function serialize(event) {
  const record = `${JSON.stringify(event)}\n`;
  if (Buffer.byteLength(record) > maxRecordBytes) {
    fail(`workflow record exceeds ${maxRecordBytes} bytes; store large results separately and submit a small receipt`);
  }
  return Buffer.from(record);
}

function writeBuffer(descriptor, record) {
  let offset = 0;
  while (offset < record.length) {
    const written = writeSync(descriptor, record, offset, record.length - offset);
    if (written <= 0) throw new Error('short workflow log write');
    offset += written;
  }
}

function createLog(path, experimentDir, event) {
  if (existsSync(path)) fail('workflow already exists for this experiment');
  const record = serialize(event);
  const temporary = resolve(experimentDir, `.workflow-init.${randomUUID()}.tmp`);
  let descriptor;
  let identity;
  let created = false;
  let installed = false;
  let writeError;
  try {
    descriptor = openSync(
      temporary,
      fsConstants.O_WRONLY | fsConstants.O_CREAT | fsConstants.O_EXCL | noFollow,
      0o644,
    );
    validateOpenedManagedFile(descriptor, temporary, experimentDir, 'atomic-init staging file');
    created = true;
    identity = fstatSync(descriptor);
    writeBuffer(descriptor, record);
    fsyncSync(descriptor);
    closeSync(descriptor);
    descriptor = undefined;
    if (existsSync(path)) fail('workflow log appeared during atomic initialization');
    renameSync(temporary, path);
    installed = true;
    syncDirectory(experimentDir);
  } catch (error) {
    writeError = error;
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
  }
  if (writeError) {
    if (created && !installed && existsSync(temporary)) {
      const current = lstatSync(temporary);
      if (current.isFile() && !current.isSymbolicLink()
        && current.dev === identity.dev && current.ino === identity.ino) {
        unlinkSync(temporary);
      }
    }
    if (writeError.code === 'EEXIST' || writeError.code === 'ELOOP') {
      fail('workflow log already exists or is a symlink');
    }
    throw writeError;
  }
}

function cleanupStaleInitTemps(root, experimentDir) {
  const candidates = readdirSync(experimentDir, { withFileTypes: true })
    .filter((entry) => /^\.workflow-init\.[a-f0-9-]{36}\.tmp$/i.test(entry.name));
  if (candidates.length > 10) fail('too many atomic-init staging files; inspect the experiment directory');
  for (const entry of candidates) {
    const candidate = resolve(experimentDir, entry.name);
    const info = lstatSync(candidate);
    if (!entry.isFile() || entry.isSymbolicLink() || !info.isFile()
      || info.isSymbolicLink() || info.nlink !== 1 || info.size > maxRecordBytes) {
      fail(`unsafe atomic-init staging path; refusing cleanup: ${repoPath(root, candidate)}`);
    }
    unlinkSync(candidate);
    console.error(`Removed uncommitted atomic-init staging file ${repoPath(root, candidate)}`);
  }
  if (candidates.length) syncDirectory(experimentDir);
}

function cleanupStaleRecoveryTemps(root, experimentDir) {
  const candidates = readdirSync(experimentDir, { withFileTypes: true })
    .filter((entry) => /^\.workflow-recovery\.[a-f0-9-]{36}\.tmp$/i.test(entry.name));
  if (candidates.length > 10) fail('too many atomic-recovery staging files; inspect the experiment directory');
  for (const entry of candidates) {
    const candidate = resolve(experimentDir, entry.name);
    const info = lstatSync(candidate);
    if (!entry.isFile() || entry.isSymbolicLink() || !info.isFile()
      || info.isSymbolicLink() || info.nlink !== 1 || info.size > maxWorkflowLogBytes) {
      fail(`unsafe atomic-recovery staging path; refusing cleanup: ${repoPath(root, candidate)}`);
    }
    unlinkSync(candidate);
    console.error(`Removed uncommitted atomic-recovery staging file ${repoPath(root, candidate)}`);
  }
  if (candidates.length) syncDirectory(experimentDir);
}

function appendRecord(path, experimentDir, record, { recovery = false } = {}) {
  validateExistingLog(path, experimentDir);
  const descriptor = openRegular(
    path,
    fsConstants.O_RDWR | fsConstants.O_APPEND,
    'workflow log',
  );
  try {
    const size = Number(validateOpenedManagedFile(
      descriptor,
      path,
      experimentDir,
      'workflow log',
    ).size);
    const limit = recovery ? maxWorkflowLogBytes : maxNormalWorkflowLogBytes;
    if (size + record.length > limit) {
      fail(`workflow log would exceed its ${limit}-byte ${recovery ? 'recovery' : 'transition'} limit; create a separately reviewed successor workflow before adding another transition`);
    }
    const delimiter = Buffer.alloc(1);
    if (size < 1 || readSync(descriptor, delimiter, 0, 1, size - 1) !== 1
      || delimiter[0] !== 0x0a) {
      fail('workflow log has no committed final newline; run repair before appending');
    }
    writeBuffer(descriptor, record);
    fsyncSync(descriptor);
  } finally {
    closeSync(descriptor);
  }
}

function preflightAppend(path, experimentDir, recordLength) {
  validateExistingLog(path, experimentDir);
  const descriptor = openRegular(path, fsConstants.O_RDONLY, 'workflow log');
  try {
    const size = Number(validateOpenedManagedFile(
      descriptor,
      path,
      experimentDir,
      'workflow log',
    ).size);
    if (size + recordLength > maxNormalWorkflowLogBytes) {
      fail(`workflow log would exceed its ${maxNormalWorkflowLogBytes}-byte transition limit; no evidence snapshots were written`);
    }
    const delimiter = Buffer.alloc(1);
    if (size < 1 || readSync(descriptor, delimiter, 0, 1, size - 1) !== 1
      || delimiter[0] !== 0x0a) {
      fail('workflow log has no committed final newline; run repair before appending');
    }
  } finally {
    closeSync(descriptor);
  }
}

function readLog(path, experimentDir) {
  validateExistingLog(path, experimentDir);
  const rawBytes = readBoundedRegular(path, {
    parent: experimentDir,
    label: 'workflow log',
    maxBytes: maxWorkflowLogBytes,
  }).bytes;
  const content = rawBytes.toString('utf8');
  const endsWithNewline = content.endsWith('\n');
  const lines = content.split('\n');
  if (endsWithNewline) lines.pop();
  const events = [];
  const warnings = [];
  let validBytes = Buffer.byteLength(content);
  let discardedBytes = 0;
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (!line.trim()) fail(`${basename(path)} has an invalid blank record at line ${index + 1}`);
    if (index === lines.length - 1 && !endsWithNewline) {
      const prefix = index === 0 ? '' : `${lines.slice(0, index).join('\n')}\n`;
      validBytes = Buffer.byteLength(prefix);
      discardedBytes = Buffer.byteLength(content) - validBytes;
      warnings.push(`incomplete final record at line ${index + 1} (${discardedBytes} byte(s)); run repair`);
      break;
    }
    try {
      events.push(JSON.parse(line));
    } catch (error) {
      fail(`${basename(path)} has invalid JSON at line ${index + 1}: ${error.message}`);
    }
  }
  if (!events.length) fail(`${basename(path)} contains no complete records`);
  return { events, warnings, validBytes, discardedBytes, rawSha256: sha256(rawBytes) };
}

function canonicalRepoRelative(root, value, label) {
  if (typeof value !== 'string' || !value || isAbsolute(value) || value.includes('\\')) {
    fail(`${label} escapes the repository or is not a canonical repository-relative path`);
  }
  const target = resolve(root, value);
  if (!pathIsInside(root, target) || repoPath(root, target) !== value) {
    fail(`${label} escapes the repository or is not a canonical repository-relative path`);
  }
  return target;
}

function assertNoLinkedComponents(parent, target, label) {
  const difference = relative(parent, target);
  let cursor = parent;
  for (const component of difference.split(sep)) {
    cursor = resolve(cursor, component);
    const info = lstatSync(cursor);
    if (info.isSymbolicLink()) fail(`${label} must not contain symlinked path components`);
  }
}

function readBoundedRegular(path, { parent, label, maxBytes }) {
  if (!pathIsInside(parent, path)) fail(`${label} is outside its managed directory`);
  assertNoLinkedComponents(parent, path, label);
  const descriptor = openRegular(path, fsConstants.O_RDONLY, label);
  try {
    const before = fstatSync(descriptor, { bigint: true });
    if (!before.isFile() || before.nlink !== 1n) fail(`${label} is not a unique regular file`);
    if (before.size < 0n || before.size > BigInt(maxBytes)) {
      fail(`${label} exceeds ${maxBytes} bytes`);
    }
    const realPath = realpathSync(path);
    if (!pathIsInside(parent, realPath)) fail(`${label} resolves outside its managed directory`);
    const linked = lstatSync(path, { bigint: true });
    if (!linked.isFile() || linked.isSymbolicLink()
      || linked.nlink !== 1n || linked.dev !== before.dev || linked.ino !== before.ino) {
      fail(`${label} changed while it was opened`);
    }
    const size = Number(before.size);
    const bytes = Buffer.alloc(size);
    let offset = 0;
    while (offset < size) {
      const count = readSync(descriptor, bytes, offset, size - offset, offset);
      if (count <= 0) fail(`${label} changed size while it was read`);
      offset += count;
    }
    const extra = Buffer.alloc(1);
    if (readSync(descriptor, extra, 0, 1, size) !== 0) {
      fail(`${label} grew while it was read`);
    }
    const after = fstatSync(descriptor, { bigint: true });
    const current = lstatSync(path, { bigint: true });
    if (after.dev !== before.dev || after.ino !== before.ino || after.size !== before.size
      || after.mtimeNs !== before.mtimeNs || after.ctimeNs !== before.ctimeNs
      || !current.isFile() || current.isSymbolicLink()
      || current.nlink !== 1n || current.dev !== before.dev || current.ino !== before.ino
      || realpathSync(path) !== realPath) {
      fail(`${label} changed while it was read`);
    }
    return {
      bytes,
      realPath,
      identity: { dev: before.dev, ino: before.ino },
    };
  } finally {
    closeSync(descriptor);
  }
}

function safeEvidenceName(value) {
  return basename(value).replace(/[^A-Za-z0-9._-]+/g, '-').slice(-100) || 'evidence';
}

function prepareArtifacts(root, paths, sequence, eventId, sources) {
  if (!Array.isArray(sources) || !sources.length) fail('at least one --artifact is required');
  if (sources.length > maxArtifacts) fail(`at most ${maxArtifacts} evidence artifacts may be submitted`);
  const seenSources = new Set();
  const prepared = [];
  let totalBytes = 0;
  for (const [index, sourceValue] of sources.entries()) {
    const source = canonicalRepoRelative(root, sourceValue, 'artifact path');
    if (!pathIsInside(paths.workflowDir, source) || pathIsInside(paths.evidenceDir, source)
      || source === paths.lockPath) {
      fail(`artifact must be a small receipt under ${repoPath(root, paths.workflowDir)} and outside evidence/: ${sourceValue}`);
    }
    if (relative(paths.workflowDir, source).split(sep).some((part) => part.startsWith('.'))) {
      fail(`artifact path contains a managed dotfile component: ${sourceValue}`);
    }
    if (!existsSync(source)) fail(`artifact does not exist: ${sourceValue}`);
    const opened = readBoundedRegular(source, {
      parent: paths.workflowDir,
      label: `artifact ${sourceValue}`,
      maxBytes: maxEvidenceBytes,
    });
    const realSource = opened.realPath;
    const normalizedSource = repoPath(root, realSource);
    if (seenSources.has(normalizedSource)) fail(`artifact was supplied more than once: ${sourceValue}`);
    seenSources.add(normalizedSource);
    const { bytes } = opened;
    totalBytes += bytes.length;
    if (totalBytes > maxEvidenceTotalBytes) {
      fail(`artifact set exceeds ${maxEvidenceTotalBytes} bytes; submit smaller receipts`);
    }
    const filename = `${String(sequence).padStart(4, '0')}-${String(index + 1).padStart(2, '0')}-${eventId}-${safeEvidenceName(sourceValue)}`;
    const destination = resolve(paths.evidenceDir, filename);
    prepared.push({
      source: realSource,
      destination,
      bytes,
      evidence: {
        source_path: normalizedSource,
        snapshot_path: repoPath(root, destination),
        sha256: sha256(bytes),
        bytes: bytes.length,
      },
    });
  }
  return prepared;
}

function writeSnapshot(path, bytes) {
  let descriptor;
  let identity;
  let created = false;
  let writeError;
  try {
    descriptor = openSync(
      path,
      fsConstants.O_WRONLY | fsConstants.O_CREAT | fsConstants.O_EXCL | noFollow,
      0o644,
    );
    validateOpenedManagedFile(descriptor, path, dirname(path), 'evidence snapshot');
    created = true;
    identity = fstatSync(descriptor);
    writeFileSync(descriptor, bytes);
    fsyncSync(descriptor);
  } catch (error) {
    writeError = error;
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
  }
  if (writeError) {
    if (created && existsSync(path)) {
      const current = lstatSync(path);
      if (current.isFile() && !current.isSymbolicLink()
        && current.dev === identity.dev && current.ino === identity.ino) {
        unlinkSync(path);
      }
    }
    if (writeError.code === 'EEXIST' || writeError.code === 'ELOOP') {
      fail(`evidence snapshot already exists or is a link: ${path}`);
    }
    throw writeError;
  }
}

function persistTransition(paths, event, prepared) {
  const record = serialize(event);
  preflightAppend(paths.logPath, dirname(paths.logPath), record.length);
  const created = [];
  let appendAttempted = false;
  try {
    for (const artifact of prepared) {
      writeSnapshot(artifact.destination, artifact.bytes);
      created.push(artifact.destination);
    }
    syncDirectory(paths.evidenceDir);
    appendAttempted = true;
    appendRecord(paths.logPath, dirname(paths.logPath), record);
  } catch (error) {
    if (!appendAttempted) {
      for (const snapshot of created) {
        const info = lstatSync(snapshot);
        if (!info.isFile() || info.isSymbolicLink() || dirname(snapshot) !== paths.evidenceDir) {
          fail('a newly created evidence snapshot changed unexpectedly; refusing cleanup');
        }
        unlinkSync(snapshot);
      }
      syncDirectory(paths.evidenceDir);
    }
    throw error;
  }
}

function validateSnapshotObject(root, paths, artifact, eventSequence, index, globalSnapshots, {
  sourceRequired = true,
} = {}) {
  const allowed = sourceRequired
    ? new Set(['source_path', 'snapshot_path', 'sha256', 'bytes'])
    : new Set(['snapshot_path', 'sha256', 'bytes']);
  exactKeys(artifact, allowed, `workflow event ${eventSequence} artifact`);
  if (sourceRequired && typeof artifact.source_path !== 'string') {
    fail(`workflow event ${eventSequence} artifact has no source_path`);
  }
  if (!sha256Pattern.test(artifact.sha256 || '') || !Number.isInteger(artifact.bytes)
    || artifact.bytes < 0 || artifact.bytes > maxEvidenceBytes) {
    fail(`workflow event ${eventSequence} has malformed artifact evidence`);
  }
  if (sourceRequired) {
    const source = canonicalRepoRelative(root, artifact.source_path, 'artifact source_path');
    if (!pathIsInside(paths.workflowDir, source) || pathIsInside(paths.evidenceDir, source)) {
      fail(`workflow event ${eventSequence} source_path is outside workflow receipts`);
    }
  }
  const snapshot = canonicalRepoRelative(root, artifact.snapshot_path, 'artifact snapshot_path');
  if (!pathIsInside(paths.evidenceDir, snapshot)) {
    fail(`workflow event ${eventSequence} snapshot is outside the evidence directory`);
  }
  if (sourceRequired) {
    const prefix = `${String(eventSequence).padStart(4, '0')}-${String(index + 1).padStart(2, '0')}-`;
    if (!basename(snapshot).startsWith(prefix)) {
      fail(`workflow event ${eventSequence} snapshot name is not canonical`);
    }
  }
  if (globalSnapshots.has(artifact.snapshot_path)) {
    fail(`workflow snapshot is referenced more than once: ${artifact.snapshot_path}`);
  }
  globalSnapshots.add(artifact.snapshot_path);
  if (!existsSync(snapshot)) fail(`workflow event ${eventSequence} is missing snapshot ${artifact.snapshot_path}`);
  const { bytes } = readBoundedRegular(snapshot, {
    parent: paths.evidenceDir,
    label: `workflow snapshot ${artifact.snapshot_path}`,
    maxBytes: maxEvidenceBytes,
  });
  if (bytes.length !== artifact.bytes || sha256(bytes) !== artifact.sha256) {
    fail(`workflow snapshot fingerprint mismatch: ${artifact.snapshot_path}`);
  }
}

function verifyEventSnapshots(root, paths, event, globalSnapshots) {
  if (!Array.isArray(event.artifacts) || !event.artifacts.length || event.artifacts.length > maxArtifacts) {
    fail(`workflow event ${event.sequence} has no valid evidence snapshots`);
  }
  event.artifacts.forEach((artifact, index) => {
    validateSnapshotObject(root, paths, artifact, event.sequence, index, globalSnapshots);
  });
}

function validateContext(context, sequence) {
  exactKeys(context, new Set(['branch', 'parent_commit']), `workflow event ${sequence} context`);
  if (context.branch !== null && (typeof context.branch !== 'string' || context.branch.length > 512)) {
    fail(`workflow event ${sequence} has invalid branch context`);
  }
  if (context.parent_commit !== null
    && (typeof context.parent_commit !== 'string' || !/^[a-f0-9]{40,64}$/i.test(context.parent_commit))) {
    fail(`workflow event ${sequence} has invalid parent commit context`);
  }
}

function validateCommonEvent(event, experiment, graph, expectedSequence, eventIds) {
  if (!isPlainObject(event) || event.schema !== schemaVersion || event.graph_version !== graph.graph_version) {
    fail(`workflow event ${expectedSequence} has an unsupported schema or graph version`);
  }
  if (event.graph_sha256 !== graph._sha256) fail(`workflow event ${expectedSequence} graph digest mismatch`);
  if (event.experiment !== experiment) fail(`workflow event ${expectedSequence} belongs to another experiment`);
  if (event.sequence !== expectedSequence) fail(`workflow event sequence must be ${expectedSequence}`);
  if (!uuidPattern.test(event.event_id || '') || eventIds.has(event.event_id)) {
    fail(`workflow event ${expectedSequence} has invalid or duplicate event_id`);
  }
  eventIds.add(event.event_id);
  if (typeof event.timestamp !== 'string' || Number.isNaN(Date.parse(event.timestamp))
    || new Date(event.timestamp).toISOString() !== event.timestamp) {
    fail(`workflow event ${expectedSequence} has invalid timestamp`);
  }
  if (!identifierPattern.test(event.actor || '') || !identifierPattern.test(event.role || '')) {
    fail(`workflow event ${expectedSequence} has invalid actor or role`);
  }
  validateContext(event.context, expectedSequence);
}

function validateEventKeys(event) {
  const common = [
    'schema', 'graph_version', 'graph_sha256', 'event_id', 'timestamp', 'experiment',
    'sequence', 'type', 'actor', 'role', 'from', 'to', 'context',
  ];
  const extras = {
    init: ['post_type', 'question', 'journal_session', 'journal_anchor_event_id', 'shelf_entry'],
    submit: ['artifacts', 'journal_checkpoint_event_id', 'note'],
    review: ['decision', 'submission_sequence', 'artifacts', 'journal_checkpoint_event_id', 'note'],
    recovery: ['discarded_bytes', 'reason', 'quarantined_snapshots'],
  };
  if (!Object.hasOwn(extras, event.type)) fail(`workflow event ${event.sequence} has invalid type ${event.type}`);
  exactKeys(event, new Set([...common, ...extras[event.type]]), `workflow event ${event.sequence}`);
  if (Object.hasOwn(event, 'note') && (typeof event.note !== 'string' || !event.note.trim()
    || event.note.length > maxNoteCharacters)) {
    fail(`workflow event ${event.sequence} has invalid note`);
  }
}

function invalidateLineage(accepted, superseded, minimumOrder, event) {
  const kept = [];
  for (const item of accepted) {
    if (item.lineage_order >= minimumOrder) {
      superseded.push({ ...item, invalidated_by: event.sequence, routed_to: event.to });
    } else {
      kept.push(item);
    }
  }
  return kept;
}

function replay(root, paths, experiment, graph, events, { verifyEvidence = true } = {}) {
  let state = null;
  let metadata = null;
  let pendingSubmission = null;
  let acceptedLineage = [];
  const supersededLineage = [];
  const routedReviews = [];
  const eventIds = new Set();
  const journalEventIds = new Set();
  const globalSnapshots = new Set();

  for (const [index, event] of events.entries()) {
    const sequence = index + 1;
    validateCommonEvent(event, experiment, graph, sequence, eventIds);
    validateEventKeys(event);
    if (sequence === 1) {
      if (event.type !== 'init' || event.from !== null || event.to !== graph.initial_state
        || event.role !== 'coordinator') fail('workflow must begin with a coordinator init event');
      if (!['research', 'understanding'].includes(event.post_type)
        || typeof event.question !== 'string' || !event.question.trim() || event.question.length > 10000
        || !identifierPattern.test(event.journal_session || '')
        || !uuidPattern.test(event.journal_anchor_event_id || '')
        || typeof event.context.branch !== 'string' || !postBranchPattern.test(event.context.branch)) {
        fail('workflow init event has invalid metadata');
      }
      if (event.post_type === 'research'
        && (typeof event.shelf_entry !== 'string' || !event.shelf_entry.trim())) {
        fail('research workflow init event is missing shelf_entry');
      }
      if (event.post_type === 'understanding' && Object.hasOwn(event, 'shelf_entry')) {
        fail('understanding workflow init event must not claim a shelf_entry');
      }
      state = event.to;
      metadata = {
        post_type: event.post_type,
        question: event.question,
        shelf_entry: event.shelf_entry,
        journal_session: event.journal_session,
        journal_anchor_event_id: event.journal_anchor_event_id,
        owning_branch: event.context.branch,
        created_at: event.timestamp,
        created_by: event.actor,
      };
      journalEventIds.add(event.journal_anchor_event_id);
      continue;
    }

    if (event.context.branch !== metadata.owning_branch) {
      fail(`workflow event ${sequence} was recorded on non-owning branch ${event.context.branch}`);
    }

    if (event.type === 'recovery') {
      if (event.actor !== 'workflow' || event.role !== 'coordinator'
        || event.from !== state || event.to !== state
        || !Number.isInteger(event.discarded_bytes) || event.discarded_bytes < 0
        || typeof event.reason !== 'string' || !event.reason.trim()) {
        fail(`workflow recovery event ${sequence} is invalid or changed state`);
      }
      const quarantined = event.quarantined_snapshots ?? [];
      if (!Array.isArray(quarantined) || (!event.discarded_bytes && !quarantined.length)) {
        fail(`workflow recovery event ${sequence} records no recovery action`);
      }
      quarantined.forEach((artifact, artifactIndex) => {
        validateSnapshotObject(root, paths, artifact, sequence, artifactIndex, globalSnapshots, {
          sourceRequired: false,
        });
      });
      continue;
    }

    if (!uuidPattern.test(event.journal_checkpoint_event_id || '')
      || journalEventIds.has(event.journal_checkpoint_event_id)) {
      fail(`workflow event ${sequence} has an invalid or reused journal checkpoint`);
    }
    journalEventIds.add(event.journal_checkpoint_event_id);

    const node = graph.states[state];
    if (!node || node.kind === 'terminal') fail(`workflow event ${sequence} follows terminal state ${state}`);
    if (event.from !== state) fail(`workflow event ${sequence} expected from=${state}`);
    if (event.role !== node.role) fail(`workflow event ${sequence} expected role=${node.role}`);
    if (verifyEvidence) verifyEventSnapshots(root, paths, event, globalSnapshots);

    if (node.kind === 'work') {
      if (event.type !== 'submit' || event.to !== node.submit_to) {
        fail(`workflow event ${sequence} cannot submit ${state} to ${event.to}`);
      }
      pendingSubmission = event;
    } else {
      if (!statePattern.test(event.decision || '') || !Number.isInteger(event.submission_sequence)) {
        fail(`workflow event ${sequence} has malformed review decision metadata`);
      }
      if (event.type !== 'review' || !Object.hasOwn(node.decisions, event.decision)
        || node.decisions[event.decision] !== event.to) {
        fail(`workflow event ${sequence} has invalid ${state} decision ${event.decision}`);
      }
      if (!pendingSubmission || event.submission_sequence !== pendingSubmission.sequence) {
        fail(`workflow event ${sequence} does not review the pending submission`);
      }
      if (event.actor.toLowerCase() === pendingSubmission.actor.toLowerCase()) {
        fail(`workflow event ${sequence} is a self-review by asserted actor ${event.actor}`);
      }
      const submittedNode = graph.states[pendingSubmission.from];
      if (event.decision === 'approve') {
        acceptedLineage = invalidateLineage(
          acceptedLineage,
          supersededLineage,
          submittedNode.lineage_order,
          event,
        );
        acceptedLineage.push({
          work_state: pendingSubmission.from,
          lineage_order: submittedNode.lineage_order,
          submission: pendingSubmission,
          review: event,
        });
      } else {
        const target = graph.states[event.to];
        if (target.kind === 'work') {
          acceptedLineage = invalidateLineage(
            acceptedLineage,
            supersededLineage,
            target.lineage_order,
            event,
          );
        }
        routedReviews.push({ sequence: event.sequence, decision: event.decision, to: event.to });
      }
      pendingSubmission = null;
    }
    state = event.to;
  }

  if (!metadata) fail('workflow has no initialization metadata');
  const stateNode = graph.states[state];
  if (stateNode.kind === 'review' && !pendingSubmission) {
    fail(`workflow is waiting at ${state} without a pending submission`);
  }
  if (stateNode.kind !== 'review' && pendingSubmission) {
    fail('workflow has an orphan submission outside a review state');
  }
  return {
    state,
    node: stateNode,
    metadata,
    pendingSubmission,
    acceptedLineage,
    supersededLineage,
    routedReviews,
    referencedSnapshots: globalSnapshots,
  };
}

function evidenceInventory(root, paths, referencedSnapshots) {
  const orphans = [];
  for (const entry of readdirSync(paths.evidenceDir, { withFileTypes: true })) {
    const candidate = resolve(paths.evidenceDir, entry.name);
    if (!entry.isFile() || entry.isSymbolicLink()) {
      fail(`evidence directory contains a non-file or link: ${repoPath(root, candidate)}`);
    }
    if (!/^\d{4,}-\d{2}-[a-f0-9-]{36}-.+/i.test(entry.name)) {
      fail(`evidence directory contains a noncanonical snapshot: ${repoPath(root, candidate)}`);
    }
    const path = repoPath(root, candidate);
    if (!referencedSnapshots.has(path)) {
      const { bytes } = readBoundedRegular(candidate, {
        parent: paths.evidenceDir,
        label: `unreferenced evidence snapshot ${path}`,
        maxBytes: maxEvidenceBytes,
      });
      orphans.push({ snapshot_path: path, sha256: sha256(bytes), bytes: bytes.length });
    }
  }
  return orphans;
}

function activeEvents(current) {
  const events = [];
  for (const item of current.acceptedLineage) events.push(item.submission, item.review);
  if (current.pendingSubmission) events.push(current.pendingSubmission);
  return [...new Map(events.map((event) => [event.sequence, event])).values()];
}

function detectSourceDrift(root, paths, current) {
  const drift = [];
  for (const event of activeEvents(current)) {
    for (const artifact of event.artifacts) {
      let reason;
      try {
        const source = canonicalRepoRelative(root, artifact.source_path, 'active source_path');
        if (!pathIsInside(paths.workflowDir, source) || !existsSync(source)) reason = 'missing';
        else {
          const { bytes } = readBoundedRegular(source, {
            parent: paths.workflowDir,
            label: `active source ${artifact.source_path}`,
            maxBytes: maxEvidenceBytes,
          });
          if (bytes.length !== artifact.bytes || sha256(bytes) !== artifact.sha256) reason = 'content changed';
        }
      } catch (error) {
        reason = error instanceof CliError ? error.message : error.message;
      }
      if (reason) drift.push({ sequence: event.sequence, source_path: artifact.source_path, reason });
    }
  }
  return drift;
}

function selectPinnedGraph(events, preferredGraph) {
  const version = events[0]?.graph_version;
  if (!Number.isInteger(version)) return preferredGraph;
  if (preferredGraph.graph_version === version) return preferredGraph;
  if (process.env.RESEARCH_WORKFLOW_GRAPH) {
    fail(`workflow requires graph version ${version}, but the configured graph is version ${preferredGraph.graph_version}`);
  }
  return loadGraph(graphPathForVersion(version));
}

function loadWorkflow(root, experiment, preferredGraph, {
  verifyEvidence = true,
  allowLock = false,
  allowOrphans = false,
} = {}) {
  const experimentDir = experimentDirectory(root, experiment);
  const paths = managedPaths(experimentDir);
  assertUnlocked(paths, allowLock);
  const loaded = readLog(paths.logPath, experimentDir);
  const graph = selectPinnedGraph(loaded.events, preferredGraph);
  const current = replay(root, paths, experiment, graph, loaded.events, { verifyEvidence });
  const orphanSnapshots = evidenceInventory(root, paths, current.referencedSnapshots);
  if (orphanSnapshots.length && !allowOrphans && !loaded.warnings.length) {
    fail(`workflow has ${orphanSnapshots.length} unreferenced evidence snapshot(s); run repair before continuing`);
  }
  const sourceDrift = detectSourceDrift(root, paths, current);
  return {
    experimentDir,
    paths,
    graph,
    ...loaded,
    ...current,
    orphanSnapshots,
    sourceDrift,
  };
}

function baseEvent(root, experiment, graph, sequence, fields) {
  return {
    schema: schemaVersion,
    graph_version: graph.graph_version,
    graph_sha256: graph._sha256,
    event_id: randomUUID(),
    timestamp: new Date().toISOString(),
    experiment,
    sequence,
    ...fields,
    context: repositoryContext(root),
  };
}

function replaceInterruptedTail(loaded, recoveryRecord) {
  const current = readBoundedRegular(loaded.paths.logPath, {
    parent: loaded.experimentDir,
    label: 'workflow log during recovery',
    maxBytes: maxWorkflowLogBytes,
  });
  if (sha256(current.bytes) !== loaded.rawSha256) {
    fail('workflow log changed after recovery inspection; refusing replacement');
  }
  const replacement = Buffer.concat([
    current.bytes.subarray(0, loaded.validBytes),
    recoveryRecord,
  ]);
  if (replacement.length > maxWorkflowLogBytes) {
    fail(`repaired workflow log would exceed ${maxWorkflowLogBytes} bytes; original tail was left intact`);
  }
  const temporary = resolve(
    loaded.experimentDir,
    `.workflow-recovery.${randomUUID()}.tmp`,
  );
  let descriptor;
  let temporaryIdentity;
  let installed = false;
  try {
    descriptor = openSync(
      temporary,
      fsConstants.O_WRONLY | fsConstants.O_CREAT | fsConstants.O_EXCL | noFollow,
      0o644,
    );
    validateOpenedManagedFile(
      descriptor,
      temporary,
      loaded.experimentDir,
      'atomic-recovery staging file',
    );
    temporaryIdentity = fstatSync(descriptor, { bigint: true });
    writeFileSync(descriptor, replacement);
    fsyncSync(descriptor);
    closeSync(descriptor);
    descriptor = undefined;

    const logIdentity = lstatSync(loaded.paths.logPath, { bigint: true });
    if (!logIdentity.isFile() || logIdentity.isSymbolicLink()
      || logIdentity.nlink !== 1n
      || logIdentity.dev !== current.identity.dev
      || logIdentity.ino !== current.identity.ino) {
      fail('workflow log changed before atomic recovery replacement');
    }
    renameSync(temporary, loaded.paths.logPath);
    installed = true;
    syncDirectory(loaded.experimentDir);
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
    if (!installed && temporaryIdentity && existsSync(temporary)) {
      const staged = lstatSync(temporary, { bigint: true });
      if (staged.isFile() && !staged.isSymbolicLink()
        && staged.dev === temporaryIdentity.dev && staged.ino === temporaryIdentity.ino) {
        unlinkSync(temporary);
      }
    }
  }
}

function repairLoaded(root, experiment, loaded) {
  if (!loaded.warnings.length && !loaded.orphanSnapshots.length) return loaded;
  const recovery = baseEvent(root, experiment, loaded.graph, loaded.events.length + 1, {
    type: 'recovery',
    actor: 'workflow',
    role: 'coordinator',
    from: loaded.state,
    to: loaded.state,
    discarded_bytes: loaded.discardedBytes,
    reason: loaded.warnings.length
      ? 'Discarded an incomplete final record and quarantined any unreferenced evidence snapshots.'
      : 'Quarantined unreferenced evidence snapshots left by an interrupted transition.',
    quarantined_snapshots: loaded.orphanSnapshots,
  });
  const recoveryRecord = serialize(recovery);
  if (loaded.warnings.length) {
    replaceInterruptedTail(loaded, recoveryRecord);
  } else {
    appendRecord(loaded.paths.logPath, loaded.experimentDir, recoveryRecord, { recovery: true });
  }
  console.error(
    `Recovered ${loaded.discardedBytes} incomplete byte(s) and quarantined ${loaded.orphanSnapshots.length} snapshot(s)`,
  );
  return loadWorkflow(root, experiment, loaded.graph, { allowLock: true });
}

function assertFresh(loaded) {
  if (loaded.sourceDrift.length) {
    const first = loaded.sourceDrift[0];
    fail(`active approved source drift at ${first.source_path}: ${first.reason}; restore it or route a reviewed revision`);
  }
}

function initialize(options, root, graph) {
  requireOnly(options, new Set(['actor', 'experiment', 'journal', 'post-type', 'question', 'shelf-entry']));
  const experiment = validateExperiment(required(options, 'experiment'));
  const actor = validateIdentifier(required(options, 'actor'), 'actor');
  const journal = validateIdentifier(required(options, 'journal'), 'journal session');
  const postType = required(options, 'post-type');
  if (!['research', 'understanding'].includes(postType)) fail('--post-type must be research or understanding');
  const question = required(options, 'question');
  if (question.length > 10000) fail('--question is too long');
  const shelfEntry = optional(options, 'shelf-entry');
  if (postType === 'research' && !shelfEntry) fail('--shelf-entry is required for a research workflow');
  if (postType === 'understanding' && shelfEntry) fail('--shelf-entry is only valid for a research workflow');
  requireOwningPostWorktree(root, 'workflow initialization');
  const journalEvents = requireJournal(root, journal);
  if (postType === 'research') requireReadyShelfEntry(root, shelfEntry);

  const experimentDir = experimentDirectory(root, experiment);
  const paths = managedPaths(experimentDir, { create: true });
  const release = acquireLock(paths);
  try {
    if (existsSync(paths.logPath)) fail(`workflow already exists for research/${experiment}`);
    cleanupStaleInitTemps(root, experimentDir);
    if (readdirSync(paths.evidenceDir).length) fail('evidence directory must be empty before workflow initialization');
    const fields = {
      type: 'init',
      actor,
      role: 'coordinator',
      from: null,
      to: graph.initial_state,
      post_type: postType,
      question,
      journal_session: journal,
      journal_anchor_event_id: journalEvents.at(-1).event_id,
    };
    if (shelfEntry) fields.shelf_entry = shelfEntry;
    createLog(paths.logPath, experimentDir, baseEvent(root, experiment, graph, 1, fields));
  } finally {
    release();
  }
  console.log(`Initialized research/${experiment} at ${graph.initial_state}`);
  console.log(`Next role: ${graph.states[graph.initial_state].role}`);
  console.log(`Log: ${repoPath(root, paths.logPath)}`);
}

function mutateWorkflow(root, experiment, preferredGraph, callback) {
  const branch = requireOwningPostWorktree(root, 'workflow mutation');
  const observed = loadWorkflow(root, experiment, preferredGraph, {
    allowLock: true,
    allowOrphans: true,
  });
  requireOwningPostWorktree(root, 'workflow mutation', observed.metadata.owning_branch);
  if (observed.warnings.length) {
    fail(`workflow has an incomplete final record; run repair for ${experiment} before another transition`);
  }
  if (observed.orphanSnapshots.length) {
    fail(`${observed.orphanSnapshots.length} unreferenced evidence snapshot(s) require an explicit repair`);
  }
  assertFresh(observed);
  const { experimentDir, paths } = observed;
  const release = acquireLock(paths);
  try {
    requireOwningPostWorktree(root, 'workflow mutation', branch);
    cleanupStaleRecoveryTemps(root, experimentDir);
    const loaded = loadWorkflow(root, experiment, preferredGraph, {
      allowLock: true,
      allowOrphans: true,
    });
    if (loaded.metadata.owning_branch !== branch) {
      fail(`workflow mutation belongs to ${loaded.metadata.owning_branch}; current worktree is on ${branch}`);
    }
    if (loaded.warnings.length) {
      fail(`workflow has an incomplete final record; run repair for ${experiment} before another transition`);
    }
    if (loaded.orphanSnapshots.length) {
      fail(`${loaded.orphanSnapshots.length} unreferenced evidence snapshot(s) require an explicit repair`);
    }
    assertFresh(loaded);
    const journalCheckpointEventId = requireFreshJournalCheckpoint(root, loaded);
    return callback(loaded, journalCheckpointEventId);
  } finally {
    release();
  }
}

function submit(options, root, graph) {
  requireOnly(options, new Set(['actor', 'artifact', 'experiment', 'note']));
  const experiment = validateExperiment(required(options, 'experiment'));
  const actor = validateIdentifier(required(options, 'actor'), 'actor');
  const note = optionalNote(options);
  mutateWorkflow(root, experiment, graph, (loaded, journalCheckpointEventId) => {
    if (loaded.node.kind !== 'work') fail(`cannot submit from ${loaded.state}; current role is ${loaded.node.role}`);
    const sequence = loaded.events.length + 1;
    const eventId = randomUUID();
    const prepared = prepareArtifacts(root, loaded.paths, sequence, eventId, options.artifact);
    const fields = {
      type: 'submit',
      actor,
      role: loaded.node.role,
      from: loaded.state,
      to: loaded.node.submit_to,
      artifacts: prepared.map(({ evidence }) => evidence),
      journal_checkpoint_event_id: journalCheckpointEventId,
    };
    if (note) fields.note = note;
    const event = baseEvent(root, experiment, loaded.graph, sequence, fields);
    event.event_id = eventId;
    serialize(event);
    persistTransition(loaded.paths, event, prepared);
    console.log(`Submitted ${loaded.state} -> ${event.to} as ${actor}`);
    console.log(`Waiting for: ${loaded.graph.states[event.to].role}`);
  });
}

function review(options, root, graph) {
  requireOnly(options, new Set(['actor', 'artifact', 'decision', 'experiment', 'note']));
  const experiment = validateExperiment(required(options, 'experiment'));
  const actor = validateIdentifier(required(options, 'actor'), 'actor');
  const decision = required(options, 'decision');
  const note = optionalNote(options);
  mutateWorkflow(root, experiment, graph, (loaded, journalCheckpointEventId) => {
    if (loaded.node.kind !== 'review') fail(`cannot review from ${loaded.state}; current role is ${loaded.node.role}`);
    if (!Object.hasOwn(loaded.node.decisions, decision)) {
      fail(`decision for ${loaded.state} must be one of: ${Object.keys(loaded.node.decisions).join(', ')}`);
    }
    const target = loaded.node.decisions[decision];
    if (actor.toLowerCase() === loaded.pendingSubmission.actor.toLowerCase()) {
      fail(`self-review is forbidden: reviewer ${actor} cannot review their own submission (asserted actor IDs must differ)`);
    }
    const sequence = loaded.events.length + 1;
    const eventId = randomUUID();
    const prepared = prepareArtifacts(root, loaded.paths, sequence, eventId, options.artifact);
    const fields = {
      type: 'review',
      actor,
      role: loaded.node.role,
      from: loaded.state,
      to: target,
      decision,
      submission_sequence: loaded.pendingSubmission.sequence,
      artifacts: prepared.map(({ evidence }) => evidence),
      journal_checkpoint_event_id: journalCheckpointEventId,
    };
    if (note) fields.note = note;
    const event = baseEvent(root, experiment, loaded.graph, sequence, fields);
    event.event_id = eventId;
    serialize(event);
    persistTransition(loaded.paths, event, prepared);
    console.log(`Reviewed ${loaded.state}: ${decision} -> ${target}`);
    console.log(`Next role: ${loaded.graph.states[target].role}`);
  });
}

function lineageSummary(item) {
  const eventSummary = (event) => ({
    sequence: event.sequence,
    actor: event.actor,
    artifacts: event.artifacts,
  });
  return {
    work_state: item.work_state,
    lineage_order: item.lineage_order,
    submission: eventSummary(item.submission),
    review: eventSummary(item.review),
    ...(item.invalidated_by ? { invalidated_by: item.invalidated_by, routed_to: item.routed_to } : {}),
  };
}

function statusSummary(experiment, loaded) {
  const { graph } = loaded;
  const submissions = loaded.events.filter((event) => event.type === 'submit' && event.from === loaded.state).length;
  const reviews = loaded.events.filter((event) => event.type === 'review' && event.from === loaded.state).length;
  const allowed = loaded.node.kind === 'work'
    ? { submit: loaded.node.submit_to }
    : loaded.node.kind === 'review' ? { ...loaded.node.decisions } : {};
  return {
    schema_version: schemaVersion,
    graph_version: graph.graph_version,
    graph_sha256: graph._sha256,
    experiment,
    ...loaded.metadata,
    state: loaded.state,
    kind: loaded.node.kind,
    label: loaded.node.label,
    role: loaded.node.role,
    iteration: loaded.node.kind === 'terminal'
      ? null
      : loaded.node.kind === 'work' ? submissions + 1 : reviews + 1,
    description: loaded.node.description,
    artifact_contract: loaded.node.artifact_contract,
    pending_submission: loaded.pendingSubmission ? {
      sequence: loaded.pendingSubmission.sequence,
      actor: loaded.pendingSubmission.actor,
      artifacts: loaded.pendingSubmission.artifacts,
    } : null,
    accepted_lineage: loaded.acceptedLineage.map(lineageSummary),
    superseded_lineage: loaded.supersededLineage.map(lineageSummary),
    routed_reviews: loaded.routedReviews,
    stale: loaded.sourceDrift.length > 0,
    stale_sources: loaded.sourceDrift,
    allowed,
    events: loaded.events.length,
    recovery_warnings: loaded.warnings,
    recovery_orphan_snapshots: loaded.orphanSnapshots,
  };
}

function showStatus(options, root, graph) {
  requireOnly(options, new Set(['experiment', 'json']));
  const experiment = validateExperiment(required(options, 'experiment'));
  const loaded = loadWorkflow(root, experiment, graph);
  const summary = statusSummary(experiment, loaded);
  if (options.json) {
    console.log(JSON.stringify(summary, null, 2));
    return;
  }
  console.log(`Experiment: ${experiment}`);
  console.log(`Post type: ${summary.post_type}`);
  console.log(`State: ${summary.state} (${summary.kind}${summary.iteration === null ? '' : `, iteration ${summary.iteration}`})`);
  console.log(`Role: ${summary.role}`);
  console.log(`Job: ${summary.description}`);
  if (summary.artifact_contract) console.log(`Exit artifact: ${summary.artifact_contract}`);
  if (summary.pending_submission) {
    console.log(`Reviewing submission ${summary.pending_submission.sequence} from ${summary.pending_submission.actor}`);
  }
  console.log(`Accepted lineage: ${summary.accepted_lineage.map((item) => item.work_state).join(' -> ') || 'none'}`);
  if (summary.stale) console.log(`STALE: ${summary.stale_sources.length} active receipt(s) changed or disappeared`);
  const choices = Object.entries(summary.allowed).map(([action, target]) => `${action} -> ${target}`);
  console.log(`Allowed: ${choices.length ? choices.join(', ') : 'none; merge or close the parked work externally'}`);
  for (const warning of summary.recovery_warnings) console.log(`Recovery required: ${warning}`);
}

function verifyOne(root, graph, experiment) {
  const loaded = loadWorkflow(root, experiment, graph);
  if (loaded.warnings.length) fail(`workflow has an incomplete final record; run repair for ${experiment}`);
  assertFresh(loaded);
  const snapshots = loaded.events.reduce(
    (count, event) => count + (event.artifacts?.length || 0) + (event.quarantined_snapshots?.length || 0),
    0,
  );
  console.log(`Verified research/${experiment}/workflow.jsonl: ${loaded.events.length} event(s), ${snapshots} snapshot(s), state=${loaded.state}`);
}

function verify(options, root, graph) {
  requireOnly(options, new Set(['all', 'experiment']));
  const hasAll = options.all === true;
  const hasExperiment = typeof options.experiment === 'string';
  if (hasAll === hasExperiment) fail('verify requires exactly one of --experiment or --all');
  if (hasExperiment) {
    verifyOne(root, graph, validateExperiment(required(options, 'experiment')));
    return;
  }
  const research = resolve(root, 'research');
  const experiments = readdirSync(research, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && !entry.isSymbolicLink())
    .map((entry) => entry.name)
    .filter((name) => experimentPattern.test(name) && existsSync(resolve(research, name, 'workflow.jsonl')))
    .sort();
  for (const experiment of experiments) verifyOne(root, graph, experiment);
  console.log(`Verified ${experiments.length} opted-in workflow log(s).`);
}

function repair(options, root, graph) {
  requireOnly(options, new Set(['experiment', 'unlock-stale']));
  const experiment = validateExperiment(required(options, 'experiment'));
  const branch = requireOwningPostWorktree(root, 'workflow repair');
  const observed = loadWorkflow(root, experiment, graph, { allowLock: true, allowOrphans: true });
  requireOwningPostWorktree(root, 'workflow repair', observed.metadata.owning_branch);
  const { experimentDir, paths } = observed;
  if (options['unlock-stale']) {
    if (clearStaleLock(paths)) console.error(`Removed a stale transition lock for research/${experiment}`);
  }
  const release = acquireLock(paths);
  try {
    requireOwningPostWorktree(root, 'workflow repair', branch);
    cleanupStaleRecoveryTemps(root, experimentDir);
    const loaded = loadWorkflow(root, experiment, graph, { allowLock: true, allowOrphans: true });
    if (loaded.metadata.owning_branch !== branch) {
      fail(`workflow repair belongs to ${loaded.metadata.owning_branch}; current worktree is on ${branch}`);
    }
    if (!loaded.warnings.length && !loaded.orphanSnapshots.length) {
      console.log(`No repair needed for research/${experiment}/workflow.jsonl`);
      return;
    }
    repairLoaded(root, experiment, loaded);
    console.log(`Repaired research/${experiment}/workflow.jsonl`);
  } finally {
    release();
  }
}

function mermaid(graph) {
  const lines = ['flowchart LR'];
  for (const [name, state] of Object.entries(graph.states)) {
    const label = state.label.replaceAll('"', "'");
    if (state.kind === 'work') lines.push(`  ${name}["${label}"]`);
    else if (state.kind === 'review') lines.push(`  ${name}{"${label}"}`);
    else lines.push(`  ${name}(["${label}"])`);
  }
  for (const [name, state] of Object.entries(graph.states)) {
    if (state.kind === 'work') lines.push(`  ${name} -->|submit| ${state.submit_to}`);
    if (state.kind === 'review') {
      for (const [decision, target] of Object.entries(state.decisions)) {
        lines.push(`  ${name} -->|${decision}| ${target}`);
      }
    }
  }
  return `${lines.join('\n')}\n`;
}

function showGraph(options, graph) {
  requireOnly(options, new Set(['format']));
  const format = optional(options, 'format') || 'mermaid';
  if (format === 'json') console.log(JSON.stringify(graph, null, 2));
  else if (format === 'mermaid') process.stdout.write(mermaid(graph));
  else fail('--format must be mermaid or json');
}

function main(argv) {
  const [command, ...rest] = argv;
  if (!command || command === 'help' || command === '--help' || rest.includes('--help')) {
    usage();
    return;
  }
  const options = parseOptions(rest);
  const graph = loadGraph();
  if (command === 'graph') {
    showGraph(options, graph);
    return;
  }
  const root = repositoryRoot();
  if (command === 'init') initialize(options, root, graph);
  else if (command === 'status') showStatus(options, root, graph);
  else if (command === 'submit') submit(options, root, graph);
  else if (command === 'review') review(options, root, graph);
  else if (command === 'verify') verify(options, root, graph);
  else if (command === 'repair') repair(options, root, graph);
  else fail(`unknown command: ${command}`);
}

try {
  main(process.argv.slice(2));
} catch (error) {
  if (error instanceof CliError) {
    console.error(`research-workflow: ${error.message}`);
    process.exitCode = 1;
  } else {
    throw error;
  }
}
