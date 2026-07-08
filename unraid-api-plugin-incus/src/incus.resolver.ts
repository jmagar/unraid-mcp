import { Resolver, Query, Mutation, Subscription, Args, Int, registerEnumType } from "@nestjs/graphql";
import { ForbiddenException, Logger } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { resolve, sep } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { IncusService } from "./incus.service.js";
import { IncusExecService } from "./incus-exec.service.js";
import { IncusConfigSyncService } from "./config-sync.service.js";
import { IncusImageBuilderService } from "./incus-image-builder.service.js";
import { IncusBuilderPresetsService } from "./incus-builder-presets.service.js";
import { IncusPackageSearchService } from "./incus-package-search.service.js";
import {
  Jail,
  JailDetail,
  HomebrewInstallStatus,
  PrivilegedCommandStatus,
  IncusConfig,
  IncusConfigInput,
  ImageBuildStatus,
  BuilderPreset,
  BuilderPresetInput,
  ImageRecord,
  PackageSearchResult,
  PackageSearchResponse,
} from "./config.entity.js";

const execFileAsync = promisify(execFile);
const APPLY_SETTINGS_SCRIPT = "/usr/local/emhttp/plugins/incus/scripts/apply-settings.sh";

enum JailAction {
  start = "start",
  stop = "stop",
  restart = "restart",
  freeze = "freeze",
  unfreeze = "unfreeze",
}
registerEnumType(JailAction, { name: "JailAction", description: "Jail lifecycle actions" });

enum PackageEcosystem {
  apt = "apt",
  npm = "npm",
  pypi = "pypi",
  brew = "brew",
}
registerEnumType(PackageEcosystem, {
  name: "PackageEcosystem",
  description: "Package catalog to search — apt is Debian/Ubuntu only",
});

@Resolver()
export class IncusResolver {
  private readonly logger = new Logger(IncusResolver.name);

  constructor(
    private readonly incus: IncusService,
    private readonly exec: IncusExecService,
    private readonly configSync: IncusConfigSyncService,
    private readonly imageBuilder: IncusImageBuilderService,
    private readonly presets: IncusBuilderPresetsService,
    private readonly packageSearch: IncusPackageSearchService,
    private readonly config: ConfigService,
  ) {}

  @Query(() => Boolean, { description: "Is incusd reachable over its unix socket?" })
  async incusHealthy(): Promise<boolean> {
    return this.incus.ping();
  }

  @Query(() => IncusConfig, { description: "Current incus.cfg, as loaded by the API" })
  async incusConfig(): Promise<IncusConfig> {
    return this.config.getOrThrow<IncusConfig>("incus");
  }

  @Mutation(() => IncusConfig, {
    description:
      "Merge changes into incus.cfg and apply them (restarts incusd + re-runs the environment setup if SERVICE is enabled, else stops it).",
  })
  async updateIncusConfig(@Args("input") input: IncusConfigInput): Promise<IncusConfig> {
    const merged = await this.configSync.applyConfigUpdate(input);
    try {
      await execFileAsync(APPLY_SETTINGS_SCRIPT, [], { timeout: 90_000 });
    } catch (err) {
      throw new Error(`Config saved, but applying it failed: ${(err as Error).message}`);
    }
    return merged;
  }

  @Query(() => [Jail], { description: "List all agent jails" })
  async jails(): Promise<Jail[]> {
    return this.incus.listJails();
  }

  @Mutation(() => Boolean, { description: "Launch a new LAN-banned agent jail" })
  async launchJail(
    @Args("name") name: string,
    @Args("image", { nullable: true }) image?: string,
    @Args("allowSudo", { nullable: true }) allowSudo?: boolean
  ): Promise<boolean> {
    await this.incus.launchJail(name, { image });

    const tsAuthKey = this.config.get<IncusConfig>("incus")?.tsAuthKey;
    if (tsAuthKey) {
      try {
        await this.exec.runOnce(name, ["tailscale", "up", `--authkey=${tsAuthKey}`, `--hostname=${name}`]);
      } catch (err) {
        this.logger.warn(`Best-effort tailscale join failed for jail "${name}": ${(err as Error).message}`);
      }
    }

    if (allowSudo) {
      const result = await this.exec.grantSudo(name);
      if (!result.success) {
        this.logger.warn(`Sudo grant requested at launch for "${name}" but failed: ${result.message}`);
      }
    }

    return true;
  }

  @Mutation(() => Boolean)
  async setJailState(
    @Args("name") name: string,
    @Args("action", { type: () => JailAction }) action: JailAction
  ): Promise<boolean> {
    await this.incus.setState(name, action);
    return true;
  }

