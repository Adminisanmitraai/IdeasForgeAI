import manifest from "../manifests/forge-cad.expert.json";
import type { ExpertCapabilityRequest, ExpertImplementation, ExpertManifest } from "../types/ExpertManifest";

export class ForgeCADExpert implements ExpertImplementation {
  getManifest(): ExpertManifest {
    return manifest as ExpertManifest;
  }

  canHandle(request: ExpertCapabilityRequest): boolean {
    const currentManifest = this.getManifest();
    return Boolean(
      request.intent && currentManifest.supportedTasks.includes(request.intent)
      || request.requiredSkills?.some((skill) => currentManifest.skills.includes(skill))
      || request.capabilityTags?.some((tag) => currentManifest.capabilityTags.includes(tag))
    );
  }

  describeCapabilities(): string[] {
    const currentManifest = this.getManifest();
    return [
      ...currentManifest.supportedTasks,
      ...currentManifest.skills,
      ...currentManifest.capabilityTags
    ];
  }
}
