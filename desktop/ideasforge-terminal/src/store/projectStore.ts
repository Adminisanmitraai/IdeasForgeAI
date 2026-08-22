import { selectTrustedWorkspace } from "../workspace/workspaceRegistry";
import { workspaceStore } from "../workspace/workspaceStore";
import type { TrustedWorkspaceRecord } from "../workspace/types";

export interface ProjectSummary {
  id: string;
  workspaceId: string;
  name: string;
  projectRoot: string;
  approvedRoot: string;
  repository?: string;
  branch?: string;
  environment: string;
  trustState: "trusted";
  lastOpenedAt?: string;
  metadata: Record<string, unknown>;
}

type Listener = (project: ProjectSummary | null) => void;
const listeners = new Set<Listener>();

function asProject(workspace: TrustedWorkspaceRecord): ProjectSummary {
  return {
    id: workspace.projectId,
    workspaceId: workspace.workspaceId,
    name: workspace.displayName,
    projectRoot: workspace.projectRoot,
    approvedRoot: workspace.approvedRoot,
    repository: workspace.repository,
    branch: workspace.branch,
    environment: workspace.environment,
    trustState: workspace.trustState,
    lastOpenedAt: workspace.lastOpenedAt,
    metadata: workspace.metadata,
  };
}

export const projectStore = {
  getProjects(): ProjectSummary[] {
    return workspaceStore.getState().workspaces.map(asProject);
  },

  getActiveProject(): ProjectSummary | null {
    const workspace = workspaceStore.getCurrentWorkspace();
    return workspace ? asProject(workspace) : null;
  },

  async setActiveProject(projectId: string): Promise<void> {
    const project = this.getProjects().find((item) => item.id === projectId);
    if (!project) return;
    workspaceStore.completeLoad(await selectTrustedWorkspace(project.workspaceId));
  },

  subscribe(listener: Listener): () => void {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
};

workspaceStore.subscribe(() => {
  const project = projectStore.getActiveProject();
  listeners.forEach((listener) => listener(project));
});
