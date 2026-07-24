import assert from 'node:assert/strict';
import {
  appendFileSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';

const script = resolve('scripts/research-log.mjs');

function fixture() {
  const directory = mkdtempSync(join(tmpdir(), 'research-log-test-'));
  return {
    directory,
    run(...args) {
      return spawnSync(process.execPath, [script, ...args], {
        cwd: resolve('.'),
        encoding: 'utf8',
        env: { ...process.env, RESEARCH_LOG_DIR: directory },
      });
    },
    cleanup() {
      rmSync(directory, { recursive: true, force: true });
    },
  };
}

test('records an append-only session and renders its recovery state', (context) => {
  const log = fixture();
  context.after(() => log.cleanup());

  let result = log.run(
    'start',
    '--session', 'test-session',
    '--title', 'A durable experiment',
    '--question', 'Does every checkpoint survive?',
  );
  assert.equal(result.status, 0, result.stderr);

  result = log.run(
    'checkpoint',
    '--session', 'test-session',
    '--summary', 'The first result landed.',
    '--next', 'Run the confirmation.',
    '--result', 'D = -0.176 eV',
  );
  assert.equal(result.status, 0, result.stderr);

  result = log.run(
    'close',
    '--session', 'test-session',
    '--summary', 'The test is complete.',
  );
  assert.equal(result.status, 0, result.stderr);

  const files = readdirSync(log.directory);
  assert.deepEqual(files, ['test-session.jsonl']);
  const records = readFileSync(join(log.directory, files[0]), 'utf8')
    .trim()
    .split('\n')
    .map(JSON.parse);
  assert.deepEqual(records.map(({ type }) => type), ['start', 'checkpoint', 'close']);
  assert.equal(records[1].result, 'D = -0.176 eV');

  result = log.run('show', '--session', 'test-session');
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /State: closed/);
  assert.match(result.stdout, /The first result landed/);

  result = log.run('note', '--session', 'test-session', '--message', 'Too late');
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /session is closed/);
});

test('recovers complete records before a truncated final append', (context) => {
  const log = fixture();
  context.after(() => log.cleanup());

  let result = log.run(
    'start',
    '--session', 'crashed-session',
    '--title', 'Interrupted experiment',
  );
  assert.equal(result.status, 0, result.stderr);
  appendFileSync(join(log.directory, 'crashed-session.jsonl'), '{"schema":1,"event_id":"cut');

  result = log.run('show', '--session', 'crashed-session');
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /Recovery: ignored incomplete final record at line 2/);

  result = log.run('verify', '--session', 'crashed-session');
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /1 recoverable trailing record/);

  result = log.run(
    'note', '--session', 'crashed-session', '--message', 'Continued after recovery',
  );
  assert.equal(result.status, 0, result.stderr);

  result = log.run('show', '--session', 'crashed-session', '--json');
  assert.equal(result.status, 0, result.stderr);
  const events = result.stdout.trim().split('\n').map(JSON.parse);
  assert.deepEqual(events.map(({ type }) => type), ['start', 'recovery', 'note']);
  assert.equal(events[1].discarded_bytes, 27);

  result = log.run('verify', '--session', 'crashed-session');
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /0 recoverable trailing record/);
});

test('rejects corruption between complete records', (context) => {
  const log = fixture();
  context.after(() => log.cleanup());

  const valid = {
    schema: 1,
    event_id: 'one',
    timestamp: '2026-07-23T00:00:00.000Z',
    session: 'broken-session',
    type: 'start',
    title: 'Broken',
    context: {},
  };
  writeFileSync(
    join(log.directory, 'broken-session.jsonl'),
    `${JSON.stringify(valid)}\nnot-json\n${JSON.stringify({ ...valid, event_id: 'two', type: 'note' })}\n`,
  );

  const result = log.run('verify', '--session', 'broken-session');
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /invalid JSON at line 2/);
});

test('resumes a closed session before accepting more records', (context) => {
  const log = fixture();
  context.after(() => log.cleanup());

  assert.equal(log.run(
    'start', '--session', 'resume-session', '--title', 'Resume me',
  ).status, 0);
  assert.equal(log.run(
    'close', '--session', 'resume-session', '--summary', 'Paused',
  ).status, 0);
  appendFileSync(join(log.directory, 'resume-session.jsonl'), '{"schema":1,"cut');
  assert.equal(log.run(
    'repair', '--session', 'resume-session',
  ).status, 0);
  let result = log.run('show', '--session', 'resume-session');
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /State: closed/);
  assert.equal(log.run(
    'resume', '--session', 'resume-session', '--message', 'Back after a crash',
  ).status, 0);
  assert.equal(log.run(
    'note', '--session', 'resume-session', '--message', 'Recovered',
  ).status, 0);

  result = log.run('show', '--session', 'resume-session');
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /State: open/);
  assert.match(result.stdout, /Back after a crash/);
});
