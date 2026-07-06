import { Module, Logger, Inject, Injectable } from "@nestjs/common";
import { ConfigModule, ConfigService } from "@nestjs/config";
import { ConfigFilePersister } from "@unraid/shared/services/config-file.js";
import { configFeature, IncusConfig } from "./config.entity.js";
import { IncusService } from "./incus.service.js";
import { IncusResolver } from "./incus.resolver.js";
import { IncusConfigSyncService } from "./src/config-sync.service.js";

/** Contract fields the unraid-api plugin loader validates against. */
export const adapter = "nestjs";

export const graphqlSchemaExtension = async () => `
  type Jail {
    name: String!
    status: String!
    ipv4: String
  }

  extend type Query {
    incusHealthy: Boolean!
    jails: [Jail!]!
  }

  extend type Mutation {
    launchJail(name: String!, image: String): Boolean!
    setJailState(name: String!, action: String!): Boolean!
    setJailWorkspace(name: String!, hostPath: String!): Boolean!
    deleteJail(name: String!): Boolean!
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
  providers: [IncusService, IncusResolver, IncusConfigPersister, IncusConfigSyncService],
})
class IncusPluginModule {
  private readonly logger = new Logger(IncusPluginModule.name);
  constructor(@Inject(ConfigService) private readonly config: ConfigService) {}
  onModuleInit() {
    this.logger.log("incus plugin initialized (state: %s)", this.config.get("incus.stateDir"));
  }
}

export const ApiModule = IncusPluginModule;
