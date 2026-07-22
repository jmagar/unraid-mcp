<script setup lang="ts">
/**
 * Server log viewer — a self-contained Aurora-dark terminal panel. It owns its
 * own palette (Aurora dark tokens, https://aurora.tootie.tv) and stays dark
 * regardless of the surrounding Unraid webGUI theme, the way a terminal should.
 * Lines are tokenized and colorized by severity, timestamp, HTTP status, and
 * logger name.
 */
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { Button, Switch } from "./components/ui";
import { fetchLogs } from "./lib/config-client";

const raw = ref("");
const auto = ref(false);
const loading = ref(false);
const lineCount = ref(300);
let timer: ReturnType<typeof setInterval> | null = null;
let pane: HTMLElement | null = null;
const paneRef = (el: unknown) => {
  pane = el as HTMLElement | null;
};

// Aurora dark tokens (registry/aurora/styles/aurora.css) + CLI violet.
const C = {
  ts: "#7c93a1",
  msg: "#e6f4fb",
  debug: "#6f8492",
  info: "#72c8f5",
  notice: "#67cbfa",
  warn: "#c6a36b",
  error: "#c78490",
  critical: "#d9909a",
  module: "#a78bfa",
  ok: "#7dd3c7",
};

const LEVEL_COLOR: Record<string, string> = {
  DEBUG: C.debug,
  INFO: C.info,
  NOTICE: C.notice,
  WARNING: C.warn,
  WARN: C.warn,
  ERROR: C.error,
  CRITICAL: C.critical,
  FATAL: C.critical,
};

interface Seg {
  t: string;
  c?: string;
  b?: boolean;
}

// One combined scanner; classify each match by which group hit.
const TOKEN_RE =
  /(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?)|\b(DEBUG|INFO|NOTICE|WARNING|WARN|ERROR|CRITICAL|FATAL)\b|(?<=" )([1-5]\d{2})\b|\b((?:unraid_mcp|rc\.unraid-mcp|uvicorn|fastmcp)[\w.-]*)/g;

function tokenize(line: string): Seg[] {
  const segs: Seg[] = [];
  let last = 0;
  let m: RegExpExecArray | null;
  TOKEN_RE.lastIndex = 0;
  while ((m = TOKEN_RE.exec(line)) !== null) {
    if (m.index > last) segs.push({ t: line.slice(last, m.index), c: C.msg });
    if (m[1]) {
      segs.push({ t: m[1], c: C.ts });
    } else if (m[2]) {
      const col = LEVEL_COLOR[m[2]] ?? C.msg;
      segs.push({ t: m[2], c: col, b: col === C.error || col === C.critical });
    } else if (m[3]) {
      const code = Number(m[3]);
      const col = code < 300 ? C.ok : code < 400 ? C.info : code < 500 ? C.warn : C.error;
      segs.push({ t: m[3], c: col, b: code >= 500 });
    } else if (m[4]) {
      segs.push({ t: m[4], c: C.module });
    }
    last = m.index + m[0].length;
  }
  if (last < line.length) segs.push({ t: line.slice(last), c: C.msg });
  if (segs.length === 0) segs.push({ t: line || " ", c: C.msg });
  return segs;
}

/** Severity of a whole line, for the left accent rail. */
function lineLevel(line: string): string {
  const m = line.match(/\b(DEBUG|INFO|NOTICE|WARNING|WARN|ERROR|CRITICAL|FATAL)\b/);
  return m ? (LEVEL_COLOR[m[1]] ?? "transparent") : "transparent";
}

const lines = computed(() => {
  const text = raw.value.replace(/\n+$/, "");
  if (!text) return [];
  return text.split("\n").map((l) => ({ rail: lineLevel(l), segs: tokenize(l) }));
});

async function refresh(scroll = true) {
  loading.value = true;
  try {
    raw.value = (await fetchLogs(lineCount.value)) || "(log is empty)";
  } catch (e) {
    raw.value = `failed to fetch log: ${e instanceof Error ? e.message : e}`;
  }
  loading.value = false;
  if (scroll && pane) requestAnimationFrame(() => (pane!.scrollTop = pane!.scrollHeight));
}

function setAuto(on: boolean) {
  auto.value = on;
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
  if (on) {
    void refresh();
    timer = setInterval(() => void refresh(), 3000);
  }
}

onMounted(() => void refresh());
onBeforeUnmount(() => {
  if (timer) clearInterval(timer);
});
</script>

<template>
  <div class="flex flex-col gap-2 rounded-lg border p-3" style="background: #07131c; border-color: #1d3d4e">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-[11px] font-semibold tracking-[0.08em] uppercase" style="color: #a7bcc9">Server log</span>
        <span class="font-mono text-xs" style="color: #7c93a1">/var/log/unraid-mcp/server.log</span>
      </div>
      <div class="flex items-center gap-3">
        <label class="flex items-center gap-1.5 text-xs" style="color: #a7bcc9">
          lines
          <select
            v-model.number="lineCount"
            class="h-7 rounded-md border bg-transparent px-1.5 text-xs"
            style="border-color: #1d3d4e; color: #e6f4fb"
            @change="refresh()"
          >
            <option value="100">100</option>
            <option value="300">300</option>
            <option value="1000">1000</option>
          </select>
        </label>
        <div class="flex items-center gap-1.5">
          <Switch :model-value="auto" @update:model-value="setAuto($event)" />
          <span class="text-xs" style="color: #a7bcc9">Follow</span>
        </div>
        <Button size="sm" variant="ghost" class="px-2" :disabled="loading" @click="refresh()">
          {{ loading ? "…" : "Refresh" }}
        </Button>
      </div>
    </div>

    <div
      :ref="paneRef"
      class="overflow-auto rounded-md font-mono text-xs leading-relaxed"
      style="background: #07111a; border: 1px solid #142a37; height: min(70vh, 640px)"
    >
      <div
        v-for="(ln, i) in lines"
        :key="i"
        class="flex gap-2 px-2 py-[1px] whitespace-pre-wrap break-words hover:bg-[#0c1a24]"
        style="border-left: 2px solid"
        :style="{ borderLeftColor: ln.rail }"
      >
        <code class="flex-1">
          <span v-for="(s, j) in ln.segs" :key="j" :style="{ color: s.c, fontWeight: s.b ? 600 : 400 }">{{ s.t }}</span>
        </code>
      </div>
      <div v-if="lines.length === 0" class="px-2 py-1" style="color: #7c93a1">(log is empty)</div>
    </div>
  </div>
</template>
