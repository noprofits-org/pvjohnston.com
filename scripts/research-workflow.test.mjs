import assert from 'node:assert/strict';
import {
  appendFileSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import { hostname, tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { spawn as spawnProcess, spawnSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import test from 'node:test';

const script = resolve('scripts/research-workflow.mjs');
const graphPath = resolve('research/workflow.graph.v1.json');

function runGit(directory, ...args) {
  const result = spawnSync('git', args, { cwd: directory, encoding: 'utf8' });
  if (result.status !== 0) {
    throw new Error(`git ${args.join(' ')} failed:\n${result.stderr}\n${result.stdout}`);
  }
  return result.stdout.trim();
}

function fixture(experiment = 'demo-experiment') {
  const sandbox = mkdtempSync(join(tmpdir(), 'research-workflow-test-'));
  const primary = join(sandbox, 'primary');
  const root = join(sandbox, 'post-worktree');
  mkdirSync(primary);
  runGit(primary, 'init', '--initial-branch=main');
  writeFileSync(join(primary, '.gitkeep'), '');
  runGit(primary, 'add', '.gitkeep');
  runGit(
    primary,
    '-c', 'user.name=Workflow Tests',
    '-c', 'user.email=workflow-tests@example.invalid',
    'commit', '-m', 'Initialize fixture',
  );
  runGit(primary, 'worktree', 'add', '-b', `post/${experiment}`, root);
  const journalDirectory = join(root, 'journal');
  const experimentDirectory = join(root, 'research', experiment);
  mkdirSync(journalDirectory, { recursive: true });
  mkdirSync(experimentDirectory, { recursive: true });
  mkdirSync(join(root, 'notes'), { recursive: true });
  writeFileSync(join(root, 'notes', 'questions.md'), [
    '# The shelf',
    '',
    '## Frozen workflow handoffs',
    '- **Status:** ready — selected for the test',
    '',
    '## Not ready yet',
    '- **Status:** observation',
    '',
  ].join('\n'));

  const session = 'test-journal';
  writeFileSync(join(journalDirectory, `${session}.jsonl`), `${JSON.stringify({
    schema: 1,
    event_id: randomUUID(),
    timestamp: '2026-08-08T00:00:00.000Z',
    session,
    type: 'start',
    title: 'Test workflow',
    context: {},
  })}\n`);

  function environment(extra = {}) {
    return {
      ...process.env,
      RESEARCH_LOG_DIR: journalDirectory,
      RESEARCH_WORKFLOW_ROOT: root,
      ...extra,
    };
  }

  return {
    sandbox,
    primary,
    root,
    experiment,
    session,
    experimentDirectory,
    journalDirectory,
    checkpoint(summary = 'Checkpoint immediately before the workflow handoff.') {
      const event = journalEvent(this, 'checkpoint', {
        summary,
        next: 'Record the workflow handoff.',
      });
      appendFileSync(this.journalPath(), `${JSON.stringify(event)}\n`);
      return event;
    },
    journalEvent(type, overrides = {}) {
      const event = journalEvent(this, type, overrides);
      appendFileSync(this.journalPath(), `${JSON.stringify(event)}\n`);
      return event;
    },
    runWithoutCheckpoint(...args) {
      return spawnSync(process.execPath, [script, ...args], {
        cwd: resolve('.'),
        encoding: 'utf8',
        env: environment(),
      });
    },
    run(...args) {
      if (args[0] === 'submit' || args[0] === 'review') this.checkpoint();
      return this.runWithoutCheckpoint(...args);
    },
    runWithEnv(extra, ...args) {
      return spawnSync(process.execPath, [script, ...args], {
        cwd: resolve('.'),
        encoding: 'utf8',
        env: environment(extra),
      });
    },
    runAsync(...args) {
      if (args[0] === 'submit' || args[0] === 'review') this.checkpoint();
      return new Promise((complete) => {
        const child = spawnProcess(process.execPath, [script, ...args], {
          cwd: resolve('.'),
          env: environment(),
        });
        let stdout = '';
        let stderr = '';
        child.stdout.setEncoding('utf8');
        child.stderr.setEncoding('utf8');
        child.stdout.on('data', (chunk) => { stdout += chunk; });
        child.stderr.on('data', (chunk) => { stderr += chunk; });
        child.on('close', (status) => complete({ status, stdout, stderr }));
      });
    },
    write(path, content) {
      const target = join(root, path);
      mkdirSync(dirname(target), { recursive: true });
      writeFileSync(target, content);
      return path;
    },
    receipt(name, content = `# ${name}\n`) {
      return this.write(`research/${experiment}/workflow/receipts/${name}`, content);
    },
    logPath() {
      return join(experimentDirectory, 'workflow.jsonl');
    },
    journalPath() {
      return join(journalDirectory, `${session}.jsonl`);
    },
    evidenceDirectory() {
      return join(experimentDirectory, 'workflow', 'evidence');
    },
    events() {
      return readFileSync(this.logPath(), 'utf8').trim().split('\n').map(JSON.parse);
    },
    snapshots() {
      return readdirSync(this.evidenceDirectory()).sort();
    },
    git(...args) {
      return runGit(root, ...args);
    },
    cleanup() {
      rmSync(sandbox, { recursive: true, force: true });
    },
  };
}

function initialize(flow, postType = 'research') {
  const args = [
    'init',
    '--experiment', flow.experiment,
    '--post-type', postType,
    '--question', 'Does the frozen workflow preserve every handoff?',
    '--journal', flow.session,
    '--actor', 'coordinator',
  ];
  if (postType === 'research') args.push('--shelf-entry', 'Frozen workflow handoffs');
  return flow.run(...args);
}

function assertFailed(result, pattern) {
  assert.notEqual(result.status, 0, `command unexpectedly succeeded:\n${result.stdout}`);
  assert.match(`${result.stderr}\n${result.stdout}`, pattern);
}

function submitCurrent(flow, state, index, artifacts = undefined) {
  const submitted = artifacts || [flow.receipt(
    `${String(index).padStart(2, '0')}-${state}-handoff-v1.md`,
    `# ${state} handoff\n\nVersion ${index}.\n`,
  )];
  const args = [
    'submit', '--experiment', flow.experiment,
    '--actor', `worker-${index}`,
  ];
  for (const artifact of submitted) args.push('--artifact', artifact);
  const result = flow.run(...args);
  assert.equal(result.status, 0, result.stderr);
  return { result, artifacts: submitted };
}

function reviewCurrent(flow, gate, index, decision = 'approve') {
  const report = flow.receipt(
    `${String(index).padStart(2, '0')}-${gate}-review-v1.md`,
    `# ${gate} review\n\nDecision: ${decision}.\n`,
  );
  const result = flow.run(
    'review', '--experiment', flow.experiment,
    '--actor', `reviewer-${index}`,
    '--decision', decision,
    '--artifact', report,
  );
  assert.equal(result.status, 0, result.stderr);
  return { result, report };
}

function approveStage(flow, state, gate, index) {
  const submission = submitCurrent(flow, state, index);
  const review = reviewCurrent(flow, gate, index);
  return { ...submission, ...review };
}

function journalEvent(flow, type, overrides = {}) {
  return {
    schema: 1,
    event_id: randomUUID(),
    timestamp: '2026-08-08T00:01:00.000Z',
    session: flow.session,
    type,
    context: {},
    ...overrides,
  };
}

test('renders the immutable v1 graph, amendment route, and PR gate', () => {
  let result = spawnSync(process.execPath, [script, 'graph', '--format', 'json'], {
    cwd: resolve('.'),
    encoding: 'utf8',
  });
  assert.equal(result.status, 0, result.stderr);
  const graph = JSON.parse(result.stdout);
  assert.equal(graph.graph_version, 1);
  assert.equal(graph.initial_state, 'brainstorm');
  assert.equal(graph.states.setup.submit_to, 'setup_review');
  assert.equal(graph.states.run_review.decisions.amend, 'protocol_amendment');
  assert.equal(graph.states.run_review.decisions.registered_retry, 'execute');
  assert.equal(graph.states.analysis_review.decisions.registered_rerun, 'execute');
  assert.equal(graph.states.protocol_amendment.submit_to, 'amendment_review');
  assert.equal(graph.states.amendment_review.decisions.approve, 'amended_setup');
  assert.equal(graph.states.amended_setup.submit_to, 'amended_setup_review');
  assert.equal(graph.states.amended_setup_review.decisions.amend, 'protocol_amendment');
  assert.equal(Object.hasOwn(graph.states.amended_setup_review.decisions, 'redesign'), false);
  assert.equal(graph.states.editorial_review.decisions.approve, 'ready_for_pr');
  assert.equal(graph.states.ready_for_pr.submit_to, 'pr_review');
  assert.equal(graph.states.pr_review.decisions.approve, 'ready_to_merge');
  assert.deepEqual(graph.terminal_states, ['ready_to_merge', 'parked']);

  result = spawnSync(process.execPath, [script, 'graph'], {
    cwd: resolve('.'),
    encoding: 'utf8',
  });
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /brainstorm -->\|submit\| question_review/);
  assert.match(result.stdout, /run_review -->\|amend\| protocol_amendment/);
  assert.match(result.stdout, /ready_for_pr -->\|submit\| pr_review/);
  assert.match(result.stdout, /pr_review -->\|approve\| ready_to_merge/);
});

test('requires a ready shelf entry and an existing open journal', (context) => {
  const flow = fixture();
  context.after(() => flow.cleanup());

  let result = flow.run(
    'init', '--experiment', flow.experiment,
    '--post-type', 'research', '--question', 'A question?',
    '--journal', flow.session, '--actor', 'coordinator',
  );
  assertFailed(result, /--shelf-entry is required/i);

  result = flow.run(
    'init', '--experiment', flow.experiment,
    '--post-type', 'research', '--question', 'A question?',
    '--journal', flow.session, '--actor', 'coordinator',
    '--shelf-entry', 'Not ready yet',
  );
  assertFailed(result, /shelf entry.*not ready/i);

  result = flow.run(
    'init', '--experiment', flow.experiment,
    '--post-type', 'research', '--question', 'A question?',
    '--journal', flow.session, '--actor', 'coordinator',
    '--shelf-entry', 'Does not exist',
  );
  assertFailed(result, /shelf entry.*(not found|does not exist)/i);

  result = flow.run(
    'init', '--experiment', flow.experiment,
    '--post-type', 'understanding', '--question', 'A question?',
    '--journal', 'missing-journal', '--actor', 'coordinator',
  );
  assertFailed(result, /journal session does not exist/i);

  const staleInitStage = join(
    flow.experimentDirectory,
    `.workflow-init.${randomUUID()}.tmp`,
  );
  writeFileSync(staleInitStage, '{"interrupted":"before-install"');
  result = initialize(flow);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stderr, /Removed uncommitted atomic-init staging file/i);
  assert.equal(readFileSync(flow.logPath()).at(-1), 0x0a);
  assert.equal(
    readdirSync(flow.experimentDirectory).some((name) => name.startsWith('.workflow-init.')),
    false,
  );
  result = flow.run('status', '--experiment', flow.experiment, '--json');
  assert.equal(result.status, 0, result.stderr);
  const status = JSON.parse(result.stdout);
  assert.equal(status.state, 'brainstorm');
  assert.equal(status.role, 'research_brainstormer');
  assert.deepEqual(status.allowed, { submit: 'question_review' });
});

test('rejects closed, mixed-session, and corrupt research journals at init', (context) => {
  const closed = fixture('closed-journal');
  const mixed = fixture('mixed-journal');
  const corrupt = fixture('corrupt-journal');
  const secondStart = fixture('second-journal-start');
  const malformedResume = fixture('malformed-journal-resume');
  context.after(() => {
    closed.cleanup();
    mixed.cleanup();
    corrupt.cleanup();
    secondStart.cleanup();
    malformedResume.cleanup();
  });

  appendFileSync(closed.journalPath(), `${JSON.stringify(journalEvent(closed, 'close', {
    summary: 'Closed before workflow initialization.',
  }))}\n`);
  assertFailed(initialize(closed), /journal.*closed|resume.*journal/i);

  appendFileSync(mixed.journalPath(), `${JSON.stringify(journalEvent(mixed, 'note', {
    session: 'another-session',
    message: 'Wrong journal.',
  }))}\n`);
  assertFailed(initialize(mixed), /journal.*mixed|another session|session mismatch/i);

  appendFileSync(corrupt.journalPath(), 'not-json\n');
  assertFailed(initialize(corrupt), /journal.*(invalid|corrupt)|invalid JSON/i);

  appendFileSync(secondStart.journalPath(), [
    JSON.stringify(journalEvent(secondStart, 'close', { summary: 'Closed once.' })),
    JSON.stringify(journalEvent(secondStart, 'start', { title: 'Illicit second start.' })),
    '',
  ].join('\n'));
  assertFailed(initialize(secondStart), /second or misplaced start/i);
  assert.equal(existsSync(secondStart.logPath()), false);

  appendFileSync(malformedResume.journalPath(), [
    JSON.stringify(journalEvent(malformedResume, 'close', { summary: 'Closed once.' })),
    JSON.stringify({ schema: 1, session: malformedResume.session, type: 'resume' }),
    '',
  ].join('\n'));
  assertFailed(initialize(malformedResume), /malformed common fields|missing message/i);
  assert.equal(existsSync(malformedResume.logPath()), false);
});

test('allows workflow writes only from the exact owning linked post worktree', (context) => {
  const primaryFlow = fixture('primary-guard');
  const featureFlow = fixture('feature-guard');
  const detachedFlow = fixture('detached-guard');
  const ownerFlow = fixture('owner-guard');
  context.after(() => {
    primaryFlow.cleanup();
    featureFlow.cleanup();
    detachedFlow.cleanup();
    ownerFlow.cleanup();
  });

  runGit(primaryFlow.primary, 'switch', '-c', 'post/primary-only');
  let result = primaryFlow.runWithEnv(
    { RESEARCH_WORKFLOW_ROOT: primaryFlow.primary },
    'init', '--experiment', primaryFlow.experiment,
    '--post-type', 'understanding', '--question', 'Can primary mutate?',
    '--journal', primaryFlow.session, '--actor', 'coordinator',
  );
  assertFailed(result, /linked non-primary worktree/i);

  featureFlow.git('switch', '-c', 'feature/not-a-post');
  assertFailed(initialize(featureFlow), /post\/<slug>.*linked non-primary worktree/i);

  detachedFlow.git('switch', '--detach');
  assertFailed(initialize(detachedFlow), /post\/<slug>.*linked non-primary worktree/i);

  assert.equal(initialize(ownerFlow).status, 0);
  const originalLog = readFileSync(ownerFlow.logPath());
  const originalSnapshots = ownerFlow.snapshots();
  const receipt = ownerFlow.receipt('wrong-post-branch.md');
  ownerFlow.git('switch', '-c', 'post/another-owner');
  result = ownerFlow.runWithoutCheckpoint(
    'submit', '--experiment', ownerFlow.experiment,
    '--actor', 'designer', '--artifact', receipt,
  );
  assertFailed(result, /belongs to post\/owner-guard/i);
  assert.deepEqual(readFileSync(ownerFlow.logPath()), originalLog);
  assert.deepEqual(ownerFlow.snapshots(), originalSnapshots);
  assert.equal(existsSync(join(ownerFlow.experimentDirectory, 'workflow', '.transition.lock')), false);
  result = ownerFlow.runWithoutCheckpoint('repair', '--experiment', ownerFlow.experiment);
  assertFailed(result, /belongs to post\/owner-guard/i);
  assert.deepEqual(readFileSync(ownerFlow.logPath()), originalLog);

  ownerFlow.git('switch', 'post/owner-guard');
  result = ownerFlow.run(
    'submit', '--experiment', ownerFlow.experiment,
    '--actor', 'designer', '--artifact', receipt,
  );
  assert.equal(result.status, 0, result.stderr);
});

test('binds every transition to a fresh final checkpoint in the open journal', (context) => {
  const flow = fixture('journal-handoff-gate');
  context.after(() => flow.cleanup());
  assert.equal(initialize(flow).status, 0);
  const handoff = flow.receipt('checkpointed-handoff.md');
  const initialLog = readFileSync(flow.logPath());

  let result = flow.runWithoutCheckpoint(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer', '--artifact', handoff,
  );
  assertFailed(result, /fresh checkpoint.*--next/i);
  assert.deepEqual(readFileSync(flow.logPath()), initialLog);
  assert.deepEqual(flow.snapshots(), []);

  flow.journalEvent('checkpoint', { summary: 'Missing the explicit next action.' });
  result = flow.runWithoutCheckpoint(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer', '--artifact', handoff,
  );
  assertFailed(result, /fresh checkpoint.*--next/i);

  flow.checkpoint('Checkpoint followed by more journal work.');
  flow.journalEvent('note', { message: 'This makes the checkpoint no longer final.' });
  result = flow.runWithoutCheckpoint(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer', '--artifact', handoff,
  );
  assertFailed(result, /fresh checkpoint.*immediately before/i);

  const submitCheckpoint = flow.checkpoint('Final checkpoint for submission.');
  result = flow.runWithoutCheckpoint(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer', '--artifact', handoff,
  );
  assert.equal(result.status, 0, result.stderr);
  assert.equal(flow.events()[1].journal_checkpoint_event_id, submitCheckpoint.event_id);

  const review = flow.receipt('checkpointed-review.md');
  result = flow.runWithoutCheckpoint(
    'review', '--experiment', flow.experiment,
    '--actor', 'reviewer', '--decision', 'approve', '--artifact', review,
  );
  assertFailed(result, /fresh checkpoint.*--next/i);

  flow.checkpoint('Checkpoint before closing the journal.');
  flow.journalEvent('close', { summary: 'Temporarily closed.' });
  result = flow.runWithoutCheckpoint(
    'review', '--experiment', flow.experiment,
    '--actor', 'reviewer', '--decision', 'approve', '--artifact', review,
  );
  assertFailed(result, /journal session is closed.*resume/i);
  flow.journalEvent('resume', { message: 'Resume for the review handoff.' });
  result = flow.runWithoutCheckpoint(
    'review', '--experiment', flow.experiment,
    '--actor', 'reviewer', '--decision', 'approve', '--artifact', review,
  );
  assertFailed(result, /fresh checkpoint.*immediately before/i);

  const reviewCheckpoint = flow.checkpoint('Final checkpoint for review.');
  result = flow.runWithoutCheckpoint(
    'review', '--experiment', flow.experiment,
    '--actor', 'reviewer', '--decision', 'approve', '--artifact', review,
  );
  assert.equal(result.status, 0, result.stderr);
  assert.equal(flow.events()[2].journal_checkpoint_event_id, reviewCheckpoint.event_id);
  assert.notEqual(submitCheckpoint.event_id, reviewCheckpoint.event_id);
  result = flow.run('verify', '--experiment', flow.experiment);
  assert.equal(result.status, 0, result.stderr);

  const validLog = readFileSync(flow.logPath(), 'utf8');
  const reusedCheckpointEvents = flow.events();
  reusedCheckpointEvents[2].journal_checkpoint_event_id =
    reusedCheckpointEvents[1].journal_checkpoint_event_id;
  writeFileSync(
    flow.logPath(),
    `${reusedCheckpointEvents.map((event) => JSON.stringify(event)).join('\n')}\n`,
  );
  result = flow.run('verify', '--experiment', flow.experiment);
  assertFailed(result, /invalid or reused journal checkpoint/i);
  writeFileSync(flow.logPath(), validLog);
});

test('reaches ready_to_merge through independent review and reports null terminal iteration', (context) => {
  const flow = fixture();
  context.after(() => flow.cleanup());
  assert.equal(initialize(flow).status, 0);

  const stages = [
    ['brainstorm', 'question_review'],
    ['setup', 'setup_review'],
    ['execute', 'run_review'],
    ['analyze', 'analysis_review'],
    ['write', 'editorial_review'],
    ['ready_for_pr', 'pr_review'],
  ];

  for (const [index, [work, gate]] of stages.entries()) {
    const number = index + 1;
    submitCurrent(flow, work, number);
    const report = flow.receipt(
      `${String(number).padStart(2, '0')}-${gate}-self-review.md`,
      `# Invalid self-review for ${gate}\n`,
    );
    const beforeLog = readFileSync(flow.logPath(), 'utf8');
    const beforeSnapshots = flow.snapshots();
    const rejected = flow.run(
      'review', '--experiment', flow.experiment,
      '--actor', `worker-${number}`, '--decision', 'approve',
      '--artifact', report,
    );
    assertFailed(rejected, /cannot approve or reject their own submission|self-review/i);
    assert.equal(readFileSync(flow.logPath(), 'utf8'), beforeLog);
    assert.deepEqual(flow.snapshots(), beforeSnapshots);
    reviewCurrent(flow, gate, number);
  }

  let result = flow.run('status', '--experiment', flow.experiment, '--json');
  assert.equal(result.status, 0, result.stderr);
  const status = JSON.parse(result.stdout);
  assert.equal(status.state, 'ready_to_merge');
  assert.equal(status.kind, 'terminal');
  assert.equal(status.iteration, null);
  assert.deepEqual(status.allowed, {});

  result = flow.run('verify', '--experiment', flow.experiment);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /13 event\(s\), 12 snapshot\(s\), state=ready_to_merge/);
  assert.equal(flow.snapshots().length, 12);
  const graphDigests = new Set(flow.events().map(({ graph_sha256: digest }) => {
    assert.match(digest, /^[a-f0-9]{64}$/);
    return digest;
  }));
  assert.equal(graphDigests.size, 1);
});

