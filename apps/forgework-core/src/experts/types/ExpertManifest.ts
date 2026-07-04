export type ExpertStatus = "active" | "experimental" | "deprecated" | "disabled";

export interface ExpertSoftwareRequirement {
  name: string;
  required: boolean;
  minimumVersion?: string | null;
}

export interface ExpertDesktopPermissions {
  requiresDesktop: boolean;
  canUseForgePilot: boolean;
  allowedActions: string[];
  blockedActions: string[];
}

export interface ExpertApprovalRequirements {
  requiresUserApprovalBeforeExecution: boolean;
  requiresUserApprovalBeforeDesktopAction: boolean;
  requiresUserApprovalBeforeFileWrite: boolean;
  requiresUserApprovalBeforeExternalSend: boolean;
}

export interface ExpertDependency {
  expertId: string;
  versionRange: string;
  required: boolean;
}

export interface ExpertManifest {
  id: string;
  name: string;
  version: string;
  description: string;
  category: string;
  priority: number;
  status: ExpertStatus;
  skills: string[];
  supportedTasks: string[];
  requiredSoftware: ExpertSoftwareRequirement[];
  desktopPermissions: ExpertDesktopPermissions;
  approvalRequirements: ExpertApprovalRequirements;
  outputTypes: string[];
  dependencies: ExpertDependency[];
  capabilityTags: string[];
  examples: string[];
}

export interface ExpertImplementation {
  getManifest(): ExpertManifest;
  canHandle(request: ExpertCapabilityRequest): boolean;
  describeCapabilities(): string[];
}

export interface ExpertCapabilityRequest {
  intent?: string;
  requiredSkills?: string[];
  desiredOutputTypes?: string[];
  capabilityTags?: string[];
}
