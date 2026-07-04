export interface MissingDependencyResult {
  expertId: string;
  dependencyId: string;
  versionRange: string;
  reason: string;
}

export interface ExpertDependencyResolutionResult {
  valid: boolean;
  loadOrder: string[];
  missingRequiredDependencies: MissingDependencyResult[];
  missingOptionalDependencies: MissingDependencyResult[];
  circularDependencies: string[][];
  warnings: string[];
}
