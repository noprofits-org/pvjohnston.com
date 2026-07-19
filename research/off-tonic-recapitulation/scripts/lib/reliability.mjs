const rating = (value) => typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= 4;
const category = (value) => Number.isInteger(value) && value >= 0 && value <= 4;

export function median(values) {
  const sorted = values.filter(rating).toSorted((left, right) => left - right);
  if (sorted.length === 0) return null;
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

export function completeOrdinalMedian(values, expected = 3) {
  if (values.length !== expected || values.some((value) => !category(value))) return null;
  return median(values);
}

export function availabilityAgreement(units) {
  const availabilityUnits = units.map((ratings) => ratings.map((value) => rating(value) ? 1 : 0));
  const agreement = directAgreement(availabilityUnits);
  const scoredPerUnit = {zero: 0, one: 0, two: 0, three: 0, other: 0};
  for (const ratings of units) {
    const count = ratings.filter(rating).length;
    const key = ["zero", "one", "two", "three"][count] ?? "other";
    scoredPerUnit[key] += 1;
  }
  return {
    scored_repetitions_per_unit: scoredPerUnit,
    pairwise_availability_agreement: agreement.exact_agreement,
    mixed_availability_units: units.filter((ratings) => {
      const count = ratings.filter(rating).length;
      return count > 0 && count < ratings.length;
    }).length
  };
}

export function directAgreement(units) {
  const differences = [];
  for (const ratings of units) {
    const present = ratings.filter(rating);
    for (let left = 0; left < present.length; left += 1) {
      for (let right = left + 1; right < present.length; right += 1) {
        differences.push(Math.abs(present[left] - present[right]));
      }
    }
  }
  if (differences.length === 0) {
    return {pairs: 0, exact_agreement: null, within_one_agreement: null, mean_absolute_difference: null, median_absolute_difference: null};
  }
  const sum = differences.reduce((total, value) => total + value, 0);
  return {
    pairs: differences.length,
    exact_agreement: differences.filter((value) => value === 0).length / differences.length,
    within_one_agreement: differences.filter((value) => value <= 1).length / differences.length,
    mean_absolute_difference: sum / differences.length,
    median_absolute_difference: median(differences)
  };
}

export function ordinalKrippendorffAlpha(units) {
  const categories = [0, 1, 2, 3, 4];
  const coincidence = categories.map(() => categories.map(() => 0));

  for (const ratings of units) {
    const present = ratings.filter(category);
    if (present.length < 2) continue;
    for (let left = 0; left < present.length; left += 1) {
      for (let right = 0; right < present.length; right += 1) {
        if (left === right) continue;
        coincidence[present[left]][present[right]] += 1 / (present.length - 1);
      }
    }
  }

  const marginals = coincidence.map((row) => row.reduce((sum, value) => sum + value, 0));
  const total = marginals.reduce((sum, value) => sum + value, 0);
  if (total <= 1) return null;

  const distance = (left, right) => {
    if (left === right) return 0;
    const low = Math.min(left, right);
    const high = Math.max(left, right);
    let mass = 0;
    for (let category = low; category <= high; category += 1) mass += marginals[category];
    mass -= (marginals[low] + marginals[high]) / 2;
    return mass ** 2;
  };

  let observed = 0;
  let expected = 0;
  for (const left of categories) {
    for (const right of categories) {
      const delta = distance(left, right);
      observed += coincidence[left][right] * delta;
      const expectedCoincidence = left === right
        ? marginals[left] * (marginals[left] - 1) / (total - 1)
        : marginals[left] * marginals[right] / (total - 1);
      expected += expectedCoincidence * delta;
    }
  }

  if (expected === 0) return null;
  return 1 - observed / expected;
}

export function summarizeReliability(units) {
  return {
    ordinal_krippendorff_alpha: ordinalKrippendorffAlpha(units),
    ...directAgreement(units)
  };
}

export function mulberry32(seed) {
  let state = seed >>> 0;
  return () => {
    state += 0x6D2B79F5;
    let value = state;
    value = Math.imul(value ^ value >>> 15, value | 1);
    value ^= value + Math.imul(value ^ value >>> 7, value | 61);
    return ((value ^ value >>> 14) >>> 0) / 4294967296;
  };
}

export function quantile(values, probability) {
  const present = values.filter((value) => typeof value === "number" && Number.isFinite(value)).toSorted((left, right) => left - right);
  if (present.length === 0) return null;
  const index = (present.length - 1) * probability;
  const low = Math.floor(index);
  const high = Math.ceil(index);
  if (low === high) return present[low];
  return present[low] + (present[high] - present[low]) * (index - low);
}

export function dossierBootstrap(caseUnits, repetitions = 2000, seed = 1701) {
  const observed = summarizeReliability(caseUnits.flat());
  const random = mulberry32(seed);
  const samples = [];
  for (let iteration = 0; iteration < repetitions; iteration += 1) {
    const units = [];
    for (let draw = 0; draw < caseUnits.length; draw += 1) {
      const selected = caseUnits[Math.floor(random() * caseUnits.length)];
      units.push(...selected);
    }
    samples.push(summarizeReliability(units));
  }
  const fields = [
    "ordinal_krippendorff_alpha",
    "exact_agreement",
    "within_one_agreement",
    "mean_absolute_difference",
    "median_absolute_difference"
  ];
  return Object.fromEntries(fields.map((field) => {
    const defined = samples.map((sample) => sample[field]).filter((value) => typeof value === "number" && Number.isFinite(value));
    return [field, {
      defined_replicates: defined.length,
      defined_fraction: defined.length / repetitions,
      lower_95: observed[field] === null ? null : quantile(defined, 0.025),
      upper_95: observed[field] === null ? null : quantile(defined, 0.975)
    }];
  }));
}
