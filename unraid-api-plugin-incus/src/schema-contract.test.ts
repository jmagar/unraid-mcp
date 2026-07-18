import { describe, expect, it } from "vitest";
import { parse, print, Kind, type DocumentNode, type FieldDefinitionNode, type InputValueDefinitionNode } from "graphql";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import ts from "typescript";

const indexPath = fileURLToPath(new URL("../index.ts", import.meta.url));
const resolverPath = fileURLToPath(new URL("./incus.resolver.ts", import.meta.url));

function fieldSignatures(document: DocumentNode, typeName: string): Record<string, string> {
  const definition = document.definitions.find((entry) =>
    (entry.kind === Kind.OBJECT_TYPE_DEFINITION ||
      entry.kind === Kind.OBJECT_TYPE_EXTENSION ||
      entry.kind === Kind.INPUT_OBJECT_TYPE_DEFINITION) && entry.name.value === typeName
  );
  if (!definition || !("fields" in definition)) throw new Error(`Missing schema type ${typeName}`);
  const fields = (definition.fields ?? []) as readonly (FieldDefinitionNode | InputValueDefinitionNode)[];
  return Object.fromEntries(fields.map((field) => {
    const args = "arguments" in field
      ? field.arguments?.map((argument) => `${argument.name.value}: ${print(argument.type)}`).join(", ")
      : undefined;
    return [field.name.value, `${args ? `(${args})` : ""}: ${print(field.type)}`];
  }));
}

function enumValues(document: DocumentNode, enumName: string): string[] {
  const definition = document.definitions.find((entry) =>
    entry.kind === Kind.ENUM_TYPE_DEFINITION && entry.name.value === enumName
  );
  if (!definition || definition.kind !== Kind.ENUM_TYPE_DEFINITION) throw new Error(`Missing enum ${enumName}`);
  return definition.values?.map((value) => value.name.value) ?? [];
}

