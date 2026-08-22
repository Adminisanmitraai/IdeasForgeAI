import type { ServiceState } from "../types/api";

export interface ServiceRegistryEntry {
  id: string;
  state: ServiceState;
  currentRoute?: string;
  description: string;
}

export const serviceRegistry: ServiceRegistryEntry[] = [
  {
    id: "architecture",
    state: "available",
    currentRoute:
      "/api/coding-agent/architecture-analyzer/analyze",
    description:
      "Existing backend architecture analyzer route.",
  },
  {
    id: "chat",
    state: "available",
    currentRoute: "/api/home-chat",
    description:
      "Existing IdeasForgeAI home-chat backend route.",
  },
  {
    id: "forgeLang",
    state: "mocked",
    description:
      "Typed frontend blueprint contract only.",
  },
  {
    id: "orchestrator",
    state: "available",
    description:
      "Future backend planning and orchestration route.",
  },
  {
    id: "agents",
    state: "available",
    description:
      "Agent registry and health route must be confirmed.",
  },
  {
    id: "git",
    state: "mocked",
    description:
      "UI-only state. No Git token or direct push logic in frontend.",
  },
  {
    id: "deployment",
    state: "mocked",
    description:
      "UI-only state. No deployment secret or direct deploy logic.",
  },
];