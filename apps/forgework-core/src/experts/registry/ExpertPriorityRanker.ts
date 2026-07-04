import type { ExpertManifest } from "../types/ExpertManifest";

export type ExpertPriorityBand = "core" | "strong" | "normal" | "low" | "disabled";

export class ExpertPriorityRanker {
  getPriorityBand(priority: number): ExpertPriorityBand {
    if (priority === 0) return "disabled";
    if (priority >= 90) return "core";
    if (priority >= 70) return "strong";
    if (priority >= 40) return "normal";
    return "low";
  }

  getPriorityBoost(priority: number): number {
    if (priority <= 0) return 0;
    return Math.min(5, priority / 20);
  }

  sortExperts(experts: ExpertManifest[]): ExpertManifest[] {
    return [...experts].sort((a, b) => {
      if (b.priority !== a.priority) return b.priority - a.priority;
      return a.name.localeCompare(b.name);
    });
  }
}
