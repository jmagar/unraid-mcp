import { Injectable, Logger } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { request as httpRequest } from "node:http";

interface IncusResponse<T = unknown> {
  type: "sync" | "async" | "error";
  status: string;
  status_code: number;
  operation?: string;
  metadata: T;
  error?: string;
  error_code?: number;
}

/**
 * Thin client for the Incus REST API over its local unix socket
 * ($INCUS_DIR/unix.socket). No `incus` CLI, no output scraping — Incus is
 * API-first, so we speak HTTP directly.
 */
@Injectable()
export class IncusService {
  private readonly logger = new Logger(IncusService.name);

  constructor(private readonly config: ConfigService) {}

  private get socketPath(): string {
    const dir = this.config.get<string>("incus.stateDir", "/mnt/user/appdata/incus");
    return `${dir}/unix.socket`;
  }

  /** Raw request against the Incus REST API. */
  private call<T = unknown>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<IncusResponse<T>> {
    const payload = body ? JSON.stringify(body) : undefined;
    return new Promise((resolve, reject) => {
      const req = httpRequest(
        {
          socketPath: this.socketPath,
          method,
          path,
          timeout: 30_000,
          headers: {
            "Content-Type": "application/json",
            ...(payload ? { "Content-Length": Buffer.byteLength(payload) } : {}),
          },
        },
        (res) => {
          let data = "";
          res.on("data", (c) => (data += c));
          res.on("end", () => {
            try {
              const parsed: IncusResponse<T> = data ? JSON.parse(data) : {};
              if (parsed.type === "error") {
                reject(new Error(`Incus API error on ${method} ${path}: ${parsed.error} (${parsed.error_code})`));
                return;
              }
              resolve(parsed);
            } catch (e) {
              reject(new Error(`Incus API parse error on ${path}: ${(e as Error).message}`));
            }
          });
        }
      );
      req.on("timeout", () => {
        req.destroy();
        reject(new Error(`Incus API request to ${path} timed out after 30s`));
      });
      req.on("error", (e) =>
        reject(new Error(`Incus socket ${this.socketPath} unreachable: ${e.message}`))
      );
      if (payload) req.write(payload);
      req.end();
    });
  }

  /** Wait for an async operation to complete. */
  private async waitForOperation(operationUrl: string, timeoutSec = 60): Promise<void> {
    const { metadata } = await this.call<{ status: string; err: string }>(
      "GET",
      `${operationUrl}/wait?timeout=${timeoutSec}`
    );
    if (metadata?.status === "Failure") {
      throw new Error(`Incus operation failed: ${metadata.err}`);
    }
  }

  /** Execute a call and wait if async. */
  private async callAndWait<T = unknown>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<IncusResponse<T>> {
    const resp = await this.call<T>(method, path, body);
    if (resp.type === "async" && resp.operation) {
      await this.waitForOperation(resp.operation);
    }
    return resp;
  }

  /** GET /1.0 — daemon reachable & basic info. */
  async ping(): Promise<boolean> {
    try {
      const resp = await this.call("GET", "/1.0");
      return resp.status_code === 200;
    } catch {
      return false;
    }
  }

  /** List jails (instances) with state, expanded to name/status/ipv4. */
  async listJails(): Promise<Array<{ name: string; status: string; ipv4?: string }>> {
    const { metadata } = await this.call<Array<Record<string, any>>>(
      "GET",
      "/1.0/instances?recursion=2"
    );
    return (metadata ?? []).map((i) => ({
      name: i.name,
      status: i.status,
      ipv4: i.state?.network?.eth0?.addresses?.find((a: any) => a.family === "inet")?.address,
    }));
  }

  /** Launch a jail from an image using the configured agent-jail profile. */
  async launchJail(name: string, opts?: { image?: string; profile?: string }): Promise<void> {
    const image = opts?.image ?? this.config.get<string>("incus.jailImage", "images:debian/trixie/cloud");
    const profile = opts?.profile ?? this.config.get<string>("incus.jailProfile", "agent-jail");
    const colonIdx = image.indexOf(":");
    const remote = colonIdx > 0 ? image.substring(0, colonIdx) : "images";
    const alias = colonIdx > 0 ? image.substring(colonIdx + 1) : image;
    await this.callAndWait("POST", "/1.0/instances", {
      name,
      type: "container",
      profiles: ["default", profile],
      source: {
        type: "image",
        protocol: "simplestreams",
        server: `https://${remote === "images" ? "images.linuxcontainers.org" : remote}`,
        alias,
      },
    });
    await this.callAndWait("PUT", `/1.0/instances/${encodeURIComponent(name)}/state`, {
      action: "start",
      timeout: 30,
    });
  }

  /** start | stop | restart | freeze | unfreeze. */
  async setState(name: string, action: "start" | "stop" | "restart" | "freeze" | "unfreeze"): Promise<void> {
    await this.callAndWait("PUT", `/1.0/instances/${encodeURIComponent(name)}/state`, {
      action,
      timeout: action === "stop" ? 30 : 15,
      force: action === "stop",
    });
  }

  async deleteJail(name: string): Promise<void> {
    // Best-effort stop before delete
    try {
      await this.callAndWait("PUT", `/1.0/instances/${encodeURIComponent(name)}/state`, {
        action: "stop",
        timeout: 15,
        force: true,
      });
    } catch {
      // Container may already be stopped
    }
    await this.callAndWait("DELETE", `/1.0/instances/${encodeURIComponent(name)}`);
  }

  /** Repoint a jail's workspace disk device to a host directory (bring-your-cwd). */
  async setWorkspace(name: string, hostPath: string): Promise<void> {
    const { metadata: inst } = await this.call<Record<string, any>>(
      "GET",
      `/1.0/instances/${encodeURIComponent(name)}`
    );
    const devices = { ...(inst.devices ?? {}) };
    devices.workspace = { type: "disk", source: hostPath, path: "/workspace", shift: "true" };
    await this.callAndWait("PATCH", `/1.0/instances/${encodeURIComponent(name)}`, { devices });
  }
}
