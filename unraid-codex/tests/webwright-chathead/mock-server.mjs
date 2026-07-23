import fs from "node:fs"
import http from "node:http"
import path from "node:path"
import { createRequire } from "node:module"

const require = createRequire(new URL("../../web-src/package.json", import.meta.url))
const { WebSocketServer } = require("ws")

const port = Number(process.env.PORT ?? 4173)
const pluginRoot = path.resolve(
  import.meta.dirname,
  "../../source/usr/local/emhttp/plugins/unraid-codex/web",
)

const html = `<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Unraid Codex UI Harness</title>
    <style>
      body { margin: 0; background: #f2f2f2; color: #202020; font: 14px Arial, sans-serif; }
      header { padding: 22px 28px; background: #242c38; color: white; }
      nav { display: flex; gap: 24px; margin-top: 18px; text-transform: uppercase; letter-spacing: .12em; }
      main { padding: 28px; }
      .cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
      .card { min-height: 150px; padding: 18px; border: 1px solid #d3d3d3; border-radius: 8px; background: white; }
    </style>
  </head>
  <body>
    <header><strong>UNRAID</strong><nav><span>Dashboard</span><span>Main</span><span>Shares</span><span>Settings</span></nav></header>
    <main>
      <h1>Incus</h1>
      <div class="cards"><div class="card">Containers</div><div class="card">Storage</div><div class="card">Network</div></div>
    </main>
    <script src="/plugins/unraid-codex/web/unraid-codex.js"></script>
  </body>
</html>`

const server = http.createServer((request, response) => {
  const requestPath = new URL(request.url, `http://${request.headers.host}`).pathname
  if (requestPath === "/plugins/unraid-codex/web/unraid-codex.js") {
    response.setHeader("content-type", "text/javascript")
    response.end(fs.readFileSync(path.join(pluginRoot, "unraid-codex.js")))
    return
  }
  if (requestPath === "/plugins/unraid-codex/web/unraid-codex.css") {
    response.setHeader("content-type", "text/css")
    response.end(fs.readFileSync(path.join(pluginRoot, "unraid-codex.css")))
    return
  }
  response.setHeader("content-type", "text/html")
  response.end(html)
})

const webSocketServer = new WebSocketServer({ noServer: true })
server.on("upgrade", (request, socket, head) => {
  if (request.url !== "/webterminal/unraid-codex-appserver/ws") {
    socket.destroy()
    return
  }
  webSocketServer.handleUpgrade(request, socket, head, (webSocket) => {
    webSocketServer.emit("connection", webSocket)
  })
})

function send(webSocket, method, params) {
  webSocket.send(JSON.stringify({ method, params }))
}

function response(webSocket, id, result) {
  webSocket.send(JSON.stringify({ id, result }))
}

webSocketServer.on("connection", (webSocket) => {
  webSocket.on("message", (buffer) => {
    const message = JSON.parse(buffer.toString())
    if (!Object.hasOwn(message, "id")) return
    if (!message.method && message.id === "approval-1") {
      send(webSocket, "turn/completed", {
        threadId: "thread-mock",
        turn: {
          id: "turn-mock",
          status: "completed",
          items: [],
          itemsView: "full",
          error: null,
        },
      })
      return
    }
    switch (message.method) {
      case "initialize":
        response(webSocket, message.id, {
          userAgent: "codex-cli/0.145.0",
          platformFamily: "unix",
          platformOs: "linux",
          platformArch: "x86_64",
        })
        break
      case "account/read":
        response(webSocket, message.id, {
          account: { type: "chatgpt", email: "agent@example.test", planType: "plus" },
          requiresOpenaiAuth: true,
        })
        break
      case "model/list":
        response(webSocket, message.id, { data: [] })
        break
      case "thread/resume":
        response(webSocket, message.id, {
          thread: {
            id: message.params.threadId,
            turns: [],
          },
        })
        break
      case "thread/start":
        response(webSocket, message.id, { thread: { id: "thread-mock", turns: [] } })
        break
      case "turn/start": {
        const turnId = "turn-mock"
        response(webSocket, message.id, { turn: { id: turnId } })
        send(webSocket, "turn/started", { threadId: "thread-mock", turn: { id: turnId } })
        const reasoning = {
          type: "reasoning",
          id: "reasoning-1",
          summary: ["Inspecting the workspace and current services."],
          content: [],
        }
        send(webSocket, "item/started", {
          threadId: "thread-mock",
          turnId,
          item: reasoning,
          startedAtMs: Date.now(),
        })
        send(webSocket, "item/completed", {
          threadId: "thread-mock",
          turnId,
          item: reasoning,
          completedAtMs: Date.now() + 400,
        })
        send(webSocket, "turn/plan/updated", {
          threadId: "thread-mock",
          turnId,
          explanation: "Inspect and report",
          plan: [
            { step: "Inspect the container", status: "completed" },
            { step: "Verify the service", status: "in_progress" },
            { step: "Summarize the result", status: "pending" },
          ],
        })
        const command = {
          type: "commandExecution",
          id: "command-1",
          command: "systemctl is-active codex-appserver",
          cwd: "/workspace",
          status: "completed",
          aggregatedOutput: "active\n",
          exitCode: 0,
        }
        send(webSocket, "item/started", {
          threadId: "thread-mock",
          turnId,
          item: { ...command, status: "inProgress", aggregatedOutput: "" },
          startedAtMs: Date.now(),
        })
        send(webSocket, "item/completed", {
          threadId: "thread-mock",
          turnId,
          item: command,
          completedAtMs: Date.now() + 700,
        })
        const tool = {
          type: "mcpToolCall",
          id: "tool-1",
          server: "labby",
          tool: "time.get_current_time",
          arguments: { timezone: "UTC" },
          status: "completed",
          result: {
            content: [{ type: "text", text: "2026-07-23 05:20 UTC" }],
            structuredContent: null,
          },
          error: null,
        }
        send(webSocket, "item/started", {
          threadId: "thread-mock",
          turnId,
          item: { ...tool, status: "inProgress", result: null },
          startedAtMs: Date.now(),
        })
        send(webSocket, "item/completed", {
          threadId: "thread-mock",
          turnId,
          item: tool,
          completedAtMs: Date.now() + 900,
        })
        const answer = {
          type: "agentMessage",
          id: "message-1",
          text: "The app server is active and the read-only Labby check succeeded.",
          phase: "final_answer",
          memoryCitation: null,
        }
        send(webSocket, "item/started", {
          threadId: "thread-mock",
          turnId,
          item: { ...answer, text: "" },
          startedAtMs: Date.now(),
        })
        send(webSocket, "item/agentMessage/delta", {
          threadId: "thread-mock",
          turnId,
          itemId: answer.id,
          delta: answer.text,
        })
        send(webSocket, "item/completed", {
          threadId: "thread-mock",
          turnId,
          item: answer,
          completedAtMs: Date.now() + 1100,
        })
        webSocket.send(
          JSON.stringify({
            id: "approval-1",
            method: "item/commandExecution/requestApproval",
            params: {
              threadId: "thread-mock",
              turnId,
              itemId: "approval-command",
              command: "touch /workspace/approved",
              reason: "Create a test marker in the workspace.",
            },
          }),
        )
        break
      }
      case "turn/interrupt":
        response(webSocket, message.id, {})
        break
      default:
        response(webSocket, message.id, {})
    }
  })
})

server.listen(port, "127.0.0.1", () => {
  process.stdout.write(`mock server listening on http://127.0.0.1:${port}\n`)
})
