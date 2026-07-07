(function () {
  const API = location.protocol + "//" + location.hostname + ":5051";
  const page = document.body.dataset.page || "";

  const menu = [
    ["Company Control"],
    ["Founder Office", "founder-office.html", "FO", page === "founder" ? "active" : "done"],
    ["Company Status", "company-status.html", "CS", page === "company" ? "active" : "done"],
    ["Approvals", "approvals-office.html", "AP", page === "approvals" ? "active" : "done"],
    ["Approval Detail", "approval-detail.html", "AD", page === "approval-detail" ? "active" : "done"],
    ["Teams", "teams-office.html", "TM", page === "teams" ? "active" : "done"],
    ["Operations", "operations-office.html", "OP", page === "operations" ? "active" : "done"],
    ["Finance", "finance-office.html", "₹", page === "finance" ? "active" : "done"],
    ["Projects", "projects-office.html", "PR", page === "projects" ? "active" : "done"],
    ["Reports", "reports-office.html", "RP", page === "reports" ? "active" : "done"],
    ["Settings", "settings-office.html", "ST", page === "settings" ? "active" : "done"],
      ["Deployment Readiness", "deployment-readiness.html", "DP", page === "deployment" ? "active" : "next"],
    ["Admin System"],
    ["Backend Health", API + "/health", "BH", "done"],
    ["Job Queue", "approvals-office.html", "JQ", "done"],
    ["Workers", "founder-office.html", "WK", "done"],
    ["Persistence", "approval-detail.html?jobId=current", "PS", "done"],
    ["Audit Logs", "#", "AL", "next"]
  ];

  function $(id) {
    return document.getElementById(id);
  }

  function nowTime() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function toast(message) {
    let el = $("toast");
    if (!el) return alert(message);
    el.textContent = message;
    el.classList.add("show");
    setTimeout(() => el.classList.remove("show"), 2300);
  }

  async function api(path, options) {
    const res = await fetch(API + path, Object.assign({ cache: "no-store" }, options || {}));
    const data = await res.json().catch(() => ({}));
    if (!res.ok || data.ok === false) throw new Error(data.message || data.error || "Request failed");
    return data;
  }

  function normalizeJobs(data) {
    if (!data) return [];
    if (Array.isArray(data.jobs)) return data.jobs;
    if (data.jobs && typeof data.jobs === "object") return Object.values(data.jobs);
    if (Array.isArray(data)) return data;
    return [];
  }

  function rank(job) {
    const s = String(job.status || "");
    if (s === "pending_founder_approval") return 1000;
    if (s === "approved_waiting_for_worker") return 700;
    if (s === "running") return 500;
    if (s === "dry_run_completed") return 100;
    return 0;
  }

  function sortJobs(jobs) {
    return jobs.slice().sort((a, b) => {
      const r = rank(b) - rank(a);
      if (r) return r;
      return new Date(b.updatedAt || b.createdAt || 0) - new Date(a.updatedAt || a.createdAt || 0);
    });
  }

  function statusText(status) {
    const s = String(status || "");
    if (s === "pending_founder_approval") return "Pending";
    if (s === "approved_waiting_for_worker") return "Approved";
    if (s === "rejected_by_founder") return "Rejected";
    if (s === "hold_for_more_info") return "On hold";
    if (s === "dry_run_completed") return "Dry-run done";
    return s.replaceAll("_", " ") || "Unknown";
  }

  function badgeClass(status) {
    if (status === "pending_founder_approval") return "pending";
    if (status === "approved_waiting_for_worker") return "approved";
    if (status === "dry_run_completed") return "";
    return "approved";
  }

  function countsFromJobs(jobs) {
    return {
      pending: jobs.filter(j => j.status === "pending_founder_approval").length,
      queued: jobs.filter(j => j.status === "approved_waiting_for_worker").length,
      running: jobs.filter(j => j.status === "running").length,
      dry: jobs.filter(j => j.status === "dry_run_completed").length
    };
  }

  function setText(id, value) {
    const el = $(id);
    if (el) el.textContent = value;
  }

  async function loadHealth() {
    try {
      const h = await api("/health");
      setText("backendState", h.phase || "Connected");
      setText("workerState", String(h.workers || 0) + " registered");
      return h;
    } catch {
      setText("backendState", "Offline");
      setText("workerState", "0 registered");
      return null;
    }
  }

  async function loadJobs() {
    const data = await api("/api/admin/jobs");
    return sortJobs(normalizeJobs(data));
  }

  function renderSummary(jobs) {
    const c = countsFromJobs(jobs);
    const online = 0;

    setText("summaryText", "I found " + c.pending + " pending approval, " + c.queued + " queued job, " + c.dry + " dry-run completed job, and " + online + " online worker.");
    setText("updatedAt", "Updated " + nowTime());
    setText("pendingCount", c.pending);
    setText("queuedCount", c.queued);
    setText("dryCount", c.dry);
    setText("pendingChip", c.pending);
  }

  function renderJobs(jobs) {
    const list = $("jobsList");
    if (!list) return;

    if (!jobs.length) {
      list.innerHTML = '<div class="job-card"><div class="job-title">No approval job found</div><div class="job-command">Create a safe pending test from the menu.</div></div>';
      return;
    }

    list.innerHTML = jobs.map(job => `
      <article class="job-card" data-job="${job.jobId}">
        <div class="job-head">
          <div class="job-title">${job.taskType || "training-plan"}</div>
          <div class="badge ${badgeClass(job.status)}">${statusText(job.status)}</div>
        </div>
        <div class="job-command">${job.requestedCommand || "No command available."}</div>
        <div class="meta-row">
          <span class="meta">${job.department || "Training Academy"}</span>
          <span class="meta">Risk: ${job.risk || "medium"}</span>
          <span class="meta">${job.jobId || ""}</span>
        </div>
        <div class="action-row">
          <button class="btn primary" data-open="${job.jobId}">Open</button>
          <button class="btn" data-refresh>Refresh</button>
          <button class="btn" data-create>Create test</button>
        </div>
      </article>
    `).join("");

    list.querySelectorAll("[data-open]").forEach(btn => {
      btn.addEventListener("click", () => {
        location.href = "approval-detail.html?jobId=" + encodeURIComponent(btn.dataset.open) + "&v=open-" + Date.now();
      });
    });

    list.querySelectorAll("[data-refresh]").forEach(btn => {
      btn.addEventListener("click", () => location.reload());
    });

    list.querySelectorAll("[data-create]").forEach(btn => {
      btn.addEventListener("click", createTestApproval);
    });
  }

  async function createTestApproval() {
    try {
      const data = await api("/api/admin/approvals/test-pending", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ requestedCommand: "ADM-3D persistence test - safe approval only" })
      });

      const jobId = data.job && data.job.jobId;
      toast("Safe pending approval created");
      if (jobId) {
        setTimeout(() => {
          location.href = "approval-detail.html?jobId=" + encodeURIComponent(jobId) + "&v=new-" + Date.now();
        }, 450);
      }
    } catch (err) {
      toast("Create failed: " + err.message);
    }
  }

  async function initApprovals() {
    await loadHealth();
    const jobs = await loadJobs();
    renderSummary(jobs);
    renderJobs(jobs);
  }

  async function getSelectedJob() {
    const params = new URLSearchParams(location.search);
    const id = params.get("jobId") || "current";

    if (id && id !== "current") {
      try {
        const data = await api("/api/admin/jobs/" + encodeURIComponent(id));
        return data.job || data;
      } catch {}
    }

    const data = await api("/api/admin/jobs/current-decision");
    return data.job || null;
  }

  function renderDetail(job, jobs) {
    renderSummary(jobs || (job ? [job] : []));

    if (!job) {
      setText("detailTitle", "No approval job found");
      setText("detailStatus", "Empty");
      setText("detailCommand", "No requested command available.");
      setText("detailJobId", "Job: none");
      setText("timeline", "No job exists yet.");
      return;
    }

    setText("detailTitle", job.taskType || "training-plan");
    setText("detailStatus", statusText(job.status));
    setText("detailCommand", job.requestedCommand || "No requested command available.");
    setText("detailJobId", "Job: " + job.jobId);
    setText("detailRisk", "Risk: " + (job.risk || "medium"));

    const statusBadge = $("detailStatus");
    if (statusBadge) statusBadge.className = "badge " + badgeClass(job.status);

    const pending = job.status === "pending_founder_approval";
    ["approveBtn", "rejectBtn", "holdBtn"].forEach(id => {
      const btn = $(id);
      if (btn) btn.disabled = !pending;
    });

    const reason = $("reasonInput");
    if (reason) {
      reason.disabled = !pending;
      reason.placeholder = pending
        ? "Write why you are approving, rejecting, or holding this request."
        : "Decision is locked unless the job is pending founder approval.";
    }

    const rows = Array.isArray(job.logs) ? job.logs : [];
    const timeline = $("timeline");
    if (timeline) {
      if (!rows.length) {
        timeline.innerHTML = '<div class="timeline-row"><div class="timeline-time">Now</div><div>No timeline events yet.</div></div>';
      } else {
        timeline.innerHTML = rows.map(log => {
          const t = log.at ? new Date(log.at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "Now";
          return '<div class="timeline-row"><div class="timeline-time">' + t + '</div><div>' + (log.message || "Status updated.") + '</div></div>';
        }).join("");
      }
    }
  }

  async function decide(decision) {
    const params = new URLSearchParams(location.search);
    let jobId = params.get("jobId") || "current";
    const reason = $("reasonInput") ? $("reasonInput").value : "";

    try {
      const selected = await getSelectedJob();
      if (selected && selected.jobId) jobId = selected.jobId;

      await api("/api/admin/jobs/" + encodeURIComponent(jobId) + "/decision", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision, reason })
      });

      toast("Founder decision saved");
      setTimeout(() => location.reload(), 700);
    } catch (err) {
      toast("Decision failed: " + err.message);
    }
  }

  async function initDetail() {
    await loadHealth();
    let jobs = [];
    try { jobs = await loadJobs(); } catch {}
    const job = await getSelectedJob().catch(() => null);
    renderDetail(job, jobs);
  }

  function initDrawer() {
    const backdrop = document.createElement("div");
    backdrop.className = "drawer-backdrop";

    const drawer = document.createElement("aside");
    drawer.className = "drawer";

    drawer.innerHTML = `
      <div class="drawer-top">
        <div>
          <div class="drawer-title">Founder Office</div>
          <div class="drawer-sub">Dark is complete. Blue is active. Grey is planned.</div>
        </div>
        <button class="drawer-close">×</button>
      </div>
      ${menu.map(item => {
        if (item.length === 1) return '<div class="drawer-section">' + item[0] + '</div>';

        const name = item[0], href = item[1], icon = item[2], state = item[3];
        const label = state === "active" ? "Now" : state === "done" ? "Done" : state === "next" ? "Next" : "Planned";
        const url = href === "#" ? "#" : href + (href.includes("?") ? "&" : "?") + "v=drawer-" + Date.now();

        return `
          <a class="drawer-item ${state}" href="${url}">
            <span class="drawer-icon">${icon}</span>
            <span>${name}</span>
            <span class="drawer-status">${label}</span>
          </a>
        `;
      }).join("")}
      <div class="drawer-footer">
        <b>IdeasForgeAI Admin</b>
        <p>ADM-3L is active. Deployment readiness is ready. Real execution remains disabled.</p>
      </div>
    `;

    document.body.appendChild(backdrop);
    document.body.appendChild(drawer);

    function open() {
      document.body.classList.add("drawer-open");
      backdrop.classList.add("open");
      drawer.classList.add("open");
    }

    function close() {
      document.body.classList.remove("drawer-open");
      backdrop.classList.remove("open");
      drawer.classList.remove("open");
    }

    document.querySelectorAll("[data-menu]").forEach(btn => btn.addEventListener("click", open));
    drawer.querySelector(".drawer-close").addEventListener("click", close);
    backdrop.addEventListener("click", close);
  }

  function initDots() {
    const dots = $("dotsMenu");
    document.querySelectorAll("[data-dots]").forEach(btn => {
      btn.addEventListener("click", () => dots && dots.classList.toggle("open"));
    });

    document.addEventListener("click", e => {
      if (!dots) return;
      if (!e.target.closest("[data-dots]") && !e.target.closest("#dotsMenu")) {
        dots.classList.remove("open");
      }
    });
  }

  function initComposer() {
    const input = $("composerInput");
    const send = $("composerSend");
    if (!input || !send) return;

    send.addEventListener("click", () => {
      const value = input.value.trim();
      if (!value) return;
      toast("Founder command noted");
      input.value = "";
    });
  }

  function bindActions() {
    const createBtn = $("createTestBtn");
    if (createBtn) createBtn.addEventListener("click", createTestApproval);

    const refreshBtn = $("refreshBtn");
    if (refreshBtn) refreshBtn.addEventListener("click", () => location.reload());

    const approveBtn = $("approveBtn");
    if (approveBtn) approveBtn.addEventListener("click", () => decide("approve"));

    const rejectBtn = $("rejectBtn");
    if (rejectBtn) rejectBtn.addEventListener("click", () => decide("reject"));

    const holdBtn = $("holdBtn");
    if (holdBtn) holdBtn.addEventListener("click", () => decide("hold"));
  }

  window.addEventListener("load", async () => {
    initDrawer();
    initDots();
    initComposer();
    bindActions();

    if (page === "approvals") await initApprovals();
    if (page === "approval-detail") await initDetail();
    if (page === "founder") await initApprovals();

if (page === "teams") {
  await loadHealth();
  const updated = document.getElementById("updatedAt");
  if (updated) updated.textContent = "Updated " + new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

if (page === "teams") {
  await loadHealth();
  const updated = document.getElementById("updatedAt");
  if (updated) updated.textContent = "Updated " + new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
  });
})();



