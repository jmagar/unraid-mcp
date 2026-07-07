import { Module, Logger, Inject, Injectable } from "@nestjs/common";
import { ConfigModule, ConfigService } from "@nestjs/config";
import { ConfigFilePersister } from "@unraid/shared/services/config-file.js";
import { configFeature, IncusConfig } from "./src/config.entity.js";
import { IncusService } from "./src/incus.service.js";
import { IncusResolver } from "./src/incus.resolver.js";
import { IncusConfigSyncService } from "./src/config-sync.service.js";
import { IncusExecService } from "./src/incus-exec.service.js";
import { IncusImageBuilderService } from "./src/incus-image-builder.service.js";
import { IncusBuilderPresetsService } from "./src/incus-builder-presets.service.js";
import { IncusPackageSearchService } from "./src/incus-package-search.service.js";

/** Contract fields the unraid-api plugin loader validates against. */
export const adapter = "nestjs";

export const graphqlSchemaExtension = async () => `
  type Jail {
    name: String!
    status: String!
    ipv4: String
  }

  type JailDetail {
    name: String!
    profiles: [String!]!
    imageOs: String
    imageRelease: String
    imageDescription: String
    storagePool: String
    networkBridge: String
    cpuLimit: String
    cpuLimitIsOverride: Boolean!
    memoryLimit: String
    memoryLimitIsOverride: Boolean!
    workspaceHostPath: String
    workspaceIsOverride: Boolean!
  }

  type ImageBuildStatus {
    id: String!
    status: String!
    alias: String!
    distro: String!
    release: String!
    packages: [String!]!
    logTail: String!
    error: String
  }

  type BuilderPreset {
    name: String!
    distro: String!
    release: String!
    packages: [String!]!
  }

  input BuilderPresetInput {
    name: String!
    distro: String!
    release: String!
    packages: [String!]!
  }

  type ImageRecord {
    alias: String!
    distro: String!
    release: String!
    packages: [String!]!
    isMaster: Boolean!
    basedOn: String
    createdAt: String!
  }

  enum PackageEcosystem { apt npm pypi brew }

  type PackageSearchResult {
    ecosystem: String!
    name: String!
    description: String
    version: String
  }

  type PackageSearchError {
    ecosystem: String!
    message: String!
  }

  type PackageSearchResponse {
    results: [PackageSearchResult!]!
    errors: [PackageSearchError!]!
  }

  extend type Query {
    incusHealthy: Boolean!
    jails: [Jail!]!
    jailDetail(name: String!): JailDetail!
    jailImageBuildStatus(buildId: String!): ImageBuildStatus
    builderPresets: [BuilderPreset!]!
    jailImages: [ImageRecord!]!
    searchPackages(ecosystem: PackageEcosystem!, query: String!, distro: String, release: String): [PackageSearchResult!]!
    searchAllPackages(query: String!, distro: String, release: String): PackageSearchResponse!
  }

  extend type Mutation {
    launchJail(name: String!, image: String): Boolean!
    setJailState(name: String!, action: String!): Boolean!
    setJailWorkspace(name: String!, hostPath: String!): Boolean!
    clearJailWorkspace(name: String!): Boolean!
    setJailLimits(name: String!, cpu: String, memory: String): Boolean!
    deleteJail(name: String!): Boolean!
    buildJailImage(distro: String!, release: String!, packages: [String!]!, alias: String!, basedOn: String, postInstallCommands: [String!]): String!
    saveBuilderPreset(input: BuilderPresetInput!): BuilderPreset!
    deleteBuilderPreset(name: String!): Boolean!
    setMasterImage(alias: String!, isMaster: Boolean!): ImageRecord!
    deleteJailImage(alias: String!): Boolean!
  }
`;

@Injectable()
class IncusConfigPersister extends ConfigFilePersister<IncusConfig> {
  constructor(configService: ConfigService) {
    super(configService);
  }
  fileName(): string {
    return "incus.json";
  }
  configKey(): string {
    return "incus";
  }
  defaultConfig(): IncusConfig {
    return configFeature() as IncusConfig;
  }
}

@Module({
  imports: [ConfigModule.forFeature(configFeature)],
  providers: [
    IncusService,
    IncusExecService,
    IncusImageBuilderService,
    IncusBuilderPresetsService,
    IncusPackageSearchService,
    IncusResolver,
    IncusConfigPersister,
    IncusConfigSyncService,
  ],
})
class IncusPluginModule {
  private readonly logger = new Logger(IncusPluginModule.name);
  constructor(@Inject(ConfigService) private readonly config: ConfigService) {}
  onModuleInit() {
    this.logger.log("incus plugin initialized (state: %s)", this.config.get("incus.stateDir"));
  }
}

export const ApiModule = IncusPluginModule;
