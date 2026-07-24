#!/usr/bin/env node

import { randomBytes, randomUUID } from 'node:crypto';
import {
  closeSync,
  existsSync,
  fsyncSync,
  mkdirSync,
  openSync,
  readFileSync,
  readdirSync,
  truncateSync,
  writeSync,
} from 'node:fs';
import { basename, join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

const schemaVersion = 1;
const maxRecordBytes = 256 * 1024;
const booleanOptions = new Set(['help', 'json', 'stdin']);
const sessionPattern = /^[a-z0-9][a-z0-9._-]{0,119}$/i;

function fail(message, exitCode = 1) {
  console.error(`research-log: ${message}`);
  process.exit(exitCode);
}

function git(args) {
  const result = spawnSync('git', args, {
    cwd: process.cwd(),
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'ignore'],
  });
  return result.status === 0 ? result.stdout.trim() : null;
}

function storageDirectory() {
  if (process.env.RESEARCH_LOG_DIR) return resolve(process.env.RESEARCH_LOG_DIR);
  const common = git(['rev-parse', '--path-format=absolute', '--git-common-dir']);
  if (!common) {
    fail('not inside a Git repository; set RESEARCH_LOG_DIR to an explicit durable directory');
  }
  return join(common, 'research-journal');
}

function repositoryContext() {
  return {
    worktree: git(['rev-parse', '--show-toplevel']),
    branch: git(['branch', '--show-current']),
    commit: git(['rev-parse', 'HEAD']),
  };
}

function parseOptions(tokens) {
  const options = { positional: [] };
  for (let index = 0; index < tokens.length; index += 1) {
    const token = tokens[index];
    if (!token.startsWith('--')) {
      options.positional.push(token);
      continue;
    }
    const key = token.slice(2);
    if (!key) fail('invalid empty option');
    if (booleanOptions.has(key)) {
      options[key] = true;
      continue;
    }
    if (index + 1 >= tokens.length) fail(`--${key} requires a value`);
    options[key] = tokens[index + 1];
    index += 1;
  }
  return options;
}

function requireOnly(options, allowed) {
  const unexpected = Object.keys(options)
    .filter((key) => key !== 'positional' && !allowed.has(key));
  if (options.positional.length) unexpected.push(...options.positional);
  if (unexpected.length) fail(`unexpected option or argument: ${unexpected[0]}`);
}

function required(options, key) {
  const value = options[key];
  if (typeof value !== 'string' || value.trim() === '') fail(`--${key} is required`);
  return value.trim();
}

function optional(options, key) {
  const value = options[key];
  return typeof value === 'string' && value.trim() !== '' ? value.trim() : undefined;
}

function sessionFrom(options) {
  const session = optional(options, 'session') || process.env.RESEARCH_SESSION_ID;
  if (!session) fail('--session is required (or set RESEARCH_SESSION_ID)');
  if (!sessionPattern.test(session)) fail(`invalid session id: ${session}`);
  return session;
}

function slug(value) {
  return value
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 36) || 'research';
}

function generatedSession(title) {
  const timestamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
  return `${timestamp}-${slug(title)}-${randomBytes(2).toString('hex')}`;
}

function ensureDirectory(directory) {
  mkdirSync(directory, { recursive: true, mode: 0o700 });
}

function syncDirectory(directory) {
  let descriptor;
  try {
    descriptor = openSync(directory, 'r');
    fsyncSync(descriptor);
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
  }
}

function serialize(event) {
  const line = `${JSON.stringify(event)}\n`;
  if (Buffer.byteLength(line) > maxRecordBytes) {
    fail(`record exceeds ${maxRecordBytes} bytes; save large output as an artifact and log its path`);
  }
  return line;
}

function writeRecord(descriptor, event) {
  const record = Buffer.from(serialize(event));
  const written = writeSync(descriptor, record, 0, record.length);
  if (written !== record.length) {
    throw new Error(`short journal write: wrote ${written} of ${record.length} bytes`);
  }
}

function createLog(path, directory, event) {
  let descriptor;
  try {
    descriptor = openSync(path, 'wx', 0o600);
    writeRecord(descriptor, event);
    fsyncSync(descriptor);
  } catch (error) {
    if (error.code === 'EEXIST') fail(`session already exists: ${event.session}`);
    throw error;
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
  }
  syncDirectory(directory);
}

