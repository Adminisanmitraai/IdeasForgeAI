const WebSocket = require("ws");
const os = require("os");

const gatewayUrl = process.env.FORGEPILOT_GATEWAY_URL || "ws://localhost:7071";
let ws = null;
let heartbeatTimer = null;
let pendingPairing = false;

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

process.stdin.on("data", (input) => {
  const answer = input.trim().toLowerCase();

  if (!pendingPairing) return;

  if (answer === "y") {
    send({ type: "APPROVE_PAIRING" });
    log("Pairing approved by user.");
  } else {
    send({ type: "DENY_PAIRING" });
    log("Pairing denied by user.");
  }

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
      mode: "script-only",
      version: "FP-2C"
    });

    heartbeatTimer = setInterval(() => {
      send({ type: "DESKTOP_HEARTBEAT" });
    }, 5000);
  });

  ws.on("message", (raw) => {
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

    if (msg.type === "PAIRING_APPROVED") {
      log("Trusted session established.");
    }
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
