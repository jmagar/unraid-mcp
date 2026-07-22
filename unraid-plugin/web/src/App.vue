<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { Badge, Button, HelpText, Input, Label, Select, Switch } from "./components/ui";
import { SECTIONS, type FieldDef } from "./fields";
import LogView from "./LogView.vue";
import {
  checkUpdate,
  fetchStats,
  loadConfig,
  resetServer,
  revealSecret,
  saveConfig,
  serviceAction,
  updateServer,
  type ConfigPayload,
  type ServiceOp,
} from "./lib/config-client";

type Tab = "dashboard" | "logs" | "settings";
const tab = ref<Tab>("dashboard");

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
let statsTimer: ReturnType<typeof setInterval> | null = null;
const latestVersion = ref("");
const checkingUpdate = ref(false);
const updating = ref(false);

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
const version = computed(() => payload.value?.version ?? { installed: "unknown", overlay: false });
const proc = computed(() => payload.value?.process ?? { pid: 0, cpu: 0, memMB: 0, uptime: 0 });
const updateAvailable = computed(() => {
  const l = latestVersion.value.replace(/^v/, "");
  return l !== "" && l !== version.value.installed;
});

const uptimeText = computed(() => {
  const s = proc.value.uptime;
  if (!s || !service.value.running) return "—";
  const d = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  const m = Math.floor((s % 3600) / 60);
  if (d) return `${d}d ${h}h`;
  if (h) return `${h}h ${m}m`;
  return `${m}m`;
});

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

async function doCheckUpdate() {
  checkingUpdate.value = true;
  error.value = "";
  try {
    latestVersion.value = await checkUpdate();
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e);
  }
  checkingUpdate.value = false;
}
async function doUpdate() {
  updating.value = true;
  await run(() => updateServer(latestVersion.value.replace(/^v/, "")));
  updating.value = false;
}
async function doReset() {
  updating.value = true;
  await run(() => resetServer());
  updating.value = false;
}

/** Poll cheap process stats while the dashboard is visible. */
async function pollStats() {
  try {
    const s = await fetchStats();
    if (payload.value) {
      payload.value.service = s.service;
      payload.value.process = s.process;
    }
  } catch {
    /* transient; next tick retries */
  }
}
function setStatsPolling(on: boolean) {
  if (statsTimer) {
    clearInterval(statsTimer);
    statsTimer = null;
  }
  if (on) statsTimer = setInterval(pollStats, 3000);
}

function switchTab(t: Tab) {
  tab.value = t;
  setStatsPolling(t === "dashboard");
}

onMounted(async () => {
  await run(() => loadConfig());
  loading.value = false;
  void doCheckUpdate();
  setStatsPolling(true);
});
onBeforeUnmount(() => {
  setStatsPolling(false);
});
</script>

