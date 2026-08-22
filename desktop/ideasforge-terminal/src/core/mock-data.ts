export const projects = [
  { name: "Website Redesign", type: "Connected repository", health: 94, activity: "2 minutes ago", pinned: true },
  { name: "IdeasForge Terminal", type: "Local workspace", health: 91, activity: "Today", pinned: true },
  { name: "Convera", type: "Connected repository", health: 89, activity: "Yesterday", pinned: false },
  { name: "ForgeStudio Mobile", type: "Cloud project", health: 83, activity: "3 days ago", pinned: false },
];

export const notifications = [
  { title: "Preview is ready", detail: "Website Redesign is running at localhost:5173", time: "Now" },
  { title: "Approval required", detail: "4 file changes are ready for review", time: "4m" },
  { title: "Tests passed", detail: "95 Convera tests completed successfully", time: "18m" },
];

export const sessions = [
  { name: "Landing page refinement", state: "Running", branch: "main", time: "12m" },
  { name: "Mobile navigation patch", state: "Paused", branch: "ui/mobile", time: "42m" },
  { name: "Convera audit", state: "Completed", branch: "convera/audit", time: "Yesterday" },
  { name: "Dependency repair", state: "Failed", branch: "fix/deps", time: "2 days" },
];

export const fileRows = [
  { name: "src/main.ts", type: "TypeScript", size: "18 KB", changed: "Now" },
  { name: "src/styles.css", type: "CSS", size: "31 KB", changed: "Now" },
  { name: "package.json", type: "JSON", size: "2 KB", changed: "Today" },
  { name: "src-tauri/tauri.conf.json", type: "JSON", size: "1 KB", changed: "Today" },
  { name: "README.md", type: "Markdown", size: "6 KB", changed: "Yesterday" },
];

export const memories = [
  { title: "Project conventions", detail: "Use deterministic PowerShell patches and preserve unrelated files.", pinned: true },
  { title: "Architecture decision", detail: "IdeasForge Terminal uses Tauri v2 with a modular TypeScript frontend.", pinned: true },
  { title: "User preference", detail: "Keep the center workspace dominant and approvals explicit.", pinned: false },
  { title: "Successful fix", detail: "Use a clean Tauri config overwrite when Windows PowerShell JSON parsing fails.", pinned: false },
  { title: "Saved instruction", detail: "Do not commit, push, or deploy before review.", pinned: true },
];

export const terminalSeed = [
  '<span class="term-command">$ ift scan repository --safe</span>',
  '<span class="term-success">✓ Repository indexed · 184 files</span>',
  '<span class="term-command">$ ift analyze architecture</span>',
  '<span class="term-success">✓ Architecture context ready</span>',
  '<span class="term-command">$ ift test --scope frontend</span>',
  '<span class="term-success">✓ 24 interface checks passed</span>',
  '<span class="term-link">● Preview server ready at http://localhost:5173</span>',
  '<span class="term-wait">◉ Waiting for approval to apply 4 file changes…</span>',
];

export const rightPlan = [
  { label: "Project setup", state: "done" },
  { label: "Build components", state: "done" },
  { label: "Style & responsive", state: "done" },
  { label: "Preview & refine", state: "active" },
];

export const intelligenceModes = [
  "Auto Intelligence",
  "Fast",
  "Deep",
  "Private",
  "Low Cost",
  "Council",
  "Specific Model",
] as const;

export const quickExamples = [
  "Build a dashboard",
  "Fix this bug",
  "Create a landing page",
  "Design a mobile app",
  "Organize my files",
  "Operate my computer",
];