test('routes exposed production changes through protocol amendment and full setup review', (context) => {
  const flow = fixture();
  context.after(() => flow.cleanup());
  assert.equal(initialize(flow).status, 0);

  approveStage(flow, 'brainstorm', 'question_review', 1);
  approveStage(flow, 'setup', 'setup_review', 2);
  submitCurrent(flow, 'execute', 3);
  reviewCurrent(flow, 'run_review', 3, 'amend');

  let result = flow.run('status', '--experiment', flow.experiment, '--json');
  assert.equal(result.status, 0, result.stderr);
  assert.equal(JSON.parse(result.stdout).state, 'protocol_amendment');

  submitCurrent(flow, 'protocol_amendment', 4);
  reviewCurrent(flow, 'amendment_review', 4, 'approve');
  result = flow.run('status', '--experiment', flow.experiment, '--json');
  assert.equal(result.status, 0, result.stderr);
  assert.equal(JSON.parse(result.stdout).state, 'amended_setup');

  submitCurrent(flow, 'amended_setup', 5);
  const invalidReview = flow.receipt('amended-setup-redesign.md', '# Invalid redesign\n');
  result = flow.run(
    'review', '--experiment', flow.experiment,
    '--actor', 'reviewer-5', '--decision', 'redesign', '--artifact', invalidReview,
  );
  assertFailed(result, /decision.*must be one of/i);
  reviewCurrent(flow, 'amended_setup_review', 5, 'approve');
  result = flow.run('status', '--experiment', flow.experiment, '--json');
  assert.equal(result.status, 0, result.stderr);
  assert.equal(JSON.parse(result.stdout).state, 'execute');
});

