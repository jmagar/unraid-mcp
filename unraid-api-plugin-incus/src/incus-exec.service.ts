import { Injectable, Logger, OnModuleDestroy } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { request as httpRequest } from "node:http";
import { randomUUID } from "node:crypto";
import WebSocket from "ws";
import { PubSub } from "graphql-subscriptions";

interface ExecSession {
  jailName: string;
  ioSocket: WebSocket;
  controlSocket: WebSocket;
}

const OUTPUT_TOPIC_PREFIX = "jailExecOutput:";

/**
 * Bridges a browser-facing GraphQL subscription/mutations to Incus's own
 * interactive exec websocket protocol (POST /1.0/instances/{name}/exec with
 * wait-for-websocket+interactive, then two raw websockets over the SAME unix
 * socket: fd "0" for combined stdin/stdout, fd "control" for resize/signals).
 * We don't expose a new HTTP/WS endpoint of our own — the browser only ever
 * talks GraphQL (queries/mutations + the existing graphql-ws subscription
 * transport already wired up on /graphql), so this rides on auth/proxying
 * that already works, instead of needing a new reverse-proxy route.
 */
@Injectable()
export class IncusExecService implements OnModuleDestroy {
  private readonly logger = new Logger(IncusExecService.name);
  private readonly sessions = new Map<string, ExecSession>();
  readonly pubsub = new PubSub();

  constructor(private readonly config: ConfigService) {}

  private get socketPath(): string {
    const dir = this.config.get<string>("incus.stateDir", "/mnt/user/appdata/incus");
    return `${dir}/unix.socket`;
  }

  onModuleDestroy() {
    for (const sessionId of this.sessions.keys()) this.stop(sessionId);
  }

  async start(jailName: string, cols = 80, rows = 24): Promise<string> {
    const { operationUrl, fds } = await this.requestExec(jailName, cols, rows);
    if (!fds?.["0"] || !fds?.control) {
      throw new Error("Incus exec response missing websocket fd secrets");
    }

    const sessionId = randomUUID();
    const ioSocket = this.connectOperationSocket(operationUrl, fds["0"]);
    const controlSocket = this.connectOperationSocket(operationUrl, fds.control);

    ioSocket.on("message", (data, isBinary) => {
      const text = isBinary ? Buffer.from(data as Buffer).toString("utf-8") : data.toString();
      void this.pubsub.publish(OUTPUT_TOPIC_PREFIX + sessionId, { jailExecOutput: text });
    });
    ioSocket.on("close", () => this.sessions.delete(sessionId));
    ioSocket.on("error", (err) => this.logger.warn(`exec io socket error (${sessionId}): ${err.message}`));
    controlSocket.on("error", (err) =>
      this.logger.warn(`exec control socket error (${sessionId}): ${err.message}`)
    );

    this.sessions.set(sessionId, { jailName, ioSocket, controlSocket });
    return sessionId;
  }

  sendInput(sessionId: string, data: string): boolean {
    const session = this.getSession(sessionId);
    if (session.ioSocket.readyState !== WebSocket.OPEN) return false;
    // Incus's exec fd-0 channel expects binary frames for stdin — a plain
    // string send() here defaults to a text frame, which it silently drops.
    session.ioSocket.send(Buffer.from(data, "utf-8"));
    return true;
  }

  resize(sessionId: string, cols: number, rows: number): boolean {
    const session = this.getSession(sessionId);
    if (session.controlSocket.readyState !== WebSocket.OPEN) return false;
    session.controlSocket.send(
      JSON.stringify({ command: "window-resize", args: { width: String(cols), height: String(rows) } })
    );
    return true;
  }

  stop(sessionId: string): boolean {
    const session = this.sessions.get(sessionId);
    if (!session) return false;
    session.ioSocket.close();
    session.controlSocket.close();
    this.sessions.delete(sessionId);
    return true;
  }

