import { describe, expect, it } from "vitest";
import { IncusExecService } from "./incus-exec.service.js";

class FakeSocket {
  readyState = 1;
  closed = 0;
  terminated = 0;
  close() { this.closed++; this.readyState = 3; }
  terminate() { this.terminated++; this.readyState = 3; }
}

describe("IncusExecService session cleanup", () => {
  it("closes both websocket peers and removes the session", () => {
    const service = new IncusExecService({ get: () => undefined } as never, { socketPath: "/tmp/incus.sock" } as never);
    const ioSocket = new FakeSocket();
    const controlSocket = new FakeSocket();
    const sessions = (service as unknown as { sessions: Map<string, unknown> }).sessions;
    sessions.set("session", {
      jailName: "agent",
      ioSocket,
      controlSocket,
      idleTimer: setTimeout(() => undefined, 60_000),
      lifetimeTimer: setTimeout(() => undefined, 60_000),
    });

    expect(service.stop("session")).toBe(true);
    expect(ioSocket.closed).toBe(1);
    expect(controlSocket.closed).toBe(1);
    expect(sessions.has("session")).toBe(false);
    expect(service.stop("session")).toBe(false);
  });
});
