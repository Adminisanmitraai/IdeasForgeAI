const WebSocket = require("ws");
const os = require("os");
const { mouse, Button, Point } = require("@nut-tree-fork/nut-js");

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

async function handleMouseCommand(msg) {
  try {
    if (msg.action === "MOVE") {
      const pos = await mouse.getPosition();
      const dx = Math.max(-100, Math.min(100, Number(msg.dx || 0)));
      const dy = Math.max(-100, Math.min(100, Number(msg.dy || 0)));
      await mouse.setPosition(new Point(pos.x + dx, pos.y + dy));
      send({ type: "MOUSE_RESULT", message: `Mouse moved by ${dx}, ${dy}` });
      return;
    }

    if (msg.action === "LEFT_CLICK") {
      await mouse.click(Button.LEFT);
      send({ type: "MOUSE_RESULT", message: "Left click completed." });
      return;
    }

    if (msg.action === "RIGHT_CLICK") {
      await mouse.click(Button.RIGHT);
      send({ type: "MOUSE_RESULT", message: "Right click completed." });
      return;
    }

    if (msg.action === "DOUBLE_CLICK") {
      await mouse.doubleClick(Button.LEFT);
      send({ type: "MOUSE_RESULT", message: "Double click completed." });
      return;
    }

    send({ type: "MOUSE_RESULT", message: "Unknown mouse action blocked." });
  } catch (error) {
    send({ type: "MOUSE_RESULT", message: `Mouse command failed: ${error.message}` });
  }
}

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
      mode: "script-only + mouse-control",
      version: "FP-3A"
    });

    heartbeatTimer = setInterval(() => {
      send({ type: "DESKTOP_HEARTBEAT" });
    }, 5000);
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

    if (msg.type === "PAIRING_APPROVED") {
      log("Trusted session established.");
    }

    if (msg.type === "MOUSE_COMMAND") {
      await handleMouseCommand(msg);
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
