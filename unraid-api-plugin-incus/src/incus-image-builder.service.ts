import { Injectable, Logger } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { createWriteStream } from "node:fs";
import { mkdir, mkdtemp, writeFile, open, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { ImageRecord } from "./config.entity.js";
import { JsonArrayStore } from "./json-store.js";

export type ImageBuildStatusValue = "queued" | "running" | "success" | "failed";

export interface ImageBuild {
  id: string;
  status: ImageBuildStatusValue;
  alias: string;
  distro: string;
  release: string;
  packages: string[];
  logFile: string;
  error?: string;
  startedAt: number;
  finishedAt?: number;
  basedOn?: string;
}

const LOG_TAIL_BYTES = 16_384;
const MAX_CONCURRENT_BUILDS = 2;
const MAX_QUEUED_BUILDS = 8;
const BUILD_RETENTION_MS = 24 * 60 * 60 * 1000;

/** Private-prefixed runtime bundled by the plugin's .plg (see incus-env.sh) — matches incusd/lxcfs/nft. */
const INCUS_PREFIX = "/usr/local/incus";

/**
 * Per-distro distrobuilder `source`/`packages` shape for the 6 distros curated in the
 * frontend dropdown (see web/src/App.vue CURATED_DISTROS). Verified against the real,
 * currently-maintained reference definitions distrobuilder's own maintainers use to build
 * images.linuxcontainers.org: github.com/lxc/lxc-ci, images/{debian,ubuntu,alpine,
 * rockylinux,almalinux,fedora}.yaml (fetched 2026-07). Downloader names cross-checked
 * against the `downloaders` registry in github.com/lxc/distrobuilder sources/source.go.
 *
 * - debian/ubuntu: `debootstrap` needs a mirror `url` and a `same_as` fallback script name
 *   (their debootstrap script directory may lag the very latest release/codename).
 * - alpinelinux: its own `alpinelinux-http` downloader, also mirror `url` + `same_as`.
 * - rockylinux/almalinux: `rockylinux-http`/`almalinux-http`, mirror `url`, no `same_as`
 *   (release comes straight from `image.release`).
 * - fedora: `fedora-http`, fixed koji `url`, no `same_as`/`variant` (release-driven too).
 */
const DISTRO_DEFINITIONS: Record<
  string,
  { downloader: string; manager: string; architecture: string; sourceExtra?: Record<string, string> }
> = {
  // Debian/Ubuntu's debootstrap wants the Debian-alias arch name ("amd64");
  // every other family here downloads from mirrors keyed by the native
  // uname-style name ("x86_64") — verified live: Alpine's downloader builds
  // its mirror URL directly from `image.architecture` and silently produces
  // a broken URL (missing version segment) when given "amd64" instead.
  // NOTE: intentionally no `same_as` fallback here — distrobuilder's debootstrap
  // downloader hardcodes `/usr/share/debootstrap/scripts` as the location it tries
  // to write the same_as symlink into, ignoring our DEBOOTSTRAP_DIR env override
  // (verified live: fails with "Failed to create symlink: ... /usr/share/debootstrap/
  // scripts/<release>: no such file or directory" since that system path doesn't
  // exist on a bare Unraid box). Every curated release must instead have a real
  // script (or symlink) present under the bundled
  // source/usr/local/incus/share/debootstrap/scripts/ directory — see that dir's
  // git history for how e.g. Ubuntu's "resolute" (26.04) was added as a symlink
  // to "gutsy", the base script every modern Ubuntu release script points to.
  debian: {
    downloader: "debootstrap",
    manager: "apt",
    architecture: "amd64",
    sourceExtra: { url: "https://deb.debian.org/debian/" },
  },
  ubuntu: {
    downloader: "debootstrap",
    manager: "apt",
    architecture: "amd64",
    sourceExtra: { url: "http://archive.ubuntu.com/ubuntu/" },
  },
  alpinelinux: {
    downloader: "alpinelinux-http",
    manager: "apk",
    architecture: "x86_64",
    sourceExtra: { url: "https://mirror.csclub.uwaterloo.ca/alpine/" },
  },
  rockylinux: {
    downloader: "rockylinux-http",
    manager: "yum",
    architecture: "x86_64",
    sourceExtra: { url: "https://download.rockylinux.org/pub/rocky/" },
  },
  almalinux: {
    downloader: "almalinux-http",
    manager: "yum",
    architecture: "x86_64",
    sourceExtra: { url: "https://almalinux.savoirfairelinux.net" },
  },
  fedora: {
    downloader: "fedora-http",
    manager: "dnf",
    architecture: "x86_64",
    sourceExtra: { url: "https://kojipkgs.fedoraproject.org" },
  },
};

/**
 * Builds custom Incus images with distrobuilder and imports them into the
 * local Incus daemon so they can be used as `jailImage` for new jails.
 *
 * distrobuilder is a separate tool from incus/incusd — it has no daemon and
 * no REST API, only a CLI that reads a YAML "definition" file describing a
 * distro + packages and produces a rootfs (and, for `build-incus`, an
 * Incus-flavoured metadata.yaml) tarball. `build-incus` supports
 * `--import-into-incus`, which imports the freshly built image straight into
 * the local Incus store (talking to the same unix socket IncusService uses),
 * so we don't need a separate `incus image import` shell-out.
 *
 * Builds run as detached child processes tracked in an in-memory Map (build
 * id -> status). There's no persistence: a plugin/API restart loses in-flight
 * build state, which is acceptable for this feature (re-run the build).
 */
@Injectable()
export class IncusImageBuilderService {
  private readonly logger = new Logger(IncusImageBuilderService.name);
  private readonly builds = new Map<string, ImageBuild>();
  private readonly imageStore: JsonArrayStore<ImageRecord>;
  private activeBuilds = 0;
  private readonly queue: Array<() => void> = [];

  constructor(private readonly config: ConfigService) {
    this.imageStore = new JsonArrayStore(() => this.imagesFilePath, isImageRecord);
  }

  private get socketPath(): string {
    const dir = this.config.get<string>("incus.stateDir", "/mnt/user/appdata/incus");
    return `${dir}/unix.socket`;
  }

  private get buildRoot(): string {
    const dir = this.config.get<string>("incus.stateDir", "/mnt/user/appdata/incus");
    return join(dir, "image-builds");
  }

  private get imagesFilePath(): string {
    const dir = this.config.get<string>("incus.stateDir", "/mnt/user/appdata/incus");
    return join(dir, "image-builds.json");
  }

  /** Kick off a build in the background; returns immediately with a build id. */
  async startBuild(
    distro: string,
    release: string,
    packages: string[],
    alias: string,
    basedOn?: string,
    postInstallCommands?: string[]
  ): Promise<string> {
    validateBuildInput(distro, release, packages, alias, postInstallCommands ?? []);
    if (this.queue.length >= MAX_QUEUED_BUILDS) throw new Error("Image build queue is full; wait for a running build to finish");
    this.pruneBuildHistory();
    const id = randomUUID();
    await mkdir(this.buildRoot, { recursive: true });
    const workDir = await mkdtemp(join(tmpdir(), `distrobuilder-${id}-`));
    const definitionPath = join(workDir, "definition.yaml");
    const outputDir = join(workDir, "output");
    await mkdir(outputDir, { recursive: true });
    const logFile = join(this.buildRoot, `${id}.log`);

    await writeFile(
      definitionPath,
      this.renderDefinition(distro, release, packages, postInstallCommands ?? []),
      "utf-8"
    );
    await writeFile(logFile, "", "utf-8");

    const build: ImageBuild = {
      id,
      status: "queued",
      alias,
      distro,
      release,
      packages,
      logFile,
      startedAt: Date.now(),
      basedOn,
    };
    this.builds.set(id, build);

    void this.enqueue(() => this.runBuild(build, definitionPath, outputDir));
    return id;
  }

  /** Full persisted image registry (empty array if no builds have succeeded yet). */
  async listImages(): Promise<ImageRecord[]> {
    return this.imageStore.read();
  }

  /** Flip a persisted image record's isMaster flag; throws if the alias isn't tracked. */
  /**
   * Exactly one image can be the golden master at a time — setting one clears the flag
   * on every other tracked image, so "master" always means "the current default", not
   * an arbitrary set of favorites.
   */
  async setMasterImage(alias: string, isMaster: boolean): Promise<ImageRecord> {
    return this.imageStore.update((images) => {
      const record = images.find((i) => i.alias === alias);
      if (!record) throw new Error(`No tracked image with alias "${alias}"`);
      if (isMaster) for (const image of images) image.isMaster = image.alias === alias;
      else record.isMaster = false;
      return record;
    });
  }

  /** Remove a tracked image record by alias. Returns whether one was actually removed. */
  async untrackImage(alias: string): Promise<boolean> {
    return this.imageStore.update((images) => {
      const idx = images.findIndex((i) => i.alias === alias);
      if (idx < 0) return false;
      images.splice(idx, 1);
      return true;
    });
  }

  private async recordImageBuilt(build: ImageBuild): Promise<void> {
    await this.imageStore.update((images) => {
      const record = {
        alias: build.alias, distro: build.distro, release: build.release,
        packages: build.packages, isMaster: false, basedOn: build.basedOn,
        createdAt: new Date().toISOString(),
      };
      const existing = images.findIndex((image) => image.alias === build.alias);
      if (existing >= 0) images[existing] = record;
      else images.push(record);
    });
  }

  /** Current status of a build, including a tail of its log. */
  async getStatus(buildId: string): Promise<(ImageBuild & { logTail: string }) | undefined> {
    const build = this.builds.get(buildId);
    if (!build) return undefined;
    const logTail = await this.tailLog(build.logFile);
    return { ...build, logTail };
  }

  /**
   * Minimal, correct distrobuilder LXC/Incus image definition: distro + release + packages.
   *
   * For the 6 curated distros (see DISTRO_DEFINITIONS), the real downloader/package-manager/
   * source fields verified against upstream lxc-ci are used. For anything else — e.g. the
   * frontend's "Other… (custom)" escape hatch — falls back to the previous generic
   * best-effort behavior (debootstrap for debian/ubuntu-like distros, else a bare
   * `downloader: distro` placeholder the caller is expected to already know is wrong for
   * their custom distro, plus apt as the package manager guess).
   */
  renderDefinition(
    distro: string,
    release: string,
    packages: string[],
    postInstallCommands: string[]
  ): string {
    const known = DISTRO_DEFINITIONS[distro];
    const downloader = known?.downloader ?? (distro === "ubuntu" || distro === "debian" ? "debootstrap" : "distro");
    const manager = known?.manager ?? "apt";
    // Debian/Ubuntu's debootstrap needs the Debian-alias name ("amd64"); every
    // other verified downloader here builds mirror URLs straight from this
    // field and needs the native uname-style name ("x86_64") instead — this
    // host has no `dpkg` to auto-detect it, so it must be set explicitly.
    const architecture = known?.architecture ?? "amd64";
    const sourceExtra = known?.sourceExtra ?? (known ? undefined : { same_as: release });

    const lines = [
      "image:",
      `  distribution: "${distro}"`,
      `  release: "${release}"`,
      `  architecture: ${architecture}`,
      `  description: "${distro} ${release} agent jail image (built via unraid incus plugin)"`,
      "",
      "source:",
      `  downloader: ${downloader}`,
      ...Object.entries(sourceExtra ?? {}).map(([key, value]) => `  ${key}: ${value}`),
      "",
      "packages:",
      `  manager: ${manager}`,
      "  update: true",
      "  cleanup: true",
      "  sets:",
      "  - action: install",
      "    packages:",
      ...packages.map((p) => `    - ${p}`),
      "",
      "targets:",
      // No fields are required here — this distrobuilder version rejects
      // unknown keys (e.g. the previously-used `incus_release` isn't a real
      // field of DefinitionTargetIncus and fails YAML unmarshalling).
      "  incus: {}",
      "",
    ];

    if (postInstallCommands.length > 0) {
      // distrobuilder writes `action` to a memfd and execs it directly (no shell
      // wrapper), so it MUST start with a shebang or it fails with "exec format
      // error" — verified against the real distrobuilder source (shared/util.go
      // RunScript). `post-packages` fires right after OS packages install (the
      // same trigger name confirmed in a real build's own log output), so
      // npm/pip/etc are already present by the time this runs.
      lines.push(
        "actions:",
        "- trigger: post-packages",
        "  action: |",
        "    #!/bin/sh",
        "    set -e",
        ...postInstallCommands.map((cmd) => `    ${cmd}`),
        ""
      );
    }

    return lines.join("\n");
  }

  private async runBuild(build: ImageBuild, definitionPath: string, outputDir: string): Promise<void> {
    build.status = "running";
    // --import-into-incus's VALUE *is* the resulting image alias (it's a Go
    // template string rendered against the definition, not a boolean flag —
    // verified against the real distrobuilder 3.2 CLI, which requires an
    // explicit argument here and has no separate --alias/-o mechanism for
    // naming the imported image).
    const args = ["build-incus", definitionPath, outputDir, `--import-into-incus=${build.alias}`];
    this.logger.log(`Starting distrobuilder build ${build.id}: distrobuilder ${args.join(" ")}`);

    // distrobuilder isn't a system package on Unraid — it (and the debootstrap
    // downloader it shells out to for debian/ubuntu, plus debootstrap's own
    // `ar` dependency) are bundled under the same private prefix as incusd/lxcfs.
    await new Promise<void>((resolvePromise) => {
      const child = spawn(`${INCUS_PREFIX}/bin/distrobuilder`, args, {
        env: {
          ...process.env,
          INCUS_SOCKET: this.socketPath,
          PATH: `${INCUS_PREFIX}/bin:${process.env.PATH ?? ""}`,
          LD_LIBRARY_PATH: `${INCUS_PREFIX}/lib${process.env.LD_LIBRARY_PATH ? ":" + process.env.LD_LIBRARY_PATH : ""}`,
          DEBOOTSTRAP_DIR: `${INCUS_PREFIX}/share/debootstrap`,
        },
      });

      const log = createWriteStream(build.logFile, { flags: "a", mode: 0o600 });
      const appendLog = (chunk: Buffer) => { if (!log.write(chunk)) child.stdout.pause(); };
      log.on("drain", () => child.stdout.resume());
      child.stdout.on("data", appendLog);
      child.stderr.on("data", appendLog);

      let settled = false;
      const finish = async (code: number | null, error?: Error) => {
        if (settled) return;
        settled = true;
        log.end();
        if (error) {
          build.status = "failed";
          build.error = error.message;
        } else if (code === 0) {
          build.status = "success";
          try {
            await this.recordImageBuilt(build);
          } catch (registryError) {
            build.status = "failed";
            build.error = `Image imported but registry update failed: ${(registryError as Error).message}`;
          }
        } else {
          build.status = "failed";
          build.error = `distrobuilder exited with code ${code}`;
        }
        build.finishedAt = Date.now();
        resolvePromise();
      };
      child.once("error", (error) => void finish(null, error));
      child.once("close", (code) => void finish(code));
    });

    // Best-effort cleanup of the scratch definition/output dir; the log file
    // under buildRoot is intentionally left behind for later status polling.
    await rm(join(definitionPath, ".."), { recursive: true, force: true }).catch(() => undefined);
  }

  private async tailLog(logFile: string): Promise<string> {
    let handle;
    try {
      handle = await open(logFile, "r");
      const { size } = await handle.stat();
      const length = Math.min(size, LOG_TAIL_BYTES);
      const data = Buffer.alloc(length);
      await handle.read(data, 0, length, Math.max(0, size - length));
      return data.toString("utf-8");
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== "ENOENT") this.logger.warn(`Unable to read build log: ${(error as Error).message}`);
      return "";
    } finally {
      await handle?.close();
    }
  }

  private enqueue(task: () => Promise<void>): Promise<void> {
    return new Promise((resolve, reject) => {
      const start = () => {
        this.activeBuilds++;
        void task().then(resolve, reject).finally(() => {
          this.activeBuilds--;
          this.queue.shift()?.();
        });
      };
      if (this.activeBuilds < MAX_CONCURRENT_BUILDS) start();
      else this.queue.push(start);
    });
  }

  private pruneBuildHistory(): void {
    const cutoff = Date.now() - BUILD_RETENTION_MS;
    for (const [id, build] of this.builds) if (build.finishedAt && build.finishedAt < cutoff) this.builds.delete(id);
  }
}

function isImageRecord(value: unknown): value is ImageRecord {
  const item = value as Partial<ImageRecord> | null;
  return !!item && typeof item.alias === "string" && typeof item.distro === "string" &&
    typeof item.release === "string" && typeof item.isMaster === "boolean" && typeof item.createdAt === "string" &&
    Array.isArray(item.packages) && item.packages.every((p) => typeof p === "string");
}

function validateBuildInput(distro: string, release: string, packages: string[], alias: string, commands: string[]): void {
  const token = /^[A-Za-z0-9][A-Za-z0-9._+@/-]{0,127}$/;
  if (!token.test(distro) || !token.test(release) || !token.test(alias)) throw new Error("Invalid distro, release, or image alias");
  if (packages.length > 200 || commands.length > 50) throw new Error("Build input exceeds package or command limits");
  if (packages.some((value) => !token.test(value))) throw new Error("Invalid package name");
  if (commands.some((value) => value.length > 4096 || value.includes("\0"))) throw new Error("Invalid post-install command");
}