function appendLog(path, event) {
  let descriptor;
  try {
    descriptor = openSync(path, 'a', 0o600);
    writeRecord(descriptor, event);
    fsyncSync(descriptor);
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
  }
}

function readLog(path) {
  const content = readFileSync(path, 'utf8');
  const rawLines = content.split('\n');
  const nonemptyIndexes = rawLines
    .map((line, index) => (line.trim() ? index : -1))
    .filter((index) => index >= 0);
  const lastNonempty = nonemptyIndexes.at(-1);
  const events = [];
  const warnings = [];
  let validBytes = Buffer.byteLength(content);
  let discardedBytes = 0;

  for (const index of nonemptyIndexes) {
    try {
      events.push(JSON.parse(rawLines[index]));
    } catch (error) {
      if (index === lastNonempty) {
        const validPrefix = index === 0 ? '' : `${rawLines.slice(0, index).join('\n')}\n`;
        validBytes = Buffer.byteLength(validPrefix);
        discardedBytes = Buffer.byteLength(content) - validBytes;
        warnings.push(
          `ignored incomplete final record at line ${index + 1} (${discardedBytes} byte(s))`,
        );
        continue;
      }
      throw new Error(`invalid JSON at line ${index + 1}: ${error.message}`);
    }
  }

  if (!events.length) throw new Error('contains no complete records');
  const expectedSession = events[0].session;
  if (!events.every((event) => event.schema === schemaVersion && event.session === expectedSession)) {
    throw new Error('contains mixed sessions or unsupported schema versions');
  }
  return { events, warnings, validBytes, discardedBytes };
}

function logPath(directory, session) {
  if (!sessionPattern.test(session)) fail(`invalid session id: ${session}`);
  return join(directory, `${session}.jsonl`);
}

function eventFor(session, type, fields) {
  return {
    schema: schemaVersion,
    event_id: randomUUID(),
    timestamp: new Date().toISOString(),
    session,
    type,
    ...fields,
    context: repositoryContext(),
  };
}

function loadSession(directory, session) {
  const path = logPath(directory, session);
  if (!existsSync(path)) fail(`unknown session: ${session}`);
  let parsed;
  try {
    parsed = readLog(path);
  } catch (error) {
    fail(`${basename(path)}: ${error.message}`);
  }
  return { path, ...parsed };
}

function stateOf(events) {
  for (let index = events.length - 1; index >= 0; index -= 1) {
    if (events[index].type === 'close') return 'closed';
    if (events[index].type === 'resume' || events[index].type === 'start') return 'open';
  }
  return 'open';
}

function repairTail(loaded, session) {
  if (!loaded.warnings.length) return;
  truncateSync(loaded.path, loaded.validBytes);
  let descriptor;
  try {
    descriptor = openSync(loaded.path, 'r');
    fsyncSync(descriptor);
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
  }
  appendLog(loaded.path, eventFor(session, 'recovery', {
    message: 'Discarded an incomplete final record left by an interrupted append.',
    discarded_bytes: loaded.discardedBytes,
  }));
}

function appendEvent(directory, session, type, fields, { allowClosed = false } = {}) {
  const loaded = loadSession(directory, session);
  if (!allowClosed && stateOf(loaded.events) === 'closed') {
    fail(`session is closed: ${session}; run resume before appending`);
  }
  repairTail(loaded, session);
  appendLog(loaded.path, eventFor(session, type, fields));
  console.log(`Recorded ${type} in ${session}`);
  console.log(`Journal: ${loaded.path}`);
}

function stdinText() {
  const value = readFileSync(0, 'utf8').trimEnd();
  if (!value) fail('--stdin received no content');
  return value;
}

function start(options, directory) {
  requireOnly(options, new Set(['title', 'question', 'session']));
  const title = required(options, 'title');
  const session = optional(options, 'session') || generatedSession(title);
  if (!sessionPattern.test(session)) fail(`invalid session id: ${session}`);
  ensureDirectory(directory);
  const path = logPath(directory, session);
  createLog(path, directory, eventFor(session, 'start', {
    title,
    question: optional(options, 'question'),
  }));
  console.log(`Started ${session}`);
  console.log(`Journal: ${path}`);
  console.log(`Next: node scripts/research-log.mjs checkpoint --session ${session} --summary "..." --next "..."`);
}

