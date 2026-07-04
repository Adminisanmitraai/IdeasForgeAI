export class ExpertRegistryError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ExpertRegistryError";
  }
}

export class ExpertManifestValidationError extends ExpertRegistryError {
  constructor(
    message: string,
    public readonly filePath?: string,
    public readonly validationErrors: string[] = []
  ) {
    super(message);
    this.name = "ExpertManifestValidationError";
  }
}

export class ExpertDiscoveryError extends ExpertRegistryError {
  constructor(message: string, public readonly directory?: string) {
    super(message);
    this.name = "ExpertDiscoveryError";
  }
}
