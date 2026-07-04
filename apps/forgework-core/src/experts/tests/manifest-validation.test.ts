import { describe, expect, it } from "vitest";
import { ExpertManifestValidator } from "../registry/ExpertManifestValidator";
import { validManifest } from "./testUtils";

describe("Manifest validation", () => {
  const validator = new ExpertManifestValidator();

  it("accepts a valid manifest", () => {
    const result = validator.validate(validManifest());
    expect(result.valid).toBe(true);
  });

  it("rejects missing id", () => {
    const manifest = validManifest() as unknown as Record<string, unknown>;
    delete manifest.id;
    const result = validator.validate(manifest);
    expect(result.valid).toBe(false);
    expect(result.errors.some((error) => error.includes("id"))).toBe(true);
  });

  it("rejects invalid priority", () => {
    const result = validator.validate(validManifest({ priority: 101 }));
    expect(result.valid).toBe(false);
    expect(result.errors.some((error) => error.includes("priority"))).toBe(true);
  });

  it("rejects invalid status", () => {
    const result = validator.validate({ ...validManifest(), status: "hidden" });
    expect(result.valid).toBe(false);
    expect(result.errors.some((error) => error.includes("status"))).toBe(true);
  });

  it("rejects missing approval requirements", () => {
    const manifest = validManifest() as unknown as Record<string, unknown>;
    delete manifest.approvalRequirements;
    const result = validator.validate(manifest);
    expect(result.valid).toBe(false);
    expect(result.errors.some((error) => error.includes("approvalRequirements"))).toBe(true);
  });
});
