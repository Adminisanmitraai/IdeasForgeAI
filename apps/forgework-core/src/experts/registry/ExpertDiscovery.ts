import { readdir, stat } from "node:fs/promises";
import path from "node:path";
import { ExpertDiscoveryError } from "./ExpertRegistryErrors";

export interface DiscoveredExpertManifestFile {
  filePath: string;
  fileName: string;
}

export class ExpertDiscovery {
  async discover(manifestDirectories: string[]): Promise<DiscoveredExpertManifestFile[]> {
    const files: DiscoveredExpertManifestFile[] = [];

    for (const directory of manifestDirectories) {
      const absoluteDirectory = path.resolve(directory);
      await this.collectManifestFiles(absoluteDirectory, files);
    }

    return files.sort((a, b) => a.filePath.localeCompare(b.filePath));
  }

  private async collectManifestFiles(directory: string, files: DiscoveredExpertManifestFile[]): Promise<void> {
    try {
      const directoryStat = await stat(directory);
      if (!directoryStat.isDirectory()) {
        throw new ExpertDiscoveryError(`Manifest path is not a directory: ${directory}`, directory);
      }
    } catch (error) {
      if (error instanceof ExpertDiscoveryError) throw error;
      throw new ExpertDiscoveryError(`Manifest directory cannot be read: ${directory}`, directory);
    }

    const entries = await readdir(directory, { withFileTypes: true });

    for (const entry of entries) {
      const entryPath = path.join(directory, entry.name);

      if (entry.isDirectory()) {
        await this.collectManifestFiles(entryPath, files);
        continue;
      }

      if (entry.isFile() && entry.name.endsWith(".expert.json")) {
        files.push({ filePath: entryPath, fileName: entry.name });
      }
    }
  }
}
