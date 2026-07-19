import path from "node:path";
import {verifyCollectionLock} from "./lib/collection-integrity.mjs";

const experimentDir = path.resolve(process.argv[2] ?? path.join(import.meta.dirname, ".."));
const {lock} = verifyCollectionLock(experimentDir);
process.stdout.write(`verified collection lock for ${lock.dataset_version}\n`);
