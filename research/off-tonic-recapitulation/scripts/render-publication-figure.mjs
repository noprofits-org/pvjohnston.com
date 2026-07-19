import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const experimentDir = path.resolve(here, "..");
const repositoryDir = path.resolve(experimentDir, "../..");
const resultsDir = path.join(experimentDir, "results", "1.0.0");
const summaryPath = path.join(resultsDir, "summary.json");
const sensitivityPath = path.join(resultsDir, "validator-contract-sensitivity.json");
const outputPath = path.join(resultsDir, "figure-1.svg");

const summary = JSON.parse(fs.readFileSync(summaryPath, "utf8"));
const sensitivity = JSON.parse(fs.readFileSync(sensitivityPath, "utf8"));

const assert = (condition, message) => {
  if (!condition) throw new Error(message);
};
const close = (actual, expected, tolerance = 1e-12) => Math.abs(actual - expected) <= tolerance;
const fmt = (value) => value.toFixed(3).replace(/^0/, "");
const esc = (value) => String(value)
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;");

assert(summary.dataset_version === "1.0.0", "unexpected primary dataset version");
assert(summary.collection_integrity?.scheduled_slot_status_counts?.analysis?.valid === 49,
  "primary analysis-valid count changed");
assert(summary.identification?.scheduled === 54, "identification schedule changed");
assert(sensitivity.response_accounting?.all_tasks_sensitivity_valid === 108,
  "prompt-aligned sensitivity no longer has 108 valid outputs");

const modelRows = [
  {id: "openai-frontier", name: "OpenAI 5.6", role: "frontier", expected: 0.8708392681972864},
  {id: "anthropic-frontier", name: "Anthropic Fable 5", role: "frontier", expected: 0.8372057683036743},
  {id: "openai-prior-generation", name: "OpenAI 5.5", role: "prior generation", expected: 0.891678992139985}
].map((row) => {
  const primary = summary.within_model[row.id];
  const aligned = sensitivity.sensitivity.within_model[row.id];
  assert(primary && aligned, `missing reliability row for ${row.id}`);
  assert(close(primary.aggregate.ordinal_krippendorff_alpha, row.expected),
    `primary alpha changed for ${row.id}`);
  return {
    ...row,
    primary: {
      alpha: primary.aggregate.ordinal_krippendorff_alpha,
      low: primary.bootstrap_95.ordinal_krippendorff_alpha.lower_95,
      high: primary.bootstrap_95.ordinal_krippendorff_alpha.upper_95
    },
    aligned: {
      alpha: aligned.aggregate.ordinal_krippendorff_alpha,
      low: aligned.bootstrap_95.ordinal_krippendorff_alpha.lower_95,
      high: aligned.bootstrap_95.ordinal_krippendorff_alpha.upper_95
    }
  };
});

const gateRows = [
  ["Output validity", "output_gate"],
  ["Repeatability", "repeatability_gate"],
  ["Cue dispersion", "dispersion_gate"],
  ["Target identity", "identification_gate"],
  ["Analysis recognition", "analysis_recognition_gate"]
].map(([label, key]) => ({
  label,
  primary: summary.preliminary_gates[key],
  aligned: sensitivity.sensitivity.preliminary_gates[key]
}));
assert(gateRows.every((row) => row.primary === false), "a primary preliminary gate changed");
assert(gateRows.filter((row) => row.aligned).map((row) => row.label).join("|") ===
  "Output validity|Repeatability", "prompt-aligned gate pattern changed");
assert(summary.automatic_expansion_gate === false &&
  sensitivity.sensitivity.automatic_expansion_gate === false,
"automatic-expansion decision changed");

const caseRows = [
  ["CASE-6U43", "Wq 48/3/iii", "target"],
  ["CASE-8JQJ", "Benda 2/iii", "target"],
  ["CASE-DZWT", "K. 570/i", "target"],
  ["CASE-Q2R9", "K. 333/i", "target"],
  ["CASE-D09B", "K. 576/i", "target"],
  ["CASE-VT57", "K. 545/i", "anchor"]
].map(([id, label, role]) => ({
  id,
  label,
  role,
  count: summary.identification.l2_events.filter((event) => event.case_id === id).length
}));
assert(caseRows.map((row) => row.count).join(",") === "0,0,0,0,6,3",
  "exact-identification distribution changed");

