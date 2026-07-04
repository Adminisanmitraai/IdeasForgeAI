import type { ExpertManifest } from "./ExpertManifest";
import type { ExpertDependencyResolutionResult } from "./ExpertDependency";

export interface InvalidManifestResult {
  filePath: string;
  errors: string[];
}

export interface DuplicateExpertIdResult {
  expertId: string;
  filePaths: string[];
}

export interface ExpertRegistryHealth {
  totalExpertsDiscovered: number;
  activeExperts: number;
  experimentalExperts: number;
  disabledExperts: number;
  deprecatedExperts: number;
  categories: number;
  invalidManifests: number;
  dependencyErrors: number;
  warnings: string[];
}

export interface ExpertRegistryReport {
  manifests: ExpertManifest[];
  activeManifests: ExpertManifest[];
  invalidManifests: InvalidManifestResult[];
  duplicateExpertIds: DuplicateExpertIdResult[];
  dependencyResolution: ExpertDependencyResolutionResult;
  health: ExpertRegistryHealth;
}
