import { readFile } from "node:fs/promises";
import path from "node:path";
import type { ExpertDependencyResolutionResult } from "../types/ExpertDependency";
import type { ExpertManifest } from "../types/ExpertManifest";
import type { DuplicateExpertIdResult, ExpertRegistryHealth, ExpertRegistryReport, InvalidManifestResult } from "../types/ExpertRegistryResult";
import { ExpertCategoryRegistry } from "./ExpertCategoryRegistry";
import { ExpertDependencyResolver } from "./ExpertDependencyResolver";
import { ExpertDiscovery } from "./ExpertDiscovery";
import { ExpertManifestValidator } from "./ExpertManifestValidator";

export interface ExpertRegistryLoaderOptions {
  manifestDirectories?: string[];
  includeExperimentalInActiveSet?: boolean;
}

export class ExpertRegistryLoader {
  private readonly discovery = new ExpertDiscovery();
  private readonly validator = new ExpertManifestValidator();
  private readonly dependencyResolver = new ExpertDependencyResolver();
  private readonly categoryRegistry = new ExpertCategoryRegistry();

  constructor(private readonly options: ExpertRegistryLoaderOptions = {}) {}

  async load(): Promise<ExpertRegistryReport> {
    const manifestDirectories = this.options.manifestDirectories?.length
      ? this.options.manifestDirectories
      : [path.resolve(process.cwd(), "src/experts/manifests")];

    const discoveredFiles = await this.discovery.discover(manifestDirectories);
    const invalidManifests: InvalidManifestResult[] = [];
    const manifests: ExpertManifest[] = [];
    const seenIds = new Map<string, string[]>();

    for (const file of discoveredFiles) {
      try {
        const raw = await readFile(file.filePath, "utf-8");
        const parsed = JSON.parse(raw) as unknown;
        const validation = this.validator.validate(parsed);

        if (!validation.valid) {
          invalidManifests.push({ filePath: file.filePath, errors: validation.errors });
          continue;
        }

        const manifest = parsed as ExpertManifest;
        manifests.push(manifest);
        seenIds.set(manifest.id, [...(seenIds.get(manifest.id) ?? []), file.filePath]);
      } catch (error) {
        invalidManifests.push({
          filePath: file.filePath,
          errors: [error instanceof Error ? error.message : "Unknown manifest parsing error."]
        });
      }
    }

    const duplicateExpertIds: DuplicateExpertIdResult[] = [...seenIds.entries()]
      .filter(([, filePaths]) => filePaths.length > 1)
      .map(([expertId, filePaths]) => ({ expertId, filePaths }));

    const duplicateIds = new Set(duplicateExpertIds.map((duplicate) => duplicate.expertId));
    const deduplicatedManifests = manifests.filter((manifest) => !duplicateIds.has(manifest.id));

    for (const duplicate of duplicateExpertIds) {
      invalidManifests.push({
        filePath: duplicate.filePaths.join(", "),
        errors: [`Duplicate expert id detected: ${duplicate.expertId}`]
      });
    }

    const activeManifests = deduplicatedManifests.filter((manifest) =>
      manifest.status === "active" || (this.options.includeExperimentalInActiveSet && manifest.status === "experimental")
    );

    const dependencyResolution = this.dependencyResolver.resolve(activeManifests);
    const health = this.createHealth(discoveredFiles.length, deduplicatedManifests, invalidManifests, dependencyResolution);

    return {
      manifests: deduplicatedManifests,
      activeManifests,
      invalidManifests,
      duplicateExpertIds,
      dependencyResolution,
      health
    };
  }

  private createHealth(
    totalExpertsDiscovered: number,
    manifests: ExpertManifest[],
    invalidManifests: InvalidManifestResult[],
    dependencyResolution: ExpertDependencyResolutionResult
  ): ExpertRegistryHealth {
    return {
      totalExpertsDiscovered,
      activeExperts: manifests.filter((manifest) => manifest.status === "active").length,
      experimentalExperts: manifests.filter((manifest) => manifest.status === "experimental").length,
      disabledExperts: manifests.filter((manifest) => manifest.status === "disabled").length,
      deprecatedExperts: manifests.filter((manifest) => manifest.status === "deprecated").length,
      categories: this.categoryRegistry.listCategories().length,
      invalidManifests: invalidManifests.length,
      dependencyErrors: dependencyResolution.missingRequiredDependencies.length + dependencyResolution.circularDependencies.length,
      warnings: dependencyResolution.warnings
    };
  }
}
