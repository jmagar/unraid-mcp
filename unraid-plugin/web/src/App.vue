<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { Badge, Button, HelpText, Input, Label, Select, Switch } from "./components/ui";
import {
  fetchLogs,
  loadConfig,
  revealSecret,
  saveConfig,
  serviceAction,
  type ConfigPayload,
  type ServiceOp,
} from "./lib/config-client";

/** Field metadata drives the whole form — one row per env var. */
interface FieldDef {
  key: string;
  label: string;
  help: string;
  kind: "text" | "secret" | "toggle" | "select" | "number";
  options?: string[];
  mono?: boolean;
  placeholder?: string;
}

interface Section {
  title: string;
  collapsed?: boolean;
  fields: FieldDef[];
}

const SECTIONS: Section[] = [
  {
    title: "Unraid API",
    fields: [
      {
        key: "UNRAID_API_URL",
        label: "GraphQL URL",
        help: "The local Unraid GraphQL endpoint, e.g. http://127.0.0.1:<webgui port>/graphql. Detected automatically at install.",
        kind: "text",
        mono: true,
        placeholder: "http://127.0.0.1/graphql",
      },
      {
        key: "UNRAID_API_KEY",
        label: "API key",
        help: "Unraid API key. Auto-provisioned at install when possible; create one with: unraid-api apikey --create --name unraidmcp -r admin --json",
        kind: "secret",
      },
      {
        key: "UNRAID_VERIFY_SSL",
        label: "Verify SSL",
        help: "Only relevant for https:// API URLs. Instead of turning this off, point it at a CA bundle path to trust a self-signed cert.",
        kind: "toggle",
      },
      {
        key: "UNRAID_ALLOW_INSECURE_TLS",
        label: "Allow insecure TLS",
        help: "Required opt-in when Verify SSL is off for an https:// URL — acknowledges the API key travels to an unverified peer.",
        kind: "toggle",
      },
    ],
  },
  {
    title: "MCP server",
    fields: [
      {
        key: "UNRAID_MCP_TRANSPORT",
        label: "Transport",
        help: "streamable-http serves MCP over HTTP (what claude.ai and Claude Code connect to); stdio is for local piping only.",
        kind: "select",
        options: ["streamable-http", "sse", "stdio"],
      },
      {
        key: "UNRAID_MCP_HOST",
        label: "Bind host",
        help: "0.0.0.0 exposes the server on all interfaces; bearer auth protects it.",
        kind: "text",
        mono: true,
        placeholder: "0.0.0.0",
      },
      {
        key: "UNRAID_MCP_PORT",
        label: "Port",
        help: "TCP port for the MCP HTTP endpoint.",
        kind: "number",
        placeholder: "6970",
      },
      {
        key: "UNRAID_MCP_TAILSCALE_SERVE",
        label: "Tailscale Serve",
        help: "Publish the MCP endpoint on your tailnet as HTTPS with automatic certs, via the official Tailscale plugin's daemon (tailscale serve). Uses a dedicated HTTPS port equal to the MCP port, so any serve config on 443 is untouched.",
        kind: "toggle",
      },
    ],
  },
  {
    title: "Authentication",
    fields: [
      {
        key: "UNRAID_MCP_BEARER_TOKEN",
        label: "Bearer token",
        help: "Pre-shared token MCP clients send as Authorization: Bearer <token>. Auto-generated at install.",
        kind: "secret",
      },
      {
        key: "UNRAID_MCP_DISABLE_HTTP_AUTH",
        label: "Disable HTTP auth",
        help: "Only behind a trusted authenticating gateway. With a non-loopback bind host this also requires Trust proxy.",
        kind: "toggle",
      },
      {
        key: "UNRAID_MCP_TRUST_PROXY",
        label: "Trust proxy",
        help: "Confirms an upstream gateway (SWAG/Authelia) enforces authentication when HTTP auth is disabled.",
        kind: "toggle",
      },
    ],
  },
  {
    title: "Tuning",
    fields: [
      {
        key: "UNRAID_MCP_LOG_LEVEL",
        label: "Log level",
        help: "Server log verbosity. Logs land in /var/log/unraid-mcp/server.log.",
        kind: "select",
        options: ["DEBUG", "INFO", "WARNING", "ERROR"],
      },
      {
        key: "UNRAID_MCP_MAX_RESPONSE_BYTES",
        label: "Response cap",
        help: "Backstop cap in bytes on serialized tool responses (default 40000 ≈ 10K tokens).",
        kind: "number",
        placeholder: "40000",
      },
      {
        key: "UNRAID_AUTO_START_SUBSCRIPTIONS",
        label: "Subscriptions",
        help: "Lazily start WebSocket subscriptions on first live-data access.",
        kind: "toggle",
      },
      {
        key: "UNRAID_MAX_RECONNECT_ATTEMPTS",
        label: "Reconnect limit",
        help: "WebSocket reconnect limit before a subscription is marked failed.",
        kind: "number",
        placeholder: "10",
      },
    ],
  },
  {
    title: "Subscription tuning",
    collapsed: true,
    fields: [
      {
        key: "UNRAID_SUBSCRIPTION_COLLECT_MAX_EVENTS",
        label: "Collect max events",
        help: "Bound on events retained while streaming a live collection call.",
        kind: "number",
        placeholder: "100",
      },
      {
        key: "UNRAID_SUBSCRIPTION_COLLECT_MAX_BYTES",
        label: "Collect max bytes",
        help: "Bound on bytes retained while streaming (default 1048576 = 1 MiB).",
        kind: "number",
        placeholder: "1048576",
      },
      {
        key: "UNRAID_SUBSCRIPTION_COLLECT_MAX_SECONDS",
        label: "Collect max seconds",
        help: "Bound on duration of a live collection window.",
        kind: "number",
        placeholder: "30",
      },
      {
        key: "UNRAID_SUBSCRIPTION_CACHE_MAX_AGE_SECONDS",
        label: "Cache max age",
        help: "Cached subscription payloads older than this are not served.",
        kind: "number",
        placeholder: "300",
      },
      {
        key: "UNRAID_SUBSCRIPTION_TIMEOUT_MAX_SECONDS",
        label: "Timeout cap",
        help: "Upper bound on per-call WebSocket timeout.",
        kind: "number",
        placeholder: "60",
      },
      {
        key: "UNRAID_MCP_ENABLE_RAW_SUBSCRIPTION_PROBE",
        label: "Raw probe",
        help: "Debug-only, data-sensitive raw frame in subscriptions/test_query. Never enable on shared deployments.",
        kind: "toggle",
      },
      {
        key: "UNRAID_MCP_LOG_FILE",
        label: "Log filename",
        help: "Log filename inside the server's logs directory (default unraid-mcp.log).",
        kind: "text",
        mono: true,
        placeholder: "unraid-mcp.log",
      },
    ],
  },
  {
    title: "Google OAuth (claude.ai)",
    collapsed: true,
    fields: [
      {
        key: "UNRAID_MCP_GOOGLE_CLIENT_ID",
        label: "Client ID",
        help: "Google OAuth Web application client ID. Setting ID and secret enables OAuth for HTTP; an explicitly set bearer token stays valid alongside.",
        kind: "text",
        mono: true,
        placeholder: "1234.apps.googleusercontent.com",
      },
      {
        key: "UNRAID_MCP_GOOGLE_CLIENT_SECRET",
        label: "Client secret",
        help: "Google OAuth client secret (GOCSPX-…).",
        kind: "secret",
      },
      {
        key: "UNRAID_MCP_GOOGLE_BASE_URL",
        label: "Base URL",
        help: "This server's public https:// base URL; must match the client's authorized redirect URI host.",
        kind: "text",
        mono: true,
        placeholder: "https://mcp.example.com",
      },
      {
        key: "UNRAID_MCP_GOOGLE_ALLOWED_EMAILS",
        label: "Allowed emails",
        help: "Comma/space-separated verified Google emails allowed to sign in.",
        kind: "text",
        mono: true,
      },
      {
        key: "UNRAID_MCP_GOOGLE_ALLOWED_DOMAINS",
        label: "Allowed domains",
        help: "Comma/space-separated verified email domains allowed to sign in.",
        kind: "text",
        mono: true,
      },
      {
        key: "UNRAID_MCP_GOOGLE_ALLOW_ANY_USER",
        label: "Allow any user",
        help: "Escape hatch for private deployments that intentionally allow any Google account.",
        kind: "toggle",
      },
      {
        key: "UNRAID_MCP_GOOGLE_REQUIRED_SCOPES",
        label: "Scopes",
        help: "OAuth scopes; default is openid + userinfo.email.",
        kind: "text",
        mono: true,
      },
      {
        key: "UNRAID_MCP_GOOGLE_REDIRECT_PATH",
        label: "Redirect path",
        help: "OAuth callback path; must match the Google client config (default /auth/callback).",
        kind: "text",
        mono: true,
        placeholder: "/auth/callback",
      },
      {
        key: "UNRAID_MCP_GOOGLE_JWT_SIGNING_KEY",
        label: "JWT signing key",
        help: "With the encryption key, persists issued tokens across restarts.",
        kind: "secret",
      },
      {
        key: "UNRAID_MCP_GOOGLE_ENCRYPTION_KEY",
        label: "Encryption key",
        help: "Fernet key for encrypting persisted tokens at rest. Set both persistence keys or neither.",
        kind: "secret",
      },
      {
        key: "UNRAID_MCP_GOOGLE_STORAGE_DIR",
        label: "Token storage dir",
        help: "Directory for persisted encrypted tokens (default ~/.unraid-mcp/oauth-tokens).",
        kind: "text",
        mono: true,
      },
    ],
  },
];

