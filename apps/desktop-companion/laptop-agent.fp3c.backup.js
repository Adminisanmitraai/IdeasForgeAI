const WebSocket = require("ws");
const os = require("os");
const screenshot = require("screenshot-desktop");
const sharp = require("sharp");
const { mouse, Button, Point, keyboard, Key } = require("@nut-tree-fork/nut-js");

const gatewayUrl = process.env.FORGEPILOT_GATEWAY_URL || "ws://localhost:7071";
let ws = null;
let heartbeatTimer = null;
let pendingPairing = false;
let screenStreaming = false;
let screenTimer = null;

const SCREEN_WIDTH = 1280;
const SCREEN_QUALITY = 60;
const SCREEN_INTERVAL = 400;

process.stdin.setEncoding("utf8");
process.stdin.resume();

function log(message) {
  console.log(`[DesktopCompanion] ${message}`);
}

function send(data) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(data));
  }
}

async function captureAndSendScreen() {
  try {
    const raw = await screenshot({ format: "png" });
    const jpeg = await sharp(raw)
      .resize({ width: SCREEN_WIDTH, withoutEnlargement: true })
      .jpeg({ quality: SCREEN_QUALITY })
      .toBuffer();

    send({
      type: "SCREEN_FRAME",
      image: jpeg.toString("base64"),
      timestamp: Date.now()
    });
  } catch (err) {
    send({ type: "SCREEN_ERROR", message: err.message });
  }
}

process.stdin.on("data", (input) => {
  const answer = input.trim().toLowerCase();
  if (!pendingPairing) return;

  send({ type: answer === "y" ? "APPROVE_PAIRING" : "DENY_PAIRING" });
  log(answer === "y" ? "Pairing approved by user." : "Pairing denied by user.");
  pendingPairing = false;
});

function connect() {
  log(`Connecting to gateway: ${gatewayUrl}`);
  ws = new WebSocket(gatewayUrl);

  ws.on("open", () => {
    log("Connected to ForgePilot Gateway");
    send({
      type: "REGISTER_DESKTOP_COMPANION",
      deviceName: os.hostname(),
      hostname: os.hostname(),
      osPlatform: os.platform(),
      osRelease: os.release(),
      mode: "mouse + keyboard + screen-preview",
      version: "FP-3C-1"
    });

    heartbeatTimer = setInterval(() => send({ type: "DESKTOP_HEARTBEAT" }), 5000);
  });

  ws.on("message", async (raw) => {
    const msg = JSON.parse(raw.toString());

    if (msg.type === "PAIRING_REQUEST") {
      pendingPairing = true;
      console.log("");
      console.log("======================================");
      console.log("ForgePilot Pairing Request");
      console.log(`Pairing Code: ${msg.pairingCode}`);
      console.log("Approve this browser connection?");
      console.log("Type y and press Enter to approve.");
      console.log("Type n and press Enter to deny.");
      console.log("======================================");
      console.log("");
    }

    if (msg.type === "START_SCREEN_STREAM") {
      if (!screenStreaming) {
        screenStreaming = true;
        screenTimer = setInterval(captureAndSendScreen, SCREEN_INTERVAL);
        send({ type: "SCREEN_STATUS", status: "started" });
        log("Screen stream started.");
      }
    }

    if (msg.type === "STOP_SCREEN_STREAM") {
      screenStreaming = false;
      if (screenTimer) clearInterval(screenTimer);
      screenTimer = null;
      send({ type: "SCREEN_STATUS", status: "stopped" });
      log("Screen stream stopped.");
    }
  });

  ws.on("close", () => {
    log("Disconnected from gateway");
    if (heartbeatTimer) clearInterval(heartbeatTimer);
    if (screenTimer) clearInterval(screenTimer);
    screenStreaming = false;
    setTimeout(connect, 5000);
  });

  ws.on("error", (err) => log(`Connection error: ${err.message}`));
}

connect();
