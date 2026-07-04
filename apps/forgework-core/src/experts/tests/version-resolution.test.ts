import { describe, expect, it } from "vitest";
import { ExpertVersionResolver } from "../registry/ExpertVersionResolver";

describe("Version resolution", () => {
  const resolver = new ExpertVersionResolver();

  it("passes compatible semver ranges", () => {
    expect(resolver.isCompatible("1.2.3", ">=1.0.0")).toBe(true);
    expect(resolver.isCompatible("1.2.3", "^1.0.0")).toBe(true);
    expect(resolver.isCompatible("1.2.3", "~1.2.0")).toBe(true);
    expect(resolver.isCompatible("1.2.3", "=1.2.3")).toBe(true);
  });

  it("fails incompatible semver ranges", () => {
    expect(resolver.isCompatible("2.0.0", "^1.0.0")).toBe(false);
    expect(resolver.isCompatible("1.1.0", "~1.2.0")).toBe(false);
  });
});