function note(options, directory) {
  requireOnly(options, new Set(['session', 'message', 'tag', 'stdin']));
  const session = sessionFrom(options);
  const message = options.stdin ? stdinText() : required(options, 'message');
  appendEvent(directory, session, 'note', { message, tag: optional(options, 'tag') });
}

function source(options, directory) {
  requireOnly(options, new Set(['session', 'source', 'title', 'finding']));
  const session = sessionFrom(options);
  appendEvent(directory, session, 'source', {
    source: required(options, 'source'),
    title: optional(options, 'title'),
    finding: required(options, 'finding'),
  });
}

function decision(options, directory) {
  requireOnly(options, new Set(['session', 'decision', 'reason', 'alternatives']));
  const session = sessionFrom(options);
  appendEvent(directory, session, 'decision', {
    decision: required(options, 'decision'),
    reason: optional(options, 'reason'),
    alternatives: optional(options, 'alternatives'),
  });
}

function checkpoint(options, directory) {
  requireOnly(options, new Set([
    'session', 'summary', 'next', 'command', 'result', 'artifact', 'stdin',
  ]));
  const session = sessionFrom(options);
  const summary = options.stdin ? stdinText() : required(options, 'summary');
  appendEvent(directory, session, 'checkpoint', {
    summary,
    next: optional(options, 'next'),
    command: optional(options, 'command'),
    result: optional(options, 'result'),
    artifact: optional(options, 'artifact'),
  });
}

function close(options, directory) {
  requireOnly(options, new Set(['session', 'summary', 'next', 'stdin']));
  const session = sessionFrom(options);
  const summary = options.stdin ? stdinText() : required(options, 'summary');
  appendEvent(directory, session, 'close', {
    summary,
    next: optional(options, 'next'),
  });
}

function resume(options, directory) {
  requireOnly(options, new Set(['session', 'message']));
  const session = sessionFrom(options);
  const loaded = loadSession(directory, session);
  if (stateOf(loaded.events) !== 'closed') fail(`session is already open: ${session}`);
  repairTail(loaded, session);
  appendLog(loaded.path, eventFor(session, 'resume', {
    message: optional(options, 'message') || 'Research resumed',
  }));
  console.log(`Resumed ${session}`);
  console.log(`Journal: ${loaded.path}`);
}

function journalFiles(directory) {
  if (!existsSync(directory)) return [];
  return readdirSync(directory)
    .filter((name) => name.endsWith('.jsonl'))
    .map((name) => join(directory, name))
    .sort();
}

function list(options, directory) {
  requireOnly(options, new Set(['json']));
  const rows = journalFiles(directory).map((path) => {
    try {
      const { events, warnings } = readLog(path);
      const first = events[0];
      const last = events.at(-1);
      return {
        session: first.session,
        state: stateOf(events),
        title: first.title || '',
        updated: last.timestamp,
        events: events.length,
        recovery_warnings: warnings,
      };
    } catch (error) {
      return {
        session: basename(path, '.jsonl'),
        state: 'invalid',
        error: error.message,
      };
    }
  }).sort((left, right) => String(right.updated || '').localeCompare(String(left.updated || '')));

  if (options.json) {
    console.log(JSON.stringify(rows, null, 2));
    return;
  }
  if (!rows.length) {
    console.log(`No research journals in ${directory}`);
    return;
  }
  for (const row of rows) {
    if (row.state === 'invalid') {
      console.log(`${row.session}\tinvalid\t${row.error}`);
      continue;
    }
    const warning = row.recovery_warnings.length ? '\trecovered-tail' : '';
    console.log(`${row.updated}\t${row.state}\t${row.events}\t${row.session}\t${row.title}${warning}`);
  }
}

function eventDetails(event) {
  const omitted = new Set(['schema', 'event_id', 'timestamp', 'session', 'type', 'context', 'title']);
  return Object.entries(event)
    .filter(([key, value]) => !omitted.has(key) && value !== undefined)
    .map(([key, value]) => `- ${key.replaceAll('_', ' ')}: ${value}`);
}

