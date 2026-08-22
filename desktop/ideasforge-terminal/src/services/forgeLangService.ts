import type { ServiceState } from "../types/api";
import type { ForgeLangBlueprint } from "../types/forgeLang";

export interface ForgeLangServiceDescriptor {
  state: ServiceState;
  message: string;
}

export const forgeLangService = {
  descriptor: {
    state: "mocked",
    message:
      "Frontend contract only. No real ForgeLang backend route is connected yet.",
  } satisfies ForgeLangServiceDescriptor,

  async createMockBlueprint(
    objective: string,
    projectId = "local-project",
  ): Promise<ForgeLangBlueprint> {
    return {
      contractVersion: "forgecode.repository.v1",
      projectId,
      intent: "build_software",
      objective,
      mode: "auto",
      requiredCapabilities: [
        "project-context",
        "architecture-analysis",
        "code-generation",
        "quality-validation",
      ],
      selectedAgents: [
        "Intent Router",
        "Architecture Analyzer",
        "ForgeCode",
        "Quality Validator",
      ],
      tasks: [
        {
          id: "understand",
          title: "Understand the requested outcome",
          status: "ready",
          dependencies: [],
        },
        {
          id: "plan",
          title: "Prepare a structured implementation plan",
          status: "pending",
          dependencies: ["understand"],
        },
      ],
      approvals: [
        {
          id: "write-approval",
          action: "Write project files",
          level: "explicit",
          reason: "File modifications require user approval.",
        },
      ],
      expectedOutputs: [
        {
          type: "plan",
          description: "Validated implementation plan",
        },
      ],
      constraints: [
        "No unrestricted shell access",
        "No Git push without explicit approval",
        "No deployment without explicit approval",
      ],
    };
  },
};