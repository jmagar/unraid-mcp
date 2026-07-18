import { describe, expect, it } from "vitest";
import { appliedPermissions, AuthAction } from "../test-stubs/@unraid/shared/use-permissions.directive.js";
import { IncusResolver } from "./incus.resolver.js";

describe("IncusResolver authorization policy", () => {
  it("attaches VMS authorization metadata to every resolver method", () => {
    const methods = Object.getOwnPropertyNames(IncusResolver.prototype).filter((name) => name !== "constructor");
    expect(appliedPermissions.map((entry) => entry.key).sort()).toEqual(methods.sort());
    expect(appliedPermissions.find((entry) => entry.key === "incusConfig")?.action).toBe(AuthAction.READ_ANY);
    expect(appliedPermissions.find((entry) => entry.key === "deleteJail")?.action).toBe(AuthAction.DELETE_ANY);
    expect(appliedPermissions.find((entry) => entry.key === "startPrivilegedCommand")?.action).toBe(AuthAction.UPDATE_ANY);
  });
});
