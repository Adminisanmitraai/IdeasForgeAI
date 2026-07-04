import path from "node:path";
import type { ExpertCategory } from "../types/ExpertCategory";
import type { ExpertMatchInput, ExpertMatchResult } from "../types/ExpertCapability";
import type { ExpertDependencyResolutionResult } from "../types/ExpertDependency";
import type { ExpertManifest } from "../types/ExpertManifest";
import type { ExpertRegistryHealth, ExpertRegistryReport } from "../types/ExpertRegistryResult";
import { ExpertCapabilityMatcher } from "./ExpertCapabilityMatcher";
import { ExpertCategoryRegistry } from "./ExpertCategoryRegistry";
import { ExpertDependencyResolver } from "./ExpertDependencyResolver";
import { ExpertPriorityRanker } from "./ExpertPriorityRanker";
import { ExpertRegistryLoader } from "./ExpertRegistryLoader";

export class ExpertRegistry {
  private report: ExpertRegistryReport | null = null;
  private readonly categoryRegistry = new ExpertCategoryRegistry();
  private readonly dependencyResolver = new ExpertDependencyResolver();
  private readonly priorityRanker = new ExpertPriorityRanker();

  private expertsById = new Map<string, ExpertManifest>();
  private expertsByCategory = new Map<string, ExpertManifest[]>();
  private expertsBySkill = new Map<string, ExpertManifest[]>();
  private expertsByTask = new Map<string, ExpertManifest[]>();
  private expertsByOutputType = new Map<string, ExpertManifest[]>();
  private expertsByCapabilityTag = new Map<string, ExpertManifest[]>();

  constructor(private readonly manifestDirectories: string[] = [path.resolve(process.cwd(), "src/experts/manifests")]) {}

  async load(): Promise<ExpertRegistryReport> {
    const loader = new ExpertRegistryLoader({ manifestDirectories: this.manifestDirectories });
    this.report = await loader.load();
    this.buildIndexes(this.report.manifests);
    return this.report;
  }

  getAllExperts(): ExpertManifest[] {
    return this.priorityRanker.sortExperts(this.ensureLoaded().manifests);
  }

  getActiveExperts(): ExpertManifest[] {
    return this.priorityRanker.sortExperts(this.ensureLoaded().activeManifests);
  }

  getExpertById(id: string): ExpertManifest | null {
    return this.expertsById.get(this.normalize(id)) ?? null;
  }

  getExpertsByCategory(category: string): ExpertManifest[] {
    return this.priorityRanker.sortExperts(this.expertsByCategory.get(this.normalize(category)) ?? []);
  }

  getExpertsBySkill(skill: string): ExpertManifest[] {
    return this.priorityRanker.sortExperts(this.expertsBySkill.get(this.normalize(skill)) ?? []);
  }

  getExpertsByTask(task: string): ExpertManifest[] {
    return this.priorityRanker.sortExperts(this.expertsByTask.get(this.normalize(task)) ?? []);
  }

  getExpertsByOutputType(outputType: string): ExpertManifest[] {
    return this.priorityRanker.sortExperts(this.expertsByOutputType.get(this.normalize(outputType)) ?? []);
  }

  getExpertsByCapabilityTag(tag: string): ExpertManifest[] {
    return this.priorityRanker.sortExperts(this.expertsByCapabilityTag.get(this.normalize(tag)) ?? []);
  }

  matchExperts(input: ExpertMatchInput): ExpertMatchResult[] {
    const matcher = new ExpertCapabilityMatcher(this.ensureLoaded().manifests);
    return matcher.match(input);
  }

  validateDependencies(): ExpertDependencyResolutionResult {
    return this.dependencyResolver.resolve(this.ensureLoaded().activeManifests);
  }

  getRegistryHealth(): ExpertRegistryHealth {
    return this.ensureLoaded().health;
  }

  listCategories(): ExpertCategory[] {
    return this.categoryRegistry.listCategories();
  }

  private buildIndexes(experts: ExpertManifest[]): void {
    this.expertsById = new Map();
    this.expertsByCategory = new Map();
    this.expertsBySkill = new Map();
    this.expertsByTask = new Map();
    this.expertsByOutputType = new Map();
    this.expertsByCapabilityTag = new Map();

    for (const expert of experts) {
      this.expertsById.set(this.normalize(expert.id), expert);
      this.addToIndex(this.expertsByCategory, expert.category, expert);
      for (const skill of expert.skills) this.addToIndex(this.expertsBySkill, skill, expert);
      for (const task of expert.supportedTasks) this.addToIndex(this.expertsByTask, task, expert);
      for (const outputType of expert.outputTypes) this.addToIndex(this.expertsByOutputType, outputType, expert);
      for (const tag of expert.capabilityTags) this.addToIndex(this.expertsByCapabilityTag, tag, expert);
    }
  }

  private addToIndex(index: Map<string, ExpertManifest[]>, key: string, expert: ExpertManifest): void {
    const normalizedKey = this.normalize(key);
    index.set(normalizedKey, [...(index.get(normalizedKey) ?? []), expert]);
  }

  private ensureLoaded(): ExpertRegistryReport {
    if (!this.report) {
      throw new Error("ExpertRegistry is not loaded. Call await registry.load() before using it.");
    }
    return this.report;
  }

  private normalize(value: string): string {
    return value.trim().toLowerCase();
  }
}
