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

export interface HomebrewInstallJob {
  id: string;
  jailName: string;
  formula: string;
  status: "running" | "success" | "failed";
  message: string;
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
  private readonly homebrewJobs = new Map<string, HomebrewInstallJob>();
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
  async runOnce(jailName: string, command: string[], timeoutSec = 60): Promise<{ exitCode: number }> {
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

    const { metadata } = await this.waitForOperation(response.operation, timeoutSec);
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

  /** A tap/formula name — letters, digits, and .-@/ (covers `wget`, `python@3.12`, `homebrew/core/wget`). */
  private static readonly HOMEBREW_FORMULA_PATTERN = /^[a-zA-Z0-9][a-zA-Z0-9._@/-]*$/;

  /**
   * Kick off a best-effort post-launch package install via Homebrew and return immediately
   * with a job id to poll — bootstrapping Homebrew plus a formula install can comfortably
   * run past a browser/reverse-proxy's default request timeout (verified live: even the
   * tiny "hello" formula's mutation call hit an HTTP 504 while the actual install kept
   * running to completion server-side regardless, since nothing was cancelling it — the
   * proxy just gave up waiting). Mirrors the same fire-and-poll pattern already used for
   * distrobuilder image builds (startBuild/getStatus) rather than blocking a mutation.
   */
  startHomebrewInstall(jailName: string, formula: string): string {
    const id = randomUUID();
    if (!IncusExecService.HOMEBREW_FORMULA_PATTERN.test(formula)) {
      this.homebrewJobs.set(id, {
        id,
        jailName,
        formula,
        status: "failed",
        message: `"${formula}" doesn't look like a valid Homebrew formula name.`,
      });
      return id;
    }
    this.homebrewJobs.set(id, { id, jailName, formula, status: "running", message: "Installing…" });
    void this.runHomebrewInstall(id, jailName, formula);
    return id;
  }

  getHomebrewInstallStatus(id: string): HomebrewInstallJob | undefined {
    return this.homebrewJobs.get(id);
  }

  /**
   * The actual work behind startHomebrewInstall, run in the background. Uses the same
   * runOnce mechanism already used for Tailscale auto-join, just aimed at a running
   * container instead of build time — Homebrew can't be baked into a build (it refuses to
   * run inside a chroot, same root-cause as it refusing to run as root at all), so this is
   * the only real way to actually install something from the Homebrew search results in
   * the Builder tab.
   *
   * Deliberately does NOT use Homebrew's official installer — verified live that it always
   * tries to create the shared system path /home/linuxbrew/.linuxbrew and requires `sudo`
   * to do so, which the agent-jail profile's non-root "agent" user doesn't have (no sudo
   * inside these containers, on purpose — see the jailDetail Homebrew HelpText). Uses
   * Homebrew's own documented no-sudo alternative instead: clone the `brew` script straight
   * into a prefix under the agent's own home directory, which needs no elevated privileges
   * at all since it's a normal write inside a directory the user already owns.
   */
  private async runHomebrewInstall(jobId: string, jailName: string, formula: string): Promise<void> {
    const fail = (message: string) => this.homebrewJobs.set(jobId, { id: jobId, jailName, formula, status: "failed", message });
    try {
      const brewPrefix = "/home/agent/.linuxbrew";
      const brewShellenv = `eval "$(${brewPrefix}/bin/brew shellenv)"`;
      const { exitCode: hasBrew } = await this.runOnce(jailName, ["test", "-x", `${brewPrefix}/bin/brew`]);

      if (hasBrew !== 0) {
        this.logger.log(`Homebrew not present in "${jailName}" — bootstrapping before installing "${formula}"`);
        const install = await this.runOnce(
          jailName,
          [
            "su",
            "-l",
            "agent",
            "-c",
            `mkdir -p ${brewPrefix}/bin && git clone --depth=1 https://github.com/Homebrew/brew ${brewPrefix}/Homebrew && ln -s ${brewPrefix}/Homebrew/bin/brew ${brewPrefix}/bin/brew`,
          ],
          180
        );
        if (install.exitCode !== 0) {
          fail(
            `Homebrew isn't installed in this container and bootstrapping it failed (exit ${install.exitCode}). It needs bash and git available inside the container.`
          );
          return;
        }
      }

      const result = await this.runOnce(
        jailName,
        ["su", "-l", "agent", "-c", `${brewShellenv} && brew install ${formula}`],
        180
      );
      if (result.exitCode !== 0) {
        fail(`brew install ${formula} failed (exit ${result.exitCode}).`);
        return;
      }
      this.homebrewJobs.set(jobId, { id: jobId, jailName, formula, status: "success", message: `${formula} installed.` });
    } catch (e) {
      fail(e instanceof Error ? e.message : String(e));
    }
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
