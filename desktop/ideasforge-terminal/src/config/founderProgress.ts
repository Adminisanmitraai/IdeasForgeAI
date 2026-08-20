export interface FounderProgressConfig {
  overallProgress: number;
  currentMilestone: string;
  showProgress: boolean;
}

export const founderProgressConfig: FounderProgressConfig = {
  overallProgress: 85,
  currentMilestone: "FOS-VOICE.3 - Voice Permission/Consent + Cost Metering + Audit Events",
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
  return (
    founderProgressConfig.showProgress &&
    normalizedFounderProgress() < 100
  );
}
