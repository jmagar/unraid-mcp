<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { init, Terminal as GhosttyTerminal, FitAddon, type IDisposable } from "ghostty-web";
import { gql } from "../graphql-client";
import { subscribe } from "../graphql-ws-client";
import { Button } from "./ui";

const props = defineProps<{ jailName: string }>();
const emit = defineEmits<{ close: [] }>();

const START_MUTATION = `
  mutation($name: String!, $cols: Int!, $rows: Int!) { startJailExec(name: $name, cols: $cols, rows: $rows) }
`;
const INPUT_MUTATION = `
  mutation($sessionId: String!, $data: String!) { sendJailExecInput(sessionId: $sessionId, data: $data) }
`;
const RESIZE_MUTATION = `
  mutation($sessionId: String!, $cols: Int!, $rows: Int!) { resizeJailExec(sessionId: $sessionId, cols: $cols, rows: $rows) }
`;
const STOP_MUTATION = `mutation($sessionId: String!) { stopJailExec(sessionId: $sessionId) }`;
const OUTPUT_SUBSCRIPTION = `subscription($sessionId: String!) { jailExecOutput(sessionId: $sessionId) }`;

const containerEl = ref<HTMLDivElement | null>(null);
const error = ref<string | null>(null);
const status = ref<"connecting" | "connected" | "disconnected">("connecting");

let term: GhosttyTerminal | null = null;
let fitAddon: FitAddon | null = null;
let sessionId: string | null = null;
let unsubscribe: (() => void) | null = null;
let onDataDisposable: IDisposable | null = null;
let onResizeDisposable: IDisposable | null = null;

/**
 * Canvas fillStyle/strokeStyle needs a resolved color, not a `var()`
 * reference — so read the actual Aurora token values off the document at
 * runtime (aurora-tokens.css defines them on :root) rather than hardcoding
 * hex copies that would drift from the design system.
 */
function auroraTheme() {
  const style = getComputedStyle(document.documentElement);
  const token = (name: string) => style.getPropertyValue(name).trim();

  const accentPrimary = token("--aurora-accent-primary");
  return {
    background: token("--aurora-page-bg"),
    foreground: token("--aurora-text-primary"),
    cursor: accentPrimary,
    selectionBackground: `color-mix(in srgb, ${accentPrimary} 22%, transparent)`,
    black: token("--aurora-page-bg"),
    red: token("--aurora-error"),
    green: token("--aurora-success"),
    yellow: token("--aurora-warn"),
    blue: token("--aurora-info"),
    magenta: token("--aurora-accent-pink"),
    cyan: accentPrimary,
    white: token("--aurora-text-primary"),
    brightBlack: token("--aurora-text-muted"),
    brightRed: token("--aurora-error-lift"),
    brightGreen: token("--aurora-success"),
    brightYellow: token("--aurora-warn"),
    brightBlue: token("--aurora-info"),
    brightMagenta: token("--aurora-accent-pink-strong"),
    brightCyan: token("--aurora-accent-strong"),
    brightWhite: "#ffffff",
  };
}

async function start() {
  if (!containerEl.value) return;

  // ghostty-web's WASM VT100 parser must be loaded once before any Terminal
  // is constructed — it's the same emulator core the native Ghostty app
  // uses, not a JS reimplementation like xterm.js.
  await init();

  term = new GhosttyTerminal({
    cols: 80,
    rows: 24,
    fontSize: 13,
    fontFamily: "JetBrains Mono, IBM Plex Mono, ui-monospace, Menlo, monospace",
    theme: auroraTheme(),
  });

  fitAddon = new FitAddon();
  term.loadAddon(fitAddon);
  term.open(containerEl.value);
  fitAddon.fit();
  // Built into FitAddon — sets up its own ResizeObserver and re-fits
  // automatically, so we don't need to manage one ourselves.
  fitAddon.observeResize();

  try {
    const data = await gql<{ startJailExec: string }>(START_MUTATION, {
      name: props.jailName,
      cols: term.cols,
      rows: term.rows,
    });
    sessionId = data.startJailExec;
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e);
    status.value = "disconnected";
    return;
  }

  status.value = "connected";
  unsubscribe = subscribe<{ jailExecOutput: string }>(
    OUTPUT_SUBSCRIPTION,
    { sessionId },
    (data) => term?.write(data.jailExecOutput),
    (e) => {
      error.value = e instanceof Error ? e.message : String(e);
      status.value = "disconnected";
    }
  );

  onDataDisposable = term.onData((data) => {
    if (sessionId) void gql(INPUT_MUTATION, { sessionId, data }).catch(() => {});
  });

  onResizeDisposable = term.onResize(({ cols, rows }) => {
    if (sessionId) void gql(RESIZE_MUTATION, { sessionId, cols, rows }).catch(() => {});
  });
}

