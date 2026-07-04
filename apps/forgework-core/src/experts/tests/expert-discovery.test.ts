import { writeFile } from "node:fs/promises";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { ExpertDiscovery } from "../registry/ExpertDiscovery";
import { ExpertRegistry } from "../registry/ExpertRegistry";
import { createTempManifestDir, validManifest, writeManifest } from "./testUtils";

describe("Expert discovery", () => {
  it("finds .expert.json files and ignores unrelated files", async () => {
    const directory = await createTempManifestDir();
    await writeManifest(directory, "test-expert.expert.json", validManifest());
    await writeFile(path.join(directory, "notes.json"), "{}", "utf-8");

    const discovery = new ExpertDiscovery();
    const files = await discovery.discover([directory]);

    expect(files).toHaveLength(1);
    expect(files[0]?.fileName).toBe("test-expert.expert.json");
  });

  it("detects duplicate expert ids through loader report", async () => {
    const directory = await createTempManifestDir();
    await writeManifest(directory, "a.expert.json", validManifest({ id: "duplicate-expert" }));
    await writeManifest(directory, "b.expert.json", validManifest({ id: "duplicate-expert", name: "DuplicateExpertB" }));

    const registry = new ExpertRegistry([directory]);
    const report = await registry.load();

    expect(report.duplicateExpertIds).toHaveLength(1);
    expect(report.invalidManifests[0]?.errors[0]).toContain("Duplicate expert id");
  });
});
