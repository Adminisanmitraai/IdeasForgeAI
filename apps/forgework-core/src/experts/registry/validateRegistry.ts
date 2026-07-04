import path from "node:path";
import { ExpertRegistry } from "./ExpertRegistry";

async function main(): Promise<void> {
  const manifestDirectory = path.resolve(__dirname, "../manifests");
  const registry = new ExpertRegistry([manifestDirectory]);
  const report = await registry.load();

  console.log(JSON.stringify(report.health, null, 2));

  if (report.invalidManifests.length > 0 || !report.dependencyResolution.valid) {
    console.error("Registry validation failed.");
    console.error(JSON.stringify({
      invalidManifests: report.invalidManifests,
      dependencyResolution: report.dependencyResolution
    }, null, 2));
    process.exitCode = 1;
  }
}

void main();
