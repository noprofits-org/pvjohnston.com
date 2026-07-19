import fs from "node:fs";
import path from "node:path";
import {buildCollectionLock} from "./lib/collection-integrity.mjs";

const args = process.argv.slice(2);
const write = args.includes("--write");
const experimentDir = path.resolve(args.find((arg) => arg !== "--write") ?? path.join(import.meta.dirname, ".."));
const lock = buildCollectionLock(experimentDir);
const body = `${JSON.stringify(lock, null, 2)}\n`;
if (write) {
  const target = path.join(experimentDir, "collection-lock.json");
  fs.writeFileSync(target, body, {flag: "wx"});
  process.stdout.write(`${target}\n`);
} else {
  process.stdout.write(body);
}