  @Mutation(() => Boolean, { description: "Repoint a jail's /workspace to a host dir" })
  async setJailWorkspace(
    @Args("name") name: string,
    @Args("hostPath") hostPath: string
  ): Promise<boolean> {
    // Validate hostPath is contained within the configured workspace root.
    // Must resolve (collapsing `..`) before comparing, and compare full path
    // segments (not a bare string prefix) so e.g. "/srv/agent-jails-evil" or
    // "/srv/agent-jails/../../etc" can't slip past a naive startsWith check.
    const wsRoot = resolve(this.config.get<string>("incus.jailWorkspaceRoot", "/srv/agent-jails"));
    const resolved = resolve(hostPath);
    if (resolved !== wsRoot && !resolved.startsWith(wsRoot + sep)) {
      throw new ForbiddenException(`hostPath must be under the workspace root (${wsRoot})`);
    }
    await this.incus.setWorkspace(name, resolved);
    return true;
  }

  @Mutation(() => Boolean, { description: "Drop a jail's workspace override, reverting to the profile's shared default" })
  async clearJailWorkspace(@Args("name") name: string): Promise<boolean> {
    await this.incus.clearWorkspaceOverride(name);
    return true;
  }

  @Mutation(() => String, {
    description: "Give a container (still on the profile's shared default workspace) its own isolated workspace directory; returns the new host path",
  })
  async migrateJailWorkspace(@Args("name") name: string): Promise<string> {
    return this.incus.migrateToOwnWorkspace(name);
  }

  @Query(() => JailDetail, { description: "Full resolved config for one jail — profile + instance overrides merged" })
  async jailDetail(@Args("name") name: string): Promise<JailDetail> {
    const [detail, sudoEnabled] = await Promise.all([
      this.incus.getJailDetail(name),
      this.exec.checkSudoEnabled(name),
    ]);
    return { ...detail, sudoEnabled };
  }

  @Mutation(() => Boolean, { description: "Grant the container's non-root agent user NOPASSWD sudo (opt-in, retroactive)" })
  async grantJailSudo(@Args("name") name: string): Promise<boolean> {
    const result = await this.exec.grantSudo(name);
    if (!result.success) {
      throw new Error(result.message);
    }
    return true;
  }

  @Mutation(() => String, {
    description:
      "Run a command inside a container as root, mediated by the operator (not exposed to the container's own agent user) — returns a job id to poll via privilegedCommandStatus",
  })
  startPrivilegedCommand(@Args("name") name: string, @Args("command") command: string): string {
    return this.exec.startPrivilegedCommand(name, command);
  }

  @Query(() => PrivilegedCommandStatus, { nullable: true, description: "Poll status/output for a privileged command job" })
  privilegedCommandStatus(@Args("id") id: string): PrivilegedCommandStatus | undefined {
    return this.exec.getPrivilegedCommandStatus(id);
  }

  @Mutation(() => Boolean, {
    description: "Override a jail's CPU/memory limits independent of its profile; pass an empty string to clear an override",
  })
  async setJailLimits(
    @Args("name") name: string,
    @Args("cpu", { nullable: true }) cpu?: string,
    @Args("memory", { nullable: true }) memory?: string
  ): Promise<boolean> {
    await this.incus.setJailLimits(name, cpu, memory);
    return true;
  }

  @Mutation(() => Boolean)
  async deleteJail(@Args("name") name: string): Promise<boolean> {
    await this.incus.deleteJail(name);
    return true;
  }

  @Mutation(() => String, { description: "Start an interactive shell session in a jail; returns a session id" })
  async startJailExec(
    @Args("name") name: string,
    @Args("cols", { type: () => Int, nullable: true }) cols?: number,
    @Args("rows", { type: () => Int, nullable: true }) rows?: number
  ): Promise<string> {
    return this.exec.start(name, cols ?? 80, rows ?? 24);
  }

  @Mutation(() => Boolean, { description: "Send terminal input (keystrokes) to an exec session" })
  sendJailExecInput(@Args("sessionId") sessionId: string, @Args("data") data: string): boolean {
    return this.exec.sendInput(sessionId, data);
  }

  @Mutation(() => Boolean, { description: "Resize an exec session's pseudo-terminal" })
  resizeJailExec(
    @Args("sessionId") sessionId: string,
    @Args("cols", { type: () => Int }) cols: number,
    @Args("rows", { type: () => Int }) rows: number
  ): boolean {
    return this.exec.resize(sessionId, cols, rows);
  }

  @Mutation(() => Boolean, { description: "Close an exec session" })
  stopJailExec(@Args("sessionId") sessionId: string): boolean {
    return this.exec.stop(sessionId);
  }

  @Subscription(() => String, { description: "Streams terminal output for an exec session" })
  jailExecOutput(@Args("sessionId") sessionId: string) {
    return this.exec.pubsub.asyncIterableIterator(`jailExecOutput:${sessionId}`);
  }

  @Mutation(() => String, {
    description:
      "Build a custom jail image with distrobuilder (distro/release/packages only) and import it into Incus under the given alias. Returns a build id to poll via jailImageBuildStatus.",
  })
  async buildJailImage(
    @Args("distro") distro: string,
    @Args("release") release: string,
    @Args("packages", { type: () => [String] }) packages: string[],
    @Args("alias") alias: string,
    @Args("basedOn", { nullable: true }) basedOn?: string,
    @Args("postInstallCommands", { type: () => [String], nullable: true }) postInstallCommands?: string[]
  ): Promise<string> {
    return this.imageBuilder.startBuild(distro, release, packages, alias, basedOn, postInstallCommands);
  }

