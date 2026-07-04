import { describe, expect, it } from "vitest";
import { ExpertCapabilityMatcher } from "../registry/ExpertCapabilityMatcher";
import { validManifest } from "./testUtils";

describe("Capability matching", () => {
  it("ranks the correct expert highest", () => {
    const matcher = new ExpertCapabilityMatcher([
      validManifest({ id: "cad", name: "CAD", priority: 90, skills: ["cad-drafting"], supportedTasks: ["create-cad-layout"], outputTypes: ["layout"], capabilityTags: ["cad"] }),
      validManifest({ id: "marketing", name: "Marketing", priority: 80, skills: ["campaign-planning"], supportedTasks: ["create-campaign"], outputTypes: ["campaign-plan"], capabilityTags: ["marketing"] })
    ]);

    const results = matcher.match({
      intent: "create-cad-layout",
      requiredSkills: ["cad-drafting"],
      desiredOutputTypes: ["layout"],
      capabilityTags: ["cad"]
    });

    expect(results[0]?.expertId).toBe("cad");
  });

  it("lowers score when skills are missing", () => {
    const matcher = new ExpertCapabilityMatcher([
      validManifest({ id: "partial", skills: ["planning"], supportedTasks: ["test-task"] })
    ]);

    const results = matcher.match({ intent: "test-task", requiredSkills: ["planning", "advanced-skill"] });
    expect(results[0]?.missingCapabilities).toContain("skill:advanced-skill");
    expect(results[0]?.score).toBeLessThan(75);
  });

  it("output type affects score", () => {
    const matcher = new ExpertCapabilityMatcher([
      validManifest({ id: "reporter", outputTypes: ["report"] }),
      validManifest({ id: "planner", outputTypes: ["plan"], priority: 70 })
    ]);

    const results = matcher.match({ desiredOutputTypes: ["report"] });
    expect(results[0]?.expertId).toBe("reporter");
  });

  it("disabled expert does not appear in normal matching", () => {
    const matcher = new ExpertCapabilityMatcher([
      validManifest({ id: "disabled", status: "disabled", supportedTasks: ["test-task"], priority: 100 })
    ]);

    const results = matcher.match({ intent: "test-task" });
    expect(results).toHaveLength(0);
  });
});
