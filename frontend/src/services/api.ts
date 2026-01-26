import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
});

export interface BatchRequest {
  batch_id: string;
  inputs: Record<string, any>[];
  output_dir: string;
  export_pdf: boolean;
  export_mcdx: boolean;
}

export interface InputConfig {
  alias: string;
  value: any;
  units?: string;  // Units specification (e.g., "in", "ft", "kip", or undefined for default)
}

export interface BatchRow {
  row: number;
  status: string;
  stage?: string;
  data?: Record<string, any>;
  pdf?: string;
  mcdx?: string;
  error?: string;
}

export interface BatchStatus {
  id: string;
  total: number;
  completed: number;
  status: string;
  results: BatchRow[];
  generated_files?: string[];
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
  inputs: Array<{ alias: string, name: string }>;
  outputs: Array<{ alias: string, name: string }>;
}

export interface FileMapping {
  source_file: string;
  source_alias: string;
  target_file: string;
  target_alias: string;
}

export interface WorkflowFile {
  file_path: string;
  inputs: InputConfig[];
  position: number;
}

export interface WorkflowConfig {
  name: string;
  files: WorkflowFile[];
  mappings: FileMapping[];
  stop_on_error: boolean;
  export_pdf: boolean;
  export_mcdx: boolean;
  output_dir?: string;
}

export type WorkflowStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "stopped";

export const WorkflowStatus = {
  PENDING: "pending" as WorkflowStatus,
  RUNNING: "running" as WorkflowStatus,
  COMPLETED: "completed" as WorkflowStatus,
  FAILED: "failed" as WorkflowStatus,
  STOPPED: "stopped" as WorkflowStatus,
} as const;

export interface WorkflowStatusResponse {
  workflow_id: string;
  status: string;
  current_file_index: number;
  total_files: number;
  completed_files: string[];
  progress: number;
  error?: string;
}

export interface WorkflowCreateResponse {
  workflow_id: string;
  status: string;
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

export const createWorkflow = async (config: WorkflowConfig): Promise<WorkflowCreateResponse> => {
  const { data } = await api.post<WorkflowCreateResponse>('/workflows', config);
  return data;
};

export const getWorkflowStatus = async (workflowId: string): Promise<WorkflowStatusResponse> => {
  const { data } = await api.get<WorkflowStatusResponse>(`/workflows/${workflowId}`);
  return data;
};

export const stopWorkflow = async (workflowId: string): Promise<ControlResponse> => {
  const { data } = await api.post<ControlResponse>(`/workflows/${workflowId}/stop`);
  return data;
};

export const openFile = async (path: string): Promise<{ status: string }> => {
  const { data } = await api.post<{ status: string }>('/files/open', { path });
  return data;
};

export const browseFile = async (): Promise<{ file_path: string | null; cancelled: boolean }> => {
  const { data } = await api.post<{ file_path: string | null; cancelled: boolean }>('/files/browse');
  return data;
};

export default api;
