import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const [markerPath, metadataPath, responsePath, stderrPath] = process.argv.slice(2);
if (!markerPath || !metadataPath || !responsePath || !stderrPath) {
  throw new Error("usage: write-completion-marker.mjs MARKER METADATA RESPONSE STDERR");
}
const hashFile = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const marker = {
  schema_version: "1.0.0",
  completed_at: new Date().toISOString(),
  metadata_file: path.basename(metadataPath),
  metadata_sha256: hashFile(metadataPath),
  response_file: path.basename(responsePath),
  response_sha256: hashFile(responsePath),
  stderr_file: path.basename(stderrPath),
  stderr_sha256: hashFile(stderrPath)
};
fs.writeFileSync(markerPath, `${JSON.stringify(marker, null, 2)}\n`, {flag: "wx"});
