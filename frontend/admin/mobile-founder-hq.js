(() => {
  const host = location.hostname || "localhost";
  const API = `${location.protocol}//${host}:5051`;
  const $ = (id) => document.getElementById(id);
  const state = { jobs: [], workers: [], filter: "all", pendingApproval: null };

  const fmtStatus = (s = "") => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
  const timeOnly = (v) => {
    try { return new Date(v).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }); } catch { return ""; }
  };

  async function api(path, options = {}) {
    const res = await fetch(API + path, {
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) }
    });
    const text = await res.text();
    let data = {};
    try { data = text ? JSON.parse(text) : {}; } catch { data = { raw: text }; }
    if (!res.ok) throw new Error(`${path} ${res.status}`);
    return data;
  }

  async function tryApi(calls) {
    let lastErr;
    for (const call of calls) {
      try { return await call(); } catch (e) { lastErr = e; }
    }
    throw lastErr || new Error("No API call available");
  }

  function statusKind(status) {
    if (status === "dry_run_completed") return "Dry Run Completed";
    if (status === "approved_waiting_for_worker") return "Waiting";
    if (status === "running" || status === "worker_seen") return "Running";
    if (status === "cancelled") return "Cancelled";
    return fmtStatus(status || "Pending");
  }

  function renderStatus(health = {}) {
    const online = Number(health.onlineWorkers || 0);
    const workers = Number(health.workers || state.workers.length || 0);
    const waiting = state.jobs.filter(j => j.status === "approved_waiting_for_worker").length;
    const running = state.jobs.filter(j => ["running", "worker_seen"].includes(j.status)).length;
    const done = state.jobs.filter(j => j.status === "dry_run_completed").length;
    const latest = state.jobs[0];
    $("workerChip").textContent = `${workers} registered, ${online} online`;
    $("queueChip").textContent = `${waiting} waiting, ${running} running, ${done} dry-run done`;
    $("latestChip").textContent = latest ? `${latest.taskType || "job"} - ${fmtStatus(latest.status)}` : "No jobs yet";
    const dot = document.querySelector(".ifm-chip i");
    if (dot) dot.className = online > 0 ? "ok" : "warn";
  }

  function renderJobs() {
    const waiting = state.jobs.filter(j => j.status === "approved_waiting_for_worker").length;
    const running = state.jobs.filter(j => ["running", "worker_seen"].includes(j.status)).length;
    const done = state.jobs.filter(j => j.status === "dry_run_completed").length;
    $("jobSummary").textContent = `${state.jobs.length} total, ${waiting} waiting, ${running} running, ${done} dry-run done`;
    const jobs = state.filter === "all" ? state.jobs : state.jobs.filter(j => j.status === state.filter || (state.filter === "running" && ["running", "worker_seen"].includes(j.status)));
    const list = $("jobList");
    list.innerHTML = "";
    if (!jobs.length) {
      list.innerHTML = '<div class="ifm-empty">No jobs in this filter.</div>';
      return;
    }
    jobs.forEach(job => {
      const logs = (job.logs || []).slice(-5).reverse();
      const card = document.createElement("article");
      card.className = "ifm-job-card";
      card.innerHTML = `
        <div class="ifm-job-title"><h3>${job.taskType || "job"}</h3><strong>${statusKind(job.status)}</strong></div>
        <p>${job.department || job.departmentId || "Founder HQ"} - ${job.requestedCommand || "No command"}</p>
        <div class="ifm-job-meta"><span>${job.jobId || "job"}</span><span>${job.risk || "risk: safe"}</span></div>
        ${logs.length ? `<div class="ifm-log">${logs.map(l => `<div><b>${timeOnly(l.at)}</b><span>${l.message || l.level || "Log"}</span></div>`).join("")}</div>` : ""}
      `;
      list.appendChild(card);
    });
  }

  async function refresh() {
    try {
      const [health, workers, jobs] = await Promise.all([
        api("/health?v=" + Date.now()).catch(() => ({})),
        api("/api/admin/workers").catch(() => ({ workers: [] })),
        api("/api/admin/jobs").catch(() => ({ jobs: [] }))
      ]);
      state.workers = workers.workers || [];
      state.jobs = (jobs.jobs || []).sort((a, b) => String(b.updatedAt || b.createdAt || "").localeCompare(String(a.updatedAt || a.createdAt || "")));
      renderStatus(health);
      renderJobs();
    } catch (e) {
      $("workerChip").textContent = "backend offline";
      $("queueChip").textContent = "not connected";
      $("latestChip").textContent = e.message;
    }
  }

  function addMessage(role, html) {
    const row = document.createElement("div");
    row.className = `ifm-row ${role}`;
    const avatar = role === "user" ? "You" : "✦";
    row.innerHTML = `<div class="ifm-avatar">${avatar}</div><div class="ifm-bubble">${html}</div>`;
    if (role === "user") row.insertBefore(row.lastChild, row.firstChild);
    $("chatStream").appendChild(row);
    row.scrollIntoView({ behavior: "smooth", block: "end" });
    return row;
  }

  function approvalCard(plan) {
    state.pendingApproval = plan;
    const row = addMessage("ai", `
      <strong>${plan.title || "Approval required"}</strong><br>
      <span style="color:rgba(255,255,255,.64)">${plan.manager || "Founder AI"} is requesting approval for <b>${plan.taskType || "task"}</b>.</span>
      <div class="ifm-job-meta"><span>Risk: ${plan.risk || "medium"}</span><span>Status: pending</span></div>
      <ol style="padding-left:20px;margin:12px 0 0;color:rgba(255,255,255,.78)">
        ${(plan.steps || ["Prepare safe plan", "Queue approved job", "Wait for worker", "Report status"]).map(s => `<li>${s}</li>`).join("")}
      </ol>
      <div class="ifm-approval-actions"><button class="approve" type="button">Approve</button><button class="reject" type="button">Reject</button></div>
    `);
    row.querySelector(".approve").onclick = () => approvePlan(plan, row);
    row.querySelector(".reject").onclick = () => rejectPlan(plan, row);
  }

  async function sendCommand(command) {
    addMessage("user", command);
    try {
      const data = await tryApi([
        () => api("/api/admin/mobile/command", { method: "POST", body: JSON.stringify({ command }) }),
        () => api("/api/admin/command", { method: "POST", body: JSON.stringify({ command }) }),
        () => api("/api/admin/chat", { method: "POST", body: JSON.stringify({ message: command, command }) })
      ]);
      const plan = data.approval || data.plan || data;
      approvalCard({
        approvalId: plan.approvalId,
        title: plan.title || "Approve AutoCAD software-layer training plan",
        manager: plan.manager || "Training Director AI",
        taskType: plan.taskType || "training-plan",
        risk: plan.risk || "medium",
        requestedCommand: command,
        steps: plan.steps
      });
    } catch {
      approvalCard({
        title: "Approve AutoCAD software-layer training plan",
        manager: "Training Director AI",
        taskType: "training-plan",
        risk: "medium",
        requestedCommand: command,
        steps: ["Read the requested software layer scope.", "Prepare/update the software skill pack safely.", "Run validation tests for commands and workflows.", "Queue only after approval; no execution without worker."]
      });
    }
  }

  async function approvePlan(plan, row) {
    const payload = { approvalId: plan.approvalId, command: plan.requestedCommand, requestedCommand: plan.requestedCommand, taskType: plan.taskType, risk: plan.risk };
    try {
      const data = await tryApi([
        () => api("/api/admin/mobile/approve", { method: "POST", body: JSON.stringify(payload) }),
        () => api("/api/admin/approvals/approve", { method: "POST", body: JSON.stringify(payload) }),
        () => api("/api/admin/jobs", { method: "POST", body: JSON.stringify(payload) })
      ]);
      const job = data.job || data;
      row.querySelector(".ifm-bubble").innerHTML += `<p style="color:#48d47d;margin:14px 0 0">Job queued: ${job.jobId || "approved"}. Status: ${job.status || "approved_waiting_for_worker"}.</p>`;
    } catch (e) {
      row.querySelector(".ifm-bubble").innerHTML += `<p style="color:#e2a43b;margin:14px 0 0">Approved locally. Backend approval endpoint not available: ${e.message}</p>`;
    }
    await refresh();
  }

  async function rejectPlan(plan, row) {
    try { await api("/api/admin/mobile/reject", { method: "POST", body: JSON.stringify({ approvalId: plan.approvalId }) }); } catch {}
    row.querySelector(".ifm-bubble").innerHTML += `<p style="color:#ff6b6b;margin:14px 0 0">Rejected.</p>`;
  }

  function boot() {
    $("drawerBtn").onclick = () => document.body.classList.add("drawer-open");
    $("ifmBackdrop").onclick = () => document.body.classList.remove("drawer-open");
    $("refreshBtn").onclick = refresh;
    $("newChatBtn").onclick = () => { $("chatStream").innerHTML = ""; document.body.classList.remove("drawer-open"); };
    $("composerForm").onsubmit = (e) => {
      e.preventDefault();
      const input = $("composerInput");
      const command = input.value.trim();
      if (!command) return;
      input.value = "";
      sendCommand(command);
    };
    document.querySelectorAll("[data-command]").forEach(btn => btn.onclick = () => sendCommand(btn.dataset.command));
    $("jobFilters").onclick = (e) => {
      const btn = e.target.closest("button[data-filter]");
      if (!btn) return;
      state.filter = btn.dataset.filter;
      [...$("jobFilters").children].forEach(b => b.classList.toggle("active", b === btn));
      renderJobs();
    };
    refresh();
    setInterval(refresh, 5000);
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
