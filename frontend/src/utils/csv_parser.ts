import Papa from 'papaparse';

export interface CSVParseResult {
  data: any[];
  meta: Papa.ParseMeta;
  errors: Papa.ParseError[];
}

/**
 * Parses a CSV file and returns the data as an array of objects.
 * Uses the first row as headers.
 */
export const parseCSV = (file: File): Promise<any[]> => {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        resolve(results.data);
      },
      error: (error) => {
        reject(error);
      },
    });
  });
};

/**
 * Reads the CSV file and returns the list of headers (first row).
 */
export const getHeaders = (file: File): Promise<string[]> => {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      preview: 1, // Only parse the first line
      complete: (results) => {
        if (results.data && results.data.length > 0) {
          resolve(results.data[0] as string[]);
        } else {
          resolve([]);
        }
      },
      error: (error) => {
        reject(error);
      },
    });
  });
};
