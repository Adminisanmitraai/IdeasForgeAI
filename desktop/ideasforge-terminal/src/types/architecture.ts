import type { ServiceState } from "./api";

export interface ArchitectureHealth {
  status?: string;
  healthy?: boolean;
  contract_version?: string;
  [key: string]: unknown;
}

export interface ArchitectureAnalyzeRequest {
  mode?: string;
  project_root?: string;
  metadata?: Record<string, unknown>;
}

export interface ArchitectureAnalyzeResponse {
  mode?: string;
  architecture?: unknown;
  capabilities?: unknown;
  contract_version?: string;
  [key: string]: unknown;
}

export interface ArchitectureServiceStatus {
  state: ServiceState;
  route: string;
  message: string;
}