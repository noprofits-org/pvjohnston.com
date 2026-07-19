import path from "node:path";

import {hashFile} from "./lib/collection-integrity.mjs";
import {
  buildReportingAddenda,
  writeReportingAddenda
} from "./lib/reporting-addenda.mjs";

const args = process.argv.slice(2);
const write = args.includes("--write");
const positional = args.filter((arg) => arg !== "--write");
if (positional.some((arg) => arg.startsWith("--")) || positional.length > 1) {
  throw new Error("usage: node scripts/build-reporting-addenda.mjs [--write] [experiment-dir]");
}
const experimentDir = path.resolve(positional[0] ?? path.join(import.meta.dirname, ".."));
const artifacts = buildReportingAddenda(experimentDir);

if (!write) {
  process.stdout.write(
    `validated ${artifacts.pairwiseBootstrap.pairs.length} named-pair bootstraps and ${artifacts.caseStatus.provenance.strictly_valid_analysis_count} case-status responses; no files written (pass --write to create addenda)\n`
  );
} else {
  const written = writeReportingAddenda(experimentDir, artifacts);
  for (const target of Object.values(written)) {
    process.stdout.write(`${target}  ${hashFile(target)}\n`);
  }
}
