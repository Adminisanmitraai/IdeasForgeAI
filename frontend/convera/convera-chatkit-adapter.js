(function () {
  function isLanHost(hostname) {
    return (
      hostname === "localhost" ||
      hostname === "127.0.0.1" ||
      hostname === "0.0.0.0" ||
      /^192\.168\./.test(hostname) ||
      /^10\./.test(hostname) ||
      /^172\.(1[6-9]|2\d|3[0-1])\./.test(hostname)
    );
  }

  function normalizeBase(base) {
    return String(base || "").replace(/\/+$/, "");
  }

  function getParams() {
    return new URLSearchParams(window.location.search);
  }

  function getApiBase() {
    var params = getParams();
    var override = params.get("apiBase") || window.CONVERA_API_BASE;
    if (override) return normalizeBase(override);

    var host = window.location.hostname || "";
    if (isLanHost(host)) return "http://" + host + ":5052";

    return "https://ideasforgeai-api.onrender.com";
  }

  function getDomainKey() {
    var params = getParams();
    var explicit = params.get("domainKey") || window.CONVERA_CHATKIT_DOMAIN_KEY;
    if (explicit) return explicit;

    return isLanHost(window.location.hostname || "") ? "local-dev" : "";
  }

  function getApiUrl() {
    return getApiBase() + "/api/chatkit";
  }

  function getStatusUrl() {
    return getApiBase() + "/api/chatkit/real-status";
  }

  var adapterState = {
    mode: "pending",
    mounted: false,
    widget: null,
    status: null,
    domainKey: getDomainKey(),
  };

  async function fetchStatus() {
    try {
      var response = await fetch(getStatusUrl(), {
        method: "GET",
        headers: { Accept: "application/json" },
      });

      if (!response.ok) {
        throw new Error("Status returned " + response.status);
      }

      adapterState.status = await response.json();
      return adapterState.status;
    } catch (error) {
      adapterState.status = {
        ok: false,
        endpoint: "/api/chatkit",
        error: error && error.message ? error.message : String(error),
      };
      return adapterState.status;
    }
  }

  async function ensureWidget(mount) {
    if (adapterState.mounted && adapterState.widget && mount.contains(adapterState.widget)) {
      return adapterState.widget;
    }

    await customElements.whenDefined("openai-chatkit");

    mount.innerHTML = "";

    var widget = document.createElement("openai-chatkit");
    widget.setOptions({
      api: {
        url: getApiUrl(),
        domainKey: adapterState.domainKey,
      },
    });
    widget.style.width = "100%";
    widget.style.height = "100%";
    widget.style.display = "block";

    mount.appendChild(widget);
    adapterState.widget = widget;
    adapterState.mounted = true;
    return widget;
  }

  function setDraftText(prompt, draftBox, draftText) {
    var clean = String(prompt || "").trim();
    if (!draftBox || !draftText) return;

    if (!clean) {
      draftBox.hidden = true;
      draftText.textContent = "";
      return;
    }

    draftText.textContent = clean;
    draftBox.hidden = false;
  }

  async function mount(options) {
    var mountNode = options && options.mount;
    var responseNode = options && options.responseNode;
    var pillNode = options && options.pillNode;

    if (!mountNode) return { ok: false, mode: "missing_mount" };

    var status = await fetchStatus();
    var hasDomainKey = !!adapterState.domainKey;

    if (!status.ok) {
      adapterState.mode = "mock";
      if (responseNode) {
        responseNode.textContent =
          "Shared ChatKit backend is not ready right now. Convera remains in safe mock guidance mode.";
      }
      if (pillNode) pillNode.textContent = "Mock only";
      mountNode.innerHTML =
        '<div class="chatkit-placeholder"><p>ChatKit backend unavailable.</p><small>' +
        (status.error || status.import_error || "Unknown status error.") +
        "</small></div>";
      return { ok: false, mode: "mock", status: status };
    }

    if (!hasDomainKey) {
      adapterState.mode = "needs_domain_key";
      if (responseNode) {
        responseNode.textContent =
          "ChatKit backend is live. Add ?domainKey=domain_pk_... to use the real assistant in Convera.";
      }
      if (pillNode) pillNode.textContent = "Key needed";
      mountNode.innerHTML =
        '<div class="chatkit-placeholder"><p>ChatKit is ready.</p><small>Add a valid <code>domainKey</code> in the URL to open the shared assistant.</small></div>';
      return { ok: false, mode: "needs_domain_key", status: status };
    }

    try {
      await ensureWidget(mountNode);
      adapterState.mode = "real";
      if (responseNode) {
        responseNode.textContent =
          "IdeasForgeAI ChatKit is active below. Use the prepared prompt card or type directly in the assistant.";
      }
      if (pillNode) pillNode.textContent = "Live";
      return { ok: true, mode: "real", status: status };
    } catch (error) {
      adapterState.mode = "mock";
      if (responseNode) {
        responseNode.textContent =
          "ChatKit frontend could not mount here, so Convera stays in safe mock guidance mode.";
      }
      if (pillNode) pillNode.textContent = "Mock only";
      mountNode.innerHTML =
        '<div class="chatkit-placeholder"><p>ChatKit widget could not load.</p><small>' +
        (error && error.message ? error.message : String(error)) +
        "</small></div>";
      return { ok: false, mode: "mock", status: status, error: error };
    }
  }

  async function preparePrompt(options) {
    var prompt = options && options.prompt;
    var mountNode = options && options.mount;
    var responseNode = options && options.responseNode;
    var pillNode = options && options.pillNode;
    var draftBox = options && options.draftBox;
    var draftText = options && options.draftText;

    setDraftText(prompt, draftBox, draftText);
    return mount({
      mount: mountNode,
      responseNode: responseNode,
      pillNode: pillNode,
    });
  }

  async function copyDraft(text) {
    var clean = String(text || "").trim();
    if (!clean) return false;

    try {
      await navigator.clipboard.writeText(clean);
      return true;
    } catch (error) {
      return false;
    }
  }

  window.ConveraChatKitAdapter = {
    getApiBase: getApiBase,
    getApiUrl: getApiUrl,
    getStatusUrl: getStatusUrl,
    getDomainKey: getDomainKey,
    getMode: function () {
      return adapterState.mode;
    },
    mount: mount,
    preparePrompt: preparePrompt,
    copyDraft: copyDraft,
  };
})();
