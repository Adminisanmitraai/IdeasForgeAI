import type {
  ExpertApprovalRequirements,
  ExpertDependency,
  ExpertDesktopPermissions,
  ExpertManifest,
  ExpertSoftwareRequirement,
  ExpertStatus
} from "../types/ExpertManifest";
import { ExpertVersionResolver } from "./ExpertVersionResolver";

export interface ManifestValidationResult {
  valid: boolean;
  errors: string[];
}

const VALID_STATUSES: ExpertStatus[] = ["active", "experimental", "deprecated", "disabled"];

export class ExpertManifestValidator {
  private readonly versionResolver = new ExpertVersionResolver();

  validate(input: unknown): ManifestValidationResult {
    const errors: string[] = [];

    if (!this.isObject(input)) {
      return { valid: false, errors: ["Manifest must be a JSON object."] };
    }

    const manifest = input as Partial<ExpertManifest>;

    this.requireString(manifest.id, "id", errors);
    this.requireString(manifest.name, "name", errors);
    this.requireString(manifest.version, "version", errors);
    this.requireString(manifest.description, "description", errors);
    this.requireString(manifest.category, "category", errors);

    if (typeof manifest.version === "string" && !this.versionResolver.isValidVersion(manifest.version)) {
      errors.push(`version must be valid semver. Received: ${manifest.version}`);
    }

    if (typeof manifest.priority !== "number" || !Number.isInteger(manifest.priority)) {
      errors.push("priority must be an integer from 0 to 100.");
    } else if (manifest.priority < 0 || manifest.priority > 100) {
      errors.push("priority must be between 0 and 100.");
    }

    if (!VALID_STATUSES.includes(manifest.status as ExpertStatus)) {
      errors.push(`status must be one of: ${VALID_STATUSES.join(", ")}.`);
    }

    this.requireStringArray(manifest.skills, "skills", errors);
    this.requireStringArray(manifest.supportedTasks, "supportedTasks", errors);
    this.requireStringArray(manifest.outputTypes, "outputTypes", errors);
    this.requireStringArray(manifest.capabilityTags, "capabilityTags", errors);
    this.requireStringArray(manifest.examples, "examples", errors);

    this.validateRequiredSoftware(manifest.requiredSoftware, errors);
    this.validateDesktopPermissions(manifest.desktopPermissions, errors);
    this.validateApprovalRequirements(manifest.approvalRequirements, errors);
    this.validateDependencies(manifest.dependencies, errors);

    return { valid: errors.length === 0, errors };
  }

  assertValid(input: unknown): asserts input is ExpertManifest {
    const result = this.validate(input);
    if (!result.valid) {
      throw new Error(`Invalid expert manifest: ${result.errors.join("; ")}`);
    }
  }

  private validateRequiredSoftware(input: unknown, errors: string[]): void {
    if (!Array.isArray(input)) {
      errors.push("requiredSoftware must be an array.");
      return;
    }

    input.forEach((item, index) => {
      if (!this.isObject(item)) {
        errors.push(`requiredSoftware[${index}] must be an object.`);
        return;
      }
      const sw = item as Partial<ExpertSoftwareRequirement>;
      this.requireString(sw.name, `requiredSoftware[${index}].name`, errors);
      this.requireBoolean(sw.required, `requiredSoftware[${index}].required`, errors);
      if (sw.minimumVersion !== undefined && sw.minimumVersion !== null && typeof sw.minimumVersion !== "string") {
        errors.push(`requiredSoftware[${index}].minimumVersion must be string or null.`);
      }
    });
  }

  private validateDesktopPermissions(input: unknown, errors: string[]): void {
    if (!this.isObject(input)) {
      errors.push("desktopPermissions must be an object.");
      return;
    }

    const permissions = input as Partial<ExpertDesktopPermissions>;
    this.requireBoolean(permissions.requiresDesktop, "desktopPermissions.requiresDesktop", errors);
    this.requireBoolean(permissions.canUseForgePilot, "desktopPermissions.canUseForgePilot", errors);
    this.requireStringArray(permissions.allowedActions, "desktopPermissions.allowedActions", errors);
    this.requireStringArray(permissions.blockedActions, "desktopPermissions.blockedActions", errors);
  }

  private validateApprovalRequirements(input: unknown, errors: string[]): void {
    if (!this.isObject(input)) {
      errors.push("approvalRequirements must be an object.");
      return;
    }

    const approval = input as Partial<ExpertApprovalRequirements>;
    this.requireBoolean(approval.requiresUserApprovalBeforeExecution, "approvalRequirements.requiresUserApprovalBeforeExecution", errors);
    this.requireBoolean(approval.requiresUserApprovalBeforeDesktopAction, "approvalRequirements.requiresUserApprovalBeforeDesktopAction", errors);
    this.requireBoolean(approval.requiresUserApprovalBeforeFileWrite, "approvalRequirements.requiresUserApprovalBeforeFileWrite", errors);
    this.requireBoolean(approval.requiresUserApprovalBeforeExternalSend, "approvalRequirements.requiresUserApprovalBeforeExternalSend", errors);
  }

  private validateDependencies(input: unknown, errors: string[]): void {
    if (!Array.isArray(input)) {
      errors.push("dependencies must be an array.");
      return;
    }

    input.forEach((item, index) => {
      if (!this.isObject(item)) {
        errors.push(`dependencies[${index}] must be an object.`);
        return;
      }
      const dependency = item as Partial<ExpertDependency>;
      this.requireString(dependency.expertId, `dependencies[${index}].expertId`, errors);
      this.requireString(dependency.versionRange, `dependencies[${index}].versionRange`, errors);
      this.requireBoolean(dependency.required, `dependencies[${index}].required`, errors);
    });
  }

  private requireString(value: unknown, field: string, errors: string[]): void {
    if (typeof value !== "string" || value.trim().length === 0) {
      errors.push(`${field} is required and must be a non-empty string.`);
    }
  }

  private requireBoolean(value: unknown, field: string, errors: string[]): void {
    if (typeof value !== "boolean") {
      errors.push(`${field} is required and must be a boolean.`);
    }
  }

  private requireStringArray(value: unknown, field: string, errors: string[]): void {
    if (!Array.isArray(value)) {
      errors.push(`${field} must be an array of strings.`);
      return;
    }

    const hasInvalidItem = value.some((item) => typeof item !== "string" || item.trim().length === 0);
    if (hasInvalidItem) {
      errors.push(`${field} must contain only non-empty strings.`);
    }
  }

  private isObject(value: unknown): value is Record<string, unknown> {
    return typeof value === "object" && value !== null && !Array.isArray(value);
  }
}