  @Query(() => ImageBuildStatus, { nullable: true, description: "Poll status/log tail for a jail image build" })
  async jailImageBuildStatus(@Args("buildId") buildId: string): Promise<ImageBuildStatus | undefined> {
    const build = await this.imageBuilder.getStatus(buildId);
    if (!build) return undefined;
    return {
      id: build.id,
      status: build.status,
      alias: build.alias,
      distro: build.distro,
      release: build.release,
      packages: build.packages,
      logTail: build.logTail,
      error: build.error,
    };
  }

  @Query(() => [ImageRecord], { description: "Persisted registry of successfully built jail images" })
  async jailImages(): Promise<ImageRecord[]> {
    return this.imageBuilder.listImages();
  }

  @Mutation(() => ImageRecord, { description: "Mark (or unmark) a tracked image as a master image" })
  async setMasterImage(
    @Args("alias") alias: string,
    @Args("isMaster") isMaster: boolean
  ): Promise<ImageRecord> {
    return this.imageBuilder.setMasterImage(alias, isMaster);
  }

  @Query(() => [BuilderPreset], { description: "Saved distrobuilder presets" })
  async builderPresets(): Promise<BuilderPreset[]> {
    return this.presets.list();
  }

  @Mutation(() => BuilderPreset, { description: "Save (upsert by name) a distrobuilder preset" })
  async saveBuilderPreset(@Args("input") input: BuilderPresetInput): Promise<BuilderPreset> {
    return this.presets.save(input);
  }

  @Mutation(() => Boolean, { description: "Delete a saved distrobuilder preset by name" })
  async deleteBuilderPreset(@Args("name") name: string): Promise<boolean> {
    return this.presets.remove(name);
  }

  @Mutation(() => Boolean, { description: "Delete a built image (and untrack it) by alias" })
  async deleteJailImage(@Args("alias") alias: string): Promise<boolean> {
    try {
      await this.incus.deleteImage(alias);
    } catch (e) {
      // Already gone from Incus (e.g. removed out-of-band) — still untrack it below
      // rather than leaving a dead record the UI can never clear.
      this.logger.warn(`deleteImage(${alias}) failed, untracking anyway: ${(e as Error).message}`);
    }
    return this.imageBuilder.untrackImage(alias);
  }

  @Mutation(() => [String!], {
    description: "Untrack any saved image record whose Incus image no longer actually exists (e.g. deleted via the incus CLI directly); returns the aliases pruned",
  })
  async pruneStaleImageRecords(): Promise<string[]> {
    const images = await this.imageBuilder.listImages();
    const pruned: string[] = [];
    for (const image of images) {
      if (!(await this.incus.imageExists(image.alias))) {
        await this.imageBuilder.untrackImage(image.alias);
        pruned.push(image.alias);
      }
    }
    return pruned;
  }

  @Mutation(() => [String!], { description: "Delete every currently-stopped container; returns the names deleted" })
  async deleteStoppedJails(): Promise<string[]> {
    return this.incus.deleteStoppedJails();
  }

  @Mutation(() => String, {
    description:
      "Kick off a best-effort Homebrew formula install into a running container (bootstrapping Homebrew itself first if needed); returns a job id to poll via homebrewInstallStatus",
  })
  installHomebrewFormula(@Args("name") name: string, @Args("formula") formula: string): string {
    return this.exec.startHomebrewInstall(name, formula);
  }

  @Query(() => HomebrewInstallStatus, { nullable: true, description: "Poll status for a Homebrew install job" })
  homebrewInstallStatus(@Args("id") id: string): HomebrewInstallStatus | undefined {
    return this.exec.getHomebrewInstallStatus(id);
  }

  @Query(() => [PackageSearchResult], {
    description: "Live package search — npm/PyPI/Homebrew are cached catalogs; apt is debian/ubuntu only and requires distro+release",
  })
  async searchPackages(
    @Args("ecosystem", { type: () => PackageEcosystem }) ecosystem: PackageEcosystem,
    @Args("query") query: string,
    @Args("distro", { nullable: true }) distro?: string,
    @Args("release", { nullable: true }) release?: string
  ): Promise<PackageSearchResult[]> {
    return this.packageSearch.search(ecosystem, query, distro, release);
  }

  @Query(() => PackageSearchResponse, {
    description:
      "Search apt + npm + PyPI + Homebrew concurrently, merged into one relevance-ranked list. apt is skipped (not an error) unless distro/release are debian/ubuntu. A source failing (timeout, 5xx) degrades gracefully — its results are just absent, reported in `errors`, the rest of the search still returns.",
  })
  async searchAllPackages(
    @Args("query") query: string,
    @Args("distro", { nullable: true }) distro?: string,
    @Args("release", { nullable: true }) release?: string
  ): Promise<PackageSearchResponse> {
    return this.packageSearch.searchAll(query, distro, release);
  }
}
