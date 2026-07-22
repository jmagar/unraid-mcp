<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { Badge, Button, HelpText, Input, Label, Select, Switch } from "./components/ui";
import {
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
        help: "Only relevant for https:// API URLs. Leave on unless you know why; for self-signed certs prefer a CA bundle path.",
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
const advancedText = ref("");
const advancedError = ref("");

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
  advancedText.value = Object.entries(p.extra)
    .map(([k, v]) => `${k}=${v}`)
    .join("\n");
}

/** Parse the advanced textarea into {key: value}; sets advancedError on bad lines. */
function parseAdvanced(): Record<string, string> | null {
  advancedError.value = "";
  const out: Record<string, string> = {};
  for (const raw of advancedText.value.split("\n")) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const eq = line.indexOf("=");
    const key = eq === -1 ? line : line.slice(0, eq).trim();
    if (!/^UNRAID_[A-Z0-9_]{1,64}$/.test(key)) {
      advancedError.value = `Not a valid variable name: ${key || raw}`;
      return null;
    }
    if (eq === -1) {
      advancedError.value = `Missing '=' after ${key}`;
      return null;
    }
    out[key] = line.slice(eq + 1).trim();
  }
  return out;
}

function secretConfigured(key: string): boolean {
  return Boolean(payload.value?.config[`${key}_configured`]);
}

const service = computed(() => payload.value?.service ?? { enabled: false, running: false });

/** The endpoint MCP clients connect to, derived from live form state. */
const endpoint = computed(() => {
  if (form.UNRAID_MCP_TRANSPORT === "stdio") return "";
  const host =
    !form.UNRAID_MCP_HOST || form.UNRAID_MCP_HOST === "0.0.0.0"
      ? window.location.hostname
      : form.UNRAID_MCP_HOST;
  return `http://${host}:${form.UNRAID_MCP_PORT || "6970"}/mcp`;
});

async function copyEndpoint() {
  if (!endpoint.value) return;
  try {
    await navigator.clipboard.writeText(endpoint.value);
    copied.value = true;
    setTimeout(() => (copied.value = false), 1500);
  } catch {
    /* clipboard unavailable over plain http — selection fallback not worth it */
  }
}

function boolVal(key: string): boolean {
  return (form[key] ?? "").toLowerCase() === "true";
}
function setBool(key: string, v: boolean) {
  form[key] = v ? "true" : "false";
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
  const advanced = parseAdvanced();
  if (advanced === null) return;
  saving.value = true;
  const changes: Record<string, string> = { ...form, ...advanced };
  // A key previously shown in Advanced but now removed is an explicit delete.
  for (const key of Object.keys(payload.value?.extra ?? {})) {
    if (!(key in advanced)) changes[key] = "";
  }
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
    // Re-mask; drop a revealed-but-unedited value so Apply keeps omitting it.
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

onMounted(async () => {
  await run(() => loadConfig());
  loading.value = false;
});
</script>

<template>
  <div class="unapi w-full max-w-6xl text-foreground flex flex-col gap-3 pb-4">
    <!-- Connection strip: identity, state, endpoint, controls — one row, no scroll -->
    <div class="rounded-lg border border-border bg-card px-4 py-3 flex flex-wrap items-center gap-x-4 gap-y-2">
      <div class="flex items-center gap-2">
        <h2 class="text-base font-semibold whitespace-nowrap">Unraid MCP</h2>
        <Badge :variant="service.running ? 'green' : 'gray'" size="sm">
          {{ service.running ? "Running" : "Stopped" }}
        </Badge>
      </div>

      <button
        v-if="endpoint"
        type="button"
        class="flex items-center gap-2 rounded-md border border-border bg-background px-2.5 py-1 font-mono text-sm text-muted-foreground hover:text-foreground hover:border-primary/60 transition-colors"
        :title="copied ? 'Copied' : 'Copy endpoint'"
        @click="copyEndpoint"
      >
        <span class="truncate max-w-[22rem]">{{ endpoint }}</span>
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
        <Button size="sm" :disabled="saving || loading" @click="apply">
          {{ saving ? "Applying…" : "Apply" }}
        </Button>
      </div>
    </div>

    <div v-if="error" role="alert" class="rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-sm text-destructive">
      {{ error }}
    </div>

    <div v-if="loading" class="text-sm text-muted-foreground">Loading configuration…</div>

    <template v-else>
      <div class="grid gap-3 lg:grid-cols-2 items-start">
        <section
          v-for="section in SECTIONS"
          :key="section.title"
          class="rounded-lg border border-border bg-card p-3 flex flex-col gap-2 min-w-0"
        >
          <h3 class="text-[11px] font-semibold tracking-[0.08em] uppercase text-muted-foreground">
            {{ section.title }}
          </h3>

          <div class="grid grid-cols-[9.5rem_minmax(0,1fr)] items-center gap-x-3 gap-y-2">
            <template v-for="field in section.fields" :key="field.key">
              <Label :for="field.key" class="text-sm self-center whitespace-nowrap">{{ field.label }}</Label>

              <!-- secret: write-only with reveal + clear -->
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

              <div v-else-if="field.kind === 'toggle'" class="flex items-center">
                <Switch :id="field.key" :model-value="boolVal(field.key)" @update:model-value="setBool(field.key, $event)" />
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

              <!-- Native Unraid help: hidden until the header “?” toggle -->
              <div class="col-span-2">
                <HelpText>{{ field.help }}</HelpText>
              </div>
            </template>
          </div>
        </section>
      </div>

      <!-- Advanced: every other env var, editable as key=value lines -->
      <section class="rounded-lg border border-border bg-card p-3 flex flex-col gap-2">
        <div class="flex items-baseline justify-between">
          <h3 class="text-[11px] font-semibold tracking-[0.08em] uppercase text-muted-foreground">Advanced</h3>
          <span class="text-xs text-muted-foreground">
            Any <span class="font-mono">UNRAID_*</span> variable, one per line — applied to
            <span class="font-mono">.env</span> with the form fields
          </span>
        </div>
        <textarea
          v-model="advancedText"
          rows="3"
          spellcheck="false"
          class="w-full resize-y rounded-md border border-input bg-background px-3 py-1.5 font-mono text-sm focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-hidden"
          placeholder="UNRAID_SUBSCRIPTION_COLLECT_MAX_EVENTS=100"
        ></textarea>
        <p v-if="advancedError" class="text-sm text-destructive">{{ advancedError }}</p>
        <div class="col-span-2 -mt-1">
          <HelpText>
            Full reference in the project README. Secret-typed variables (Google OAuth keys) can be
            set here but are write-only: they disappear from this box after saving and stay stored.
            Removing a listed line deletes that variable on Apply.
          </HelpText>
        </div>
      </section>
    </template>
  </div>
</template>
