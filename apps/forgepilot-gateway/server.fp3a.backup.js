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

let desktopSocket = null;
let pairingCode = null;
let trusted = false;

let desktop = {
  online: false,
  trusted: false,
  pairingCode: "",
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
        hostname: msg.hostname || "",
        osPlatform: msg.osPlatform || "",
        osRelease: msg.osRelease || "",
        mode: msg.mode || "script-only",
        version: msg.version || "FP-3A",
        connectedAt: new Date().toISOString(),
        lastHeartbeatAt: new Date().toISOString()
      };
      send(ws, { type: "REGISTERED", message: "Desktop Companion registered." });
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
      if (!desktop.online || !desktopSocket) {
        send(ws, { type: "LOG", message: "No desktop online for pairing." });
        return;
      }

      pairingCode = makePairingCode();
      trusted = false;

      send(desktopSocket, {
        type: "PAIRING_REQUEST",
        pairingCode,
        message: "Browser requested pairing."
      });

      broadcast({ type: "LOG", message: `Pairing requested. Code: ${pairingCode}` });
      broadcastStatus();
      return;
    }

    if (msg.type === "APPROVE_PAIRING") {
      if (ws.role !== "desktop") return;

      trusted = true;
      broadcast({ type: "LOG", message: "Desktop approved pairing. Trusted session established." });
      send(ws, { type: "PAIRING_APPROVED", message: "Trusted session established." });
      broadcastStatus();
      return;
    }

    if (msg.type === "DENY_PAIRING") {
      if (ws.role !== "desktop") return;

      trusted = false;
      pairingCode = null;
      broadcast({ type: "LOG", message: "Desktop denied pairing." });
      broadcastStatus();
      return;
    }

    if (msg.type === "MOUSE_COMMAND") {
      if (ws.role !== "browser") return;

      if (!trusted) {
        send(ws, { type: "LOG", message: "Mouse command blocked: desktop is not trusted." });
        return;
      }

      if (!desktopSocket || desktopSocket.readyState !== WebSocket.OPEN) {
        send(ws, { type: "LOG", message: "Mouse command blocked: desktop offline." });
        return;
      }

      const allowedActions = ["MOVE", "LEFT_CLICK", "RIGHT_CLICK", "DOUBLE_CLICK"];
      if (!allowedActions.includes(msg.action)) {
        send(ws, { type: "LOG", message: "Mouse command blocked: invalid action." });
        return;
      }

      send(desktopSocket, {
        type: "MOUSE_COMMAND",
        action: msg.action,
        dx: Number(msg.dx || 0),
        dy: Number(msg.dy || 0)
      });

      broadcast({ type: "LOG", message: `Mouse command sent: ${msg.action}` });
      return;
    }

    if (msg.type === "MOUSE_RESULT") {
      if (ws.role !== "desktop") return;
      broadcast({ type: "LOG", message: msg.message || "Mouse command completed." });
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
  console.log(`ForgePilot Cloud Gateway FP-3A running on http://localhost:${PORT}`);
});
