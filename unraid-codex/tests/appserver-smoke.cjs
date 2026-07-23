#!/usr/bin/env node
"use strict";

const WebSocket = require(process.env.WS_MODULE || "ws");

const socketPath = process.argv[2] || "/run/unraid-codex/appserver.sock";
const socket = new WebSocket(`ws+unix://${socketPath}:/`, {
  perMessageDeflate: false,
});
const pending = new Map();
let nextId = 1;

function request(method, params = {}) {
  const id = nextId++;
  socket.send(JSON.stringify({ id, method, params }));
  return new Promise((resolve, reject) => {
    pending.set(String(id), { resolve, reject });
  });
}

socket.on("message", (data) => {
  const message = JSON.parse(data.toString());
  if (!Object.prototype.hasOwnProperty.call(message, "id") || message.method) return;
  const waiter = pending.get(String(message.id));
  if (!waiter) return;
  pending.delete(String(message.id));
  if (message.error) waiter.reject(new Error(message.error.message || "request failed"));
  else waiter.resolve(message.result);
});

socket.on("error", (error) => {
  console.error(error.message);
  process.exitCode = 1;
});

socket.on("open", async () => {
  try {
    await request("initialize", {
      clientInfo: { name: "unraid-codex-smoke", title: "Unraid Codex Smoke", version: "0.1.0" },
      capabilities: {
        experimentalApi: true,
        requestAttestation: false,
        mcpServerOpenaiFormElicitation: true,
      },
    });
    socket.send(JSON.stringify({ method: "initialized", params: {} }));

    const account = await request("account/read", { refreshToken: false });
    const started = await request("thread/start", {
      cwd: "/workspace",
      approvalPolicy: {
        granular: {
          sandbox_approval: true,
          rules: true,
          skill_approval: true,
          request_permissions: true,
          mcp_elicitations: true,
        },
      },
      sandbox: "danger-full-access",
      serviceName: "unraid-chathead-smoke",
    });
    const threadId = started.thread.id;
    let resumed = null;
    let resumeDeferredUntilFirstTurn = false;
    try {
      resumed = await request("thread/resume", { threadId });
    } catch (error) {
      if (Boolean(account.requiresOpenaiAuth && !account.account) &&
          error.message.includes("no rollout found")) {
        resumeDeferredUntilFirstTurn = true;
      } else {
        throw error;
      }
    }
    const mcp = await request("mcpServerStatus/list", { threadId });
    const servers = mcp.data || mcp.servers || [];

    console.log(
      JSON.stringify({
        initialized: true,
        accountRequired: Boolean(account.requiresOpenaiAuth && !account.account),
        threadStarted: Boolean(threadId),
        threadResumed: resumed ? resumed.thread.id === threadId : false,
        resumeDeferredUntilFirstTurn,
        mcpServers: servers.map((server) => server.name || server.id).filter(Boolean),
      }),
    );
    socket.close();
  } catch (error) {
    console.error(error.message);
    socket.close();
    process.exitCode = 1;
  }
});

setTimeout(() => {
  console.error("app-server smoke timed out");
  socket.terminate();
  process.exit(1);
}, 20_000).unref();