const C = {
  cream: "#F5F2EA",
  paper: "#FFFDF8",
  ink: "#1A1D2B",
  muted: "#696D78",
  rule: "#D9D2C2",
  grid: "#E8E2D6",
  indigo: "#465C9B",
  indigoDark: "#2F417A",
  indigoLight: "#8FA5E3",
  pass: "#35695A",
  passPale: "#DDEBE5",
  fail: "#9A4F4C",
  failPale: "#F2DFDC",
  anchor: "#B57A24",
  anchorPale: "#F0E2C5"
};
const sans = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif";
const serif = "Georgia,'Times New Roman',serif";
const svg = [];
const add = (value) => svg.push(value);
const text = (x, y, value, attrs = "") => add(`<text x="${x}" y="${y}" ${attrs}>${esc(value)}</text>`);
const line = (x1, y1, x2, y2, attrs = "") => add(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" ${attrs}/>`);
const rect = (x, y, width, height, attrs = "") => add(`<rect x="${x}" y="${y}" width="${width}" height="${height}" ${attrs}/>`);
const circle = (cx, cy, r, attrs = "") => add(`<circle cx="${cx}" cy="${cy}" r="${r}" ${attrs}/>`);
const panel = (x, y, width, height) => rect(x, y, width, height,
  `rx="18" fill="${C.paper}" stroke="${C.rule}" stroke-width="1.5"`);
const callout = (letter, x, y) => {
  circle(x, y, 15, `fill="${C.indigoDark}"`);
  text(x, y + 5.5, letter,
    `fill="white" font-family="${sans}" font-size="15" font-weight="750" text-anchor="middle"`);
};
const diamond = (cx, cy, radius, attrs = "") => {
  add(`<path d="M ${cx} ${cy - radius} L ${cx + radius} ${cy} L ${cx} ${cy + radius} L ${cx - radius} ${cy} Z" ${attrs}/>`);
};
const gateMark = (cx, cy, passed) => {
  circle(cx, cy, 11,
    `fill="${passed ? C.passPale : C.failPale}" stroke="${passed ? C.pass : C.fail}" stroke-width="1.4"`);
  if (passed) {
    add(`<path d="M ${cx - 4.5} ${cy} L ${cx - 1} ${cy + 3.7} L ${cx + 5.5} ${cy - 4.2}" fill="none" stroke="${C.pass}" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"/>`);
  } else {
    line(cx - 4, cy - 4, cx + 4, cy + 4, `stroke="${C.fail}" stroke-width="1.9" stroke-linecap="round"`);
    line(cx + 4, cy - 4, cx - 4, cy + 4, `stroke="${C.fail}" stroke-width="1.9" stroke-linecap="round"`);
  }
};

add(`<?xml version="1.0" encoding="UTF-8"?>`);
add(`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-labelledby="title desc">`);
add(`<title id="title">Repeatable, but not blind</title>`);
add(`<desc id="desc">Three panels compare ordinal test-retest reliability, frozen and prompt-aligned feasibility gates, and exact work-and-movement identification across six music dossiers.</desc>`);
rect(0, 0, 1200, 630, `fill="${C.cream}"`);

text(42, 39, "OFF-TONIC RECAPITULATION  ·  DATASET 1.0.0  ·  108 CALLS",
  `fill="${C.indigo}" font-family="${sans}" font-size="13" font-weight="750" letter-spacing="1.45"`);
text(40, 92, "Repeatable, but not blind",
  `fill="${C.ink}" font-family="${serif}" font-size="45" font-weight="700" letter-spacing="-0.8"`);
text(42, 124, "Ordinal reliability  ·  feasibility gates  ·  exact dossier identification",
  `fill="${C.muted}" font-family="${sans}" font-size="17" font-weight="500"`);
line(40, 145, 1160, 145, `stroke="${C.rule}" stroke-width="1.5"`);

// Panel A: ordinal reliability.
panel(40, 164, 495, 426);
callout("A", 66, 194);
text(92, 201, "Test–retest reliability",
  `fill="${C.ink}" font-family="${sans}" font-size="20" font-weight="750"`);
text(64, 230, "ordinal Krippendorff α · 95% dossier bootstrap",
  `fill="${C.muted}" font-family="${sans}" font-size="12.5" font-weight="500"`);
circle(70, 256, 5.5, `fill="${C.indigo}"`);
text(82, 260, "frozen primary", `fill="${C.muted}" font-family="${sans}" font-size="11.5"`);
diamond(176, 256, 6, `fill="${C.paper}" stroke="${C.anchor}" stroke-width="2"`);
text(188, 260, "prompt-aligned post hoc", `fill="${C.muted}" font-family="${sans}" font-size="11.5"`);

const plotA = {left: 206, right: 500, top: 281, bottom: 520};
const xAlpha = (value) => plotA.left + value * (plotA.right - plotA.left);
for (const tick of [0, 0.5, 1]) {
  const x = xAlpha(tick);
  line(x, plotA.top, x, plotA.bottom,
    `stroke="${C.grid}" stroke-width="1"${tick === 0.5 ? " stroke-dasharray=\"3 5\"" : ""}`);
  text(x, 542, tick.toFixed(1),
    `fill="${C.muted}" font-family="${sans}" font-size="11.5" text-anchor="middle"`);
}
const thresholdX = xAlpha(0.67);
line(thresholdX, plotA.top, thresholdX, plotA.bottom,
  `stroke="${C.indigoLight}" stroke-width="1.4" stroke-dasharray="5 5"`);
text(thresholdX, 277, "0.67 threshold",
  `fill="${C.indigo}" font-family="${sans}" font-size="10.5" font-weight="650" text-anchor="middle"`);

const reliabilityY = [322, 405, 488];
modelRows.forEach((row, index) => {
  const y = reliabilityY[index];
  text(64, y - 3, row.name,
    `fill="${C.ink}" font-family="${sans}" font-size="14" font-weight="700"`);
  text(64, y + 15, row.role,
    `fill="${C.muted}" font-family="${sans}" font-size="10.5" font-weight="600" letter-spacing="0.55"`);
  const primaryY = y - (row.id === "anthropic-frontier" ? 8 : 0);
  line(xAlpha(row.primary.low), primaryY, xAlpha(row.primary.high), primaryY,
    `stroke="${C.indigo}" stroke-width="3" stroke-linecap="round"`);
  line(xAlpha(row.primary.low), primaryY - 5, xAlpha(row.primary.low), primaryY + 5,
    `stroke="${C.indigo}" stroke-width="1.5"`);
  line(xAlpha(row.primary.high), primaryY - 5, xAlpha(row.primary.high), primaryY + 5,
    `stroke="${C.indigo}" stroke-width="1.5"`);
  circle(xAlpha(row.primary.alpha), primaryY, 6.2, `fill="${C.indigo}" stroke="${C.paper}" stroke-width="1.5"`);
  if (row.id === "anthropic-frontier") {
    const alignedY = y + 9;
    line(xAlpha(row.aligned.low), alignedY, xAlpha(row.aligned.high), alignedY,
      `stroke="${C.anchor}" stroke-width="2.2" stroke-linecap="round"`);
    line(xAlpha(row.aligned.low), alignedY - 4, xAlpha(row.aligned.low), alignedY + 4,
      `stroke="${C.anchor}" stroke-width="1.3"`);
    line(xAlpha(row.aligned.high), alignedY - 4, xAlpha(row.aligned.high), alignedY + 4,
      `stroke="${C.anchor}" stroke-width="1.3"`);
    diamond(xAlpha(row.aligned.alpha), alignedY, 6.5,
      `fill="${C.paper}" stroke="${C.anchor}" stroke-width="2"`);
    text(xAlpha(row.primary.alpha), primaryY - 10, `${fmt(row.primary.alpha)}*`,
      `fill="${C.indigoDark}" font-family="${sans}" font-size="11" font-weight="700" text-anchor="middle"`);
    text(xAlpha(row.aligned.alpha), alignedY + 19, fmt(row.aligned.alpha),
      `fill="${C.anchor}" font-family="${sans}" font-size="11" font-weight="700" text-anchor="middle"`);
  } else {
    text(510, y + 4, fmt(row.primary.alpha),
      `fill="${C.indigoDark}" font-family="${sans}" font-size="11" font-weight="700" text-anchor="end"`);
  }
});
text(64, 568, "* available case · 10/15 target calls",
  `fill="${C.muted}" font-family="${sans}" font-size="10.5" font-style="italic"`);

// Panel B: feasibility gates.
panel(553, 164, 298, 426);
callout("B", 579, 194);
text(605, 201, "Feasibility gates",
  `fill="${C.ink}" font-family="${sans}" font-size="20" font-weight="750"`);
text(755, 245, "PRIMARY",
  `fill="${C.muted}" font-family="${sans}" font-size="9.5" font-weight="750" letter-spacing="0.8" text-anchor="middle"`);
text(821, 245, "POST HOC",
  `fill="${C.muted}" font-family="${sans}" font-size="9.5" font-weight="750" letter-spacing="0.7" text-anchor="middle"`);
const gateY = [283, 330, 377, 424, 471];
gateRows.forEach((row, index) => {
  const y = gateY[index];
  if (index > 0) line(576, y - 24, 828, y - 24, `stroke="${C.grid}" stroke-width="1"`);
  text(576, y + 4, row.label,
    `fill="${C.ink}" font-family="${sans}" font-size="12.5" font-weight="600"`);
  gateMark(755, y, row.primary);
  gateMark(821, y, row.aligned);
});
line(576, 505, 828, 505, `stroke="${C.rule}" stroke-width="1.5"`);
text(576, 535, "AUTO-EXPAND",
  `fill="${C.ink}" font-family="${sans}" font-size="11" font-weight="800" letter-spacing="0.75"`);
gateMark(755, 531, summary.automatic_expansion_gate);
gateMark(821, 531, sensitivity.sensitivity.automatic_expansion_gate);
text(576, 566, "2/6 cues qualified post hoc · 4/6 required",
  `fill="${C.muted}" font-family="${sans}" font-size="10.5"`);

// Panel C: exact identification.
panel(869, 164, 291, 426);
callout("C", 895, 194);
text(921, 201, "Exact identification",
  `fill="${C.ink}" font-family="${sans}" font-size="20" font-weight="750"`);
text(893, 230, "L2 work + movement · probes / 9",
  `fill="${C.muted}" font-family="${sans}" font-size="12.5" font-weight="500"`);
const barLeft = 1007;
const barRight = 1131;
const barWidth = barRight - barLeft;
const xCount = (value) => barLeft + (value / 9) * barWidth;
for (const tick of [0, 3, 6, 9]) {
  const x = xCount(tick);
  line(x, 259, x, 544, `stroke="${C.grid}" stroke-width="1"`);
  text(x, 253, String(tick),
    `fill="${C.muted}" font-family="${sans}" font-size="10.5" text-anchor="middle"`);
}
const identificationY = [286, 330, 374, 418, 462, 532];
caseRows.forEach((row, index) => {
  const y = identificationY[index];
  if (row.role === "anchor") {
    line(893, 493, 1134, 493, `stroke="${C.rule}" stroke-width="1.5" stroke-dasharray="4 4"`);
    text(893, 511, "SENSITIVITY ANCHOR",
      `fill="${C.anchor}" font-family="${sans}" font-size="9" font-weight="800" letter-spacing="0.8"`);
  }
  text(893, y + 4, row.label,
    `fill="${row.count > 0 ? C.ink : C.muted}" font-family="${sans}" font-size="12.5" font-weight="${row.count > 0 ? 750 : 550}"`);
  rect(barLeft, y - 8, barWidth, 16, `rx="8" fill="${C.grid}"`);
  if (row.count > 0) {
    rect(barLeft, y - 8, xCount(row.count) - barLeft, 16,
      `rx="8" fill="${row.role === "anchor" ? C.anchor : C.indigo}"`);
  }
  text(1143, y + 4, String(row.count),
    `fill="${row.role === "anchor" ? C.anchor : row.count > 0 ? C.indigoDark : C.muted}" font-family="${sans}" font-size="12" font-weight="800" text-anchor="middle"`);
});

add(`</svg>`);
fs.writeFileSync(outputPath, `${svg.join("\n")}\n`, "utf8");
console.log(path.relative(repositoryDir, outputPath));
