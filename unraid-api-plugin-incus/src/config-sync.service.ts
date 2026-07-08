import { Injectable, Logger, OnModuleInit, OnModuleDestroy } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { existsSync, readFileSync, writeFileSync, statSync, unlinkSync, renameSync, watch, FSWatcher } from "node:fs";
import { join } from "node:path";
import { IncusConfig } from "./config.entity.js";

const CFG_LOCK_STALE_MS = 15_000;
const CFG_LOCK_RETRY_MS = 200;
const CFG_LOCK_MAX_RETRIES = 5; // ~1s total, for applyConfigUpdate's "wait a bit then retry" path

@Injectable()
export class IncusConfigSyncService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(IncusConfigSyncService.name);
  private cfgWatcher?: FSWatcher;
  private jsonWatcher?: FSWatcher;
  private isSyncing = false;

  constructor(private readonly configService: ConfigService) {}

  // Primary paths on Unraid, with fallbacks for development/testing
  private readonly cfgPath = existsSync("/boot/config/plugins/incus/incus.cfg")
    ? "/boot/config/plugins/incus/incus.cfg"
    : join(process.cwd(), "incus.cfg");

  private readonly cfgLockPath = `${this.cfgPath}.lock`;

  // The persisted JSON lives wherever @unraid/shared's ConfigFilePersister
  // puts it — PATHS_CONFIG_MODULES + "incus.json" (e.g.
  // /boot/config/plugins/dynamix.my.servers/configs/incus.json), NOT under
  // this plugin's own /boot/config/plugins/incus/ directory. Hardcoding the
  // latter silently watched/wrote the wrong file (or a disconnected
  // dev-cwd fallback) on every real deployment.
  private readonly jsonPath = process.env.PATHS_CONFIG_MODULES
    ? join(process.env.PATHS_CONFIG_MODULES, "incus.json")
    : join(process.cwd(), "incus.json");

  onModuleInit() {
    this.logger.log(`Initializing config sync (cfg: ${this.cfgPath}, json: ${this.jsonPath})`);
    
    // 1. Perform initial sync (shell incus.cfg is the ultimate system source of truth)
    void this.syncCfgToJSON();

    // 2. Start watching both files
    this.setupWatchers();
  }

  onModuleDestroy() {
    this.cfgWatcher?.close();
    this.jsonWatcher?.close();
  }

  /**
   * Applies a partial config update directly: writes incus.cfg AND incus.json
   * ourselves and updates ConfigService's in-memory value, synchronously and
   * unconditionally. Used by the GraphQL mutation instead of just calling
   * `configService.set()` and hoping @unraid/shared's ConfigFilePersister
   * reactively persists it — that depends on its `changes$` observable
   * actually firing for a plain `@nestjs/config` ConfigService.set() call,
   * which is not guaranteed and was the root cause of edits silently not
   * surviving a page refresh.
   *
   * Locked (bounded retry, real await between attempts — NOT a synchronous
   * blocking sleep; Atomics.wait() was tried first and rejected because it
   * blocks the entire Node event loop, not just this call, which would have
   * frozen every other in-flight request during any lock contention) around
   * the read-modify-write. The only other writer left in this process is the
   * file-watcher-triggered sync below, and true reentrancy between two
   * synchronous read+write sections isn't possible in Node's single-threaded
   * model, but this still protects against a genuine cross-process race: an
   * admin hand-editing incus.cfg over SSH at the same moment a settings-form
   * save comes in. A failed acquire throws rather than silently proceeding
   * unprotected or silently dropping the edit.
   */
  async applyConfigUpdate(input: Partial<IncusConfig>): Promise<IncusConfig> {
    if (!existsSync(this.cfgPath)) {
      throw new Error(`incus.cfg not found at ${this.cfgPath}`);
    }
    const lockToken = await this.acquireCfgLock(CFG_LOCK_MAX_RETRIES);
    if (!lockToken) {
      throw new Error("incus.cfg is locked by another process — please retry");
    }
    this.isSyncing = true;
    try {
      const cfgContent = readFileSync(this.cfgPath, "utf-8");
      const current = this.mapShellToTS(this.parseShellConfig(cfgContent));
      const merged = { ...current, ...input } as IncusConfig;

      this.writeFileAtomic(this.cfgPath, this.updateShellConfig(cfgContent, input));
      this.writeFileAtomic(this.jsonPath, JSON.stringify(merged, null, 2));
      this.configService.set("incus", merged);
      return merged;
    } finally {
      this.isSyncing = false;
      this.releaseCfgLock(lockToken);
    }
  }

  /**
   * Reads incus.cfg, parses it, and updates incus.json if values differ.
   */
  private async syncCfgToJSON() {
    if (this.isSyncing) return;
    if (!existsSync(this.cfgPath)) {
      this.logger.warn(`incus.cfg not found at ${this.cfgPath}, skipping initial sync`);
      return;
    }

    // Single attempt (maxRetries=0): this is a background, file-watcher-
    // triggered sync, not a request waiting on a response. If the lock is
    // busy, skip this cycle — the next fs-change event (including our own
    // subsequent read finding nothing changed) will retry.
    const lockToken = await this.acquireCfgLock(0);
    if (!lockToken) {
      this.logger.debug(`incus.cfg is locked by another writer; skipping this cfg->json sync cycle`);
      return;
    }

    try {
      this.isSyncing = true;
      const cfgContent = readFileSync(this.cfgPath, "utf-8");
      const parsedCfg = this.parseShellConfig(cfgContent);
      const mappedConfig = this.mapShellToTS(parsedCfg);

      let currentJson: Partial<IncusConfig> = {};
      if (existsSync(this.jsonPath)) {
        try {
          currentJson = JSON.parse(readFileSync(this.jsonPath, "utf-8"));
        } catch {
          this.logger.warn(`Failed to parse existing incus.json, overwriting`);
        }
      }

      // Check if sync is actually needed to avoid redundant writes
      if (this.isConfigDifferent(currentJson, mappedConfig)) {
        this.logger.log(`Syncing changes from incus.cfg to incus.json`);
        const newJson = { ...currentJson, ...mappedConfig };
        this.writeFileAtomic(this.jsonPath, JSON.stringify(newJson, null, 2));
        // Keep ConfigService's in-memory value current too — otherwise an
        // external edit to incus.cfg (or ConfigFilePersister loading the old
        // file into memory before this ever runs, at boot) leaves GraphQL
        // serving stale config even though the files on disk are correct.
        this.configService.set("incus", newJson);
      }
    } catch (err) {
      this.logger.error(`Error syncing incus.cfg to incus.json: ${(err as Error).message}`);
    } finally {
      this.isSyncing = false;
      this.releaseCfgLock(lockToken);
    }
  }

  /**
   * Reads incus.json, and updates incus.cfg line-by-line while preserving comments and other settings.
   */
  private async syncJSONToCfg(retriesLeft = 5) {
    if (this.isSyncing) return;
    if (!existsSync(this.jsonPath)) return;

    // Unlike syncCfgToJSON (which just re-reads the same source of truth on
    // the next fs event if it skips a cycle), the JSON change we're trying to
    // sync right now has already happened — giving up permanently on lock
    // contention could silently drop it forever if nothing touches
    // incus.json again. Bounded retry instead of one attempt.
    const lockToken = await this.acquireCfgLock(0);
    if (!lockToken) {
      if (retriesLeft > 0) {
        this.logger.debug(`incus.cfg is locked; retrying json->cfg sync in ${CFG_LOCK_RETRY_MS}ms (${retriesLeft} left)`);
        setTimeout(() => void this.syncJSONToCfg(retriesLeft - 1), CFG_LOCK_RETRY_MS);
      } else {
        this.logger.warn(`incus.cfg stayed locked after repeated retries; giving up on this json->cfg sync cycle`);
      }
      return;
    }

    try {
      this.isSyncing = true;
      const jsonContent = readFileSync(this.jsonPath, "utf-8");
      const parsedJson: Partial<IncusConfig> = JSON.parse(jsonContent);

      if (!existsSync(this.cfgPath)) {
        this.logger.warn(`incus.cfg not found at ${this.cfgPath}, cannot sync from JSON`);
        return;
      }

      const cfgContent = readFileSync(this.cfgPath, "utf-8");
      const parsedCfg = this.parseShellConfig(cfgContent);
      const mappedConfig = this.mapShellToTS(parsedCfg);

      // Check if sync is actually needed to avoid redundant writes
      if (this.isConfigDifferent(mappedConfig, parsedJson)) {
        this.logger.log(`Syncing changes from incus.json to incus.cfg`);
        const updatedCfgContent = this.updateShellConfig(cfgContent, parsedJson);
        this.writeFileAtomic(this.cfgPath, updatedCfgContent);
        this.configService.set("incus", { ...mappedConfig, ...parsedJson });
      }
    } catch (err) {
      this.logger.error(`Error syncing incus.json to incus.cfg: ${(err as Error).message}`);
    } finally {
      this.isSyncing = false;
      this.releaseCfgLock(lockToken);
    }
  }

  /**
   * Set up watches on both files to propagate live edits.
   */
  private setupWatchers() {
    try {
      if (existsSync(this.cfgPath)) {
        this.cfgWatcher = this.watchResilient(this.cfgPath, () => void this.syncCfgToJSON(), (w) => (this.cfgWatcher = w));
      }
      if (existsSync(this.jsonPath)) {
        this.jsonWatcher = this.watchResilient(this.jsonPath, () => void this.syncJSONToCfg(), (w) => (this.jsonWatcher = w));
      }
    } catch (err) {
      this.logger.warn(`Failed to set up config file watchers: ${(err as Error).message}`);
    }
  }

  /**
   * fs.watch() follows the inode, not the path: editors that save via
   * rename-replace (vim, atomic writes) leave the watcher attached to the old,
   * now-unlinked inode, so it silently stops firing for all future edits at
   * that path. On a "rename" event we tear down and re-arm a fresh watcher on
   * the same path (once the new file lands there) so edits keep propagating.
   */
  private watchResilient(path: string, onChange: () => void, setRef: (w: FSWatcher | undefined) => void): FSWatcher {
    const watcher = watch(path, (event) => {
      if (event === "rename") {
        watcher.close();
        setTimeout(() => {
          if (existsSync(path)) {
            setRef(this.watchResilient(path, onChange, setRef));
          } else {
            setRef(undefined);
          }
          onChange();
        }, 100);
        return;
      }
      // Debounce slightly to allow writes to finish
      setTimeout(onChange, 100);
    });
    return watcher;
  }

  /**
   * Helper to check if two configuration subsets differ.
   */
  private isConfigDifferent(a: Partial<IncusConfig>, b: Partial<IncusConfig>): boolean {
    const keys: Array<keyof IncusConfig> = [
      "enabled",
      "stateDir",
      "storageDriver",
      "storageSource",
      "storagePoolName",
      "jailBridge",
      "jailSubnet",
      "jailNat",
      "jailIpv6",
      "aclName",
      "aclBlock",
      "aclAllow",
      "aclDefaultEgress",
      "aclDefaultIngress",
      "jailProfile",
      "jailImage",
      "jailNesting",
      "jailCpu",
      "jailMemory",
      "jailWorkspaceRoot",
      "jailAgentUid",
      "jailAgentGid",
      "jailBindMounts",
      "tsAuthKey",
      "dashboardWidgetEnable",
    ];
    for (const key of keys) {
      if (a[key] !== b[key] && b[key] !== undefined) {
        return true;
      }
    }
    return false;
  }

  /**
   * Parse simple shell config (KEY="VALUE") into record.
   * Public (not just private) so it's directly unit-testable; still not part
   * of any external/GraphQL-facing contract.
   */
  parseShellConfig(content: string): Record<string, string> {
    const result: Record<string, string> = {};
    const lines = content.split(/\r?\n/);
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const eqIdx = trimmed.indexOf("=");
      if (eqIdx > 0) {
        const key = trimmed.substring(0, eqIdx).trim();
        let val = trimmed.substring(eqIdx + 1).trim();
        // Remove trailing comment if any (e.g. KEY="VAL" # comment)
        const hashIdx = val.indexOf("#");
        if (hashIdx >= 0) {
          val = val.substring(0, hashIdx).trim();
        }
        // Remove surrounding quotes if present
        if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
          val = val.substring(1, val.length - 1);
        }
        result[key] = val;
      }
    }
    return result;
  }

  /**
   * Map parsed shell keys to the TypeScript IncusConfig entity properties.
   * Public for unit testing (see parseShellConfig).
   */
  mapShellToTS(shell: Record<string, string>): Partial<IncusConfig> {
    const config: Partial<IncusConfig> = {};
    if (shell.SERVICE !== undefined) config.enabled = shell.SERVICE === "enabled";
    if (shell.INCUS_DIR !== undefined) config.stateDir = shell.INCUS_DIR;
    if (shell.STORAGE_DRIVER !== undefined) config.storageDriver = shell.STORAGE_DRIVER;
    if (shell.STORAGE_SOURCE !== undefined) config.storageSource = shell.STORAGE_SOURCE;
    if (shell.STORAGE_POOL_NAME !== undefined) config.storagePoolName = shell.STORAGE_POOL_NAME;
    if (shell.JAIL_BRIDGE !== undefined) config.jailBridge = shell.JAIL_BRIDGE;
    if (shell.JAIL_SUBNET !== undefined) config.jailSubnet = shell.JAIL_SUBNET;
    if (shell.JAIL_NAT !== undefined) config.jailNat = shell.JAIL_NAT === "true";
    if (shell.JAIL_IPV6 !== undefined) config.jailIpv6 = shell.JAIL_IPV6;
    if (shell.ACL_NAME !== undefined) config.aclName = shell.ACL_NAME;
    if (shell.ACL_BLOCK !== undefined) config.aclBlock = shell.ACL_BLOCK;
    if (shell.ACL_ALLOW !== undefined) config.aclAllow = shell.ACL_ALLOW;
    if (shell.ACL_DEFAULT_EGRESS !== undefined) config.aclDefaultEgress = shell.ACL_DEFAULT_EGRESS;
    if (shell.ACL_DEFAULT_INGRESS !== undefined) config.aclDefaultIngress = shell.ACL_DEFAULT_INGRESS;
    if (shell.JAIL_PROFILE !== undefined) config.jailProfile = shell.JAIL_PROFILE;
    if (shell.JAIL_IMAGE !== undefined) config.jailImage = shell.JAIL_IMAGE;
    if (shell.JAIL_NESTING !== undefined) config.jailNesting = shell.JAIL_NESTING === "true";
    if (shell.JAIL_CPU !== undefined) config.jailCpu = shell.JAIL_CPU;
    if (shell.JAIL_MEMORY !== undefined) config.jailMemory = shell.JAIL_MEMORY;
    if (shell.JAIL_WORKSPACE_ROOT !== undefined) config.jailWorkspaceRoot = shell.JAIL_WORKSPACE_ROOT;
    if (shell.JAIL_AGENT_UID !== undefined) config.jailAgentUid = shell.JAIL_AGENT_UID;
    if (shell.JAIL_AGENT_GID !== undefined) config.jailAgentGid = shell.JAIL_AGENT_GID;
    if (shell.JAIL_BIND_MOUNTS !== undefined) config.jailBindMounts = shell.JAIL_BIND_MOUNTS;
    if (shell.TS_AUTHKEY !== undefined) config.tsAuthKey = shell.TS_AUTHKEY;
    if (shell.DASHBOARD_WIDGET_ENABLE !== undefined) {
      config.dashboardWidgetEnable = shell.DASHBOARD_WIDGET_ENABLE === "true";
    }
    return config;
  }

  /** Quote a value so it is inert when sourced by bash, regardless of content. */
  private shellSingleQuote(val: string): string {
    return `'${val.replace(/'/g, `'\\''`)}'`;
  }

  /**
   * Sentinel-lockfile mutex guarding the incus.cfg/incus.json pair (one lock
   * for both — applyConfigUpdate writes them together as one logical unit).
   * Node has no cross-process flock() without a native addon, so this is a
   * plain exclusive-create-based lock: atomic create, a stale timeout so a
   * crashed holder can't wedge things forever, token verification before
   * delete so a lock that went stale and was stolen by someone else can't be
   * deleted out from under its new holder.
   *
   * @param maxRetries 0 = single attempt, no wait (for the background
   *   watcher-triggered syncs, which must never stall the event loop).
   *   >0 = retry up to maxRetries times, `await`-ing a real setTimeout-based
   *   delay between attempts (for applyConfigUpdate — worth a short wait
   *   before giving up). Deliberately NOT Atomics.wait: that blocks the
   *   entire event loop, not just this call, which would freeze every other
   *   in-flight request for the whole retry window — verified by actually
   *   running it, not just reasoning about it, before landing this version.
   */
  private async acquireCfgLock(maxRetries: number): Promise<string | null> {
    const token = `${process.pid}-${Math.random().toString(16).slice(2)}`;
    let attempt = 0;
    while (true) {
      try {
        writeFileSync(this.cfgLockPath, token, { flag: "wx" });
        return token;
      } catch (err) {
        if ((err as NodeJS.ErrnoException).code !== "EEXIST") return null;
        try {
          const before = statSync(this.cfgLockPath);
          const age = Date.now() - before.mtimeMs;
          if (age > CFG_LOCK_STALE_MS) {
            // Re-stat and compare inode immediately before unlinking — a bare
            // "stat, then unlink" has a window where a legitimate new holder
            // could create a fresh lock in between, which we'd then delete
            // out from under them. An inode change (unlink+recreate always
            // allocates a new inode on ext4/xfs/zfs) means that happened;
            // abort the steal and retry instead. This narrows the race to
            // the few microseconds between this second stat and the unlink
            // call itself, rather than the whole stale-timeout window.
            const now = statSync(this.cfgLockPath);
            if (now.ino === before.ino && now.mtimeMs === before.mtimeMs) {
              unlinkSync(this.cfgLockPath); // holder likely crashed; steal it
            }
            continue;
          }
        } catch {
          continue; // lock vanished, or a competitor grabbed it between our stat and unlink — retry
        }
      }
      if (attempt >= maxRetries) return null;
      attempt++;
      await new Promise((resolve) => setTimeout(resolve, CFG_LOCK_RETRY_MS));
    }
  }

  private releaseCfgLock(token: string | null): void {
    if (!token) return;
    try {
      if (readFileSync(this.cfgLockPath, "utf-8") === token) {
        unlinkSync(this.cfgLockPath);
      }
    } catch (err) {
      this.logger.debug(`incus.cfg lock release no-op: ${(err as Error).message}`);
    }
  }

  /**
   * Write-to-temp-then-rename so a concurrent reader (e.g. bash sourcing
   * incus.cfg) never sees a torn file. Carries over the existing file's mode
   * rather than letting the temp file fall back to the process umask —
   * incus.cfg can contain TS_AUTHKEY, and a wider default (e.g. umask 022 ->
   * 0644, world-readable) would quietly loosen its permissions on every save.
   */
  private writeFileAtomic(path: string, content: string): void {
    const tmpPath = `${path}.tmp-${process.pid}`;
    const mode = existsSync(path) ? statSync(path).mode & 0o777 : 0o600;
    writeFileSync(tmpPath, content, { encoding: "utf-8", mode });
    renameSync(tmpPath, path);
  }

  /** Renders one config value the way updateShellConfig writes it (enabled/disabled, true/false, or as-is). */
  private formatShellValue(
    tsKey: keyof IncusConfig,
    val: unknown,
    booleanAsEnabledDisabled: Set<keyof IncusConfig>,
    booleanAsTrueFalse: Set<keyof IncusConfig>
  ): string {
    if (booleanAsEnabledDisabled.has(tsKey)) return val ? "enabled" : "disabled";
    if (booleanAsTrueFalse.has(tsKey)) return val ? "true" : "false";
    return String(val);
  }

  /**
   * Updates matching shell variables in shell config file line-by-line to
   * preserve comments. Keys with no existing line are appended — an install
   * whose incus.cfg predates a given key (e.g. an existing install toggling
   * the new DASHBOARD_WIDGET_ENABLE setting) would otherwise have the update
   * silently discarded: the UI shows the new value, but since the key was
   * never written, the actual file (and anything reading it, like
   * IncusDashboard.page's Cond= gate) keeps its old default behavior forever.
   * Public for unit testing (see parseShellConfig).
   */
  updateShellConfig(content: string, updates: Partial<IncusConfig>): string {
    const lines = content.split(/\r?\n/);
    const keyMap: Record<keyof IncusConfig, string> = {
      enabled: "SERVICE",
      stateDir: "INCUS_DIR",
      storageDriver: "STORAGE_DRIVER",
      storageSource: "STORAGE_SOURCE",
      storagePoolName: "STORAGE_POOL_NAME",
      jailBridge: "JAIL_BRIDGE",
      jailSubnet: "JAIL_SUBNET",
      jailNat: "JAIL_NAT",
      jailIpv6: "JAIL_IPV6",
      aclName: "ACL_NAME",
      aclBlock: "ACL_BLOCK",
      aclAllow: "ACL_ALLOW",
      aclDefaultEgress: "ACL_DEFAULT_EGRESS",
      aclDefaultIngress: "ACL_DEFAULT_INGRESS",
      jailProfile: "JAIL_PROFILE",
      jailImage: "JAIL_IMAGE",
      jailNesting: "JAIL_NESTING",
      jailCpu: "JAIL_CPU",
      jailMemory: "JAIL_MEMORY",
      jailWorkspaceRoot: "JAIL_WORKSPACE_ROOT",
      jailAgentUid: "JAIL_AGENT_UID",
      jailAgentGid: "JAIL_AGENT_GID",
      jailBindMounts: "JAIL_BIND_MOUNTS",
      tsAuthKey: "TS_AUTHKEY",
      dashboardWidgetEnable: "DASHBOARD_WIDGET_ENABLE",
    };
    const booleanAsEnabledDisabled = new Set<keyof IncusConfig>(["enabled"]);
    const booleanAsTrueFalse = new Set<keyof IncusConfig>(["jailNat", "jailNesting", "dashboardWidgetEnable"]);
    const seen = new Set<keyof IncusConfig>();

    const newLines = lines.map((line) => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) return line;
      const eqIdx = trimmed.indexOf("=");
      if (eqIdx > 0) {
        const key = trimmed.substring(0, eqIdx).trim();
        // Check if we have an update mapping for this shell variable key
        const tsKey = Object.keys(keyMap).find(
          (k) => keyMap[k as keyof IncusConfig] === key
        ) as keyof IncusConfig | undefined;

        if (tsKey && updates[tsKey] !== undefined) {
          seen.add(tsKey);
          const strVal = this.formatShellValue(tsKey, updates[tsKey], booleanAsEnabledDisabled, booleanAsTrueFalse);

          const originalRightHand = trimmed.substring(eqIdx + 1).trim();
          // Retain comments if they were on the same line
          const hashIdx = originalRightHand.indexOf("#");
          const comment = hashIdx >= 0 ? originalRightHand.substring(hashIdx) : "";

          // incus.cfg is sourced directly as a bash script (`. "$CFG"`) by
          // incus-init.sh and rc.incus, as root, on every array start/restart.
          // Always emit single-quoted values — inside single quotes bash
          // performs no expansion at all ($, `, ;, etc are inert) — so an
          // untrusted config value can never inject a shell command here.
          return `${key}=${this.shellSingleQuote(strVal)}${comment ? " " + comment : ""}`;
        }
      }
      return line;
    });

    const appended: string[] = [];
    for (const tsKey of Object.keys(updates) as Array<keyof IncusConfig>) {
      if (updates[tsKey] === undefined || seen.has(tsKey)) continue;
      const shellKey = keyMap[tsKey];
      if (!shellKey) continue;
      const strVal = this.formatShellValue(tsKey, updates[tsKey], booleanAsEnabledDisabled, booleanAsTrueFalse);
      appended.push(`${shellKey}=${this.shellSingleQuote(strVal)}`);
    }

    return [...newLines, ...appended].join("\n");
  }
}
