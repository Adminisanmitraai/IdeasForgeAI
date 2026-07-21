import { getTerminalApiConfig } from "./config";
import { transportFetch } from "./nativeHttpTransport";

export type FounderWorkspaceStatus =
  | "available"
  | "degraded"
  | "unavailable"
  | "planned";

export interface FounderWorkspaceRecord {
  workspace_id: string;
  title: string;
  domain: string;
  route: string;
  status: FounderWorkspaceStatus;
  read_only: boolean;
  capability_ids: string[];
  execution_boundary: string;
}

export interface FounderProgressRecord {
  overall_progress: number;
  current_milestone: string;
  show_progress: boolean;
  updated_at: string;
  source: "certified_manifest";
  contract_version: "founder-os-progress.v1";
}

export type FounderProgressResult =
  | {
      ok: true;
      progress: FounderProgressRecord;
    }
  | {
      ok: false;
      reason: string;
    };

export type FounderWorkspaceCatalogueResult =
  | { ok: true; workspaces: FounderWorkspaceRecord[] }
  | { ok: false; reason: string };

const WORKSPACES_PATH = "/api/founder-os/v1/workspaces";
const PROGRESS_PATH = "/api/founder-os/v1/progress";
const REQUEST_TIMEOUT_MS = 8_000;
const WORKSPACE_STATUSES = new Set<FounderWorkspaceStatus>([
  "available",
  "degraded",
  "unavailable",
  "planned",
]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function isPrivateHost(hostname: string): boolean {
  const normalized = hostname.toLowerCase();
  if (normalized.endsWith(".local")) return true;
  if (/^10\./.test(normalized) || /^192\.168\./.test(normalized)) return true;

  const match = normalized.match(/^172\.(\d{1,2})\./);
  return match !== null && Number(match[1]) >= 16 && Number(match[1]) <= 31;
}

function catalogueBaseUrl(): string {
  const configured = getTerminalApiConfig().baseUrl;

  try {
    const url = new URL(configured);
    const frontendHost = globalThis.location?.hostname ?? "";
    const backendIsLoopback = url.hostname === "127.0.0.1" || url.hostname === "localhost";

    if (backendIsLoopback && isPrivateHost(frontendHost)) {
      url.hostname = frontendHost;
    }

    return url.toString().replace(/\/+$/, "");
  } catch {
    return configured.replace(/\/+$/, "");
  }
}

function parseWorkspace(value: unknown): FounderWorkspaceRecord | null {
  if (!isRecord(value)) return null;

  const status = value.status;
  const capabilities = value.capability_ids;
  if (
    typeof value.workspace_id !== "string" ||
    typeof value.title !== "string" ||
    typeof value.domain !== "string" ||
    typeof value.route !== "string" ||
    !value.route.startsWith("/") ||
    typeof status !== "string" ||
    !WORKSPACE_STATUSES.has(status as FounderWorkspaceStatus) ||
    typeof value.read_only !== "boolean" ||
    !Array.isArray(capabilities) ||
    !capabilities.every((item) => typeof item === "string") ||
    typeof value.execution_boundary !== "string"
  ) {
    return null;
  }

  return {
    workspace_id: value.workspace_id,
    title: value.title,
    domain: value.domain,
    route: value.route,
    status: status as FounderWorkspaceStatus,
    read_only: value.read_only,
    capability_ids: [...capabilities],
    execution_boundary: value.execution_boundary,
  };
}

function parseFounderProgress(
  payload: unknown,
): FounderProgressRecord | null {
  if (
    !isRecord(payload) ||
    payload.ok !== true ||
    !isRecord(payload.data)
  ) {
    return null;
  }

  const data = payload.data;

  if (
    typeof data.overall_progress !== "number" ||
    !Number.isInteger(data.overall_progress) ||
    data.overall_progress < 0 ||
    data.overall_progress > 100 ||
    typeof data.current_milestone !== "string" ||
    data.current_milestone.trim().length === 0 ||
    typeof data.show_progress !== "boolean" ||
    typeof data.updated_at !== "string" ||
    Number.isNaN(Date.parse(data.updated_at)) ||
    data.source !== "certified_manifest" ||
    data.contract_version !== "founder-os-progress.v1"
  ) {
    return null;
  }

  return {
    overall_progress: data.overall_progress,
    current_milestone: data.current_milestone.trim(),
    show_progress: data.show_progress,
    updated_at: data.updated_at,
    source: "certified_manifest",
    contract_version: "founder-os-progress.v1",
  };
}


function parseCatalogue(payload: unknown): FounderWorkspaceRecord[] | null {
  if (!isRecord(payload) || payload.ok !== true || !isRecord(payload.data)) {
    return null;
  }

  const workspaces = payload.data.workspaces;
  if (!Array.isArray(workspaces)) return null;

  const parsed = workspaces.map(parseWorkspace);
  if (parsed.some((item) => item === null)) return null;

  return parsed as FounderWorkspaceRecord[];
}

export async function fetchFounderProgress():
  Promise<FounderProgressResult> {
  const controller = new AbortController();

  const timeout = globalThis.setTimeout(
    () => controller.abort(),
    REQUEST_TIMEOUT_MS,
  );

  const config = getTerminalApiConfig();

  const headers = new Headers({
    Accept: "application/json",
  });

  if (config.founderToken) {
    headers.set(
      "Authorization",
      `Bearer ${config.founderToken}`,
    );

    headers.set(
      "X-IF-Founder-Token",
      config.founderToken,
    );
  }

  try {
    const response = await transportFetch(
      `${catalogueBaseUrl()}${PROGRESS_PATH}`,
      {
        method: "GET",
        headers,
        signal: controller.signal,
      },
    );

    if (!response.ok) {
      return {
        ok: false,
        reason:
          `Founder progress request returned ${response.status}.`,
      };
    }

    const progress = parseFounderProgress(
      await response.json(),
    );

    return progress
      ? {
          ok: true,
          progress,
        }
      : {
          ok: false,
          reason:
            "Founder progress response did not match the certified contract.",
        };
  } catch {
    return {
      ok: false,
      reason: "Founder progress is unavailable.",
    };
  } finally {
    globalThis.clearTimeout(timeout);
  }
}


export async function fetchFounderWorkspaceCatalogue(): Promise<FounderWorkspaceCatalogueResult> {
  const controller = new AbortController();
  const timeout = globalThis.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  const config = getTerminalApiConfig();

  const headers = new Headers({
    Accept: "application/json",
  });

  if (config.founderToken) {
    headers.set(
      "Authorization",
      `Bearer ${config.founderToken}`,
    );

    headers.set(
      "X-IF-Founder-Token",
      config.founderToken,
    );
  }

  try {
    const response = await transportFetch(
      `${catalogueBaseUrl()}${WORKSPACES_PATH}`,
      {
        method: "GET",
        headers,
        signal: controller.signal,
      },
    );

    if (!response.ok) {
      return { ok: false, reason: `Catalogue request returned ${response.status}.` };
    }

    const workspaces = parseCatalogue(await response.json());
    return workspaces
      ? { ok: true, workspaces }
      : { ok: false, reason: "Catalogue response did not match the read-only contract." };
  } catch {
    return { ok: false, reason: "Founder OS catalogue is unavailable." };
  } finally {
    globalThis.clearTimeout(timeout);
  }
}