test('rejects inherited-property decisions without log or snapshot side effects', (context) => {
  const flow = fixture();
  context.after(() => flow.cleanup());
  assert.equal(initialize(flow).status, 0);
  submitCurrent(flow, 'brainstorm', 1);
  const report = flow.receipt('inherited-decision-review.md', '# Invalid decision\n');

  for (const decision of ['constructor', 'toString', '__proto__']) {
    const beforeLog = readFileSync(flow.logPath(), 'utf8');
    const beforeSnapshots = flow.snapshots();
    const result = flow.run(
      'review', '--experiment', flow.experiment,
      '--actor', `reviewer-${decision}`, '--decision', decision,
      '--artifact', report,
    );
    assertFailed(result, /decision.*(must be one of|not allowed|invalid)/i);
    assert.equal(readFileSync(flow.logPath(), 'utf8'), beforeLog);
    assert.deepEqual(flow.snapshots(), beforeSnapshots);
  }
});

test('rejects a symlinked workflow directory before writing outside the experiment', (context) => {
  const flow = fixture();
  const outside = mkdtempSync(join(tmpdir(), 'research-workflow-outside-'));
  context.after(() => {
    flow.cleanup();
    rmSync(outside, { recursive: true, force: true });
  });
  symlinkSync(outside, join(flow.experimentDirectory, 'workflow'), 'dir');

  const result = initialize(flow);
  assertFailed(result, /workflow.*(link|symlink|real directory)|managed directory.*outside/i);
  assert.deepEqual(readdirSync(outside), []);
});

