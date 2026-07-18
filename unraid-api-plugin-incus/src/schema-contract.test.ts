import { describe, expect, it } from "vitest";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

describe("plugin GraphQL schema contract", () => {
  it("contains every privileged resolver and the write-only secret contract", async () => {
    const source = await readFile(fileURLToPath(new URL("../index.ts", import.meta.url)), "utf-8");
    const schema = source.match(/graphqlSchemaExtension = async \(\) => `([\s\S]*?)`;\n/)?.[1] ?? "";
    expect(schema).toMatch(/incusConfig:\s*IncusConfig!/);
    const outputConfig = schema.match(/type IncusConfig \{([\s\S]*?)\n  \}/)?.[1] ?? "";
    expect(outputConfig).toContain("tsAuthKeyConfigured: Boolean!");
    expect(outputConfig).not.toMatch(/\btsAuthKey:/);
    expect(schema).toMatch(/setJailState\(name: String!, action: JailAction!\)/);
    for (const field of ["updateIncusConfig", "startJailExec", "sendJailExecInput", "resizeJailExec", "stopJailExec"]) {
      expect(schema).toContain(`${field}(`);
    }
    expect(schema).toContain("jailExecOutput(sessionId: String!): String!");
  });
});
