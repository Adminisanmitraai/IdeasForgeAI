(function () {
  const API = location.protocol + "//" + location.hostname + ":5051";
  const ENDPOINT = API + "/api/admin/system-summary";

  const map = {
    workers: d => d.summary?.workers ?? 0,
    active_workers: d => d.summary?.active_workers ?? 0,
    worker_health_percent: d => (d.summary?.worker_health ?? 0) + "%",
    worker_accuracy_percent: d => (d.summary?.worker_accuracy ?? 0) + "%",
    jobs: d => d.summary?.jobs ?? 0,
    waiting_approval: d => d.summary?.waiting_approval ?? 0,
    approved: d => d.summary?.approved ?? 0,
    apply_requested: d => d.summary?.apply_requested ?? 0,
    audit_events: d => d.summary?.audit_events ?? 0,
    persistence_readiness_percent: d => (d.summary?.persistence_readiness ?? 0) + "%",
    execution: d => d.summary?.execution || "locked",
    readiness_percent: d => (d.overall?.readiness ?? 0) + "%",
    risk_level: d => d.overall?.risk_level || "Low",
    phase: d => d.phase || "ADM-4C-13"
  };

  function value(data, key) {
    if (map[key]) return map[key](data);
    return "";
  }

  function update(data) {
    window.IFAI_ADMIN_SYSTEM_SUMMARY = data;

    document.querySelectorAll("[data-admin-summary]").forEach(el => {
      const key = el.getAttribute("data-admin-summary");
      const next = String(value(data, key));
      if (next && el.textContent !== next) el.textContent = next;
    });

    document.body.dataset.adminSummaryLoaded = "true";
    document.body.dataset.adminExecution = data.summary?.execution || "locked";
  }

  async function load() {
    try {
      const res = await fetch(ENDPOINT, { cache: "no-store" });
      const data = await res.json();
      if (data.ok) update(data);
    } catch (err) {
      window.IFAI_ADMIN_SYSTEM_SUMMARY_ERROR = String(err.message || err);
      document.body.dataset.adminSummaryLoaded = "false";
    }
  }

  window.IFAIAdminSystemSummary = { load, endpoint: ENDPOINT };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", load);
  else load();

  setInterval(load, 30000);
})();
