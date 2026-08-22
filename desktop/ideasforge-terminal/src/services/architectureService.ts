import { apiClient } from "./apiClient";
import type {
  ArchitectureAnalyzeRequest,
  ArchitectureAnalyzeResponse,
  ArchitectureHealth,
  ArchitectureServiceStatus,
} from "../types/architecture";

const HEALTH_ROUTE =
  "/api/coding-agent/architecture-analyzer/health";
const ANALYZE_ROUTE =
  "/api/coding-agent/architecture-analyzer/analyze";

export const architectureService = {
  status: {
    state: "available",
    route: ANALYZE_ROUTE,
    message:
      "Existing IdeasForgeAI architecture analyzer route. Availability depends on the local backend.",
  } satisfies ArchitectureServiceStatus,

  getHealth(signal?: AbortSignal) {
    return apiClient.get<ArchitectureHealth>(HEALTH_ROUTE, { signal });
  },

  analyze(
    input: ArchitectureAnalyzeRequest,
    signal?: AbortSignal,
  ) {
    return apiClient.post<ArchitectureAnalyzeResponse>(
      ANALYZE_ROUTE,
      input,
      { signal },
    );
  },
};