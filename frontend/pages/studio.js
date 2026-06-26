const generateBtn = document.getElementById("generateBtn");
const appNameInput = document.getElementById("appName");
const ideaText = document.getElementById("ideaText");
const statusBadge = document.getElementById("statusBadge");
const summaryBox = document.getElementById("summaryBox");
const agentRows = document.getElementById("agentRows");
const rawOutput = document.getElementById("rawOutput");

const API_URL = "http://127.0.0.1:8100/api/generate";

function setStatus(text, mode = "neutral") {
  statusBadge.textContent = text;

  if (mode === "success") {
    statusBadge.style.background = "rgba(34, 197, 94, 0.18)";
    statusBadge.style.color = "#bbf7d0";
  } else if (mode === "error") {
    statusBadge.style.background = "rgba(239, 68, 68, 0.18)";
    statusBadge.style.color = "#fecaca";
  } else {
    statusBadge.style.background = "rgba(148, 163, 184, 0.2)";
    statusBadge.style.color = "#dbeafe";
  }
}

function slugify(value) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "") || "generated-product";
}

function renderAgents(results) {
  agentRows.innerHTML = "";

  results.forEach((item) => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${item.agent_name || ""}</td>
      <td>${item.status || ""}</td>
      <td>${item.summary || ""}</td>
    `;

    agentRows.appendChild(row);
  });
}

generateBtn.addEventListener("click", async () => {
  const idea = ideaText.value.trim();
  const app_name = appNameInput.value.trim();

  if (!idea) {
    setStatus("Missing idea", "error");
    summaryBox.textContent = "Please write a product idea first.";
    return;
  }

  generateBtn.disabled = true;
  generateBtn.textContent = "Generating...";
  setStatus("Generating", "neutral");
  summaryBox.textContent = "IdeasForgeAI agents are building the product plan...";
  agentRows.innerHTML = "";
  rawOutput.textContent = "";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        idea,
        app_name,
        target_platforms: ["web", "mobile"],
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    const folderName = slugify(data.project_name || app_name || "generated-product");

    setStatus(data.status || "Done", data.status === "success" ? "success" : "error");

    summaryBox.innerHTML = `
      <strong>Project:</strong> ${data.project_name || "Untitled"}<br/>
      <strong>Status:</strong> ${data.status || "unknown"}<br/>
      <strong>Export:</strong> D:\\APPS\\IdeasForgeAI\\generated-apps\\${folderName}
    `;

    renderAgents(data.results || []);
    rawOutput.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    setStatus("Error", "error");
    summaryBox.textContent = error.message;
  } finally {
    generateBtn.disabled = false;
    generateBtn.textContent = "Generate App";
  }
});

const refreshProjectsBtn = document.getElementById("refreshProjectsBtn");
const projectsGallery = document.getElementById("projectsGallery");

async function loadProjects() {
  if (!projectsGallery) return;

  projectsGallery.textContent = "Loading generated apps...";

  try {
    const response = await fetch("http://127.0.0.1:8100/api/projects");

    if (!response.ok) {
      throw new Error(`Project list API error: ${response.status}`);
    }

    const data = await response.json();
    const projects = data.projects || [];

    if (!projects.length) {
      projectsGallery.textContent = "No generated apps yet.";
      return;
    }

    projectsGallery.innerHTML = "";

    projects.forEach((project) => {
      const card = document.createElement("div");
      card.className = "project-card";

      const idea = project.original_idea
        ? project.original_idea.slice(0, 160)
        : "Generated app folder created by IdeasForgeAI.";

      card.innerHTML = `
        <h3>${project.project_name}</h3>
        <p>${idea}${idea.length >= 160 ? "..." : ""}</p>
        <div class="project-actions">
          ${
            project.has_preview
              ? `<a href="${project.preview_url}" target="_blank">Open Preview</a>`
              : `<span>No preview yet</span>`
          }
          <span>${project.folder_path}</span>
        </div>
      `;

      projectsGallery.appendChild(card);
    });
  } catch (error) {
    projectsGallery.textContent = error.message;
  }
}

if (refreshProjectsBtn) {
  refreshProjectsBtn.addEventListener("click", loadProjects);
}

window.addEventListener("load", loadProjects);