test('rejects symlinked evidence and log paths without modifying their targets', (context) => {
  const evidenceFlow = fixture('linked-evidence');
  const logFlow = fixture('linked-log');
  const outside = mkdtempSync(join(tmpdir(), 'research-workflow-outside-'));
  context.after(() => {
    evidenceFlow.cleanup();
    logFlow.cleanup();
    rmSync(outside, { recursive: true, force: true });
  });

  assert.equal(initialize(evidenceFlow).status, 0);
  rmSync(evidenceFlow.evidenceDirectory(), { recursive: true });
  const outsideEvidence = join(outside, 'evidence');
  mkdirSync(outsideEvidence);
  symlinkSync(outsideEvidence, evidenceFlow.evidenceDirectory(), 'dir');
  const handoff = evidenceFlow.receipt('linked-evidence-handoff.md');
  let result = evidenceFlow.run(
    'submit', '--experiment', evidenceFlow.experiment,
    '--actor', 'designer', '--artifact', handoff,
  );
  assertFailed(result, /evidence.*(link|symlink|outside|real directory)/i);
  assert.deepEqual(readdirSync(outsideEvidence), []);

  assert.equal(initialize(logFlow).status, 0);
  const victim = join(outside, 'victim.jsonl');
  const original = readFileSync(logFlow.logPath(), 'utf8');
  writeFileSync(victim, original);
  rmSync(logFlow.logPath());
  symlinkSync(victim, logFlow.logPath(), 'file');
  const receipt = logFlow.receipt('linked-log-handoff.md');
  result = logFlow.run(
    'submit', '--experiment', logFlow.experiment,
    '--actor', 'designer', '--artifact', receipt,
  );
  assertFailed(result, /workflow.*(regular file|link|symlink|outside)/i);
  assert.equal(readFileSync(victim, 'utf8'), original);
});

