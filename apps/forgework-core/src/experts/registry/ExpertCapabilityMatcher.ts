import type { ExpertMatchInput, ExpertMatchResult } from "../types/ExpertCapability";
import type { ExpertManifest } from "../types/ExpertManifest";
import { ExpertPriorityRanker } from "./ExpertPriorityRanker";

export class ExpertCapabilityMatcher {
  private readonly priorityRanker = new ExpertPriorityRanker();

  constructor(private readonly experts: ExpertManifest[]) {}

  match(input: ExpertMatchInput): ExpertMatchResult[] {
    const normalizedInput = this.normalizeInput(input);

    const results = this.experts
      .filter((expert) => this.isEligible(expert, normalizedInput))
      .map((expert) => this.scoreExpert(expert, normalizedInput))
      .filter((result) => result.score > 0 || normalizedInput.directExpertId === result.expertId)
      .sort((a, b) => {
        if (b.score !== a.score) return b.score - a.score;
        if (b.expert.priority !== a.expert.priority) return b.expert.priority - a.expert.priority;
        return a.expert.name.localeCompare(b.expert.name);
      });

    return results;
  }

  private scoreExpert(expert: ExpertManifest, input: Required<ExpertMatchInput>): ExpertMatchResult {
    let score = 0;
    const reasons: string[] = [];
    const missingCapabilities: string[] = [];

    const supportedTasks = new Set(expert.supportedTasks.map(this.normalize));
    const skills = new Set(expert.skills.map(this.normalize));
    const capabilityTags = new Set(expert.capabilityTags.map(this.normalize));
    const outputTypes = new Set(expert.outputTypes.map(this.normalize));
    const softwareNames = new Set(input.softwareContext.map(this.normalize));

    if (input.intent && supportedTasks.has(this.normalize(input.intent))) {
      score += 40;
      reasons.push(`Supported task matched ${input.intent}.`);
    } else if (input.intent) {
      missingCapabilities.push(`task:${input.intent}`);
    }

    if (input.requiredSkills.length > 0) {
      const matchedSkills = input.requiredSkills.filter((skill) => skills.has(this.normalize(skill)));
      score += (matchedSkills.length / input.requiredSkills.length) * 25;
      if (matchedSkills.length > 0) reasons.push(`Matched ${matchedSkills.length} required skill(s).`);
      for (const missingSkill of input.requiredSkills.filter((skill) => !skills.has(this.normalize(skill)))) {
        missingCapabilities.push(`skill:${missingSkill}`);
      }
    }

    if (input.capabilityTags.length > 0) {
      const matchedTags = input.capabilityTags.filter((tag) => capabilityTags.has(this.normalize(tag)));
      score += (matchedTags.length / input.capabilityTags.length) * 15;
      if (matchedTags.length > 0) reasons.push(`Matched ${matchedTags.length} capability tag(s).`);
      for (const missingTag of input.capabilityTags.filter((tag) => !capabilityTags.has(this.normalize(tag)))) {
        missingCapabilities.push(`capabilityTag:${missingTag}`);
      }
    }

    if (input.desiredOutputTypes.length > 0) {
      const matchedOutputTypes = input.desiredOutputTypes.filter((outputType) => outputTypes.has(this.normalize(outputType)));
      score += (matchedOutputTypes.length / input.desiredOutputTypes.length) * 10;
      if (matchedOutputTypes.length > 0) reasons.push(`Matched ${matchedOutputTypes.length} desired output type(s).`);
      for (const missingOutputType of input.desiredOutputTypes.filter((outputType) => !outputTypes.has(this.normalize(outputType)))) {
        missingCapabilities.push(`outputType:${missingOutputType}`);
      }
    }

    if (expert.requiredSoftware.length === 0) {
      score += 5;
      reasons.push("No required software dependency.");
    } else {
      const requiredSoftware = expert.requiredSoftware.filter((software) => software.required);
      const optionalSoftware = expert.requiredSoftware.filter((software) => !software.required);
      const allRequiredAvailable = requiredSoftware.every((software) => softwareNames.has(this.normalize(software.name)));
      const optionalAvailable = optionalSoftware.some((software) => softwareNames.has(this.normalize(software.name)));

      if (allRequiredAvailable) {
        score += optionalAvailable || requiredSoftware.length > 0 ? 5 : 3;
        reasons.push("Software context is compatible.");
      } else {
        for (const software of requiredSoftware.filter((item) => !softwareNames.has(this.normalize(item.name)))) {
          missingCapabilities.push(`software:${software.name}`);
        }
      }
    }

    const priorityBoost = this.priorityRanker.getPriorityBoost(expert.priority);
    if (priorityBoost > 0) {
      score += priorityBoost;
      reasons.push(`Priority boost applied (${this.priorityRanker.getPriorityBand(expert.priority)} expert).`);
    }

    if (input.directExpertId && this.normalize(input.directExpertId) === this.normalize(expert.id)) {
      score = Math.max(score, 70);
      reasons.push("Direct expert request matched.");
    }

    const requiresApproval = Object.values(expert.approvalRequirements).some(Boolean);

    return {
      expertId: expert.id,
      expert,
      score: Math.min(100, Math.round(score)),
      reasons,
      missingCapabilities,
      requiresApproval
    };
  }

  private isEligible(expert: ExpertManifest, input: Required<ExpertMatchInput>): boolean {
    if (expert.priority === 0 && this.normalize(input.directExpertId) !== this.normalize(expert.id)) return false;
    if (expert.status === "active") return true;
    if (expert.status === "experimental") return input.includeExperimental;
    if (expert.status === "deprecated") return input.includeDeprecated;
    if (expert.status === "disabled") return input.includeDisabled && this.normalize(input.directExpertId) === this.normalize(expert.id);
    return false;
  }

  private normalizeInput(input: ExpertMatchInput): Required<ExpertMatchInput> {
    return {
      intent: input.intent ?? "",
      requiredSkills: input.requiredSkills ?? [],
      desiredOutputTypes: input.desiredOutputTypes ?? [],
      capabilityTags: input.capabilityTags ?? [],
      softwareContext: input.softwareContext ?? [],
      riskLevel: input.riskLevel ?? "low",
      directExpertId: input.directExpertId ?? "",
      includeExperimental: input.includeExperimental ?? false,
      includeDeprecated: input.includeDeprecated ?? false,
      includeDisabled: input.includeDisabled ?? false
    };
  }

  private normalize(value: string): string {
    return value.trim().toLowerCase();
  }
}
