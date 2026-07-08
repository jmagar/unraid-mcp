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

export interface PrivilegedCommandJob {
  id: string;
  jailName: string;
  command: string;
  status: "running" | "success" | "failed";
  exitCode?: number;
  stdout?: string;
  stderr?: string;
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
  private readonly privilegedJobs = new Map<string, PrivilegedCommandJob>();
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
   * where nothing needs to stream output back to a client. Pass
   * `captureOutput: true` to also fetch stdout/stderr — Incus writes these to
   * retrievable log files when `record-output` is set; we fetch then delete
   * them so they don't pile up on the container's own log storage.
   */
  async runOnce(
    jailName: string,
    command: string[],
    timeoutSec = 60,
    captureOutput = false
  ): Promise<{ exitCode: number; stdout?: string; stderr?: string }> {
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
    const exitCode = metadata?.metadata?.return ?? -1;
    if (!captureOutput) return { exitCode };

    const output = metadata?.metadata?.output;
    const [stdout, stderr] = await Promise.all([
      output?.["1"] ? this.fetchAndDeleteLog(output["1"]) : Promise.resolve(undefined),
      output?.["2"] ? this.fetchAndDeleteLog(output["2"]) : Promise.resolve(undefined),
    ]);
    return { exitCode, stdout, stderr };
  }

  /** GET /1.0/operations/{id}/wait and return its metadata once the operation reaches a terminal state. */
  private async waitForOperation(
    operationUrl: string,
    timeoutSec = 60
  ): Promise<{
    metadata?: { metadata?: { return?: number; output?: Record<string, string> } };
  }> {
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

  /** GET a log file's content by its absolute API path, then DELETE it so exec output doesn't pile up. */
  private async fetchAndDeleteLog(logPath: string): Promise<string> {
    const content = await new Promise<string>((resolve, reject) => {
      const req = httpRequest({ socketPath: this.socketPath, method: "GET", path: logPath, timeout: 15_000 }, (res) => {
        let data = "";
        res.on("data", (c) => (data += c));
        res.on("end", () => resolve(data));
      });
      req.on("timeout", () => {
        req.destroy();
        reject(new Error("Incus log fetch timed out"));
      });
      req.on("error", (e) => reject(new Error(`Incus socket unreachable: ${e.message}`)));
      req.end();
    });
    await new Promise<void>((resolve) => {
      const req = httpRequest({ socketPath: this.socketPath, method: "DELETE", path: logPath, timeout: 15_000 }, () =>
        resolve()
      );
      req.on("timeout", () => {
        req.destroy();
        resolve();
      });
      req.on("error", () => resolve());
      req.end();
    });
    return content;
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

  // --- Sudo grant/check for the container's non-root "agent" user -----------------------
  // "No sudo for agent" is a deliberate default (see jailDetail HelpText / CLAUDE.md's
  // threat model — a compromised dependency running as agent shouldn't be able to
  // self-escalate). Granting it is an explicit, opt-in operator action, either at launch
  // or retroactively on an already-running container. Runs as root (no `su -l agent`
  // wrapper, unlike Homebrew) since only root can install the sudo package and write
  // sudoers.d. Best-effort across package managers since the curated distro list spans
  // apt/apk/dnf/yum.

  // Newline-separated, not `&&`/`||`-joined on one line — joining a line that already
  // ends in `||` with another `&&` produces `|| &&` back-to-back, which is invalid POSIX
  // shell syntax (verified live: dash, Debian's default /bin/sh, rejected it outright).
  private static readonly GRANT_SUDO_SCRIPT = [
    "set -e",
    "command -v sudo >/dev/null 2>&1 || apt-get install -y sudo || apk add --no-cache sudo || dnf install -y sudo || yum install -y sudo",
    "mkdir -p /etc/sudoers.d",
    "echo 'agent ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/agent",
    "chmod 0440 /etc/sudoers.d/agent",
  ].join("\n");

  async grantSudo(jailName: string): Promise<{ success: boolean; message: string }> {
    try {
      const result = await this.runOnce(jailName, ["sh", "-c", IncusExecService.GRANT_SUDO_SCRIPT], 120, true);
      if (result.exitCode !== 0) {
        return {
          success: false,
          message: `Granting sudo failed (exit ${result.exitCode}): ${(result.stderr || result.stdout || "").trim().slice(0, 300)}`,
        };
      }
      return { success: true, message: "Sudo granted to agent (NOPASSWD)." };
    } catch (e) {
      return { success: false, message: e instanceof Error ? e.message : String(e) };
    }
  }

  async checkSudoEnabled(jailName: string): Promise<boolean> {
    try {
      const { exitCode } = await this.runOnce(jailName, ["test", "-f", "/etc/sudoers.d/agent"]);
      return exitCode === 0;
    } catch {
      return false;
    }
  }

  // --- Operator-mediated privileged command — runs as root, never available to the ------
  // container's own agent user. Safe complement to the sudo toggle: covers one-off needs
  // (a forgotten apt package, a quick fix) on containers where sudo is deliberately left
  // off, without ever handing the agent user itself any new capability. Fire-and-poll for
  // the same reason as the Homebrew installer — an arbitrary command (e.g. `apt update &&
  // apt install ...`) can easily outlast a blocking request's timeout.

  startPrivilegedCommand(jailName: string, command: string): string {
    const id = randomUUID();
    this.privilegedJobs.set(id, { id, jailName, command, status: "running", message: "Running…" });
    void this.runPrivilegedCommand(id, jailName, command);
    return id;
  }

  getPrivilegedCommandStatus(id: string): PrivilegedCommandJob | undefined {
    return this.privilegedJobs.get(id);
  }

  private async runPrivilegedCommand(jobId: string, jailName: string, command: string): Promise<void> {
    try {
      const result = await this.runOnce(jailName, ["sh", "-c", command], 180, true);
      this.privilegedJobs.set(jobId, {
        id: jobId,
        jailName,
        command,
        status: result.exitCode === 0 ? "success" : "failed",
        exitCode: result.exitCode,
        stdout: result.stdout,
        stderr: result.stderr,
        message: result.exitCode === 0 ? "Command finished." : `Command exited with code ${result.exitCode}.`,
      });
    } catch (e) {
      this.privilegedJobs.set(jobId, {
        id: jobId,
        jailName,
        command,
        status: "failed",
        message: e instanceof Error ? e.message : String(e),
      });
    }
  }
}
