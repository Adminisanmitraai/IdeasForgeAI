import {
  fetchFounderWorkspaceCatalogue,
  type FounderWorkspaceStatus,
} from "../services/founderOsApi";

export type FounderModuleId =
  | "dashboard"
  | "terminal"
  | "code"
  | "worker"
  | "studio"
  | "work"
  | "browser"
  | "forge-structure"
  | "mobile"
  | "admin";

export type FounderModuleStatus = FounderWorkspaceStatus;

export const founderModuleStatusLabels: Record<FounderModuleStatus, string> = {
  available: "Available",
  degraded: "Degraded",
  unavailable: "Unavailable",
  planned: "Planned",
};

export type FounderCatalogueLoadState = "loading" | "ready" | "fallback";

export type FounderModuleIconKey =
  | "dashboard"
  | "terminal"
  | "code"
  | "worker"
  | "studio"
  | "work"
  | "browser"
  | "forge-structure"
  | "forge-structure"
  | "mobile"
  | "admin";

export interface FounderModuleDefinition {
  id: FounderModuleId;
  label: string;
  route: string;
  icon: FounderModuleIconKey;
  status: FounderModuleStatus;
  description: string;
  longDescription: string;
  futureCapability: string;
  relationships: readonly string[];
  dashboardPriority?: number;
  compatibilityRoutes: readonly string[];
  catalogueWorkspaceId?: string;
  readOnly?: boolean;
  capabilityIds?: readonly string[];
  executionBoundary?: string;
}

export const founderModules: readonly FounderModuleDefinition[] = [
  {
    id: "dashboard",
    label: "Founder OS",
    route: "/dashboard",
    icon: "dashboard",
    status: "available",
    description: "Founder dashboard and operating overview.",
    longDescription: "A private operating overview for navigating and shaping the IdeasForgeAI product system.",
    futureCapability: "Cross-module operating intelligence and Founder decision support.",
    relationships: ["Coordinates every Founder OS module."],
    compatibilityRoutes: [],
    catalogueWorkspaceId: "founder-os",
  },
  {
    id: "terminal",
    label: "Founder OS",
    route: "/terminal",
    icon: "terminal",
    status: "available",
    description: "Chat-first terminal workspace.",
    longDescription: "The conversational operating surface for directing work across trusted IdeasForgeAI capabilities.",
    futureCapability: "Deeper cross-module orchestration with explicit Founder control.",
    relationships: ["Directs Code, Worker, Studio, and future operational modules."],
    dashboardPriority: 4,
    compatibilityRoutes: [
      "/chat", "/projects", "/sessions", "/files", "/memory", "/agents",
      "/ghost-workspace", "/help", "/settings", "/project-settings",
      "/diff-review", "/preview",
    ],
    catalogueWorkspaceId: "terminal",
  },
  {
    id: "code", label: "Code", route: "/code", icon: "code", status: "available",
    description: "ForgeCode operating workspace.",
    longDescription: "Software engineering coordination for repositories, architecture, changes, tests, and review.",
    futureCapability: "End-to-end engineering plans, supervised execution, and delivery coordination.",
    relationships: ["Receives direction from Terminal and delegates controlled execution to Worker."],
    dashboardPriority: 2,
    compatibilityRoutes: ["/coding"],
    catalogueWorkspaceId: "forgecode",
  },
  {
    id: "worker", label: "Worker", route: "/worker", icon: "worker", status: "planned",
    description: "Future execution backbone.",
    longDescription: "The supervised execution backbone for safe, observable work across Founder OS.",
    futureCapability: "Queued jobs, execution plans, approvals, progress, evidence, and recovery controls.",
    relationships: ["Coordinates execution for Code and future operational modules."],
    dashboardPriority: 1,
    compatibilityRoutes: [],
    catalogueWorkspaceId: "worker",
  },
  {
    id: "studio", label: "Studio", route: "/studio", icon: "studio", status: "available",
    description: "ForgeStudio design workspace.",
    longDescription: "The visual product and interface design surface for IdeasForgeAI experiences.",
    futureCapability: "Design systems, concepts, prototypes, and structured handoff to Code.",
    relationships: ["Hands approved product and interface direction to Code."],
    compatibilityRoutes: ["/design"],
    catalogueWorkspaceId: "studio",
  },
  {
    id: "work", label: "Work", route: "/work", icon: "work", status: "planned",
    description: "Future professional intelligence workspace.",
    longDescription: "A professional intelligence surface for structured research, documents, analysis, and workflows.",
    futureCapability: "Research synthesis, professional deliverables, and repeatable operating workflows.",
    relationships: ["Uses Browser research and Worker execution under Founder direction."],
    compatibilityRoutes: [],
    catalogueWorkspaceId: "work",
  },
  {
    id: "browser", label: "Browser", route: "/browser", icon: "browser", status: "planned",
    description: "Future integrated browser and research workspace.",
    longDescription: "A controlled web research and browser-operations surface for Founder OS.",
    futureCapability: "Traceable research, supervised web operations, and evidence capture.",
    relationships: ["Supplies verified web context to Work, Terminal, and other modules."],
    compatibilityRoutes: [],
    catalogueWorkspaceId: "browser",
  },
  {
    id: "forge-structure",
    label: "ForgeStructure",
    route: "/forge-structure",
    icon: "forge-structure",
    status: "available",
    description: "Structural engineering and CAD workspace.",
    longDescription: "A controlled engineering workspace for structural geometry, loads, members, drawings, verification, and AutoCAD-compatible exports.",
    futureCapability: "Supervised structural analysis, member design, connections, foundations, fabrication packages, and controlled drawing generation.",
    relationships: [
      "Uses certified Forge Structure backend contracts and CAD generation.",
      "Exports controlled DXF packages for inspection in AutoCAD.",
      "Remains read-only until generation actions are explicitly connected.",
    ],
    dashboardPriority: 5,
    compatibilityRoutes: [],
    readOnly: true,
    capabilityIds: [
      "forge-structure-project-read",
      "forge-structure-cad-catalogue",
      "forge-structure-verification-read",
    ],
    executionBoundary: "read-only-ui-foundation",
  },
  {
    id: "mobile", label: "Mobile", route: "/mobile", icon: "mobile", status: "planned",
    description: "Future mobile connection and control surface.",
    longDescription: "Remote Founder access for monitoring, directing, reviewing, and approving work.",
    futureCapability: "Secure mobile oversight, alerts, approvals, and lightweight control.",
    relationships: ["Extends Founder OS oversight beyond the desktop shell."],
    compatibilityRoutes: [],
    catalogueWorkspaceId: "mobile",
  },
  {
    id: "admin", label: "Admin", route: "/admin", icon: "admin", status: "planned",
    description: "Governance and business control plane.",
    longDescription: "The governance surface for policy, permissions, providers, billing, security, audit, and support.",
    futureCapability: "Centralized governance, risk controls, provider administration, and audit visibility.",
    relationships: ["Governs Worker execution and cross-module operating policy."],
    dashboardPriority: 3,
    compatibilityRoutes: [],
  },
] as const;