const payload = ref<ConfigPayload | null>(null);
const form = reactive<Record<string, string>>({});
const secretEdits = reactive<
  Record<string, { value: string; clear: boolean; show: boolean; original: string | null }>
>({});
const loading = ref(true);
const saving = ref(false);
const busy = ref(false);
const error = ref("");
const savedFlash = ref(false);
const copied = ref(false);
const logText = ref("");
const logOpen = ref(false);
const logAuto = ref(false);
let logTimer: ReturnType<typeof setInterval> | null = null;

const secretKeys = SECTIONS.flatMap((s) => s.fields)
  .filter((f) => f.kind === "secret")
  .map((f) => f.key);

function hydrate(p: ConfigPayload) {
  payload.value = p;
  for (const section of SECTIONS) {
    for (const f of section.fields) {
      if (f.kind === "secret") {
        if (!secretEdits[f.key]) {
          secretEdits[f.key] = { value: "", clear: false, show: false, original: null };
        } else {
          secretEdits[f.key].value = "";
          secretEdits[f.key].clear = false;
          secretEdits[f.key].show = false;
          secretEdits[f.key].original = null;
        }
      } else {
        form[f.key] = String(p.config[f.key] ?? "");
      }
    }
  }
}

function secretConfigured(key: string): boolean {
  return Boolean(payload.value?.config[`${key}_configured`]);
}

