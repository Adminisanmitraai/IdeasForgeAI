const express = require("express");
const cors = require("cors");
const http = require("http");
const path = require("path");
const WebSocket = require("ws");

const PORT = Number(process.env.PORT || 7070);

const app = express();
app.use(cors());
app.use(express.static(path.join(__dirname, "public")));

app.get("/", (_req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

let laptopSocket = null;
const browserSockets = new Set();
const laptopState = {
  online: false,
  deviceName: "Unavailable",
  mode: "script-only",
};

function log(message, extra) {
  if (extra !== undefined) {
    console.log(`[DesktopCompanion] ${message}`, extra);
    return;
  }
  console.log(`[DesktopCompanion] ${message}`);
}

function sendJson(socket, payload) {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    return false;
  }

  try {
    socket.send(JSON.stringify(payload));
    return true;
  } catch (error) {
    log("Failed to send payload.", error.message);
    return false;
  }
}

function broadcastToBrowsers(payload) {
  for (const socket of browserSockets) {
    sendJson(socket, payload);
  }
}

function currentStatusPayload() {
  return {
    type: "LAPTOP_STATUS",
    online: laptopState.online,
    deviceName: laptopState.deviceName,
    mode: laptopState.mode,
  };
}

function setLaptopOffline(reason) {
  laptopSocket = null;
  laptopState.online = false;
  laptopState.deviceName = "Unavailable";
  laptopState.mode = "script-only";
  log(`Laptop agent offline${reason ? `: ${reason}` : ""}`);
  broadcastToBrowsers(currentStatusPayload());
}

function parsePayload(rawData) {
  try {
    return { ok: true, value: JSON.parse(rawData.toString()) };
  } catch (error) {
    return { ok: false, error };
  }
}

wss.on("connection", (socket, request) => {
  log(`WebSocket client connected from ${request.socket.remoteAddress || "unknown"}`);

  socket.on("message", (rawData) => {
    const parsed = parsePayload(rawData);
    if (!parsed.ok) {
      log("Invalid JSON received.");
      sendJson(socket, {
        type: "ERROR",
        message: "Invalid JSON payload.",
      });
      return;
    }

    const payload = parsed.value;
    const messageType = payload.type || "";

    if (messageType === "REGISTER_BROWSER") {
      socket.clientType = "browser";
      browserSockets.add(socket);
      log("Browser/mobile agent registered.");
      sendJson(socket, {
        type: "INFO",
        message: "Browser/mobile agent connected to Desktop Companion.",
      });
      sendJson(socket, currentStatusPayload());
      return;
    }

    if (messageType === "REGISTER_LAPTOP") {
      socket.clientType = "laptop";
      laptopSocket = socket;
      laptopState.online = true;
      laptopState.deviceName = String(payload.deviceName || "Unnamed Device");
      laptopState.mode = "script-only";
      log(`Laptop agent registered: ${laptopState.deviceName}`);
      broadcastToBrowsers(currentStatusPayload());
      return;
    }

    if (messageType === "RUN_TEST_TASK") {
      if (socket.clientType !== "browser") {
        sendJson(socket, {
          type: "ERROR",
          message: "Only the browser/mobile agent can request RUN_TEST_TASK.",
        });
        return;
      }

      if (!laptopSocket || laptopSocket.readyState !== WebSocket.OPEN) {
        log("RUN_TEST_TASK requested while laptop agent is offline.");
        sendJson(socket, {
          type: "TASK_RESULT",
          success: false,
          message: "Laptop agent is offline.",
          createdFilePath: null,
          deviceName: laptopState.deviceName,
        });
        return;
      }

      const task = String(
        payload.task || "Create the IdeasForgeAI connection test file on Desktop."
      ).trim();
      log("Relaying safe test task to laptop agent.");
      sendJson(laptopSocket, {
        type: "RUN_TEST_TASK",
        task,
      });
      return;
    }

    if (messageType === "TASK_RESULT") {
      if (socket.clientType !== "laptop") {
        sendJson(socket, {
          type: "ERROR",
          message: "Only the laptop agent can send TASK_RESULT.",
        });
        return;
      }

      log("Task result received from laptop agent.", {
        success: Boolean(payload.success),
        createdFilePath: payload.createdFilePath || null,
      });
      broadcastToBrowsers({
        type: "TASK_RESULT",
        success: Boolean(payload.success),
        message: String(payload.message || "Task completed."),
        createdFilePath: payload.createdFilePath || null,
        deviceName: laptopState.deviceName,
      });
      return;
    }

    sendJson(socket, {
      type: "ERROR",
      message: `Unsupported message type: ${messageType || "unknown"}`,
    });
  });

  socket.on("close", () => {
    if (socket.clientType === "browser") {
      browserSockets.delete(socket);
      log("Browser/mobile agent disconnected.");
    }

    if (socket.clientType === "laptop" && socket === laptopSocket) {
      setLaptopOffline("socket closed");
    }
  });

  socket.on("error", (error) => {
    log("Socket error.", error.message);
  });
});

server.on("error", (error) => {
  log("Server error.", error.message);
});

server.listen(PORT, () => {
  log(`Desktop Companion server listening at http://localhost:${PORT}`);
});
