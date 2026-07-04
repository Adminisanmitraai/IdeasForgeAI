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
const wss = new WebSocket.Server({ server, maxPayload: 20 * 1024 * 1024 });

let desktopSocket = null;
let pairingCode = null;
let trusted = false;

let desktop = {
  online: false,
  trusted: false,
  pairingCode: "",
  deviceName: "",
  mode: "mouse + keyboard + screen-preview",
  version: "",
  lastHeartbeatAt: ""
};

const browsers = new Set();

function send(ws, data) {
  if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(data));
}

function broadcast(data) {
  for (const browser of browsers) send(browser, data);
}

function broadcastStatus() {
  desktop.trusted = trusted;
  desktop.pairingCode = pairingCode || "";
  broadcast({ type: "DEVICE_STATUS", desktop });
}

function makePairingCode() {
  return String(Math.floor(100000 + Math.random() * 900000));
}

function forwardToDesktop(ws, msg, label) {
  if (ws.role !== "browser") return;

  if (!trusted) {
    send(ws, { type: "LOG", message: `${label} blocked: desktop is not trusted.` });
    return;
  }

  if (!desktopSocket || desktopSocket.readyState !== WebSocket.OPEN) {
    send(ws, { type: "LOG", message: `${label} blocked: desktop offline.` });
    return;
  }

  send(desktopSocket, msg);
  broadcast({ type: "LOG", message: `${label} sent.` });
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
      desktopSocket = ws;
      desktop = {
        online: true,
        trusted,
        pairingCode: pairingCode || "",
        deviceName: msg.deviceName || "Unknown",
        mode: msg.mode || "mouse + keyboard + screen-preview",
        version: msg.version || "FP-3D-1",
        lastHeartbeatAt: new Date().toISOString()
      };
      send(ws, { type: "REGISTERED" });
      broadcast({ type: "LOG", message: `Desktop connected: ${desktop.deviceName}` });
      broadcastStatus();
      return;
    }

    if (msg.type === "DESKTOP_HEARTBEAT") {
      desktop.online = true;
      desktop.lastHeartbeatAt = new Date().toISOString();
      broadcastStatus();
      return;
    }

    if (msg.type === "REQUEST_PAIRING") {
      pairingCode = makePairingCode();
      trusted = false;
      send(desktopSocket, { type: "PAIRING_REQUEST", pairingCode });
      broadcast({ type: "LOG", message: `Pairing requested. Code: ${pairingCode}` });
      broadcastStatus();
      return;
    }

    if (msg.type === "APPROVE_PAIRING" && ws.role === "desktop") {
      trusted = true;
      send(ws, { type: "PAIRING_APPROVED" });
      broadcast({ type: "LOG", message: "Desktop approved pairing. Trusted session established." });
      broadcastStatus();
      return;
    }

    if (msg.type === "START_SCREEN_STREAM" || msg.type === "STOP_SCREEN_STREAM") {
      forwardToDesktop(ws, msg, msg.type);
      return;
    }

    if (msg.type === "MOUSE_COMMAND" || msg.type === "KEYBOARD_COMMAND" || msg.type === "PREVIEW_CLICK") {
      forwardToDesktop(ws, msg, msg.type);
      return;
    }

    if (msg.type === "SCREEN_FRAME") {
      if (ws.role !== "desktop") return;
      broadcast({
        type: "SCREEN_FRAME",
        image: msg.image,
        timestamp: msg.timestamp,
        screenWidth: msg.screenWidth,
        screenHeight: msg.screenHeight
      });
      return;
    }

    if (msg.type.endsWith("_RESULT") || msg.type === "SCREEN_STATUS" || msg.type === "SCREEN_ERROR") {
      if (ws.role !== "desktop") return;
      broadcast({ type: "LOG", message: msg.message || `${msg.type} received.` });
      return;
    }
  });

  ws.on("close", () => {
    if (ws.role === "browser") browsers.delete(ws);
    if (ws.role === "desktop") {
      desktop.online = false;
      desktopSocket = null;
      broadcast({ type: "LOG", message: "Desktop disconnected." });
      broadcastStatus();
    }
  });
});

server.listen(PORT, () => {
  console.log(`ForgePilot Cloud Gateway FP-3D-1 running on http://localhost:${PORT}`);
});