test('multi-artifact failure is transactional and can be retried without orphan evidence', (context) => {
  const flow = fixture();
  context.after(() => flow.cleanup());
  assert.equal(initialize(flow).status, 0);
  const first = flow.receipt('transaction-first.md', '# First receipt\n');
  const second = `research/${flow.experiment}/workflow/receipts/transaction-second.md`;

  const oversized = flow.write(
    `research/${flow.experiment}/workflow/receipts/oversized.md`,
    Buffer.alloc((1024 * 1024) + 1, 0x61),
  );
  let result = flow.run(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer', '--artifact', oversized,
  );
  assertFailed(result, /artifact.*exceeds 1048576 bytes/i);
  assert.deepEqual(flow.snapshots(), []);
  assert.deepEqual(flow.events().map(({ type }) => type), ['init']);

  result = flow.run(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer', '--artifact', first, '--artifact', second,
  );
  assertFailed(result, /artifact.*(does not exist|missing)/i);
  assert.deepEqual(flow.snapshots(), []);
  assert.deepEqual(flow.events().map(({ type }) => type), ['init']);

  flow.write(second, '# Second receipt\n');
  result = flow.run(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer', '--artifact', first, '--artifact', second,
  );
  assert.equal(result.status, 0, result.stderr);
  assert.equal(flow.snapshots().length, 2);
  assert.deepEqual(flow.events().map(({ type }) => type), ['init', 'submit']);
  result = flow.run('verify', '--experiment', flow.experiment);
  assert.equal(result.status, 0, result.stderr);

  const staleRecovery = join(
    flow.experimentDirectory,
    `.workflow-recovery.${randomUUID()}.tmp`,
  );
  writeFileSync(staleRecovery, '# Uncommitted recovery replacement\n');
  result = flow.run('repair', '--experiment', flow.experiment);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stderr, /Removed uncommitted atomic-recovery staging file/i);
  assert.equal(existsSync(staleRecovery), false);
});

test('validates submit and review note length before persisting any transition', (context) => {
  const flow = fixture('bounded-notes');
  context.after(() => flow.cleanup());
  assert.equal(initialize(flow).status, 0);
  const handoff = flow.receipt('bounded-note-handoff.md');
  const tooLong = 'x'.repeat(10_001);
  const maximum = 'y'.repeat(10_000);

  let beforeLog = readFileSync(flow.logPath());
  let beforeSnapshots = flow.snapshots();
  let result = flow.run(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer', '--artifact', handoff, '--note', tooLong,
  );
  assertFailed(result, /--note is too long.*10000/i);
  assert.deepEqual(readFileSync(flow.logPath()), beforeLog);
  assert.deepEqual(flow.snapshots(), beforeSnapshots);

  result = flow.run(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer', '--artifact', handoff, '--note', maximum,
  );
  assert.equal(result.status, 0, result.stderr);
  assert.equal(flow.events()[1].note.length, 10_000);

  const review = flow.receipt('bounded-note-review.md');
  beforeLog = readFileSync(flow.logPath());
  beforeSnapshots = flow.snapshots();
  result = flow.run(
    'review', '--experiment', flow.experiment,
    '--actor', 'reviewer', '--decision', 'approve', '--artifact', review, '--note', tooLong,
  );
  assertFailed(result, /--note is too long.*10000/i);
  assert.deepEqual(readFileSync(flow.logPath()), beforeLog);
  assert.deepEqual(flow.snapshots(), beforeSnapshots);

  result = flow.run(
    'review', '--experiment', flow.experiment,
    '--actor', 'reviewer', '--decision', 'approve', '--artifact', review, '--note', maximum,
  );
  assert.equal(result.status, 0, result.stderr);
  assert.equal(flow.events()[2].note.length, 10_000);
  result = flow.run('verify', '--experiment', flow.experiment);
  assert.equal(result.status, 0, result.stderr);
});

