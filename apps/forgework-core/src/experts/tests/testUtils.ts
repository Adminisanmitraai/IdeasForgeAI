import { mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import type { ExpertManifest } from "../types/ExpertManifest";

export async function createTempManifestDir(): Promise<string> {
  return mkdtemp(path.join(tmpdir(), "fw-expert-4a-"));
}

export async function writeManifest(directory: string, fileName: string, manifest: unknown): Promise<void> {
  await writeFile(path.join(directory, fileName), JSON.stringify(manifest, null, 2), "utf-8");
}

export function validManifest(overrides: Partial<ExpertManifest> = {}): ExpertManifest {
  return {
    id: "test-expert",
    name: "TestExpert",
    version: "1.0.0",
    description: "Valid test expert manifest.",
    category: "general-professional",
    priority: 75,
    status: "active",
    skills: ["test-skill", "planning"],
    supportedTasks: ["test-task"],
    requiredSoftware: [],
    desktopPermissions: {
      requiresDesktop: false,
      canUseForgePilot: true,
      allowedActions: ["screen-preview"],
      blockedActions: ["delete-files", "send-email", "make-payment"]
    },
    approvalRequirements: {
      requiresUserApprovalBeforeExecution: true,
      requiresUserApprovalBeforeDesktopAction: true,
      requiresUserApprovalBeforeFileWrite: true,
      requiresUserApprovalBeforeExternalSend: true
    },
    outputTypes: ["plan", "report"],
    dependencies: [],
    capabilityTags: ["test", "professional"],
    examples: ["Run a valid expert test."],
    ...overrides
  };
}
