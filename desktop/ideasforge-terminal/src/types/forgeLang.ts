export interface ForgeLangTask {
  id: string;
  title: string;
  assignedAgent?: string;
  status: "pending" | "ready" | "running" | "waiting" | "done" | "failed";
  dependencies: string[];
}

export interface ForgeLangApproval {
  id: string;
  action: string;
  level: "none" | "review" | "explicit";
  reason: string;
}

export interface ForgeLangOutput {
  type: string;
  path?: string;
  description: string;
}

export interface ForgeLangBlueprint {
  contractVersion: string;
  projectId: string;
  intent: string;
  objective: string;
  mode: string;
  requiredCapabilities: string[];
  selectedAgents: string[];
  tasks: ForgeLangTask[];
  approvals: ForgeLangApproval[];
  expectedOutputs: ForgeLangOutput[];
  constraints: string[];
}