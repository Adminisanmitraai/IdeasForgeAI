export const TERMINAL_API_CONTRACT =
  "forgecode.terminal-api.v1" as const;

export const TERMINAL_DISCOVERY_CONTRACT =
  "forgecode.build-test-discovery.v1" as const;

export type TerminalGatewayStatus =
  | "idle"
  | "checking"
  | "discovering"
  | "planning"
  | "ready"
  | "failed"
  | "offline";

export type TerminalDiscoveryStatus =
  | "idle"
  | "loading"
  | "succeeded"
  | "failed";

export type TerminalPlanStatus =
  | "idle"
  | "loading"
  | "succeeded"
  | "failed";

export type TerminalPreviewStatus =
  | "idle"
  | "loading"
  | "succeeded"
  | "failed";

export interface TerminalApiError {
  code: string;
  message: string;
  status?: number;
  retryable?: boolean;
  details?: unknown;
}

export interface TerminalApiEnvelope<T> {
  ok: boolean;
  contract_version: string;
  code: string;
  data: T;
  errors: TerminalApiError[];
}

export interface TerminalCapabilities {
  capabilities: Record<string, boolean>;
  contracts: {
    planner: string;
    runtime: string;
    session: string;
    audit: string;
    approval: string;
    discovery?: string;
    preview?: string;
  };
}

export interface TerminalDiscoveryRequest {
  project_id: string;
  project_root: string;
  approved_root: string;
}

export interface DiscoveredCommand {
  id: string;
  category: string;
  label: string;
  argv: string[];
  working_directory: string;
  ecosystem: string;
  package_manager: string | null;
  framework: string | null;
  confidence: string;
  risk: string;
  requires_approval: boolean;
  read_only: boolean;
  mutates_files: boolean;
  installs_dependencies: boolean;
  starts_long_running_process: boolean;
  requires_network: boolean;
  expected_outputs: string[];
  required_files: string[];
  evidence: unknown[];
  warnings: string[];
  metadata: Record<string, unknown>;
}

export interface BuildTestDiscoveryResult {
  ok: boolean;
  project_id: string;
  commands: DiscoveredCommand[];
  recommended_validation_sequence: string[];
  recommended_build_sequence: string[];
  recommended_test_sequence: string[];
  recommended_dev_sequence: string[];
  warnings: string[];
  errors: Array<{
    code: string;
    message: string;
  }>;
  statistics: Record<string, number>;
  capabilities: Record<string, boolean>;
  contract_version: string;
  profile?: Record<string, unknown>;
}

export interface TerminalDiscoveryData {
  project_id: string;
  project_root: string;
  approved_root: string;
  command_ids: string[];
  discovered_commands: DiscoveredCommand[];
  discovery: BuildTestDiscoveryResult;
}

export interface TerminalPlanPayload {
  project_id: string;
  project_root: string;
  approved_root: string;
  command_ids: string[];
  discovered_commands: DiscoveredCommand[];
  discovered_command_contract_version: string;
}

export interface TerminalPlanStep {
  step_id: string;
  command_id: string;
  label: string;
  category: string;
  argv: string[];
  executable: string;
  working_directory: string;
  risk: string;
  requires_approval: boolean;
  approval_granted: boolean;
  timeout_seconds: number;
  maximum_output_bytes: number;
  maximum_error_bytes: number;
  expected_outputs: string[];
  success_criteria: string[];
  warnings: string[];
  metadata: Record<string, unknown>;
}

export interface TerminalExecutionPlan {
  ok: boolean;
  project_id: string;
  project_root: string;
  steps: TerminalPlanStep[];
  risk: string;
  requires_approval: boolean;
  approval_reasons: string[];
  warnings: string[];
  errors: Array<{
    code: string;
    message: string;
  }>;
  statistics: Record<string, number>;
  capabilities: Record<string, boolean>;
  contract_version: string;
}

export interface TerminalPlanData {
  plan_sha256: string;
  plan: TerminalExecutionPlan;
}

export interface TerminalPreviewRequest {
  plan_sha256: string;
  project_id: string;
  workspace_id: string;
  workspace_root: string;
  approved_root: string;
  trust_state: "trusted";
}

export interface TerminalPreviewRisk {
  level: "low" | "medium" | "high" | "critical";
  reasons: string[];
}

export interface TerminalPreviewOperation {
  operation_id: string;
  sequence: number;
  type: "read" | "command" | "file_create" | "file_modify" | "file_delete" | "git" | "database" | "deployment" | "unsupported";
  title: string;
  description: string;
  command_id: string | null;
  command_preview: string | null;
  working_directory: string | null;
  affected_paths: string[];
  mutates_workspace: boolean;
  requires_approval: boolean;
  risk_level: "low" | "medium" | "high" | "critical";
  blocked: boolean;
  block_reason: string | null;
  rollback_available: boolean;
  expected_result: string | null;
}

export interface TerminalPreviewValidationStep {
  name: string;
  command_preview: string | null;
  required: boolean;
}

export interface TerminalExecutionPreview {
  preview_id: string;
  contract_version: "forgecode.terminal-execution-preview.v1";
  project_id: string;
  workspace_id: string | null;
  workspace_root: string;
  plan_id: string | null;
  summary: string;
  status: "ready" | "blocked" | "invalid";
  execution_enabled: false;
  approval_required: boolean;
  risk: TerminalPreviewRisk;
  operations: TerminalPreviewOperation[];
  validation_steps: TerminalPreviewValidationStep[];
  warnings: string[];
  blocked_reasons: string[];
  created_at: string;
}

export interface TerminalPreviewData {
  preview: TerminalExecutionPreview;
}

export interface TerminalGatewaySnapshot {
  status: TerminalGatewayStatus;
  connected: boolean;
  backendUrl: string;
  requestId: number;
  capabilities: TerminalCapabilities | null;
  discoveryStatus: TerminalDiscoveryStatus;
  discovery: TerminalDiscoveryData | null;
  discoveredCommands: DiscoveredCommand[];
  discoveredCommandIds: string[];
  selectedCommandIds: string[];
  discoveryWarnings: string[];
  discoveryError: TerminalApiError | null;
  discoveryProjectId: string | null;
  discoveryContractVersion: string | null;
  planStatus: TerminalPlanStatus;
  plan: TerminalPlanData | null;
  planError: TerminalApiError | null;
  previewStatus: TerminalPreviewStatus;
  preview: TerminalExecutionPreview | null;
  previewError: TerminalApiError | null;
  error: TerminalApiError | null;
  lastRequest:
    | TerminalPlanPayload
    | TerminalDiscoveryRequest
    | TerminalPreviewRequest
    | null;
  updatedAt: string | null;
}
