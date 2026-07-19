import fs from "node:fs";
import {parseAndValidateResponse} from "./lib/response-validator.mjs";

const [task, expectedCase, dossierPath, responsePath] = process.argv.slice(2);
if (!task || !expectedCase || !dossierPath || !responsePath) {
  throw new Error("usage: validate-output.mjs TASK CASE_ID DOSSIER RESPONSE");
}

const dossier = JSON.parse(fs.readFileSync(dossierPath, "utf8"));
const response = fs.readFileSync(responsePath, "utf8");
parseAndValidateResponse({task, expectedCase, dossier, response});

process.stdout.write(`valid: ${task} ${expectedCase}\n`);
