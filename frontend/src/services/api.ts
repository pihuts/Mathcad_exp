import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
});

export interface BatchRequest {
  batch_id: string;
  inputs: Record<string, any>[];
  output_dir: string;
}

export interface BatchRow {
  row: number;
  status: string;
  data?: Record<string, any>;
  pdf?: string;
  error?: string;
}

export interface BatchStatus {
  id: string;
  total: number;
  completed: number;
  status: string;
  results: BatchRow[];
  error?: string;
}

export interface ControlResponse {
  status: string;
  message: string;
}

export interface JobResponse {
  job_id: string;
  status: string;
}

export interface MetaData {
  inputs: Array<{alias: string, name: string}>;
  outputs: Array<{alias: string, name: string}>;
}

export const startBatch = async (config: BatchRequest): Promise<ControlResponse> => {
  const { data } = await api.post<ControlResponse>('/batch/start', config);
  return data;
};

export const getBatchStatus = async (id: string): Promise<BatchStatus> => {
  const { data } = await api.get<BatchStatus>(`/batch/${id}`);
  return data;
};

export const stopBatch = async (id: string): Promise<ControlResponse> => {
  const { data } = await api.post<ControlResponse>(`/batch/${id}/stop`);
  return data;
};

export const getInputs = async (path: string): Promise<MetaData> => {
  const { data } = await api.post<MetaData>('/engine/analyze', { path });
  return data;
};

export default api;