<template>
  <div class="unapi @container w-full max-w-[1400px] text-foreground flex flex-col gap-3 pb-4">
    <!-- Tab bar -->
    <div class="flex items-center gap-1 border-b border-border">
      <button
        v-for="t in (['dashboard', 'logs', 'settings'] as Tab[])"
        :key="t"
        type="button"
        class="px-4 py-2 text-sm font-medium capitalize border-b-2 -mb-px transition-colors"
        :class="tab === t ? 'border-primary text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground'"
        @click="switchTab(t)"
      >
        {{ t }}
      </button>
    </div>

    <div v-if="error" role="alert" class="rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-sm text-destructive">
      {{ error }}
    </div>

    <div v-if="loading" class="text-sm text-muted-foreground">Loading…</div>

    <!-- ── DASHBOARD ─────────────────────────────────────────────── -->
    <template v-else-if="tab === 'dashboard'">
      <div class="grid gap-3 @min-[880px]:grid-cols-2 items-start">
        <!-- LEFT: Connection, then Resources -->
        <div class="flex flex-col gap-3">
          <section class="rounded-lg border border-border bg-card p-4 flex flex-col gap-2">
            <h3 class="text-base font-semibold">Connection</h3>
            <button
              v-if="endpoint"
              type="button"
              class="flex items-center gap-2 rounded-md border border-border bg-background px-2.5 py-1.5 font-mono text-sm text-muted-foreground hover:text-foreground hover:border-primary/60 transition-colors w-full"
              :title="copied ? 'Copied' : 'Copy endpoint'"
              @click="copyEndpoint"
            >
              <span class="truncate flex-1 text-start">{{ endpoint }}</span>
              <span class="text-xs uppercase tracking-wide shrink-0" :class="copied ? 'text-unraid-green-500' : 'text-primary'">{{ copied ? "copied" : "copy" }}</span>
            </button>
            <span v-else class="text-sm text-muted-foreground">stdio transport — no network endpoint</span>
            <p class="text-xs text-muted-foreground">
              Transport <span class="font-mono text-foreground">{{ form.UNRAID_MCP_TRANSPORT }}</span> ·
              authenticate with the bearer token from Settings
            </p>
          </section>

          <section class="rounded-lg border border-border bg-card p-4 flex flex-col gap-3">
            <h3 class="text-base font-semibold">Resources</h3>
            <div class="grid grid-cols-3 gap-2">
              <div class="rounded-md bg-background border border-border p-2 text-center">
                <div class="text-lg font-semibold tabular-nums">{{ service.running ? proc.cpu.toFixed(1) + "%" : "—" }}</div>
                <div class="text-xs text-muted-foreground">CPU</div>
              </div>
              <div class="rounded-md bg-background border border-border p-2 text-center">
                <div class="text-lg font-semibold tabular-nums">{{ service.running ? proc.memMB.toFixed(0) + " MB" : "—" }}</div>
                <div class="text-xs text-muted-foreground">Memory</div>
              </div>
              <div class="rounded-md bg-background border border-border p-2 text-center">
                <div class="text-lg font-semibold tabular-nums">{{ uptimeText }}</div>
                <div class="text-xs text-muted-foreground">Uptime</div>
              </div>
            </div>
            <p class="text-xs text-muted-foreground">PID {{ proc.pid || "—" }} · updates live</p>
          </section>
        </div>

        <!-- RIGHT: Server, then Version -->
        <div class="flex flex-col gap-3">
          <section class="rounded-lg border border-border bg-card p-4 flex flex-col gap-3">
            <div class="flex items-center gap-2">
              <h3 class="text-base font-semibold">Server</h3>
              <Badge :variant="service.running ? 'green' : 'gray'" size="sm">
                {{ service.running ? "Running" : "Stopped" }}
              </Badge>
              <Badge v-if="boolVal('UNRAID_MCP_TAILSCALE_SERVE') && tailscale.available" variant="orange" size="sm">tailnet</Badge>
            </div>
            <div class="flex items-center gap-2">
              <Button size="sm" variant="outline" :disabled="busy" @click="svc(service.running ? 'stop' : 'start')">
                {{ service.running ? "Stop" : "Start" }}
              </Button>
              <Button size="sm" variant="outline" :disabled="busy || !service.running" @click="svc('restart')">Restart</Button>
              <div class="ms-auto flex items-center gap-1.5" :title="service.enabled ? 'Starts with the array' : 'Does not start with the array'">
                <Switch :model-value="service.enabled" :disabled="busy" @update:model-value="svc($event ? 'enable' : 'disable')" />
                <span class="text-sm text-muted-foreground">Autostart</span>
              </div>
            </div>
          </section>

          <section class="rounded-lg border border-border bg-card p-4 flex flex-col gap-2">
            <div class="flex items-center gap-2">
              <h3 class="text-base font-semibold">Version</h3>
              <span class="font-mono text-sm">{{ version.installed }}</span>
              <Badge v-if="version.overlay" variant="gray" size="sm">updated</Badge>
              <Badge v-if="updateAvailable" variant="orange" size="sm">update available</Badge>
            </div>
            <p v-if="latestVersion" class="text-xs text-muted-foreground">
              latest release <span class="font-mono text-foreground">{{ latestVersion.replace(/^v/, "") }}</span>
            </p>
            <div class="flex items-center gap-2">
              <Button size="sm" variant="ghost" class="px-2" :disabled="checkingUpdate || updating" @click="doCheckUpdate">
                {{ checkingUpdate ? "Checking…" : "Check" }}
              </Button>
              <Button v-if="updateAvailable" size="sm" :disabled="updating" @click="doUpdate">
                {{ updating ? "Updating…" : `Update to ${latestVersion.replace(/^v/, "")}` }}
              </Button>
              <Button v-if="version.overlay" size="sm" variant="outline" :disabled="updating" @click="doReset">Revert to bundled</Button>
            </div>
          </section>
        </div>
      </div>
    </template>

    <!-- ── LOGS ──────────────────────────────────────────────────── -->
    <LogView v-else-if="tab === 'logs'" />

    <!-- ── SETTINGS ──────────────────────────────────────────────── -->
    <template v-else>
      <div class="flex items-center justify-end gap-3">
        <span v-if="savedFlash" class="text-sm text-unraid-green-500">Saved — restarted</span>
        <Button size="sm" :disabled="saving" @click="apply">{{ saving ? "Applying…" : "Apply" }}</Button>
      </div>

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
                <Switch :id="field.key" :model-value="boolVal(field.key)" :disabled="fieldDisabled(field)" @update:model-value="setBool(field.key, $event)" />
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

      <p v-if="payload && Object.keys(payload.extra).length" class="text-xs text-muted-foreground px-1">
        Also in <span class="font-mono">/boot/config/plugins/unraid-mcp/.env</span> (preserved on save):
        <span class="font-mono">{{ Object.keys(payload.extra).join(", ") }}</span>
      </p>
    </template>
  </div>
</template>
