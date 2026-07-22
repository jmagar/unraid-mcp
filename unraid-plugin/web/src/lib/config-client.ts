/**
 * Transport to the plugin's PHP settings endpoint.
 *
 * Auth is the webGUI session cookie (same-origin) plus Unraid's CSRF token.
 * The token script may not have executed before our element mounts, so we
 * poll briefly for window.csrf_token before the first mutating request —
 * the same race guard incus-unraid's graphql-client uses.
 */

const ENDPOINT = "/plugins/unraid-mcp/include/config.php";

declare global {
  interface Window {
    csrf_token?: string;
  }
}

export interface ServiceState {
  enabled: boolean;
  running: boolean;
}

export interface ConfigPayload {
  config: Record<string, string | boolean>;
  extra: Record<string, string>;
  service: ServiceState;
}

async function csrfToken(): Promise<string> {
  for (let i = 0; i < 20; i++) {
    if (window.csrf_token) return window.csrf_token;
    await new Promise((r) => setTimeout(r, 100));
  }
  return window.csrf_token ?? "";
}

async function request(init?: RequestInit): Promise<ConfigPayload> {
  const res = await fetch(ENDPOINT, { credentials: "include", ...init });
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(body?.error ?? `request failed: HTTP ${res.status}`);
  }
  return body as ConfigPayload;
}

export function loadConfig(): Promise<ConfigPayload> {
  return request();
}

async function post(payload: object): Promise<ConfigPayload> {
  return request({
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Csrf-Token": await csrfToken(),
    },
    body: JSON.stringify(payload),
  });
}

/** Save changed keys. Secrets: send a value to replace, "" to clear, omit to keep. */
export function saveConfig(changes: Record<string, string>): Promise<ConfigPayload> {
  return post({ action: "save", changes });
}

export type ServiceOp = "start" | "stop" | "restart" | "enable" | "disable";

export function serviceAction(op: ServiceOp): Promise<ConfigPayload> {
  return post({ action: "service", op });
}

/** Fetch a stored secret value (session + CSRF gated server-side). */
export async function revealSecret(key: string): Promise<string> {
  const res = await fetch(ENDPOINT, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-Csrf-Token": await csrfToken(),
    },
    body: JSON.stringify({ action: "reveal", key }),
  });
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(body?.error ?? `reveal failed: HTTP ${res.status}`);
  }
  return String(body?.value ?? "");
}
