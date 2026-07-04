const express = require("express");
const http = require("http");
const path = require("path");
const cors = require("cors");
const WebSocket = require("ws");

const PORT = process.env.PORT || 7071;
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

let desktop = {
  online: false,
  deviceName: "",
  hostname: "",
  osPlatform: "",
  osRelease: "",
  mode: "script-only",
  version: "",
  connectedAt: "",
  lastHeartbeatAt: ""
};

const browsers = new Set();

function send(ws, data) {
  if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(data));
}

function broadcastStatus() {
  for (const browser of browsers) {
    send(browser, { type: "DEVICE_STATUS", desktop });
  }
}

wss.on("connection", (ws) => {
  ws.role = "unknown";

  ws.on("message", (raw) => {
    let msg;
    try {
      msg = JSON.parse(raw.toString());
    } catch {
      send(ws, { type: "ERROR", message: "Invalid JSON" });
      return;
    }

    if (msg.type === "REGISTER_BROWSER") {
      ws.role = "browser";
      browsers.add(ws);
      send(ws, { type: "DEVICE_STATUS", desktop });
      send(ws, { type: "LOG", message: "Browser connected to gateway." });
      return;
    }

    if (msg.type === "REGISTER_DESKTOP_COMPANION") {
      ws.role = "desktop";
      desktop = {
        online: true,
        deviceName: msg.deviceName || "Unknown",
        hostname: msg.hostname || "",
        osPlatform: msg.osPlatform || "",
        osRelease: msg.osRelease || "",
        mode: msg.mode || "script-only",
        version: msg.version || "FP-2B",
        connectedAt: new Date().toISOString(),
        lastHeartbeatAt: new Date().toISOString()
      };
      send(ws, { type: "REGISTERED", message: "Desktop Companion registered." });
      broadcastStatus();
      return;
    }

    if (msg.type === "DESKTOP_HEARTBEAT") {
      desktop.online = true;
      desktop.lastHeartbeatAt = new Date().toISOString();
      broadcastStatus();
    }
  });

  ws.on("close", () => {
    if (ws.role === "browser") browsers.delete(ws);
    if (ws.role === "desktop") {
      desktop.online = false;
      broadcastStatus();
    }
  });
});

server.listen(PORT, () => {
  console.log(`ForgePilot Cloud Gateway running on http://localhost:${PORT}`);
});