async function resolverMethods(): Promise<Record<"Query" | "Mutation" | "Subscription", string[]>> {
  const source = await readFile(resolverPath, "utf-8");
  const file = ts.createSourceFile(resolverPath, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
  const result = { Query: [] as string[], Mutation: [] as string[], Subscription: [] as string[] };
  for (const statement of file.statements) {
    if (!ts.isClassDeclaration(statement) || statement.name?.text !== "IncusResolver") continue;
    for (const member of statement.members) {
      if (!ts.isMethodDeclaration(member) || !member.name || !ts.isIdentifier(member.name)) continue;
      for (const decorator of ts.getDecorators(member) ?? []) {
        if (!ts.isCallExpression(decorator.expression) || !ts.isIdentifier(decorator.expression.expression)) continue;
        const kind = decorator.expression.expression.text;
        if (kind === "Query" || kind === "Mutation" || kind === "Subscription") result[kind].push(member.name.text);
      }
    }
  }
  return result;
}

describe("plugin GraphQL schema contract", () => {
  it("parses and exactly matches every resolver operation", async () => {
    const source = await readFile(indexPath, "utf-8");
    const schema = source.match(/graphqlSchemaExtension = async \(\) => `([\s\S]*?)`;\n/)?.[1];
    expect(schema, "graphqlSchemaExtension template").toBeTruthy();
    const document = parse(schema!);

    const expected = {
      Query: {
        incusHealthy: ": Boolean!",
        incusConfig: ": IncusConfig!",
        jails: ": [Jail!]!",
        jailDetail: "(name: String!): JailDetail!",
        jailImageBuildStatus: "(buildId: String!): ImageBuildStatus",
        homebrewInstallStatus: "(id: String!): HomebrewInstallStatus",
        privilegedCommandStatus: "(id: String!): PrivilegedCommandStatus",
        builderPresets: ": [BuilderPreset!]!",
        jailImages: ": [ImageRecord!]!",
        searchPackages: "(ecosystem: PackageEcosystem!, query: String!, distro: String, release: String): [PackageSearchResult!]!",
        searchAllPackages: "(query: String!, distro: String, release: String): PackageSearchResponse!",
      },
      Mutation: {
        updateIncusConfig: "(input: IncusConfigInput!): IncusConfig!",
        launchJail: "(name: String!, image: String, allowSudo: Boolean): Boolean!",
        setJailState: "(name: String!, action: JailAction!): Boolean!",
        setJailWorkspace: "(name: String!, hostPath: String!): Boolean!",
        clearJailWorkspace: "(name: String!): Boolean!",
        migrateJailWorkspace: "(name: String!): String!",
        setJailLimits: "(name: String!, cpu: String, memory: String): Boolean!",
        deleteJail: "(name: String!): Boolean!",
        deleteStoppedJails: ": [String!]!",
        installHomebrewFormula: "(name: String!, formula: String!): String!",
        grantJailSudo: "(name: String!): Boolean!",
        startPrivilegedCommand: "(name: String!, command: String!): String!",
        buildJailImage: "(distro: String!, release: String!, packages: [String!]!, alias: String!, basedOn: String, postInstallCommands: [String!]): String!",
        saveBuilderPreset: "(input: BuilderPresetInput!): BuilderPreset!",
        deleteBuilderPreset: "(name: String!): Boolean!",
        setMasterImage: "(alias: String!, isMaster: Boolean!): ImageRecord!",
        deleteJailImage: "(alias: String!): Boolean!",
        pruneStaleImageRecords: ": [String!]!",
        startJailExec: "(name: String!, cols: Int, rows: Int): String!",
        sendJailExecInput: "(sessionId: String!, data: String!): Boolean!",
        resizeJailExec: "(sessionId: String!, cols: Int!, rows: Int!): Boolean!",
        stopJailExec: "(sessionId: String!): Boolean!",
      },
      Subscription: {
        jailExecOutput: "(sessionId: String!): String!",
      },
    };

    const methods = await resolverMethods();
    for (const kind of ["Query", "Mutation", "Subscription"] as const) {
      const actual = fieldSignatures(document, kind);
      expect(actual).toEqual(expected[kind]);
      expect(methods[kind].sort()).toEqual(Object.keys(expected[kind]).sort());
    }
  });

  it("matches the canonical config, status, metric, and enum contracts", async () => {
    const source = await readFile(indexPath, "utf-8");
    const schema = source.match(/graphqlSchemaExtension = async \(\) => `([\s\S]*?)`;\n/)?.[1] ?? "";
    const document = parse(schema);

    expect(fieldSignatures(document, "Jail")).toEqual({
      name: ": String!", status: ": String!", ipv4: ": String",
      cpuUsageNs: ": String", memoryUsageBytes: ": String", memoryTotalBytes: ": String",
    });
    const outputConfig = fieldSignatures(document, "IncusConfig");
    const inputConfig = fieldSignatures(document, "IncusConfigInput");
    expect(Object.keys(outputConfig)).toEqual([
      "enabled", "stateDir", "storageDriver", "storageSource", "storagePoolName", "jailBridge",
      "jailSubnet", "jailNat", "jailIpv6", "aclName", "aclBlock", "aclAllow", "aclDefaultEgress",
      "aclDefaultIngress", "jailProfile", "jailImage", "jailNesting", "jailCpu", "jailMemory",
      "jailWorkspaceRoot", "jailAgentUid", "jailAgentGid", "jailBindMounts", "tsAuthKeyConfigured",
      "dashboardWidgetEnable",
    ]);
    expect(outputConfig).not.toHaveProperty("tsAuthKey");
    expect(inputConfig.tsAuthKey).toBe(": String");
    expect(inputConfig).not.toHaveProperty("tsAuthKeyConfigured");
    expect(fieldSignatures(document, "PrivilegedCommandStatus").status).toBe(": JobStatus!");
    expect(fieldSignatures(document, "HomebrewInstallStatus").status).toBe(": JobStatus!");
    expect(fieldSignatures(document, "ImageBuildStatus").status).toBe(": ImageBuildState!");
    expect(enumValues(document, "JailAction")).toEqual(["start", "stop", "restart", "freeze", "unfreeze"]);
    expect(enumValues(document, "JobStatus")).toEqual(["running", "success", "failed"]);
    expect(enumValues(document, "ImageBuildState")).toEqual(["queued", "running", "success", "failed"]);
    expect(enumValues(document, "PackageEcosystem")).toEqual(["apt", "npm", "pypi", "brew"]);
  });
});