const service = computed(() => payload.value?.service ?? { enabled: false, running: false });
const tailscale = computed(
  () => payload.value?.tailscale ?? { available: false, dnsName: "", serveActive: false },
);

/** The endpoint MCP clients connect to, derived from live form state. */
const endpoint = computed(() => {
  if (form.UNRAID_MCP_TRANSPORT === "stdio") return "";
  const port = form.UNRAID_MCP_PORT || "6970";
  if (boolVal("UNRAID_MCP_TAILSCALE_SERVE") && tailscale.value.dnsName) {
    return `https://${tailscale.value.dnsName}:${port}/mcp`;
  }
  const host =
    !form.UNRAID_MCP_HOST || form.UNRAID_MCP_HOST === "0.0.0.0"
      ? window.location.hostname
      : form.UNRAID_MCP_HOST;
  return `http://${host}:${port}/mcp`;
});

async function copyEndpoint() {
  if (!endpoint.value) return;
  try {
    await navigator.clipboard.writeText(endpoint.value);
    copied.value = true;
    setTimeout(() => (copied.value = false), 1500);
  } catch {
    /* clipboard unavailable over plain http */
  }
}

function boolVal(key: string): boolean {
  return (form[key] ?? "").toLowerCase() === "true";
}
function setBool(key: string, v: boolean) {
  form[key] = v ? "true" : "false";
}

function fieldDisabled(field: FieldDef): boolean {
  return field.key === "UNRAID_MCP_TAILSCALE_SERVE" && !tailscale.value.available;
}

async function run(fn: () => Promise<ConfigPayload>) {
  error.value = "";
  try {
    hydrate(await fn());
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e);
  }
}

async function apply() {
  saving.value = true;
  const changes: Record<string, string> = { ...form };
  for (const key of secretKeys) {
    const edit = secretEdits[key];
    if (edit?.clear) changes[key] = "";
    else if (edit?.value && edit.value !== edit.original) changes[key] = edit.value;
    // untouched (or revealed-but-unchanged) secrets are omitted -> kept server-side
  }
  await run(() => saveConfig(changes));
  saving.value = false;
  if (!error.value) {
    savedFlash.value = true;
    setTimeout(() => (savedFlash.value = false), 2500);
  }
}