test('serializes concurrent transitions without duplicate sequences or orphan snapshots', async (context) => {
  const flow = fixture('concurrent-transition');
  context.after(() => flow.cleanup());
  assert.equal(initialize(flow).status, 0);
  const first = flow.receipt('concurrent-first.md', '# First contender\n');
  const second = flow.receipt('concurrent-second.md', '# Second contender\n');

  const results = await Promise.all([
    flow.runAsync(
      'submit', '--experiment', flow.experiment,
      '--actor', 'designer-one', '--artifact', first,
    ),
    flow.runAsync(
      'submit', '--experiment', flow.experiment,
      '--actor', 'designer-two', '--artifact', second,
    ),
  ]);
  assert.equal(results.filter(({ status }) => status === 0).length, 1);
  assert.match(
    results.find(({ status }) => status !== 0).stderr,
    /(transition is locked|cannot submit from question_review)/i,
  );
  assert.deepEqual(flow.events().map(({ sequence }) => sequence), [1, 2]);
  assert.deepEqual(flow.events().map(({ type }) => type), ['init', 'submit']);
  assert.equal(flow.snapshots().length, 1);
  const result = flow.run('verify', '--experiment', flow.experiment);
  assert.equal(result.status, 0, result.stderr);
});

test('stale-lock repair refuses a live owner and removes only a dead same-host lock', (context) => {
  const flow = fixture('stale-lock');
  context.after(() => flow.cleanup());
  assert.equal(initialize(flow).status, 0);
  const lockPath = join(flow.experimentDirectory, 'workflow', '.transition.lock');
  const lock = (pid, processStartTicks = null) => `${JSON.stringify({
    pid,
    hostname: hostname(),
    timestamp: '2026-08-08T00:00:00.000Z',
    lock_id: randomUUID(),
    boot_id: null,
    process_start_ticks: processStartTicks,
  })}\n`;

  writeFileSync(lockPath, lock(process.pid));
  let result = flow.run(
    'repair', '--experiment', flow.experiment, '--unlock-stale',
  );
  assertFailed(result, /lock owner PID .*still alive/i);
  assert.equal(existsSync(lockPath), true);

  writeFileSync(lockPath, lock(process.pid, '0'));
  result = flow.run(
    'repair', '--experiment', flow.experiment, '--unlock-stale',
  );
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stderr, /Removed a stale transition lock/i);
  assert.equal(existsSync(lockPath), false);

  writeFileSync(lockPath, lock(2147483647));
  result = flow.run(
    'repair', '--experiment', flow.experiment, '--unlock-stale',
  );
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stderr, /Removed a stale transition lock/i);
  assert.equal(existsSync(lockPath), false);
  result = flow.run('verify', '--experiment', flow.experiment);
  assert.equal(result.status, 0, result.stderr);
});

test('newline-terminated junk is corruption, while a partial tail is recoverable', (context) => {
  const corrupt = fixture('newline-corrupt');
  const partial = fixture('partial-tail');
  const missingDelimiter = fixture('missing-delimiter');
  context.after(() => {
    corrupt.cleanup();
    partial.cleanup();
    missingDelimiter.cleanup();
  });

  assert.equal(initialize(corrupt).status, 0);
  appendFileSync(corrupt.logPath(), 'not-json\n');
  const corruptBytes = readFileSync(corrupt.logPath(), 'utf8');
  let result = corrupt.run('status', '--experiment', corrupt.experiment, '--json');
  assertFailed(result, /invalid JSON.*line 2|corrupt.*final/i);
  const blockedReceipt = corrupt.receipt('blocked-by-corruption.md');
  result = corrupt.run(
    'submit', '--experiment', corrupt.experiment,
    '--actor', 'designer', '--artifact', blockedReceipt,
  );
  assertFailed(result, /invalid JSON.*line 2|corrupt.*final/i);
  assert.equal(readFileSync(corrupt.logPath(), 'utf8'), corruptBytes);
  assert.deepEqual(corrupt.snapshots(), []);

  assert.equal(initialize(partial).status, 0);
  submitCurrent(partial, 'brainstorm', 1);
  appendFileSync(partial.logPath(), '{"schema":1,"cut');
  result = partial.run('status', '--experiment', partial.experiment, '--json');
  assert.equal(result.status, 0, result.stderr);
  assert.match(JSON.parse(result.stdout).recovery_warnings[0], /incomplete final record/i);
  const partialBytes = readFileSync(partial.logPath());
  const partialSnapshots = partial.snapshots();
  const recoveredReview = partial.receipt('recovered-review.md');
  result = partial.run(
    'review', '--experiment', partial.experiment,
    '--actor', 'reviewer', '--decision', 'approve', '--artifact', recoveredReview,
  );
  assertFailed(result, /incomplete final record.*repair/i);
  assert.deepEqual(readFileSync(partial.logPath()), partialBytes);
  assert.deepEqual(partial.snapshots(), partialSnapshots);
  result = partial.run('repair', '--experiment', partial.experiment);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(partial.events().map(({ type }) => type), ['init', 'submit', 'recovery']);
  result = partial.run(
    'review', '--experiment', partial.experiment,
    '--actor', 'reviewer', '--decision', 'approve', '--artifact', recoveredReview,
  );
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(partial.events().map(({ type }) => type), ['init', 'submit', 'recovery', 'review']);
  result = partial.run('verify', '--experiment', partial.experiment);
  assert.equal(result.status, 0, result.stderr);

  assert.equal(initialize(missingDelimiter).status, 0);
  submitCurrent(missingDelimiter, 'brainstorm', 1);
  const unterminated = readFileSync(missingDelimiter.logPath());
  assert.equal(unterminated.at(-1), 0x0a);
  writeFileSync(missingDelimiter.logPath(), unterminated.subarray(0, -1));
  result = missingDelimiter.run('status', '--experiment', missingDelimiter.experiment, '--json');
  assert.equal(result.status, 0, result.stderr);
  const delimiterStatus = JSON.parse(result.stdout);
  assert.equal(delimiterStatus.state, 'brainstorm');
  assert.match(delimiterStatus.recovery_warnings[0], /incomplete final record/i);
  assert.equal(delimiterStatus.recovery_orphan_snapshots.length, 1);
  const delimiterBytes = readFileSync(missingDelimiter.logPath());
  const delimiterSnapshots = missingDelimiter.snapshots();
  const replacement = missingDelimiter.receipt('replacement-after-missing-delimiter.md');
  result = missingDelimiter.run(
    'submit', '--experiment', missingDelimiter.experiment,
    '--actor', 'replacement-designer', '--artifact', replacement,
  );
  assertFailed(result, /incomplete final record.*repair/i);
  assert.deepEqual(readFileSync(missingDelimiter.logPath()), delimiterBytes);
  assert.deepEqual(missingDelimiter.snapshots(), delimiterSnapshots);
  result = missingDelimiter.run('repair', '--experiment', missingDelimiter.experiment);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(missingDelimiter.events().map(({ type }) => type), ['init', 'recovery']);
  result = missingDelimiter.run(
    'submit', '--experiment', missingDelimiter.experiment,
    '--actor', 'replacement-designer', '--artifact', replacement,
  );
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(
    missingDelimiter.events().map(({ type }) => type),
    ['init', 'recovery', 'submit'],
  );
  result = missingDelimiter.run('verify', '--experiment', missingDelimiter.experiment);
  assert.equal(result.status, 0, result.stderr);
});

