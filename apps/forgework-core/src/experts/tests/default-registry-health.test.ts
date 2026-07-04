import path from "node:path";
import { describe, expect, it } from "vitest";
import { ExpertRegistry } from "../registry/ExpertRegistry";

describe("Default registry health", () => {
  it("loads the sample registry with at least 18 active experts", async () => {
    const manifestDirectory = path.resolve(__dirname, "../manifests");
    const registry = new ExpertRegistry([manifestDirectory]);
    const report = await registry.load();

    expect(report.health.totalExpertsDiscovered).toBeGreaterThanOrEqual(18);
    expect(report.health.activeExperts).toBeGreaterThanOrEqual(18);
    expect(report.health.invalidManifests).toBe(0);
    expect(report.dependencyResolution.valid).toBe(true);
  });
});
