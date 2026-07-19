import path from "node:path";

import {
  buildIdentificationAdjudicationArtifacts,
  writeIdentificationAdjudicationArtifacts
} from "./lib/identification-adjudication-packet.mjs";

const args = process.argv.slice(2);
const write = args.includes("--write");
const positional = args.filter((arg) => arg !== "--write");
if (positional.some((arg) => arg.startsWith("--")) || positional.length > 1) {
  throw new Error("usage: node scripts/build-identification-adjudication-packet.mjs [--write] [experiment-dir]");
}
const experimentDir = path.resolve(positional[0] ?? path.join(import.meta.dirname, ".."));
const artifacts = buildIdentificationAdjudicationArtifacts(experimentDir);

if (!write) {
  process.stdout.write(
    `validated ${artifacts.packet.length} masked identification judgments; no files written (pass --write to create the packet)\n`
  );
} else {
  const written = writeIdentificationAdjudicationArtifacts(experimentDir, artifacts);
  for (const target of Object.values(written)) process.stdout.write(`${target}\n`);
}
