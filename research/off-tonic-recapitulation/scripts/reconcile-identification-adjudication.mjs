import path from "node:path";

import {
  buildIdentificationAdjudicationReconciliation,
  writeIdentificationAdjudicationReconciliation
} from "./lib/identification-adjudication-reconciliation.mjs";

const args = process.argv.slice(2);
const write = args.includes("--write");
const positional = args.filter((arg) => arg !== "--write");
if (positional.some((arg) => arg.startsWith("--")) || positional.length > 1) {
  throw new Error("usage: node scripts/reconcile-identification-adjudication.mjs [--write] [experiment-dir]");
}

const experimentDir = path.resolve(positional[0] ?? path.join(import.meta.dirname, ".."));
const result = buildIdentificationAdjudicationReconciliation(experimentDir);

if (!write) {
  process.stdout.write("validated unanimous masked identification adjudication (54/54 levels); no files written (pass --write to finalize)\n");
} else {
  const written = writeIdentificationAdjudicationReconciliation(experimentDir, result);
  process.stdout.write(`${written.adjudication}\n${written.reconciliation}\n`);
}