async function toggleSecret(key: string) {
  const edit = secretEdits[key];
  if (!edit) return;
  if (edit.show) {
    edit.show = false;
    if (edit.value === edit.original) {
      edit.value = "";
      edit.original = null;
    }
    return;
  }
  if (!edit.value && secretConfigured(key)) {
    try {
      const v = await revealSecret(key);
      edit.value = v;
      edit.original = v;
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e);
      return;
    }
  }
  edit.show = true;
}

async function svc(op: ServiceOp) {
  busy.value = true;
  await run(() => serviceAction(op));
  busy.value = false;
}

async function refreshLogs() {
  try {
    logText.value = (await fetchLogs(300)) || "(log is empty)";
  } catch (e) {
    logText.value = `failed to fetch log: ${e instanceof Error ? e.message : e}`;
  }
}

function setLogAuto(on: boolean) {
  logAuto.value = on;
  if (logTimer) {
    clearInterval(logTimer);
    logTimer = null;
  }
  if (on) {
    void refreshLogs();
    logTimer = setInterval(() => void refreshLogs(), 3000);
  }
}

async function toggleLog() {
  logOpen.value = !logOpen.value;
  if (logOpen.value && !logText.value) await refreshLogs();
  if (!logOpen.value) setLogAuto(false);
}

onMounted(async () => {
  await run(() => loadConfig());
  loading.value = false;
});
onBeforeUnmount(() => setLogAuto(false));
</script>

