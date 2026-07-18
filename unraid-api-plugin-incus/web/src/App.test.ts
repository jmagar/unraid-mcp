import { mount, flushPromises } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App.vue";

const { gqlMock } = vi.hoisted(() => ({ gqlMock: vi.fn() }));
vi.mock("./graphql-client", () => ({ gql: gqlMock }));

describe("App", () => {
  afterEach(() => vi.useRealTimers());
  beforeEach(() => {
    gqlMock.mockReset();
    gqlMock.mockImplementation((query: string) => {
      if (query.includes("incusConfig")) return Promise.resolve({ incusConfig: { enabled: true, jailCpu: "", jailMemory: "", tsAuthKeyConfigured: false } });
      if (query.includes("incusHealthy")) return Promise.resolve({ incusHealthy: true, jails: [] });
      if (query.includes("builderPresets")) return Promise.resolve({ builderPresets: [] });
      if (query.includes("jailImages")) return Promise.resolve({ jailImages: [] });
      return Promise.resolve({});
    });
  });

  it("wires accessible tabs and keyboard navigation through the real app shell", async () => {
    const wrapper = mount(App, { attachTo: document.body });
    await flushPromises();
    const tabs = wrapper.findAll('[role="tab"]');
    expect(tabs.map((tab) => tab.text())).toEqual(["Builder", "Containers", "Config"]);
    expect(tabs[1].attributes("aria-selected")).toBe("true");

    await tabs[1].trigger("keydown", { key: "ArrowRight" });
    await flushPromises();
    expect(wrapper.get("#incus-tab-config").attributes("aria-selected")).toBe("true");
    expect(wrapper.get("#incus-panel-config").attributes("role")).toBe("tabpanel");
    expect(wrapper.get('label[for="config-enabled"]').text()).toContain("Enable Incus");
    wrapper.unmount();
  });

  it("invalidates an in-flight package search as soon as the query is cleared", async () => {
    vi.useFakeTimers();
    let resolveSearch!: (value: unknown) => void;
    gqlMock.mockImplementation((query: string) => {
      if (query.includes("incusConfig")) return Promise.resolve({ incusConfig: { enabled: true, jailCpu: "", jailMemory: "", tsAuthKeyConfigured: false } });
      if (query.includes("incusHealthy")) return Promise.resolve({ incusHealthy: true, jails: [] });
      if (query.includes("builderPresets")) return Promise.resolve({ builderPresets: [] });
      if (query.includes("jailImages")) return Promise.resolve({ jailImages: [] });
      if (query.includes("searchAllPackages")) return new Promise((resolve) => { resolveSearch = resolve; });
      return Promise.resolve({});
    });
    const wrapper = mount(App);
    await flushPromises();
    await wrapper.get("#incus-tab-builder").trigger("click");
    await wrapper.get("#package-search").setValue("curl");
    await vi.advanceTimersByTimeAsync(400);
    await wrapper.get("#package-search").setValue("");
    resolveSearch({ searchAllPackages: { results: [{ ecosystem: "apt", name: "stale-package" }], errors: [] } });
    await flushPromises();
    expect(wrapper.text()).not.toContain("stale-package");
    wrapper.unmount();
    vi.useRealTimers();
  });
});
