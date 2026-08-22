export type WorkerTaskState =
  | "draft"
  | "queued"
  | "awaiting_approval"
  | "approved"
  | "running"
  | "paused"
  | "blocked"
  | "failed"
  | "cancelled"
  | "completed";

export type WorkerTaskPriority = "low" | "normal" | "high" | "critical";
export type WorkerApprovalState =
  | "not_required"
  | "pending"
  | "approved"
  | "rejected";
export type WorkerTimelineState =
  | "pending"
  | "active"
  | "completed"
  | "blocked"
  | "failed"
  | "skipped";
export type WorkerTone = "neutral" | "info" | "warning" | "danger" | "success";

export interface WorkerStatusMeta {
  label: string;
  description: string;
  tone: WorkerTone;
  order: number;
}

export const workerStatusMeta: Record<WorkerTaskState, WorkerStatusMeta> = {
  draft: { label: "Draft", description: "Defined but not queued.", tone: "neutral", order: 0 },
  queued: { label: "Queued", description: "Ready for a future executor.", tone: "info", order: 1 },
  awaiting_approval: { label: "Awaiting approval", description: "Paused at a human decision boundary.", tone: "warning", order: 2 },
  approved: { label: "Approved", description: "Approved and waiting to run.", tone: "success", order: 3 },
  running: { label: "Running", description: "Actively progressing through its plan.", tone: "info", order: 4 },
  paused: { label: "Paused", description: "Intentionally suspended.", tone: "warning", order: 5 },
  blocked: { label: "Blocked", description: "Cannot proceed without new context.", tone: "danger", order: 6 },
  failed: { label: "Failed", description: "Stopped after an unsuccessful step.", tone: "danger", order: 7 },
  cancelled: { label: "Cancelled", description: "Ended before completion.", tone: "neutral", order: 8 },
  completed: { label: "Completed", description: "Finished successfully.", tone: "success", order: 9 },
};

export interface WorkerTimelineItem {
  id: string;
  label: string;
  detail: string;
  state: WorkerTimelineState;
  time?: string;
}

export interface WorkerLogEntry {
  id: string;
  level: "info" | "notice" | "warning" | "error";
  time: string;
  message: string;
}

export interface WorkerDiagnostic {
  id: string;
  severity: "healthy" | "notice" | "warning" | "error";
  label: string;
  detail: string;
}

export interface WorkerTask {
  id: string;
  title: string;
  summary: string;
  state: WorkerTaskState;
  priority: WorkerTaskPriority;
  source: "Terminal" | "Code";
  workspace: string;
  approval: WorkerApprovalState;
  approvalNote: string;
  progress: number;
  createdAt: string;
  updatedAt: string;
  currentStep: string;
  nextStep: string;
  timeline: WorkerTimelineItem[];
  activity: WorkerLogEntry[];
  logs: WorkerLogEntry[];
  diagnostics: WorkerDiagnostic[];
}

export interface WorkerScreenState {
  tasks: WorkerTask[];
  dataMode: "local_fixture";
  availability: "foundation_ready";
  lastUpdated: string;
}

export type WorkerFilter = "all" | "running" | "awaiting_approval" | "blocked" | "completed";
