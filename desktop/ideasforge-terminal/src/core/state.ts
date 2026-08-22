import type { AppState } from "./types";
import { terminalSeed } from "./mock-data";

export const state: AppState = {
  activeView: "chat",
  activeProject: "Website Redesign",
  intelligenceMode: "Auto Intelligence",
  connection: "Connected",
  leftCollapsed: false,
  rightCollapsed: false,
  overlay: null,
  expandedSections: new Set(["context", "plan", "approval"]),
  chatMessages: [
    {
      id: 1,
      role: "user",
      text: "Build a modern landing page for IdeasForgeAI with a hero section, feature grid, and footer. Use dark mode with purple accents.",
    },
    {
      id: 2,
      role: "assistant",
      text: "Great. I’ll plan the structure, generate the code, and create a matching design. Here is the plan and current progress.",
      card: "plan",
    },
  ],
  composerValue: "",
  generating: false,
  terminalRunning: false,
  terminalMaximized: false,
  terminalLines: [...terminalSeed],
  approvalStatus: "pending",
  codingTab: "Overview",
  designTab: "Web page",
  ghostMode: "Supervised",
  ghostRunning: true,
  toast: "",
};
