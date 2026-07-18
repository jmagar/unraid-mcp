import { describe, expect, it } from "vitest";
import { buildConfigUpdate } from "./configPayload";
import type { IncusConfig } from "../types";

const config = { enabled: true, tsAuthKeyConfigured: true } as IncusConfig;

describe("buildConfigUpdate", () => {
  it("omits secret fields when no replacement is requested", () => {
    expect(buildConfigUpdate(config, { replacement: "", clear: false })).toEqual({ enabled: true });
  });

  it("sends only an explicit replacement or clear value", () => {
    expect(buildConfigUpdate(config, { replacement: "new-secret", clear: false })).toEqual({ enabled: true, tsAuthKey: "new-secret" });
    expect(buildConfigUpdate(config, { replacement: "ignored", clear: true })).toEqual({ enabled: true, tsAuthKey: "" });
  });
});