// ADM-3D-F14-MOVE-COMPOSER-INTO-ASSISTANT
function admMoveComposerInsideAssistant() {
  const composer = document.querySelector(".composer");
  const assistant = document.querySelector(".assistant-row");
  const stats = assistant ? assistant.querySelector(".stats") : null;

  if (!composer || !assistant || !stats) return;

  if (composer.parentElement !== assistant) {
    assistant.insertBefore(composer, stats);
  }
}

window.addEventListener("load", function () {
  admMoveComposerInsideAssistant();
  setTimeout(admMoveComposerInsideAssistant, 250);
  setTimeout(admMoveComposerInsideAssistant, 900);
});
// END-ADM-3D-F14-MOVE-COMPOSER-INTO-ASSISTANT


// ADM-3L-DEPLOYMENT-MENU-PATCH-START
(function () {
  const DEPLOY_URL = "deployment-readiness.html?v=adm3l-drawer-final";

  function isDeploymentPage() {
    return location.pathname.includes("deployment-readiness") ||
      document.body?.dataset?.page === "deployment";
  }

  function findDrawer() {
    const candidates = Array.from(document.querySelectorAll("aside,nav,div"))
      .filter((el) => {
        const text = (el.innerText || "").trim();
        return (
          text.length > 80 &&
          text.length < 3200 &&
          text.includes("Founder Office") &&
          text.includes("COMPANY CONTROL") &&
          text.includes("Settings")
        );
      })
      .sort((a, b) => (a.innerText || "").length - (b.innerText || "").length);

    return candidates[0] || null;
  }

  function exactText(root, value) {
    return Array.from(root.querySelectorAll("*")).find((el) => {
      return (el.textContent || "").trim() === value;
    });
  }

  function makeDeploymentRow() {
    const active = isDeploymentPage();

    const row = document.createElement("a");
    row.href = DEPLOY_URL;
    row.setAttribute("data-adm3l-deployment-row", "true");

    row.style.cssText = [
      "display:flex",
      "align-items:center",
      "gap:14px",
      "width:calc(100% - 48px)",
      "margin:8px 24px",
      "padding:12px 14px",
      "border-radius:18px",
      "text-decoration:none",
      "box-sizing:border-box",
      active ? "background:#eaf2ff" : "background:transparent",
      "color:#111"
    ].join(";");

    row.innerHTML =
      '<span style="' +
        'width:44px;height:44px;border-radius:14px;' +
        'display:flex;align-items:center;justify-content:center;' +
        'font-weight:900;font-size:15px;' +
        (active ? 'background:#d8eaff;color:#2563eb;' : 'background:#f4f5f6;color:#727985;') +
      '">DP</span>' +
      '<span style="flex:1;font-weight:900;font-size:22px;letter-spacing:-.04em;line-height:1.05;">Deployment Readiness</span>' +
      '<strong style="font-size:16px;font-weight:900;color:' + (active ? '#2563eb' : '#111') + ';">' +
        (active ? "Now" : "Done") +
      '</strong>';

    return row;
  }

  function updateFooter(drawer) {
    const footer = Array.from(drawer.querySelectorAll("*"))
      .filter((el) => (el.textContent || "").includes("IdeasForgeAI Admin"))
      .sort((a, b) => (a.textContent || "").length - (b.textContent || "").length)[0];

    if (!footer) return;

    const footerText = Array.from(footer.querySelectorAll("*"))
      .find((el) => (el.textContent || "").includes("ADM-3L is active"));

    if (footerText) {
      footerText.textContent =
        "ADM-3L is active. Deployment readiness is ready. Real execution remains disabled.";
    }
  }

  function applyDeploymentMenuPatch() {
    const drawer = findDrawer();
    if (!drawer) return;

    if (!(drawer.innerText || "").includes("Deployment Readiness")) {
      const row = makeDeploymentRow();

      const adminSystem = exactText(drawer, "ADMIN SYSTEM");
      if (adminSystem && adminSystem.parentElement) {
        adminSystem.parentElement.insertBefore(row, adminSystem);
      } else {
        drawer.appendChild(row);
      }
    }

    updateFooter(drawer);
  }

  document.addEventListener("DOMContentLoaded", function () {
    setTimeout(applyDeploymentMenuPatch, 200);
  });

  document.addEventListener("click", function () {
    setTimeout(applyDeploymentMenuPatch, 120);
    setTimeout(applyDeploymentMenuPatch, 450);
  }, true);

  const observer = new MutationObserver(function () {
    applyDeploymentMenuPatch();
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true
  });

  setTimeout(applyDeploymentMenuPatch, 500);
  setTimeout(applyDeploymentMenuPatch, 1500);
})();
// ADM-3L-DEPLOYMENT-MENU-PATCH-END


