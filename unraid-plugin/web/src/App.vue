<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { Badge, Button, HelpText, Input, Label, Select, Switch } from "./components/ui";
import {
  loadConfig,
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
  eyebrow: string;
  title: string;
  fields: FieldDef[];
}

const SECTIONS: Section[] = [
  {
    eyebrow: "Connection",
    title: "Unraid API",
    fields: [
      {
        key: "UNRAID_API_URL",
        label: "GraphQL URL",
        help: "The local Unraid GraphQL endpoint. http://127.0.0.1/graphql on this box.",
        kind: "text",
        mono: true,
        placeholder: "http://127.0.0.1/graphql",
      },
      {
        key: "UNRAID_API_KEY",
        label: "API key",
        help: "Unraid API key. Auto-provisioned at install when possible; create one with: unraid-api apikey --create",
        kind: "secret",
      },
      {
        key: "UNRAID_VERIFY_SSL",
        label: "Verify SSL",
        help: "Disable for self-signed certificates (typical for local access).",
        kind: "toggle",
      },
    ],
  },
  {
    eyebrow: "Server",
    title: "MCP server",
    fields: [
      {
        key: "UNRAID_MCP_TRANSPORT",
        label: "Transport",
        help: "streamable-http serves MCP over HTTP; stdio is for local piping only.",
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
        key: "UNRAID_MCP_LOG_LEVEL",
        label: "Log level",
        help: "Server log verbosity. Logs land in /var/log/unraid-mcp/server.log.",
        kind: "select",
        options: ["DEBUG", "INFO", "WARNING", "ERROR"],
      },
      {
        key: "UNRAID_MCP_MAX_RESPONSE_BYTES",
        label: "Max response bytes",
        help: "Backstop cap on serialized tool responses (default 40000 ≈ 10K tokens).",
        kind: "number",
        placeholder: "40000",
      },
    ],
  },
  {
    eyebrow: "Auth",
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
    eyebrow: "Subscriptions",
    title: "Live data",
    fields: [
      {
        key: "UNRAID_AUTO_START_SUBSCRIPTIONS",
        label: "Auto-start subscriptions",
        help: "Lazily start WebSocket subscriptions on first live-data access.",
        kind: "toggle",
      },
      {
        key: "UNRAID_MAX_RECONNECT_ATTEMPTS",
        label: "Max reconnect attempts",
        help: "WebSocket reconnect limit before a subscription is marked failed.",
        kind: "number",
        placeholder: "10",
      },
    ],
  },
];

const payload = ref<ConfigPayload | null>(null);
const form = reactive<Record<string, string>>({});
const secretEdits = reactive<Record<string, { value: string; clear: boolean; show: boolean }>>({});
const loading = ref(true);
const saving = ref(false);
const busy = ref(false);
const error = ref("");
const savedFlash = ref(false);

const secretKeys = SECTIONS.flatMap((s) => s.fields)
  .filter((f) => f.kind === "secret")
  .map((f) => f.key);