<template>
  <div class="unapi @container w-full max-w-[1400px] text-foreground flex flex-col gap-3 pb-4">
    <!-- Connection strip -->
    <div class="rounded-lg border border-border bg-card px-4 py-3 flex flex-wrap items-center gap-x-4 gap-y-2">
      <div class="flex items-center gap-2">
        <h2 class="text-base font-semibold whitespace-nowrap">Unraid MCP</h2>
        <Badge :variant="service.running ? 'green' : 'gray'" size="sm">
          {{ service.running ? "Running" : "Stopped" }}
        </Badge>
        <Badge v-if="boolVal('UNRAID_MCP_TAILSCALE_SERVE') && tailscale.available" variant="orange" size="sm">
          tailnet
        </Badge>
      </div>

      <button
        v-if="endpoint"
        type="button"
        class="flex items-center gap-2 rounded-md border border-border bg-background px-2.5 py-1 font-mono text-sm text-muted-foreground hover:text-foreground hover:border-primary/60 transition-colors"
        :title="copied ? 'Copied' : 'Copy endpoint'"
        @click="copyEndpoint"
      >
        <span class="truncate max-w-[26rem]">{{ endpoint }}</span>
        <span class="text-xs uppercase tracking-wide" :class="copied ? 'text-unraid-green-500' : 'text-primary'">
          {{ copied ? "copied" : "copy" }}
        </span>
      </button>
      <span v-else class="text-sm text-muted-foreground">stdio transport — no network endpoint</span>

      <div class="ms-auto flex items-center gap-2">
        <span v-if="savedFlash" class="text-sm text-unraid-green-500 whitespace-nowrap">Saved — restarted</span>
        <div class="flex items-center gap-1.5" :title="service.enabled ? 'Start automatically with the array' : 'Do not start with the array'">
          <Switch :model-value="service.enabled" :disabled="busy" @update:model-value="svc($event ? 'enable' : 'disable')" />
          <span class="text-sm text-muted-foreground">Autostart</span>
        </div>
        <Button size="sm" variant="outline" :disabled="busy" @click="svc(service.running ? 'stop' : 'start')">
          {{ service.running ? "Stop" : "Start" }}
        </Button>
        <Button size="sm" variant="outline" :disabled="busy || !service.running" @click="svc('restart')">
          Restart
        </Button>
        <Button size="sm" variant="outline" @click="toggleLog">{{ logOpen ? "Hide log" : "Log" }}</Button>
        <Button size="sm" :disabled="saving || loading" @click="apply">
          {{ saving ? "Applying…" : "Apply" }}
        </Button>
      </div>
    </div>

    <div v-if="error" role="alert" class="rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-sm text-destructive">
      {{ error }}
    </div>

    <!-- Log viewer -->
    <section v-if="logOpen" class="rounded-lg border border-border bg-card p-3 flex flex-col gap-2">
      <div class="flex items-center justify-between">
        <h3 class="text-[11px] font-semibold tracking-[0.08em] uppercase text-muted-foreground">
          Server log <span class="normal-case tracking-normal font-normal">/var/log/unraid-mcp/server.log</span>
        </h3>
        <div class="flex items-center gap-2">
          <div class="flex items-center gap-1.5">
            <Switch :model-value="logAuto" @update:model-value="setLogAuto($event)" />
            <span class="text-xs text-muted-foreground">Follow</span>
          </div>
          <Button size="sm" variant="ghost" class="px-2" @click="refreshLogs">Refresh</Button>
        </div>
      </div>
      <pre class="max-h-72 overflow-auto rounded-md bg-background border border-border p-2 font-mono text-xs leading-relaxed whitespace-pre-wrap">{{ logText }}</pre>
    </section>

    <div v-if="loading" class="text-sm text-muted-foreground">Loading configuration…</div>

    <template v-else>
      <div class="grid gap-3 @min-[880px]:grid-cols-2 items-start">
        <component
          :is="section.collapsed ? 'details' : 'section'"
          v-for="section in SECTIONS"
          :key="section.title"
          class="rounded-lg border border-border bg-card p-3 flex flex-col gap-2 min-w-0"
        >
          <summary
            v-if="section.collapsed"
            class="cursor-pointer select-none text-[11px] font-semibold tracking-[0.08em] uppercase text-muted-foreground marker:text-primary"
          >
            {{ section.title }}
          </summary>
          <h3 v-else class="text-[11px] font-semibold tracking-[0.08em] uppercase text-muted-foreground">
            {{ section.title }}
          </h3>

          <div class="grid grid-cols-[9.5rem_minmax(0,1fr)] items-center gap-x-3 gap-y-2" :class="section.collapsed ? 'mt-2' : ''">
            <template v-for="field in section.fields" :key="field.key">
              <Label :for="field.key" class="text-sm self-center leading-tight">{{ field.label }}</Label>

              <div v-if="field.kind === 'secret'" class="flex items-center gap-1.5 min-w-0">
                <Input
                  :id="field.key"
                  v-model="secretEdits[field.key].value"
                  :type="secretEdits[field.key].show ? 'text' : 'password'"
                  class="h-8 font-mono text-sm flex-1 min-w-0"
                  :placeholder="secretConfigured(field.key) ? '•••••• configured' : 'not set'"
                  :disabled="secretEdits[field.key].clear"
                  autocomplete="new-password"
                  data-1p-ignore
                  data-lpignore="true"
                  data-bwignore="true"
                  data-form-type="other"
                />
                <Button size="sm" variant="ghost" class="px-2" @click="toggleSecret(field.key)">
                  {{ secretEdits[field.key].show ? "Hide" : "Show" }}
                </Button>
                <Button
                  v-if="secretConfigured(field.key)"
                  size="sm"
                  :variant="secretEdits[field.key].clear ? 'destructive' : 'ghost'"
                  class="px-2"
                  @click="secretEdits[field.key].clear = !secretEdits[field.key].clear"
                >
                  {{ secretEdits[field.key].clear ? "Will clear" : "Clear" }}
                </Button>
              </div>

              <div v-else-if="field.kind === 'toggle'" class="flex items-center gap-2">
                <Switch
                  :id="field.key"
                  :model-value="boolVal(field.key)"
                  :disabled="fieldDisabled(field)"
                  @update:model-value="setBool(field.key, $event)"
                />
                <span v-if="fieldDisabled(field)" class="text-xs text-muted-foreground">Tailscale plugin not detected</span>
              </div>

              <Select v-else-if="field.kind === 'select'" :id="field.key" v-model="form[field.key]" class="[&>select]:h-8 [&>select]:py-1">
                <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
              </Select>

              <Input
                v-else
                :id="field.key"
                v-model="form[field.key]"
                :type="field.kind === 'number' ? 'number' : 'text'"
                class="h-8 text-sm"
                :class="field.mono ? 'font-mono' : ''"
                :placeholder="field.placeholder ?? ''"
              />

              <div class="col-span-2">
                <HelpText>{{ field.help }}</HelpText>
              </div>
            </template>
          </div>
        </component>
      </div>

      <!-- Unmanaged keys: single quiet line, only when present -->
      <p v-if="payload && Object.keys(payload.extra).length" class="text-xs text-muted-foreground px-1">
        Also in <span class="font-mono">/boot/config/plugins/unraid-mcp/.env</span> (preserved on save):
        <span class="font-mono">{{ Object.keys(payload.extra).join(", ") }}</span>
      </p>
    </template>
  </div>
</template>
