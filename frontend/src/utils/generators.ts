/**
 * Generates an array of numbers from start to end with a given step.
 */
export const generateRange = (start: number, end: number, step: number): number[] => {
  if (step === 0) return [start];
  const results: number[] = [];
  
  if (step > 0) {
    for (let i = start; i <= end; i += step) {
      // Handle floating point precision issues
      results.push(Number(i.toFixed(10)));
    }
  } else {
    for (let i = start; i >= end; i += step) {
      results.push(Number(i.toFixed(10)));
    }
  }
  
  return results;
};

/**
 * Generates Cartesian product of all inputs.
 * inputsMap: { [alias]: Array of values }
 * Returns: Array of objects { [alias]: value }
 */
export const generateCartesian = (inputsMap: Record<string, any[]>): Record<string, any>[] => {
  const keys = Object.keys(inputsMap);
  if (keys.length === 0) return [];

  const results: Record<string, any>[] = [{}];

  for (const key of keys) {
    const values = inputsMap[key];
    const nextResults: Record<string, any>[] = [];

    for (const result of results) {
      for (const value of values) {
        nextResults.push({ ...result, [key]: value });
      }
    }
    results.splice(0, results.length, ...nextResults);
  }

  return results;
};

/**
 * Zips inputs together row-by-row.
 * inputsMap: { [alias]: Array of values }
 * Returns: Array of objects { [alias]: value }
 */
export const generateZip = (inputsMap: Record<string, any[]>): Record<string, any>[] => {
  const keys = Object.keys(inputsMap);
  if (keys.length === 0) return [];

  const minLength = Math.min(...keys.map(key => inputsMap[key].length));
  const results: Record<string, any>[] = [];

  for (let i = 0; i < minLength; i++) {
    const row: Record<string, any> = {};
    for (const key of keys) {
      row[key] = inputsMap[key][i];
    }
    results.push(row);
  }

  return results;
};
