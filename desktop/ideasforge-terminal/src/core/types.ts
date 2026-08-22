export type ViewId =
  | "chat"
  | "coding"
  | "design"
  | "projects"
  | "sessions"
  | "files"
  | "memory"
  | "ghost"
  | "help";

export type OverlayId =
  | "project"
  | "mode"
  | "connection"
  | "search"
  | "notifications"
  | "profile"
  | "settings"
  | "project-settings"
  | "approval"
  | "diff"
  | "preview"
  | "task"
  | "ghost-full"
  | "confirm-delete"
  | null;

export type IntelligenceMode =
  | "Auto Intelligence"
  | "Fast"
  | "Deep"
  | "Private"
  | "Low Cost"
  | "Council"
  | "Specific Model";

export type ConnectionState = "Connected" | "Reconnecting" | "Offline";

export interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  text: string;
  card?: "plan" | "approval" | "completion" | "error" | "design" | "file";
}

export interface AppState {
  activeView: ViewId;
  activeProject: string;
  intelligenceMode: IntelligenceMode;
  connection: ConnectionState;
  leftCollapsed: boolean;
  rightCollapsed: boolean;
  overlay: OverlayId;
  expandedSections: Set<string>;
  chatMessages: ChatMessage[];
  composerValue: string;
  generating: boolean;
  terminalRunning: boolean;
  terminalMaximized: boolean;
  terminalLines: string[];
  approvalStatus: "pending" | "approved" | "rejected";
  codingTab: string;
  designTab: string;
  ghostMode: string;
  ghostRunning: boolean;
  toast: string;
}