// ADM-3L-FOOTER-FINAL-PATCH-START
(function () {
  function updateAdmFooter() {
    const nodes = Array.from(document.querySelectorAll("*"));
    nodes.forEach((el) => {
      const text = (el.textContent || "").trim();

      if (text.includes("ADM-3D is active")) {
        el.textContent = text.replace(
          "ADM-3D is active. Founder approvals are safe. Real execution remains disabled.",
          "ADM-3L is active. Deployment readiness is ready. Real execution remains disabled."
        ).replace("ADM-3D is active", "ADM-3L is active");
      }

      if (
        text.includes("IdeasForgeAI Admin") &&
        text.includes("Founder approvals are safe")
      ) {
        const children = Array.from(el.querySelectorAll("*"));
        children.forEach((child) => {
          const childText = (child.textContent || "").trim();
          if (childText.includes("ADM-3D") || childText.includes("Founder approvals are safe")) {
            child.textContent =
              "ADM-3L is active. Deployment readiness is ready. Real execution remains disabled.";
          }
        });
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    setTimeout(updateAdmFooter, 200);
    setTimeout(updateAdmFooter, 800);
  });

  document.addEventListener("click", function () {
    setTimeout(updateAdmFooter, 120);
    setTimeout(updateAdmFooter, 500);
  }, true);

  new MutationObserver(updateAdmFooter).observe(document.documentElement, {
    childList: true,
    subtree: true
  });
})();
// ADM-3L-FOOTER-FINAL-PATCH-END


// ADM-3M-COMPANY-STATUS-ACTIVE-PATCH-START
(function () {
  function isCompanyStatusPage() {
    return location.pathname.includes("company-status") ||
      document.body?.dataset?.page === "company-status";
  }

  function patchCompanyStatusIdentity() {
    if (!isCompanyStatusPage()) return;

    // Fix any visible top chip still saying Projects
    document.querySelectorAll("*").forEach((el) => {
      const text = (el.textContent || "").trim();

      if (text === "Projects") {
        el.textContent = "Company";
      }

      if (text.includes("Projects") && text.includes("ADM-")) {
        el.textContent = text.replace("Projects", "Company").replace(/ADM-[0-9A-Z]+/, "ADM-3M");
      }

      if (text === "Company Status") {
        const row = el.closest("a,div,li,button");
        if (row && row.innerText && row.innerText.includes("Done")) {
          row.querySelectorAll("*").forEach((child) => {
            if ((child.textContent || "").trim() === "Done") {
              child.textContent = "Now";
              child.style.color = "#2563eb";
            }
          });

          row.style.background = "#eaf2ff";
          row.style.borderRadius = "18px";

          const badge = row.querySelector("span");
          if (badge) {
            badge.style.background = "#d8eaff";
            badge.style.color = "#2563eb";
          }
        }
      }

      if (text === "Deployment Readiness") {
        const row = el.closest("a,div,li,button");
        if (row && row.innerText && row.innerText.includes("Next")) {
          row.querySelectorAll("*").forEach((child) => {
            if ((child.textContent || "").trim() === "Next") {
              child.textContent = "Done";
              child.style.color = "#111";
            }
          });
        }
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    setTimeout(patchCompanyStatusIdentity, 150);
    setTimeout(patchCompanyStatusIdentity, 600);
  });

  document.addEventListener("click", function () {
    setTimeout(patchCompanyStatusIdentity, 120);
    setTimeout(patchCompanyStatusIdentity, 500);
  }, true);

  new MutationObserver(patchCompanyStatusIdentity).observe(document.documentElement, {
    childList: true,
    subtree: true
  });
})();
// ADM-3M-COMPANY-STATUS-ACTIVE-PATCH-END


// ADM-3M2D-COMPANY-DRAWER-FIX-START
(function () {
  function isCompanyStatusPage() {
    return location.pathname.includes("company-status") ||
      document.body?.dataset?.page === "company-status";
  }

  function patchCompanyDrawer() {
    if (!isCompanyStatusPage()) return;

    document.querySelectorAll("*").forEach((el) => {
      const text = (el.textContent || "").trim();

      if (text === "Projects") {
        el.textContent = "Company";
      }

      if (text === "Company Status") {
        const row = el.closest("a,div,li,button");
        if (row && row.innerText && row.innerText.includes("Done")) {
          row.querySelectorAll("*").forEach((child) => {
            if ((child.textContent || "").trim() === "Done") {
              child.textContent = "Now";
              child.style.color = "#2563eb";
            }
          });

          row.style.background = "#eaf2ff";
          row.style.borderRadius = "18px";

          const badge = row.querySelector("span");
          if (badge) {
            badge.style.background = "#d8eaff";
            badge.style.color = "#2563eb";
          }
        }
      }

      if (text === "Deployment Readiness") {
        const row = el.closest("a,div,li,button");
        if (row && row.innerText && row.innerText.includes("Now")) {
          row.querySelectorAll("*").forEach((child) => {
            if ((child.textContent || "").trim() === "Now") {
              child.textContent = "Done";
              child.style.color = "#111";
            }
          });
          row.style.background = "transparent";
        }
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    setTimeout(patchCompanyDrawer, 150);
    setTimeout(patchCompanyDrawer, 700);
  });

  document.addEventListener("click", function () {
    setTimeout(patchCompanyDrawer, 120);
    setTimeout(patchCompanyDrawer, 500);
  }, true);

  new MutationObserver(patchCompanyDrawer).observe(document.documentElement, {
    childList: true,
    subtree: true
  });
})();
// ADM-3M2D-COMPANY-DRAWER-FIX-END
