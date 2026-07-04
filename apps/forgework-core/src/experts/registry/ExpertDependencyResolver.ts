import type { ExpertDependencyResolutionResult, MissingDependencyResult } from "../types/ExpertDependency";
import type { ExpertManifest } from "../types/ExpertManifest";
import { ExpertVersionResolver } from "./ExpertVersionResolver";

export class ExpertDependencyResolver {
  private readonly versionResolver = new ExpertVersionResolver();

  resolve(experts: ExpertManifest[]): ExpertDependencyResolutionResult {
    const expertsById = new Map(experts.map((expert) => [expert.id, expert]));
    const missingRequiredDependencies: MissingDependencyResult[] = [];
    const missingOptionalDependencies: MissingDependencyResult[] = [];
    const warnings: string[] = [];
    const graph = new Map<string, string[]>();

    for (const expert of experts) {
      graph.set(expert.id, []);

      for (const dependency of expert.dependencies) {
        const dependencyExpert = expertsById.get(dependency.expertId);

        if (!dependencyExpert) {
          const missing: MissingDependencyResult = {
            expertId: expert.id,
            dependencyId: dependency.expertId,
            versionRange: dependency.versionRange,
            reason: "Dependency expert is not registered."
          };

          if (dependency.required) missingRequiredDependencies.push(missing);
          else missingOptionalDependencies.push(missing);
          continue;
        }

        if (!this.versionResolver.isCompatible(dependencyExpert.version, dependency.versionRange)) {
          const missing: MissingDependencyResult = {
            expertId: expert.id,
            dependencyId: dependency.expertId,
            versionRange: dependency.versionRange,
            reason: `Dependency version ${dependencyExpert.version} does not satisfy ${dependency.versionRange}.`
          };

          if (dependency.required) missingRequiredDependencies.push(missing);
          else missingOptionalDependencies.push(missing);
          continue;
        }

        graph.get(expert.id)?.push(dependency.expertId);
      }
    }

    for (const missing of missingOptionalDependencies) {
      warnings.push(`Optional dependency ${missing.dependencyId} for ${missing.expertId} is unavailable: ${missing.reason}`);
    }

    const circularDependencies = this.detectCycles(graph);
    const loadOrder = circularDependencies.length === 0 ? this.topologicalSort(graph) : [];

    return {
      valid: missingRequiredDependencies.length === 0 && circularDependencies.length === 0,
      loadOrder,
      missingRequiredDependencies,
      missingOptionalDependencies,
      circularDependencies,
      warnings
    };
  }

  private detectCycles(graph: Map<string, string[]>): string[][] {
    const cycles: string[][] = [];
    const visiting = new Set<string>();
    const visited = new Set<string>();
    const stack: string[] = [];

    const visit = (node: string): void => {
      if (visiting.has(node)) {
        const cycleStart = stack.indexOf(node);
        if (cycleStart >= 0) {
          cycles.push([...stack.slice(cycleStart), node]);
        }
        return;
      }

      if (visited.has(node)) return;

      visiting.add(node);
      stack.push(node);

      for (const dependency of graph.get(node) ?? []) {
        visit(dependency);
      }

      stack.pop();
      visiting.delete(node);
      visited.add(node);
    };

    for (const node of graph.keys()) {
      visit(node);
    }

    return cycles;
  }

  private topologicalSort(graph: Map<string, string[]>): string[] {
    const visited = new Set<string>();
    const order: string[] = [];

    const visit = (node: string): void => {
      if (visited.has(node)) return;
      visited.add(node);

      for (const dependency of graph.get(node) ?? []) {
        visit(dependency);
      }

      order.push(node);
    };

    for (const node of graph.keys()) {
      visit(node);
    }

    return order;
  }
}
