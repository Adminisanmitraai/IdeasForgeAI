import { describe, expect, it } from "vitest";
import { ExpertDependencyResolver } from "../registry/ExpertDependencyResolver";
import { validManifest } from "./testUtils";

describe("Dependency resolution", () => {
  const resolver = new ExpertDependencyResolver();

  it("passes when required dependency is found", () => {
    const result = resolver.resolve([
      validManifest({ id: "base" }),
      validManifest({ id: "child", dependencies: [{ expertId: "base", versionRange: ">=1.0.0", required: true }] })
    ]);

    expect(result.valid).toBe(true);
    expect(result.loadOrder.indexOf("base")).toBeLessThan(result.loadOrder.indexOf("child"));
  });

  it("fails when required dependency is missing", () => {
    const result = resolver.resolve([
      validManifest({ id: "child", dependencies: [{ expertId: "base", versionRange: ">=1.0.0", required: true }] })
    ]);

    expect(result.valid).toBe(false);
    expect(result.missingRequiredDependencies).toHaveLength(1);
  });

  it("warns when optional dependency is missing", () => {
    const result = resolver.resolve([
      validManifest({ id: "child", dependencies: [{ expertId: "optional-base", versionRange: ">=1.0.0", required: false }] })
    ]);

    expect(result.valid).toBe(true);
    expect(result.missingOptionalDependencies).toHaveLength(1);
    expect(result.warnings.length).toBeGreaterThan(0);
  });

  it("detects circular dependency", () => {
    const result = resolver.resolve([
      validManifest({ id: "a", dependencies: [{ expertId: "b", versionRange: ">=1.0.0", required: true }] }),
      validManifest({ id: "b", dependencies: [{ expertId: "a", versionRange: ">=1.0.0", required: true }] })
    ]);

    expect(result.valid).toBe(false);
    expect(result.circularDependencies.length).toBeGreaterThan(0);
  });
});
