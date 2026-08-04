#!/usr/bin/env node

// Project the committed aggregate tables of the agent-inbox corpus into typed,
// deterministically formatted values used by the accompanying post. The raw
// message corpus is private and is not committed; these CSV aggregates are the
// analysis inputs of record. Check mode recomputes every metric from the CSVs
// and compares the result to the committed projection byte for byte.

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const experimentDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(experimentDir, '../..');
const metricsPath = resolve(experimentDir, 'metrics.json');
const inputNames = ['corpus-totals.csv', 'senders.csv', 'daily.csv', 'filename-tokens.csv', 'joiner-window.csv'];
const arguments_ = process.argv.slice(2);
const checkOnly = arguments_.length === 1 && arguments_[0] === '--check';

if (!(arguments_.length === 0 || checkOnly)) {
  console.error('usage: node research/agent-inbox-corpus/generate-metrics.mjs [--check]');
  process.exit(2);
}

function readCsv(name) {
  const path = resolve(experimentDir, name);
  if (!existsSync(path)) {
    console.error(`${name} is missing`);
    process.exit(1);
  }
  const lines = readFileSync(path, 'utf8').trim().split('\n');
  const header = lines[0].split(',');
  return lines.slice(1).map((line) => {
    const cells = line.split(',');
    return Object.fromEntries(header.map((key, index) => [key, cells[index]]));
  });
}

function sha256(repositoryPath) {
  return createHash('sha256').update(readFileSync(resolve(root, repositoryPath))).digest('hex');
}

const totals = Object.fromEntries(readCsv('corpus-totals.csv').map((r) => [r.key, Number(r.value)]));
const senders = readCsv('senders.csv').map((r) => ({
  sender: r.sender,
  first: r.first_date,
  last: r.last_date,
  messages: Number(r.messages),
  bytes: Number(r.bytes),
}));
const daily = readCsv('daily.csv').map((r) => ({
  date: r.date,
  messages: Number(r.messages),
  bytes: Number(r.bytes),
}));
const tokens = readCsv('filename-tokens.csv').map((r) => ({
  token: r.token,
  filenames: Number(r.filenames),
}));

const DAY_MS = 86_400_000;
const dayNumber = (iso) => Date.UTC(...iso.split('-').map(Number).map((v, i) => (i === 1 ? v - 1 : v))) / DAY_MS;
const spanDays = (a, b) => dayNumber(b) - dayNumber(a);

// The four roles the accompanying post names as the surviving cast.
const SURVIVORS = ['sightline', 'bosun', 'shipwright', 'drawbridge'];
// joiner's first and last message timestamps, transcribed from the withheld
// corpus into the committed, fingerprinted joiner-window.csv.
const joinerWindow = Object.fromEntries(readCsv('joiner-window.csv').map((r) => [r.key, r.value]));
const hhmmToMinutes = (hhmm) => {
  const [h, m] = hhmm.split(':').map(Number);
  return h * 60 + m;
};
const JOINER_FIRST_MINUTES = hhmmToMinutes(joinerWindow.joiner_first_message_hhmm);
const JOINER_LAST_MINUTES = hhmmToMinutes(joinerWindow.joiner_last_message_hhmm);

// Table 1 merges case variants of one token: SCREAMING_SNAKE folds into the
// kebab-lowercase spelling (PR_READY into pr-ready, DEPLOY_LIVE into
// deploy-live).
const mergedTokenCounts = new Map();
for (const { token, filenames } of tokens) {
  const canonical = token.toLowerCase().replace(/_/g, '-');
  mergedTokenCounts.set(canonical, (mergedTokenCounts.get(canonical) ?? 0) + filenames);
}
const mergedToken = (canonical) => {
  if (!mergedTokenCounts.has(canonical)) throw new Error(`no token ${canonical}`);
  return mergedTokenCounts.get(canonical);
};

const firstDate = daily[0].date;
const lastDate = daily.at(-1).date;
const oneDayLabels = senders.filter((s) => s.first === s.last).length;
const fortnightLabels = senders.filter((s) => spanDays(s.first, s.last) >= 14).length;
const busiestDay = daily.reduce((best, d) => (d.messages > best.messages ? d : best));

// Calendar weeks starting Monday, keyed by the Monday's day number.
const weeks = new Map();
for (const d of daily) {
  const n = dayNumber(d.date);
  const monday = n - ((n + 3) % 7); // 1970-01-01 was a Thursday.
  const week = weeks.get(monday) ?? { messages: 0, bytes: 0 };
  week.messages += d.messages;
  week.bytes += d.bytes;
  weeks.set(monday, week);
}
const weekKeys = [...weeks.keys()].sort((a, b) => a - b);
const weekly = weekKeys.map((k) => weeks.get(k));
const peakWeek = weekly.reduce((best, w) => (w.messages > best.messages ? w : best));
const finalWeek = weekly.at(-1);
const firstFourWeeks = weekly.slice(0, 4).reduce((sum, w) => sum + w.messages, 0);
const totalDated = weekly.reduce((sum, w) => sum + w.messages, 0);

const joiner = senders.find((s) => s.sender === 'joiner');
const survivorMessages = senders
  .filter((s) => SURVIVORS.includes(s.sender))
  .reduce((sum, s) => sum + s.messages, 0);

const fixed = (digits) => ({ style: 'fixed', digits });
const integerMetric = (value, description, unit) => ({
  type: 'integer',
  value,
  description,
  ...(unit ? { unit } : {}),
});
const numberMetric = (value, format, description, unit) => ({
  type: 'number',
  value,
  format,
  description,
  ...(unit ? { unit } : {}),
});

