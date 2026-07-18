import { describe, expect, it, vi } from "vitest";
import { startPolling } from "./polling";

describe("startPolling", () => {
  it("does not overlap slow executions", async () => {
    vi.useFakeTimers();
    let resolveTask!: () => void;
    const task = vi.fn(() => new Promise<void>((resolve) => { resolveTask = resolve; }));
    const poller = startPolling(task, 100, { immediate: true });

    await vi.advanceTimersByTimeAsync(500);
    expect(task).toHaveBeenCalledTimes(1);

    resolveTask();
    await Promise.resolve();
    await vi.advanceTimersByTimeAsync(99);
    expect(task).toHaveBeenCalledTimes(1);
    await vi.advanceTimersByTimeAsync(1);
    expect(task).toHaveBeenCalledTimes(2);

    poller.stop();
    vi.useRealTimers();
  });

  it("stops future schedules", async () => {
    vi.useFakeTimers();
    const task = vi.fn(async () => {});
    const poller = startPolling(task, 100);
    poller.stop();
    await vi.advanceTimersByTimeAsync(500);
    expect(task).not.toHaveBeenCalled();
    vi.useRealTimers();
  });
});
