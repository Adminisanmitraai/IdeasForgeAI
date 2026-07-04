import manifest from "../manifests/forge-research.expert.json";
import type { ExpertCapabilityRequest, ExpertImplementation, ExpertManifest } from "../types/ExpertManifest";

export class ForgeResearchExpert implements ExpertImplementation {
  getManifest(): ExpertManifest {
    return manifest as ExpertManifest;
  }

  canHandle(request: ExpertCapabilityRequest): boolean {
    const currentManifest = this.getManifest();
    return Boolean(
      request.intent && currentManifest.supportedTasks.includes(request.intent)
      || request.requiredSkills?.some((skill) => currentManifest.skills.includes(skill))
      || request.desiredOutputTypes?.some((outputType) => currentManifest.outputTypes.includes(outputType))
    );
  }

  describeCapabilities(): string[] {
    const currentManifest = this.getManifest();
    return [
      ...currentManifest.supportedTasks,
      ...currentManifest.skills,
      ...currentManifest.outputTypes
    ];
  }
}
