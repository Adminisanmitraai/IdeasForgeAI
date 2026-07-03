const fs = require("fs/promises");
const os = require("os");
const path = require("path");
const WebSocket = require("ws");

const SERVER_URL = process.env.DESKTOP_COMPANION_SERVER_URL || "ws://localhost:7070";
const DEVICE_NAME = os.hostname();
const MODE = "script-only";

function log(message, extra) {
  if (extra !== undefined) {
    console.log(`[LaptopAgent] ${message}`, extra);
    return;
  }
  console.log(`[LaptopAgent] ${message}`);
}

function desktopFilePath() {
  return path.join(os.homedir(), "Desktop", "ideasforgeai_connection_test.txt");
}

function buildFileContent(task) {
  return [
    "IdeasForgeAI ForgePilot Desktop Companion",
    `Device name: ${DEVICE_NAME}`,
    `Task received: ${task}`,
    "Status completed",
    "Script-only mode confirmation",
  ].join("\n");
}

async function runTestTask(socket, task) {
  const filePath = desktopFilePath();
  try {
    await fs.writeFile(filePath, buildFileContent(task), "utf8");
    log(`File created: ${filePath}`);
    socket.send(
      JSON.stringify({
        type: "TASK_RESULT",
        success: true,
        message: "Test task completed successfully.",
        createdFilePath: filePath,
      })
    );
  } catch (error) {
    log("Failed to create Desktop test file.", error.message);
    socket.send(
      JSON.stringify({
        type: "TASK_RESULT",
        success: false,
        message: `Failed to create Desktop test file: ${error.message}`,
        createdFilePath: null,
      })
    );
  }
}

function connect() {
  const socket = new WebSocket(SERVER_URL);

  socket.on("open", () => {
    log(`Connected to ${SERVER_URL}`);
    socket.send(
      JSON.stringify({
        type: "REGISTER_LAPTOP",
        deviceName: DEVICE_NAME,
        mode: MODE,
      })
    );
    log(`Registered laptop agent: ${DEVICE_NAME} (${MODE})`);
  });

  socket.on("message", async (rawData) => {
    try {
      const payload = JSON.parse(rawData.toString());
      if (payload.type !== "RUN_TEST_TASK") {
        return;
      }

      const task = String(payload.task || "No task provided.");
      log(`Received task: ${task}`);
      await runTestTask(socket, task);
    } catch (error) {
      log("Error processing incoming message.", error.message);
    }
  });

  socket.on("close", () => {
    log("Connection closed.");
  });

  socket.on("error", (error) => {
    log("Connection error.", error.message);
  });
}

connect();
