import type { ExpertManifest } from "./ExpertManifest";

export type ExpertRiskLevel = "low" | "medium" | "high" | "critical";

export interface ExpertMatchInput {
  intent?: string;
  requiredSkills?: string[];
  desiredOutputTypes?: string[];
  capabilityTags?: string[];
  softwareContext?: string[];
  riskLevel?: ExpertRiskLevel;
  directExpertId?: string;
  includeExperimental?: boolean;
  includeDeprecated?: boolean;
  includeDisabled?: boolean;
}

export interface ExpertMatchResult {
  expertId: string;
  expert: ExpertManifest;
  score: number;
  reasons: string[];
  missingCapabilities: string[];
  requiresApproval: boolean;
}