async function stop() {
  onDataDisposable?.dispose();
  onResizeDisposable?.dispose();
  fitAddon?.dispose();
  unsubscribe?.();
  term?.dispose();
  if (sessionId) {
    await gql(STOP_MUTATION, { sessionId }).catch(() => {});
  }
}

onMounted(start);
onBeforeUnmount(stop);

function close() {
  emit("close");
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center" style="background: var(--aurora-overlay)">
    <div
      class="flex w-[90vw] max-w-4xl flex-col overflow-hidden"
      style="
        border: 1px solid var(--aurora-border-strong);
        border-radius: var(--aurora-radius-2);
        background: var(--aurora-page-bg);
        box-shadow: var(--aurora-shadow-strong);
      "
    >
      <!-- Title bar — matches the aurora terminal chrome used elsewhere (incus-web) -->
      <div
        class="flex shrink-0 items-center gap-2.5"
        style="
          height: 42px;
          padding: 0 14px;
          border-bottom: 1px solid var(--aurora-border-default);
          background: var(--aurora-panel-strong);
        "
      >
        <svg width="10" height="14" viewBox="0 0 10 14" fill="none" aria-hidden="true" style="flex-shrink: 0">
          <path d="M5 0L9 2.5L5 5L1 2.5Z" fill="var(--aurora-accent-primary)" opacity="0.95" />
          <path d="M5 3L9 5.5L5 8L1 5.5Z" fill="var(--aurora-accent-primary)" opacity="0.75" />
          <path d="M5 6L9 8.5L5 11L1 8.5Z" fill="var(--aurora-accent-primary)" opacity="0.5" />
          <path d="M5 9L9 11.5L5 14L1 11.5Z" fill="var(--aurora-accent-primary)" opacity="0.28" />
        </svg>
        <span
          class="min-w-0 flex-1 truncate"
          style="color: var(--aurora-text-muted); font-family: var(--aurora-font-mono); font-size: 12px; font-weight: 520"
        >
          {{ jailName }}
        </span>
        <span
          style="
            padding: 3px 7px;
            border: 1px solid var(--aurora-accent-primary-border);
            border-radius: 4px;
            background: var(--aurora-accent-primary-surface);
            color: var(--aurora-accent-primary-foreground);
            font-family: var(--aurora-font-mono);
            font-size: 10.5px;
            font-weight: 600;
          "
        >ghostty-web</span>
        <div class="ml-auto flex items-center gap-1.5" style="color: var(--aurora-text-muted); font-size: 11px; font-weight: 560">
          <span
            style="width: 7px; height: 7px; border-radius: 999px"
            :style="{
              background: status === 'connected' ? 'var(--aurora-success)' : status === 'connecting' ? 'var(--aurora-warn)' : 'var(--aurora-error)',
              boxShadow: `0 0 7px ${status === 'connected' ? 'var(--aurora-success)' : status === 'connecting' ? 'var(--aurora-warn)' : 'var(--aurora-error)'}`,
            }"
          />
          <span>{{ status === "connected" ? "Connected" : status === "connecting" ? "Connecting…" : "Disconnected" }}</span>
        </div>
        <Button size="sm" variant="outline" @click="close">Close</Button>
      </div>

      <div
        v-if="error"
        class="px-4 py-2 text-sm"
        style="background: var(--aurora-error-surface); color: var(--aurora-error-foreground); border-bottom: 1px solid var(--aurora-error-border)"
      >
        {{ error }}
      </div>

      <div class="p-4" style="background: var(--aurora-page-bg)">
        <div ref="containerEl" class="h-[60vh] w-full overflow-hidden"></div>
      </div>
    </div>
  </div>
</template>
