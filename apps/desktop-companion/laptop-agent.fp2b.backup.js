const WebSocket = require("ws");
const os = require("os");

const gatewayUrl = process.env.FORGEPILOT_GATEWAY_URL || "ws://localhost:7071";
let ws = null;
let heartbeatTimer = null;

function log(message) {
  console.log(`[DesktopCompanion] ${message}`);
}

function connect() {
  log(`Connecting to gateway: ${gatewayUrl}`);
  ws = new WebSocket(gatewayUrl);

  ws.on("open", () => {
    log("Connected to ForgePilot Gateway");

    ws.send(JSON.stringify({
      type: "REGISTER_DESKTOP_COMPANION",
      deviceName: os.hostname(),
      hostname: os.hostname(),
      osPlatform: os.platform(),
      osRelease: os.release(),
      mode: "script-only",
      version: "FP-2B"
    }));

    log("Registered with gateway");

    heartbeatTimer = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "DESKTOP_HEARTBEAT" }));
        log("Heartbeat sent");
      }
    }, 5000);
  });

  ws.on("message", (raw) => {
    log(`Gateway message: ${raw.toString()}`);
  });

  ws.on("close", () => {
    log("Disconnected from gateway");
    if (heartbeatTimer) clearInterval(heartbeatTimer);
    setTimeout(connect, 5000);
  });

  ws.on("error", (err) => {
    log(`Connection error: ${err.message}`);
  });
}

connect();