function hydrate(p: ConfigPayload) {
  payload.value = p;
  for (const section of SECTIONS) {
    for (const f of section.fields) {
      if (f.kind === "secret") {
        if (!secretEdits[f.key]) {
          secretEdits[f.key] = { value: "", clear: false, show: false };
        } else {
          secretEdits[f.key].value = "";
          secretEdits[f.key].clear = false;
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
  saving.value = true;
  const changes: Record<string, string> = { ...form };
  for (const key of secretKeys) {
    const edit = secretEdits[key];
    if (edit?.clear) changes[key] = "";
    else if (edit?.value) changes[key] = edit.value;
    // untouched secrets are omitted -> kept server-side
  }
  await run(() => saveConfig(changes));
  saving.value = false;
  if (!error.value) {
    savedFlash.value = true;
    setTimeout(() => (savedFlash.value = false), 2500);
  }
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
  <div class="unapi w-full max-w-4xl text-foreground flex flex-col gap-6 pb-8">
    <!-- Masthead: service state + controls -->
    <div class="rounded-lg border border-border bg-card p-4 flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <h2 class="text-lg font-semibold">Unraid MCP Server</h2>
        <Badge :variant="service.running ? 'green' : 'gray'" size="sm">
          {{ service.running ? "Running" : "Stopped" }}
        </Badge>
        <Badge :variant="service.enabled ? 'orange' : 'gray'" size="sm">
          {{ service.enabled ? "Autostart on" : "Autostart off" }}
        </Badge>
      </div>
      <div class="flex items-center gap-2">
        <Button size="sm" variant="outline" :disabled="busy" @click="svc(service.enabled ? 'disable' : 'enable')">
          {{ service.enabled ? "Disable" : "Enable" }}
        </Button>
        <Button
          size="sm"
          variant="outline"
          :disabled="busy"
          @click="svc(service.running ? 'stop' : 'start')"
        >
          {{ service.running ? "Stop" : "Start" }}
        </Button>
        <Button size="sm" variant="outline" :disabled="busy || !service.running" @click="svc('restart')">
          Restart
        </Button>
      </div>
    </div>

    <div v-if="error" role="alert" class="rounded-md border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
      {{ error }}
    </div>

    <div v-if="loading" class="text-sm text-muted-foreground">Loading configuration…</div>

    <template v-else>
      <section
        v-for="section in SECTIONS"
        :key="section.title"
        class="rounded-lg border border-border bg-card p-4 flex flex-col gap-4"
      >
        <div>
          <p class="text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground">
            {{ section.eyebrow }}
          </p>
          <h3 class="text-base font-semibold">{{ section.title }}</h3>
        </div>

        <div class="grid grid-cols-[14rem_1fr] items-center gap-x-4 gap-y-4">
          <template v-for="field in section.fields" :key="field.key">
            <Label :for="field.key" class="self-center">{{ field.label }}</Label>

            <!-- secret: write-only with reveal + clear -->
            <div v-if="field.kind === 'secret'" class="flex items-center gap-2">
              <Input
                :id="field.key"
                v-model="secretEdits[field.key].value"
                :type="secretEdits[field.key].show ? 'text' : 'password'"
                class="font-mono flex-1"
                :placeholder="secretConfigured(field.key) ? '•••••• (configured — type to replace)' : 'not set'"
                :disabled="secretEdits[field.key].clear"
              />
              <Button size="sm" variant="outline" @click="secretEdits[field.key].show = !secretEdits[field.key].show">
                {{ secretEdits[field.key].show ? "Hide" : "Show" }}
              </Button>
              <Button
                v-if="secretConfigured(field.key)"
                size="sm"
                :variant="secretEdits[field.key].clear ? 'destructive' : 'outline'"
                @click="secretEdits[field.key].clear = !secretEdits[field.key].clear"
              >
                {{ secretEdits[field.key].clear ? "Will clear" : "Clear" }}
              </Button>
            </div>

            <div v-else-if="field.kind === 'toggle'" class="flex items-center">
              <Switch :id="field.key" :model-value="boolVal(field.key)" @update:model-value="setBool(field.key, $event)" />
            </div>

            <Select v-else-if="field.kind === 'select'" :id="field.key" v-model="form[field.key]">
              <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
            </Select>

            <Input
              v-else
              :id="field.key"
              v-model="form[field.key]"
              :type="field.kind === 'number' ? 'number' : 'text'"
              :class="field.mono ? 'font-mono' : ''"
              :placeholder="field.placeholder ?? ''"
            />

            <div class="col-span-2 -mt-3">
              <HelpText>{{ field.help }}</HelpText>
            </div>
          </template>
        </div>
      </section>

      <!-- Unmanaged keys present in the env file: shown read-only -->
      <section
        v-if="payload && Object.keys(payload.extra).length"
        class="rounded-lg border border-border bg-card p-4 flex flex-col gap-2"
      >
        <p class="text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground">Advanced</p>
        <h3 class="text-base font-semibold">Other variables in .env</h3>
        <p class="text-sm text-muted-foreground">
          Present in the config file but not managed by this page; edit them in
          <span class="font-mono">/boot/config/plugins/unraid-mcp/.env</span>.
        </p>
        <div class="font-mono text-sm text-muted-foreground">
          <div v-for="(v, k) in payload.extra" :key="k">{{ k }}={{ v }}</div>
        </div>
      </section>

      <div class="flex items-center justify-end gap-3">
        <span v-if="savedFlash" class="text-sm text-unraid-green-500">Saved — service restarted.</span>
        <Button :disabled="saving" @click="apply">{{ saving ? "Applying…" : "Apply" }}</Button>
      </div>
    </template>
  </div>
</template>
