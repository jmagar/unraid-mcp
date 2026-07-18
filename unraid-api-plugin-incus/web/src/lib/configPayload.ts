import type { IncusConfig } from "../types";

/** Build the mutation payload without ever echoing the server's secret state. */
export function buildConfigUpdate(
  config: IncusConfig,
  secret: { replacement: string; clear: boolean }
): Record<string, unknown> {
  const { tsAuthKeyConfigured: _configured, ...publicConfig } = config;
  if (secret.clear) return { ...publicConfig, tsAuthKey: "" };
  if (secret.replacement) return { ...publicConfig, tsAuthKey: secret.replacement };
  return publicConfig;
}