let catalogueLoadState: FounderCatalogueLoadState = "loading";
let catalogueFailureReason = "";
let catalogueRequest: Promise<void> | null = null;
const catalogueListeners = new Set<() => void>();

function emitCatalogueChange(): void {
  catalogueListeners.forEach((listener) => listener());
}

export function getFounderNavigationModules(): readonly FounderModuleDefinition[] {
  return founderModules.filter((module) => module.id !== "admin");
}

export function getFounderCatalogueState(): Readonly<{
  status: FounderCatalogueLoadState;
  reason: string;
}> {
  return { status: catalogueLoadState, reason: catalogueFailureReason };
}

export function subscribeFounderCatalogue(listener: () => void): () => void {
  catalogueListeners.add(listener);
  return () => catalogueListeners.delete(listener);
}

export function initializeFounderCatalogue(): Promise<void> {
  if (catalogueRequest) return catalogueRequest;

  catalogueRequest = fetchFounderWorkspaceCatalogue().then((result) => {
    if (!result.ok) {
      catalogueLoadState = "fallback";
      catalogueFailureReason = result.reason;
      emitCatalogueChange();
      return;
    }

    const records = new Map(
      result.workspaces.map((workspace) => [workspace.workspace_id, workspace]),
    );

    getFounderNavigationModules().forEach((module) => {
      const record = module.catalogueWorkspaceId
        ? records.get(module.catalogueWorkspaceId)
        : undefined;

      if (!record) {
        module.status = "unavailable";
        module.readOnly = true;
        module.capabilityIds = [];
        module.executionBoundary = "unavailable";
        return;
      }

      module.status = record.status;
      module.readOnly = record.read_only;
      module.capabilityIds = [...record.capability_ids];
      module.executionBoundary = record.execution_boundary;
    });

    catalogueLoadState = "ready";
    catalogueFailureReason = "";
    emitCatalogueChange();
  });

  return catalogueRequest;
}

export function getFounderModuleStatusLabel(
  module: FounderModuleDefinition,
): string {
  return founderModuleStatusLabels[module.status];
}

function normalizeModulePath(path: string): string {
  const normalized = path.trim().split(/[?#]/, 1)[0] || "/dashboard";
  const withSlash = normalized.startsWith("/") ? normalized : `/${normalized}`;
  return withSlash.length > 1 ? withSlash.replace(/\/+$/, "") : withSlash;
}

export function resolveFounderModule(path: string): FounderModuleDefinition {
  const normalized = normalizeModulePath(path);

  if (normalized.startsWith("/task/")) {
    return founderModules.find((module) => module.id === "terminal")!;
  }

  return founderModules.find(
    (module) => module.route === normalized || module.compatibilityRoutes.includes(normalized),
  ) ?? founderModules[0];
}
