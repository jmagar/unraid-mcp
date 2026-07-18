export interface PollController {
  stop(): void;
  trigger(): Promise<void>;
}

/**
 * Poll an async task without ever overlapping invocations. The next timer is
 * scheduled only after the current task settles, so a slow API cannot create
 * an ever-growing queue of stale requests.
 */
export function startPolling(
  task: () => Promise<void>,
  intervalMs: number,
  options: { immediate?: boolean; onError?: (error: unknown) => void } = {}
): PollController {
  let stopped = false;
  let inFlight: Promise<void> | null = null;
  let timer: ReturnType<typeof setTimeout> | null = null;
  const visibilityTarget = typeof document === "undefined" ? null : document;

  const schedule = () => {
    if (stopped) return;
    timer = setTimeout(() => void run(), intervalMs);
  };

  const run = async () => {
    if (stopped) return;
    if (visibilityTarget?.hidden) {
      schedule();
      return;
    }
    if (inFlight) return inFlight;
    inFlight = task().catch((error) => options.onError?.(error)).finally(() => {
      inFlight = null;
      schedule();
    });
    return inFlight;
  };

  if (options.immediate) void run();
  else schedule();

  const onVisibilityChange = () => {
    if (!visibilityTarget?.hidden && !stopped && !inFlight) {
      if (timer) clearTimeout(timer);
      timer = null;
      void run();
    }
  };
  visibilityTarget?.addEventListener("visibilitychange", onVisibilityChange);

  return {
    stop() {
      stopped = true;
      if (timer) clearTimeout(timer);
      timer = null;
      visibilityTarget?.removeEventListener("visibilitychange", onVisibilityChange);
    },
    trigger: run,
  };
}
