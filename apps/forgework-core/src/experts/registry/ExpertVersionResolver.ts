import semver from "semver";

export class ExpertVersionResolver {
  isValidVersion(version: string): boolean {
    return semver.valid(version) !== null;
  }

  isCompatible(version: string, range: string): boolean {
    if (!this.isValidVersion(version)) return false;

    const normalizedRange = this.normalizeRange(range);
    return semver.satisfies(version, normalizedRange, { includePrerelease: false });
  }

  normalizeRange(range: string): string {
    const trimmed = range.trim();
    if (trimmed.startsWith("=")) {
      return trimmed.slice(1).trim();
    }

    if (semver.valid(trimmed)) {
      return trimmed;
    }

    return trimmed;
  }
}
