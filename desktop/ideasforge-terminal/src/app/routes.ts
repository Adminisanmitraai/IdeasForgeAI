export type RouteId =
  | "dashboard"
  | "chat"
  | "coding"
  | "design"
  | "worker"
  | "work"
  | "browser"
  | "forge-structure"
  | "mobile"
  | "admin"
  | "projects"
  | "sessions"
  | "files"
  | "memory"
  | "agents"
  | "ghost-workspace"
  | "help"
  | "settings"
  | "project-settings"
  | "diff-review"
  | "preview"
  | "task";

export interface RouteDefinition {
  id: RouteId;
  path: string;
  label: string;
  nav: boolean;
}

export const routes: RouteDefinition[] = [
  { id: "dashboard", path: "/dashboard", label: "Founder OS", nav: false },
  { id: "chat", path: "/terminal", label: "Terminal", nav: false },
  { id: "coding", path: "/code", label: "Code", nav: false },
  { id: "worker", path: "/worker", label: "Worker", nav: false },
  { id: "design", path: "/studio", label: "Studio", nav: false },
  { id: "work", path: "/work", label: "Work", nav: false },
  { id: "browser", path: "/browser", label: "Browser", nav: false },
  {
    id: "forge-structure",
    path: "/forge-structure",
    label: "ForgeStructure",
    nav: false,
  },
  { id: "mobile", path: "/mobile", label: "Mobile", nav: false },
  { id: "admin", path: "/admin", label: "Admin", nav: false },
  { id: "chat", path: "/chat", label: "Chat", nav: true },
  { id: "coding", path: "/coding", label: "Coding", nav: true },
  { id: "design", path: "/design", label: "Design", nav: true },
  { id: "projects", path: "/projects", label: "Projects", nav: true },
  { id: "sessions", path: "/sessions", label: "Sessions", nav: true },
  { id: "files", path: "/files", label: "Files", nav: true },
  { id: "memory", path: "/memory", label: "Memory", nav: true },
  { id: "agents", path: "/agents", label: "Agents", nav: true },
  {
    id: "ghost-workspace",
    path: "/ghost-workspace",
    label: "Ghost Workspace",
    nav: true,
  },
  { id: "help", path: "/help", label: "Help", nav: true },
  { id: "settings", path: "/settings", label: "Settings", nav: false },
  {
    id: "project-settings",
    path: "/project-settings",
    label: "Project Settings",
    nav: false,
  },
  {
    id: "diff-review",
    path: "/diff-review",
    label: "Diff Review",
    nav: false,
  },
  { id: "preview", path: "/preview", label: "Preview", nav: false },
  { id: "task", path: "/task/:taskId", label: "Task", nav: false },
];

export interface ResolvedRoute {
  id: RouteId;
  path: string;
  params: Record<string, string>;
}

function normalizePath(path: string): string {
  const value = path.trim() || "/dashboard";
  return value.startsWith("/") ? value : `/${value}`;
}

export function resolveRoute(path: string): ResolvedRoute {
  const normalized = normalizePath(path);

  const taskMatch = normalized.match(/^\/task\/([^/]+)$/);
  if (taskMatch) {
    return {
      id: "task",
      path: normalized,
      params: { taskId: decodeURIComponent(taskMatch[1]) },
    };
  }

  const exact = routes.find((route) => route.path === normalized);
  if (exact) {
    return { id: exact.id, path: normalized, params: {} };
  }

  return { id: "dashboard", path: "/dashboard", params: {} };
}
