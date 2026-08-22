import type {
  TerminalApiError,
  TerminalDiscoveryRequest,
  TerminalGatewaySnapshot,
  TerminalPlanPayload,
  TerminalPreviewRequest,
} from "../models/terminal";

import {
  beginDiscoveryRequest,
  beginTerminalRequest,
  beginPreviewRequest,
  completePreview,
  completeDiscovery,
  completeTerminalPlan,
  failDiscovery,
  failTerminalPlan,
  failPreview,
  getTerminalSnapshot,
  updateTerminalSnapshot,
} from "../state/terminalStore";

import {
  TerminalApiRequestError,
  terminalApi,
} from "./terminalApi";

function normalizeError(
  error: unknown,
): TerminalApiError {
  if (error instanceof TerminalApiRequestError) {
    return {
      code: error.code,
      message: error.message,
      status: error.status,
      retryable: error.retryable,
      details: error.details,
    };
  }

  return {
    code: "terminal_gateway_error",
    message:
      error instanceof Error
        ? error.message
        : "The terminal request failed.",
    retryable: false,
    details: error,
  };
}

export class TerminalGateway {
  async checkConnection():
  Promise<Readonly<TerminalGatewaySnapshot>> {
    updateTerminalSnapshot({
      status: "checking",
      error: null,
    });

    try {
      const capabilities =
        await terminalApi.getCapabilities();

      return updateTerminalSnapshot({
        status: "idle",
        connected: true,
        capabilities,
        error: null,
      });
    } catch (error) {
      const normalized = normalizeError(error);

      return failTerminalPlan(normalized);
    }
  }

  async discoverCommands(
    payload: TerminalDiscoveryRequest,
  ): Promise<Readonly<TerminalGatewaySnapshot>> {
    const requestId =
      beginDiscoveryRequest(payload);

    try {
      const discovery =
        await terminalApi.discoverCommands(payload);

      if (
        getTerminalSnapshot().requestId !==
        requestId
      ) {
        return getTerminalSnapshot();
      }

      return completeDiscovery(discovery);
    } catch (error) {
      if (
        getTerminalSnapshot().requestId !==
        requestId
      ) {
        return getTerminalSnapshot();
      }

      const normalized = normalizeError(error);
      return failDiscovery(normalized);
    }
  }

  async createPlan(
    payload: TerminalPlanPayload,
  ): Promise<Readonly<TerminalGatewaySnapshot>> {
    const requestId =
      beginTerminalRequest(payload);

    try {
      const plan =
        await terminalApi.createPlan(payload);

      if (
        getTerminalSnapshot().requestId !==
        requestId
      ) {
        return getTerminalSnapshot();
      }

      return completeTerminalPlan(plan);
    } catch (error) {
      if (
        getTerminalSnapshot().requestId !==
        requestId
      ) {
        return getTerminalSnapshot();
      }

      const normalized = normalizeError(error);

      return updateTerminalSnapshot({
        status:
          normalized.code ===
          "terminal_backend_unreachable"
            ? "offline"
            : "failed",
        connected: false,
        error: normalized,
      });
    }
  }

  async createPreview(
    payload: TerminalPreviewRequest,
  ): Promise<Readonly<TerminalGatewaySnapshot>> {
    const requestId = beginPreviewRequest(payload);
    try {
      const data = await terminalApi.createPreview(payload);
      if (getTerminalSnapshot().requestId !== requestId) return getTerminalSnapshot();
      return completePreview(data.preview);
    } catch (error) {
      if (getTerminalSnapshot().requestId !== requestId) return getTerminalSnapshot();
      return failPreview(normalizeError(error));
    }
  }
}

export const terminalGateway =
  new TerminalGateway();