  /**
   * Non-interactive, fire-and-forget exec: runs `command` inside `jailName`
   * with no websockets, waits for the operation to finish, and returns its
   * exit code. Used for best-effort in-jail setup steps (e.g. `tailscale up`)
   * where nothing needs to stream output back to a client.
   */
  async runOnce(jailName: string, command: string[]): Promise<{ exitCode: number }> {
    const payload = JSON.stringify({
      command,
      "wait-for-websocket": false,
      interactive: false,
      "record-output": true,
    });

    // Same envelope shape as requestExec: the top-level `operation` is the
    // operation URL to poll, and the exec-specific fields (here, `return`)
    // are nested one level deeper, under `metadata.metadata`.
    const response = await new Promise<{ operation?: string }>((resolve, reject) => {
      const req = httpRequest(
        {
          socketPath: this.socketPath,
          method: "POST",
          path: `/1.0/instances/${encodeURIComponent(jailName)}/exec`,
          timeout: 15_000,
          headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(payload) },
        },
        (res) => {
          let data = "";
          res.on("data", (c) => (data += c));
          res.on("end", () => {
            try {
              resolve(JSON.parse(data));
            } catch (e) {
              reject(new Error(`Failed to parse exec response: ${(e as Error).message}`));
            }
          });
        }
      );
      req.on("timeout", () => {
        req.destroy();
        reject(new Error("Incus exec request timed out"));
      });
      req.on("error", (e) => reject(new Error(`Incus socket unreachable: ${e.message}`)));
      req.write(payload);
      req.end();
    });

    if (!response.operation) {
      throw new Error("Incus exec did not return an operation");
    }

    const { metadata } = await this.waitForOperation(response.operation);
    return { exitCode: metadata?.metadata?.return ?? -1 };
  }

  /** GET /1.0/operations/{id}/wait and return its metadata once the operation reaches a terminal state. */
  private async waitForOperation(
    operationUrl: string,
    timeoutSec = 60
  ): Promise<{ metadata?: { metadata?: { return?: number } } }> {
    return new Promise((resolve, reject) => {
      const req = httpRequest(
        {
          socketPath: this.socketPath,
          method: "GET",
          path: `${operationUrl}/wait?timeout=${timeoutSec}`,
          timeout: (timeoutSec + 10) * 1000,
        },
        (res) => {
          let data = "";
          res.on("data", (c) => (data += c));
          res.on("end", () => {
            try {
              resolve(JSON.parse(data));
            } catch (e) {
              reject(new Error(`Failed to parse operation wait response: ${(e as Error).message}`));
            }
          });
        }
      );
      req.on("timeout", () => {
        req.destroy();
        reject(new Error("Incus operation wait timed out"));
      });
      req.on("error", (e) => reject(new Error(`Incus socket unreachable: ${e.message}`)));
      req.end();
    });
  }

  private getSession(sessionId: string): ExecSession {
    const session = this.sessions.get(sessionId);
    if (!session) throw new Error(`Unknown exec session: ${sessionId}`);
    return session;
  }

  /** POST /1.0/instances/{name}/exec and wait for the operation to report its websocket fds. */
  private async requestExec(
    jailName: string,
    cols: number,
    rows: number
  ): Promise<{ operationUrl: string; fds: Record<string, string> }> {
    const payload = JSON.stringify({
      command: ["/bin/bash"],
      environment: { TERM: "xterm-256color" },
      "wait-for-websocket": true,
      interactive: true,
      width: cols,
      height: rows,
    });

    // The top-level `metadata` is the operation object itself; the exec-specific
    // fd secrets are nested one level deeper, in *its* own `metadata` field.
    const response = await new Promise<{
      operation?: string;
      metadata?: { metadata?: { fds?: Record<string, string> } };
    }>((resolve, reject) => {
        const req = httpRequest(
          {
            socketPath: this.socketPath,
            method: "POST",
            path: `/1.0/instances/${encodeURIComponent(jailName)}/exec`,
            timeout: 15_000,
            headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(payload) },
          },
          (res) => {
            let data = "";
            res.on("data", (c) => (data += c));
            res.on("end", () => {
              try {
                resolve(JSON.parse(data));
              } catch (e) {
                reject(new Error(`Failed to parse exec response: ${(e as Error).message}`));
              }
            });
          }
        );
        req.on("timeout", () => {
          req.destroy();
          reject(new Error("Incus exec request timed out"));
        });
        req.on("error", (e) => reject(new Error(`Incus socket unreachable: ${e.message}`)));
        req.write(payload);
        req.end();
      }
    );

    const fds = response.metadata?.metadata?.fds;
    if (!response.operation || !fds) {
      throw new Error("Incus exec did not return an operation with websocket fds");
    }
    return { operationUrl: response.operation, fds };
  }

  /** Connect to one of an operation's fd websockets, which Incus serves over its own unix socket. */
  private connectOperationSocket(operationUrl: string, secret: string): WebSocket {
    // `ws` supports unix sockets via the `ws+unix://<path>:<url-path>` scheme.
    const wsUrl = `ws+unix://${this.socketPath}:${operationUrl}/websocket?secret=${encodeURIComponent(secret)}`;
    return new WebSocket(wsUrl);
  }
}
