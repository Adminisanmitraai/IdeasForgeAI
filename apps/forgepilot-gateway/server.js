const cors = require("cors");
const express = require("express");
const http = require("http");
const path = require("path");
const WebSocket = require("ws");

const PORT = 7071;
const STATUS_PAYLOAD = {
  type: "gateway-status",
  title: "ForgePilot Cloud Gateway",
  status: "Waiting for Desktop Companion...",
  desktopMessage: "No desktop communication yet.",
  heartbeatMessage: "No heartbeat yet.",
  pairingMessage: "No pairing yet.",
  taskRelayMessage: "No task relay yet."
};

const app = express();
app.use(cors());
app.use(express.static(path.join(__dirname, "public")));

app.get("/", (_req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

function sendStatus(socket) {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(STATUS_PAYLOAD));
  }
}

wss.on("connection", (socket) => {
  sendStatus(socket);

  socket.on("message", () => {
    sendStatus(socket);
  });
});

server.listen(PORT, () => {
  console.log(`ForgePilot Cloud Gateway listening at http://localhost:${PORT}`);
});
