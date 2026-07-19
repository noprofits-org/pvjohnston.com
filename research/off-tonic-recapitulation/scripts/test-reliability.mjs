import assert from "node:assert/strict";
import {
  availabilityAgreement,
  completeOrdinalMedian,
  directAgreement,
  median,
  ordinalKrippendorffAlpha,
  summarizeReliability,
  dossierBootstrap
} from "./lib/reliability.mjs";

assert.equal(median([0, 2, 4]), 2);
assert.equal(median([0, 2]), 1);
assert.equal(median([null]), null);
assert.equal(completeOrdinalMedian([0, 1, 2]), 1);
assert.equal(completeOrdinalMedian([0, 1, null]), null);
assert.equal(completeOrdinalMedian([0, 1]), null);

const perfect = [[0, 0, 0], [1, 1, 1], [4, 4, 4]];
assert.equal(ordinalKrippendorffAlpha(perfect), 1);
assert.equal(directAgreement(perfect).exact_agreement, 1);

const constant = [[2, 2, 2], [2, 2, 2]];
assert.equal(ordinalKrippendorffAlpha(constant), null);

// Canonical 3-coder, 15-unit example from Krippendorff's published
// computational example. Direct substitution in the ordinal-distance formula
// gives alpha = 0.8067214199413153.
const canonicalA = [null, null, null, null, null, 3, 4, 1, 2, 1, 1, 3, 3, null, 3];
const canonicalB = [1, null, 2, 1, 3, 3, 4, 3, null, null, null, null, null, null, null];
const canonicalC = [null, null, 2, 1, 3, 4, 4, null, 2, 1, 1, 3, 3, null, 4];
const canonicalUnits = canonicalA.map((_, index) => [canonicalA[index], canonicalB[index], canonicalC[index]]);
assert.ok(Math.abs(ordinalKrippendorffAlpha(canonicalUnits) - 0.8067214199413153) < 1e-12);

const mixed = summarizeReliability([[0, 1, 2], [2, 2, 3]]);
assert.equal(mixed.pairs, 6);
assert.equal(mixed.exact_agreement, 1 / 6);
assert.equal(mixed.within_one_agreement, 5 / 6);
assert.equal(mixed.mean_absolute_difference, 1);

const intervals = dossierBootstrap([perfect, [[0, 1, 0], [3, 4, 3]]], 100, 7);
assert.ok(intervals.exact_agreement.lower_95 >= 0);
assert.ok(intervals.exact_agreement.upper_95 <= 1);
assert.equal(intervals.exact_agreement.defined_replicates, 100);

const availability = availabilityAgreement([[null, 2, 3], [1, 1, 1], [null, null, null]]);
assert.equal(availability.mixed_availability_units, 1);
assert.deepEqual(availability.scored_repetitions_per_unit, {zero: 1, one: 0, two: 1, three: 1, other: 0});

const undefinedIntervals = dossierBootstrap([constant], 20, 3);
assert.equal(undefinedIntervals.ordinal_krippendorff_alpha.lower_95, null);
assert.equal(undefinedIntervals.ordinal_krippendorff_alpha.upper_95, null);

process.stdout.write("reliability tests passed\n");