test('requires explicit repair to quarantine an orphan snapshot from an interrupted transition', (context) => {
  const flow = fixture('orphan-recovery');
  context.after(() => flow.cleanup());
  assert.equal(initialize(flow).status, 0);
  const orphan = join(
    flow.evidenceDirectory(),
    `0002-01-${randomUUID()}-interrupted-handoff.md`,
  );
  writeFileSync(orphan, '# Fully written before an interrupted ledger append\n');

  let result = flow.run('verify', '--experiment', flow.experiment);
  assertFailed(result, /unreferenced evidence snapshot.*repair/i);
  const receipt = flow.receipt('after-orphan.md', '# Valid handoff after repair\n');
  result = flow.run(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer', '--artifact', receipt,
  );
  assertFailed(result, /unreferenced evidence snapshot.*explicit repair/i);

  result = flow.run('repair', '--experiment', flow.experiment);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(flow.events().map(({ type }) => type), ['init', 'recovery']);
  assert.equal(flow.events()[1].quarantined_snapshots.length, 1);
  result = flow.run('verify', '--experiment', flow.experiment);
  assert.equal(result.status, 0, result.stderr);

  result = flow.run(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer', '--artifact', receipt,
  );
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(flow.events().map(({ sequence }) => sequence), [1, 2, 3]);
});

test('active accepted source drift fails verification but superseded source drift is exempt', (context) => {
  const flow = fixture();
  context.after(() => flow.cleanup());
  assert.equal(initialize(flow).status, 0);

  const superseded = flow.receipt('brainstorm-v1.md', '# First proposal\n');
  let result = flow.run(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer-one', '--artifact', superseded,
  );
  assert.equal(result.status, 0, result.stderr);
  const revision = flow.receipt('question-review-revise-v1.md', '# Revise\n');
  result = flow.run(
    'review', '--experiment', flow.experiment,
    '--actor', 'reviewer-one', '--decision', 'revise', '--artifact', revision,
  );
  assert.equal(result.status, 0, result.stderr);

  const active = flow.receipt('brainstorm-v2.md', '# Accepted proposal\n');
  result = flow.run(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer-two', '--artifact', active,
  );
  assert.equal(result.status, 0, result.stderr);
  const approval = flow.receipt('question-review-approve-v2.md', '# Approve\n');
  result = flow.run(
    'review', '--experiment', flow.experiment,
    '--actor', 'reviewer-two', '--decision', 'approve', '--artifact', approval,
  );
  assert.equal(result.status, 0, result.stderr);

  flow.write(superseded, '# Changed after being superseded\n');
  result = flow.run('verify', '--experiment', flow.experiment);
  assert.equal(result.status, 0, result.stderr);

  flow.write(active, '# Changed after active approval\n');
  result = flow.run('verify', '--experiment', flow.experiment);
  assertFailed(result, /active.*(stale|changed)|source.*fingerprint mismatch|accepted.*artifact.*changed/i);
});

test('rejects snapshot tampering, path escape, missing evidence, and middle corruption', (context) => {
  const flow = fixture();
  context.after(() => flow.cleanup());
  assert.equal(initialize(flow).status, 0);

  let result = flow.run(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer', '--artifact', '../outside.md',
  );
  assertFailed(result, /artifact.*(inside|workflow|receipt)|path.*escape/i);

  result = flow.run(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer',
    '--artifact', `research/${flow.experiment}/workflow/receipts/missing.md`,
  );
  assertFailed(result, /artifact.*(does not exist|missing)/i);

  const handoff = flow.receipt('tamper-handoff.md', '# Handoff\n');
  result = flow.run(
    'submit', '--experiment', flow.experiment,
    '--actor', 'designer', '--artifact', handoff,
  );
  assert.equal(result.status, 0, result.stderr);
  const snapshot = join(flow.evidenceDirectory(), flow.snapshots()[0]);
  writeFileSync(snapshot, '# Tampered snapshot\n');
  result = flow.run('verify', '--experiment', flow.experiment);
  assertFailed(result, /snapshot fingerprint mismatch/i);

  writeFileSync(snapshot, Buffer.alloc((1024 * 1024) + 1, 0x62));
  result = flow.run('verify', '--experiment', flow.experiment);
  assertFailed(result, /snapshot.*exceeds 1048576 bytes/i);

  writeFileSync(snapshot, readFileSync(join(flow.root, handoff)));
  let lines = readFileSync(flow.logPath(), 'utf8').trim().split('\n');
  const wrongBranchEvent = JSON.parse(lines[1]);
  wrongBranchEvent.context.branch = 'post/not-the-owner';
  writeFileSync(flow.logPath(), `${lines[0]}\n${JSON.stringify(wrongBranchEvent)}\n`);
  result = flow.run('verify', '--experiment', flow.experiment);
  assertFailed(result, /recorded on non-owning branch/i);

  lines = [lines[0], lines[1]];
  writeFileSync(flow.logPath(), `${lines[0]}\nnot-json\n${lines[1]}\n`);
  result = flow.run('verify', '--experiment', flow.experiment);
  assertFailed(result, /invalid JSON at line 2/i);
});

