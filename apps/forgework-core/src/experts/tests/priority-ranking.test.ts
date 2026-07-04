import { describe, expect, it } from "vitest";
import { ExpertCapabilityMatcher } from "../registry/ExpertCapabilityMatcher";
import { ExpertPriorityRanker } from "../registry/ExpertPriorityRanker";
import { validManifest } from "./testUtils";

describe("Priority ranking", () => {
  it("higher-priority expert gets a boost", () => {
    const matcher = new ExpertCapabilityMatcher([
      validManifest({ id: "low", priority: 40, supportedTasks: ["same-task"] }),
      validManifest({ id: "high", priority: 100, supportedTasks: ["same-task"] })
    ]);

    const results = matcher.match({ intent: "same-task" });
    expect(results[0]?.expertId).toBe("high");
  });

  it("priority never pushes score beyond 100", () => {
    const matcher = new ExpertCapabilityMatcher([
      validManifest({ id: "core", priority: 100, supportedTasks: ["x"], skills: ["a"], outputTypes: ["b"], capabilityTags: ["c"] })
    ]);

    const results = matcher.match({ intent: "x", requiredSkills: ["a"], desiredOutputTypes: ["b"], capabilityTags: ["c"] });
    expect(results[0]?.score).toBeLessThanOrEqual(100);
  });

  it("returns correct priority bands", () => {
    const ranker = new ExpertPriorityRanker();
    expect(ranker.getPriorityBand(100)).toBe("core");
    expect(ranker.getPriorityBand(80)).toBe("strong");
    expect(ranker.getPriorityBand(60)).toBe("normal");
    expect(ranker.getPriorityBand(20)).toBe("low");
    expect(ranker.getPriorityBand(0)).toBe("disabled");
  });
});
