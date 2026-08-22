export type IconName =
  | "menu"
  | "dashboard"
  | "terminal"
  | "code"
  | "worker"
  | "studio"
  | "work"
  | "browser"
  | "forge-structure"
  | "mobile"
  | "admin"
  | "chat"
  | "coding"
  | "design"
  | "projects"
  | "sessions"
  | "files"
  | "memory"
  | "agents"
  | "ghost"
  | "help"
  | "search"
  | "bell"
  | "settings"
  | "collapse"
  | "context";

const paths: Record<IconName, string> = {
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  dashboard: '<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><rect x="14" y="14" width="6" height="6" rx="1"/>',
  terminal: '<rect x="3.5" y="5" width="17" height="14" rx="2"/><path d="m7 9 3 3-3 3M12.5 15H17"/>',
  code: '<path d="m8 8-4 4 4 4M16 8l4 4-4 4M14 5l-4 14"/>',
  worker: '<circle cx="12" cy="12" r="3"/><path d="M12 3.5v2M12 18.5v2M3.5 12h2M18.5 12h2M6 6l1.4 1.4M16.6 16.6 18 18M18 6l-1.4 1.4M7.4 16.6 6 18"/>',
  studio: '<path d="M12 3a9 9 0 1 0 0 18h1.4a1.6 1.6 0 0 0 0-3.2H12a2 2 0 0 1 0-4h2.8A6.2 6.2 0 0 0 21 7.6C21 5 17 3 12 3Z"/><circle cx="7.5" cy="10" r=".7"/><circle cx="10" cy="6.8" r=".7"/><circle cx="14" cy="6.5" r=".7"/>',
  work: '<rect x="3.5" y="7" width="17" height="12" rx="2"/><path d="M9 7V5h6v2M3.5 12h17M10 12v2h4v-2"/>',
  browser: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.2 3 14.8 0 18M12 3c-3 3.2-3 14.8 0 18"/>',
  "forge-structure": '<path d="M4 20V8l8-5 8 5v12"/><path d="M4 9h16M7 20v-7h10v7M9 13l3-3 3 3"/>',
  mobile: '<rect x="7" y="2.5" width="10" height="19" rx="2"/><path d="M10 5h4M11 18.5h2"/>',
  admin: '<path d="M12 3 19 6v5c0 4.6-2.7 7.8-7 10-4.3-2.2-7-5.4-7-10V6l7-3Z"/><path d="M9 12l2 2 4-4"/>',
  chat: '<path d="M7 16.5 4 20v-4.2A8 8 0 1 1 20 12"/><path d="M8 10h8M8 14h5"/>',
  coding: '<path d="m8 9-4 3 4 3M16 9l4 3-4 3M14 5l-4 14"/>',
  design: '<path d="m4 20 4.5-1 9.7-9.7a2.1 2.1 0 0 0-3-3L5.5 16 4 20Z"/><path d="m13.8 7.8 2.4 2.4"/>',
  projects: '<path d="M3.5 7.5h6l2-2h9v13h-17z"/><path d="M3.5 9.5h17"/>',
  sessions: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3.5 2"/>',
  files: '<path d="M6 3.5h8l4 4v13H6z"/><path d="M14 3.5v4h4"/>',
  memory: '<path d="M8 6.5a4 4 0 0 1 8 0v1a3 3 0 0 1 2 2.8v3.4a3 3 0 0 1-2 2.8v1a4 4 0 0 1-8 0v-1a3 3 0 0 1-2-2.8v-3.4a3 3 0 0 1 2-2.8z"/>',
  agents: '<rect x="6" y="8" width="12" height="9" rx="2"/><path d="M9 4h6v4M9 12h.01M15 12h.01M9 20v-3M15 20v-3"/>',
  ghost: '<path d="M6 19V9a6 6 0 0 1 12 0v10l-3-2-3 2-3-2-3 2Z"/>',
  help: '<circle cx="12" cy="12" r="9"/><path d="M9.8 9a2.4 2.4 0 1 1 3.2 2.3c-.8.3-1 1-1 1.7M12 17h.01"/>',
  search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 4 4"/>',
  bell: '<path d="M6.5 17h11l-1.2-1.8V11a4.3 4.3 0 0 0-8.6 0v4.2z"/><path d="M10 19.5h4"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1l2-1.5-2-3.5-2.4 1A7 7 0 0 0 15 6l-.3-2.5h-4L10.5 6A7 7 0 0 0 9 7L6.5 6 4.5 9.5 6.5 11a7 7 0 0 0 0 2l-2 1.5 2 3.5 2.5-1a7 7 0 0 0 1.5 1l.3 2.5h4L15 18a7 7 0 0 0 1.5-1l2.4 1 2-3.5-2-1.5a7 7 0 0 0 .1-1Z"/>',
  collapse: '<path d="M5 4h14v16H5zM10 4v16"/><path d="m15 9-3 3 3 3"/>',
  context: '<path d="M5 4h14v16H5z"/><path d="M8 8h8M8 12h8M8 16h5"/>',
};

export function icon(name: IconName): string {
  return `<svg class="ui-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name]}</svg>`;
}