test('pins each ledger to an immutable graph digest and rejects invalid graph structures', (context) => {
  const flow = fixture();
  const invalidInitialFlow = fixture('invalid-initial-state');
  context.after(() => {
    flow.cleanup();
    invalidInitialFlow.cleanup();
  });
  assert.equal(initialize(flow).status, 0);
  const initEvent = flow.events()[0];
  assert.match(initEvent.graph_sha256, /^[a-f0-9]{64}$/);

  const graph = JSON.parse(readFileSync(graphPath, 'utf8'));
  const invalidInitial = structuredClone(graph);
  invalidInitial.initial_state = 'question_review';
  const invalidInitialPath = invalidInitialFlow.write(
    'invalid-initial-state-graph.json',
    `${JSON.stringify(invalidInitial, null, 2)}\n`,
  );
  let result = invalidInitialFlow.runWithEnv(
    { RESEARCH_WORKFLOW_GRAPH: join(invalidInitialFlow.root, invalidInitialPath) },
    'init',
    '--experiment', invalidInitialFlow.experiment,
    '--post-type', 'understanding',
    '--question', 'Can an invalid graph initialize?',
    '--journal', invalidInitialFlow.session,
    '--actor', 'coordinator',
  );
  assertFailed(result, /initial_state.*work state/i);
  assert.equal(existsSync(invalidInitialFlow.logPath()), false);

  const missingApprove = structuredClone(graph);
  missingApprove.states.question_review.decisions.accept =
    missingApprove.states.question_review.decisions.approve;
  delete missingApprove.states.question_review.decisions.approve;
  const missingApprovePath = invalidInitialFlow.write(
    'invalid-missing-approve-graph.json',
    `${JSON.stringify(missingApprove, null, 2)}\n`,
  );
  result = invalidInitialFlow.runWithEnv(
    { RESEARCH_WORKFLOW_GRAPH: join(invalidInitialFlow.root, missingApprovePath) },
    'graph', '--format', 'json',
  );
  assertFailed(result, /review state.*must declare.*approve/i);

  const forwardNonApprove = structuredClone(graph);
  forwardNonApprove.states.question_review.decisions.skip = 'write';
  const forwardNonApprovePath = invalidInitialFlow.write(
    'invalid-forward-nonapprove-graph.json',
    `${JSON.stringify(forwardNonApprove, null, 2)}\n`,
  );
  result = invalidInitialFlow.runWithEnv(
    { RESEARCH_WORKFLOW_GRAPH: join(invalidInitialFlow.root, forwardNonApprovePath) },
    'graph', '--format', 'json',
  );
  assertFailed(result, /non-approve decision.*cannot advance lineage/i);

  const terminalBypass = structuredClone(graph);
  terminalBypass.states.question_review.decisions.ship = 'ready_to_merge';
  const terminalBypassPath = invalidInitialFlow.write(
    'invalid-terminal-bypass-graph.json',
    `${JSON.stringify(terminalBypass, null, 2)}\n`,
  );
  result = invalidInitialFlow.runWithEnv(
    { RESEARCH_WORKFLOW_GRAPH: join(invalidInitialFlow.root, terminalBypassPath) },
    'graph', '--format', 'json',
  );
  assertFailed(result, /non-approve decision.*cannot target.*successful terminal/i);

  const altered = structuredClone(graph);
  altered.states.brainstorm.description += ' Altered without a version bump.';
  const alteredPath = flow.write('altered-same-version-graph.json', `${JSON.stringify(altered, null, 2)}\n`);
  result = flow.runWithEnv(
    { RESEARCH_WORKFLOW_GRAPH: join(flow.root, alteredPath) },
    'status', '--experiment', flow.experiment, '--json',
  );
  assertFailed(result, /graph.*(digest|fingerprint|hash).*mismatch|graph bytes.*changed/i);

  const reviewToReview = structuredClone(graph);
  reviewToReview.states.question_review.decisions.second_review = 'setup_review';
  const reviewToReviewPath = flow.write(
    'invalid-review-to-review-graph.json',
    `${JSON.stringify(reviewToReview, null, 2)}\n`,
  );
  result = flow.runWithEnv(
    { RESEARCH_WORKFLOW_GRAPH: join(flow.root, reviewToReviewPath) },
    'graph', '--format', 'json',
  );
  assertFailed(result, /review.*(cannot target|targets).*review|pending submission/i);

  const trapped = structuredClone(graph);
  trapped.states.question_review.decisions.trap = 'trap_work';
  trapped.states.trap_work = {
    kind: 'work',
    role: 'experiment_engineer',
    lineage_order: 99,
    label: 'Trap work',
    description: 'A deliberately invalid branch.',
    submit_to: 'trap_review',
    artifact_contract: 'Never valid.',
  };
  trapped.states.trap_review = {
    kind: 'review',
    role: 'independent_reviewer',
    label: 'Trap review',
    description: 'A deliberately invalid cycle.',
    decisions: { revise: 'trap_work' },
    artifact_contract: 'Never valid.',
  };
  const trappedPath = flow.write('invalid-trapped-graph.json', `${JSON.stringify(trapped, null, 2)}\n`);
  result = flow.runWithEnv(
    { RESEARCH_WORKFLOW_GRAPH: join(flow.root, trappedPath) },
    'graph', '--format', 'json',
  );
  assertFailed(result, /must declare.*approve|cannot reach.*terminal|trapped.*terminal|no terminal path/i);
});
