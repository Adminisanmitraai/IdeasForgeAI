export interface FounderProgressConfig {
  overallProgress: number;
  currentMilestone: string;
  showProgress: boolean;
}

export const founderProgressConfig: FounderProgressConfig = {
  overallProgress: 92,
  currentMilestone: "FOS-BRAIN-1 - Universal Entity Contracts + Context Graph Extension",
  showProgress: true,
};

export function normalizedFounderProgress(): number {
  const value = founderProgressConfig.overallProgress;
  if (!Number.isFinite(value)) {
    return 0;
  }
  return Math.min(100, Math.max(0, value));
}

export function shouldShowFounderProgress(): boolean {
  return founderProgressConfig.showProgress && normalizedFounderProgress() < 100;
}