const metrics = {
  total_messages: integerMetric(totals.total_messages, 'Message files in the corpus', 'messages'),
  corpus_megabytes: numberMetric(
    Math.round((totals.total_bytes / 1e6) * 10) / 10,
    fixed(1),
    'Total size of the message files',
    'MB',
  ),
  distinct_sender_labels: integerMetric(
    totals.distinct_sender_labels,
    'Distinct sender labels parsed from message filenames',
    'labels',
  ),
  distinct_inbox_directories: integerMetric(
    totals.distinct_inbox_directories,
    'Distinct inbox directories the messages are filed under',
    'directories',
  ),
  surviving_role_count: integerMetric(
    SURVIVORS.length,
    'Roles the accompanying post names as the surviving cast',
    'roles',
  ),
  corpus_span_days: integerMetric(
    spanDays(firstDate, lastDate),
    'Days from the first dated message to the last',
    'days',
  ),
  active_days: integerMetric(daily.length, 'Calendar days carrying at least one message', 'days'),
  one_day_labels: integerMetric(
    oneDayLabels,
    'Sender labels whose first and last dated message fall on the same day',
    'labels',
  ),
  fortnight_labels: integerMetric(
    fortnightLabels,
    'Sender labels whose first and last dated message are at least fourteen days apart',
    'labels',
  ),
  survivor_message_share_percent: numberMetric(
    Math.round((survivorMessages / totalDated) * 1000) / 10,
    fixed(1),
    'Share of dated messages written by the four surviving labels',
    '%',
  ),
  busiest_day_messages: integerMetric(
    busiestDay.messages,
    'Messages written on the busiest single day',
    'messages',
  ),
  peak_week_messages: integerMetric(
    peakWeek.messages,
    'Messages written in the busiest calendar week',
    'messages',
  ),
  final_week_messages: integerMetric(
    finalWeek.messages,
    'Messages written in the last calendar week of the corpus',
    'messages',
  ),
  peak_to_final_week_ratio: numberMetric(
    Math.round((peakWeek.messages / finalWeek.messages) * 10) / 10,
    fixed(1),
    'Busiest calendar week divided by the last calendar week, by message count',
    'ratio',
  ),
  first_four_weeks_share_percent: numberMetric(
    Math.round((firstFourWeeks / totalDated) * 1000) / 10,
    fixed(1),
    'Share of dated messages written in the first four calendar weeks',
    '%',
  ),
  joiner_messages: integerMetric(joiner.messages, 'Messages signed by the joiner label', 'messages'),
  joiner_career_hours: numberMetric(
    Math.round(((JOINER_LAST_MINUTES - JOINER_FIRST_MINUTES) / 60) * 10) / 10,
    fixed(1),
    'Elapsed time from the joiner label’s first message to its last',
    'h',
  ),
  filenames_with_explicit_recipient: integerMetric(
    totals.filenames_with_explicit_recipient,
    'Filenames encoding an explicit recipient the filename convention never specified',
    'filenames',
  ),
  filenames_with_allcaps_token: integerMetric(
    totals.filenames_with_allcaps_token,
    'Filenames carrying at least one all-capitals status token',
    'filenames',
  ),
  distinct_filename_tokens: integerMetric(
    tokens.length,
    'Distinct status tokens counted in the filename vocabulary',
    'tokens',
  ),
  token_deploy_live: integerMetric(
    mergedToken('deploy-live'),
    'Filenames carrying the deploy-live token, case variants merged',
    'filenames',
  ),
  token_pr_ready: integerMetric(
    mergedToken('pr-ready'),
    'Filenames carrying the pr-ready token, case variants merged',
    'filenames',
  ),
  token_ack: integerMetric(
    mergedToken('ack'),
    'Filenames carrying the ack token, case variants merged',
    'filenames',
  ),
  token_merge_ok: integerMetric(
    mergedToken('merge-ok'),
    'Filenames carrying the merge-ok token, case variants merged',
    'filenames',
  ),
  token_go: integerMetric(
    mergedToken('go'),
    'Filenames carrying the GO token, case variants merged',
    'filenames',
  ),
  token_hold: integerMetric(
    mergedToken('hold'),
    'Filenames carrying the HOLD token, case variants merged',
    'filenames',
  ),
  token_merged: integerMetric(
    mergedToken('merged'),
    'Filenames carrying the MERGED token, case variants merged',
    'filenames',
  ),
  token_merge_block: integerMetric(
    mergedToken('merge-block'),
    'Filenames carrying the merge-block token, case variants merged',
    'filenames',
  ),
};

const payload = {
  schema_version: 1,
  experiment: 'agent-inbox-corpus',
  provenance: {
    generated_at: '2026-08-03T00:00:00Z',
    generator: relative(root, fileURLToPath(import.meta.url)),
    inputs: inputNames.map((name) => {
      const path = relative(root, resolve(experimentDir, name));
      return { path, sha256: sha256(path) };
    }),
  },
  metrics,
};

const serialized = `${JSON.stringify(payload, undefined, 2)}\n`;

if (checkOnly) {
  if (!existsSync(metricsPath)) {
    console.error('metrics.json is missing');
    process.exit(1);
  }
  const committed = readFileSync(metricsPath, 'utf8');
  const committedPayload = JSON.parse(committed);
  const rebuilt = { ...payload, provenance: { ...payload.provenance, generated_at: committedPayload.provenance.generated_at } };
  const expected = `${JSON.stringify(rebuilt, undefined, 2)}\n`;
  if (committed !== expected) {
    console.error('metrics.json does not match a fresh projection of the committed inputs');
    process.exit(1);
  }
  console.log('agent-inbox-corpus: projection matches committed inputs');
  process.exit(0);
}

writeFileSync(metricsPath, serialized);
console.log(`wrote ${relative(root, metricsPath)}`);