function show(options, directory) {
  requireOnly(options, new Set(['session', 'json']));
  const session = sessionFrom(options);
  const { events, warnings } = loadSession(directory, session);
  if (options.json) {
    for (const event of events) console.log(JSON.stringify(event));
    return;
  }
  const first = events[0];
  console.log(`# ${first.title || session}`);
  console.log('');
  console.log(`Session: ${session}`);
  console.log(`State: ${stateOf(events)}`);
  console.log(`Events: ${events.length}`);
  for (const warning of warnings) console.log(`Recovery: ${warning}`);

  for (const event of events) {
    console.log('');
    console.log(`## ${event.timestamp} · ${event.type}`);
    console.log('');
    const details = eventDetails(event);
    if (details.length) console.log(details.join('\n'));
    const context = event.context || {};
    if (context.branch || context.commit) {
      console.log(`- git: ${context.branch || '(detached)'} @ ${(context.commit || 'unknown').slice(0, 12)}`);
    }
  }
}

function verify(options, directory) {
  requireOnly(options, new Set(['session']));
  const selectedSession = optional(options, 'session');
  const paths = selectedSession
    ? [logPath(directory, selectedSession)]
    : journalFiles(directory);
  if (selectedSession && !existsSync(paths[0])) fail(`unknown session: ${selectedSession}`);
  let failures = 0;
  let recovered = 0;
  for (const path of paths) {
    try {
      const { events, warnings } = readLog(path);
      recovered += warnings.length;
      console.log(`ok ${basename(path)}: ${events.length} complete record(s)${warnings.length ? `; ${warnings.join('; ')}` : ''}`);
    } catch (error) {
      failures += 1;
      console.error(`invalid ${basename(path)}: ${error.message}`);
    }
  }
  if (failures) fail(`${failures} invalid journal(s)`);
  console.log(`Verified ${paths.length} journal(s); ${recovered} recoverable trailing record(s) ignored`);
}

function repair(options, directory) {
  requireOnly(options, new Set(['session']));
  const session = sessionFrom(options);
  const loaded = loadSession(directory, session);
  if (!loaded.warnings.length) {
    console.log(`No repair needed for ${session}`);
    return;
  }
  const discardedBytes = loaded.discardedBytes;
  repairTail(loaded, session);
  console.log(`Repaired ${session}; discarded ${discardedBytes} incomplete trailing byte(s)`);
  console.log(`Journal: ${loaded.path}`);
}

function usage() {
  console.log(`Crash-resistant, append-only research journal.

Usage:
  research-log.mjs start --title TEXT [--question TEXT] [--session ID]
  research-log.mjs note --session ID (--message TEXT | --stdin) [--tag TAG]
  research-log.mjs source --session ID --source URL_OR_PATH --finding TEXT [--title TEXT]
  research-log.mjs decision --session ID --decision TEXT [--reason TEXT] [--alternatives TEXT]
  research-log.mjs checkpoint --session ID (--summary TEXT | --stdin) [--next TEXT]
      [--command TEXT] [--result TEXT] [--artifact PATH]
  research-log.mjs close --session ID (--summary TEXT | --stdin) [--next TEXT]
  research-log.mjs resume --session ID [--message TEXT]
  research-log.mjs list [--json]
  research-log.mjs show --session ID [--json]
  research-log.mjs verify [--session ID]
  research-log.mjs repair --session ID
  research-log.mjs path

Storage defaults to <git-common-dir>/research-journal, shared by every worktree.
Set RESEARCH_LOG_DIR to override it in tests or outside Git. Set
RESEARCH_SESSION_ID to omit repeated --session arguments. Do not log secrets.`);
}

const [command, ...tokens] = process.argv.slice(2);
const options = parseOptions(tokens);
if (!command || command === 'help' || options.help) {
  usage();
  process.exit(0);
}

const directory = storageDirectory();

switch (command) {
  case 'start':
    start(options, directory);
    break;
  case 'note':
    note(options, directory);
    break;
  case 'source':
    source(options, directory);
    break;
  case 'decision':
    decision(options, directory);
    break;
  case 'checkpoint':
    checkpoint(options, directory);
    break;
  case 'close':
    close(options, directory);
    break;
  case 'resume':
    resume(options, directory);
    break;
  case 'list':
    list(options, directory);
    break;
  case 'show':
    show(options, directory);
    break;
  case 'verify':
    verify(options, directory);
    break;
  case 'repair':
    repair(options, directory);
    break;
  case 'path':
    requireOnly(options, new Set());
    console.log(directory);
    break;
  default:
    fail(`unknown command: ${command}; run research-log.mjs help`);
}
