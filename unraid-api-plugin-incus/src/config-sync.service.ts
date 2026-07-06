import { Injectable, Logger, OnModuleInit, OnModuleDestroy } from "@nestjs/common";
import { existsSync, readFileSync, writeFileSync, watch, FSWatcher } from "node:fs";
import { join } from "node:path";
import { IncusConfig } from "./config.entity.js";

@Injectable()
export class IncusConfigSyncService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(IncusConfigSyncService.name);
  private cfgWatcher?: FSWatcher;
  private jsonWatcher?: FSWatcher;
  private isSyncing = false;

  // Primary paths on Unraid, with fallbacks for development/testing
  private readonly cfgPath = existsSync("/boot/config/plugins/incus/incus.cfg")
    ? "/boot/config/plugins/incus/incus.cfg"
    : join(process.cwd(), "incus.cfg");

  private readonly jsonPath = existsSync("/boot/config/plugins/incus/incus.json")
    ? "/boot/config/plugins/incus/incus.json"
    : join(process.cwd(), "incus.json");

  onModuleInit() {
    this.logger.log(`Initializing config sync (cfg: ${this.cfgPath}, json: ${this.jsonPath})`);
    
    // 1. Perform initial sync (shell incus.cfg is the ultimate system source of truth)
    this.syncCfgToJSON();

    // 2. Start watching both files
    this.setupWatchers();
  }

  onModuleDestroy() {
    this.cfgWatcher?.close();
    this.jsonWatcher?.close();
  }

  /**
   * Reads incus.cfg, parses it, and updates incus.json if values differ.
   */
  private syncCfgToJSON() {
    if (this.isSyncing) return;
    if (!existsSync(this.cfgPath)) {
      this.logger.warn(`incus.cfg not found at ${this.cfgPath}, skipping initial sync`);
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
        writeFileSync(this.jsonPath, JSON.stringify(newJson, null, 2), "utf-8");
      }
    } catch (err) {
      this.logger.error(`Error syncing incus.cfg to incus.json: ${(err as Error).message}`);
    } finally {
      this.isSyncing = false;
    }
  }

  /**
   * Reads incus.json, and updates incus.cfg line-by-line while preserving comments and other settings.
   */
  private syncJSONToCfg() {
    if (this.isSyncing) return;
    if (!existsSync(this.jsonPath)) return;

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
        writeFileSync(this.cfgPath, updatedCfgContent, "utf-8");
      }
    } catch (err) {
      this.logger.error(`Error syncing incus.json to incus.cfg: ${(err as Error).message}`);
    } finally {
      this.isSyncing = false;
    }
  }

  /**
   * Set up watches on both files to propagate live edits.
   */
  private setupWatchers() {
    try {
      if (existsSync(this.cfgPath)) {
        this.cfgWatcher = watch(this.cfgPath, (event) => {
          if (event === "change") {
            // Debounce slightly to allow writes to finish
            setTimeout(() => this.syncCfgToJSON(), 100);
          }
        });
      }

      if (existsSync(this.jsonPath)) {
        this.jsonWatcher = watch(this.jsonPath, (event) => {
          if (event === "change") {
            // Debounce slightly to allow writes to finish
            setTimeout(() => this.syncJSONToCfg(), 100);
          }
        });
      }
    } catch (err) {
      this.logger.warn(`Failed to set up config file watchers: ${(err as Error).message}`);
    }
  }

  /**
   * Helper to check if two configuration subsets differ.
   */
  private isConfigDifferent(a: Partial<IncusConfig>, b: Partial<IncusConfig>): boolean {
    const keys: Array<keyof IncusConfig> = [
      "enabled",
      "stateDir",
      "jailBridge",
      "aclBlock",
      "jailImage",
      "jailProfile",
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
   */
  private parseShellConfig(content: string): Record<string, string> {
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
   */
  private mapShellToTS(shell: Record<string, string>): Partial<IncusConfig> {
    const config: Partial<IncusConfig> = {};
    if (shell.SERVICE !== undefined) {
      config.enabled = shell.SERVICE === "enabled";
    }
    if (shell.INCUS_DIR !== undefined) {
      config.stateDir = shell.INCUS_DIR;
    }
    if (shell.JAIL_BRIDGE !== undefined) {
      config.jailBridge = shell.JAIL_BRIDGE;
    }
    if (shell.ACL_BLOCK !== undefined) {
      config.aclBlock = shell.ACL_BLOCK;
    }
    if (shell.JAIL_IMAGE !== undefined) {
      config.jailImage = shell.JAIL_IMAGE;
    }
    if (shell.JAIL_PROFILE !== undefined) {
      config.jailProfile = shell.JAIL_PROFILE;
    }
    return config;
  }

  /**
   * Updates matching shell variables in shell config file line-by-line to preserve comments.
   */
  private updateShellConfig(content: string, updates: Partial<IncusConfig>): string {
    const lines = content.split(/\r?\n/);
    const keyMap: Record<keyof IncusConfig, string> = {
      enabled: "SERVICE",
      stateDir: "INCUS_DIR",
      jailBridge: "JAIL_BRIDGE",
      aclBlock: "ACL_BLOCK",
      jailImage: "JAIL_IMAGE",
      jailProfile: "JAIL_PROFILE",
    };

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
          const val = updates[tsKey];
          let strVal = "";
          if (tsKey === "enabled") {
            strVal = val ? "enabled" : "disabled";
          } else {
            strVal = String(val);
          }

          const originalRightHand = trimmed.substring(eqIdx + 1).trim();
          // Retain comments if they were on the same line
          const hashIdx = originalRightHand.indexOf("#");
          const comment = hashIdx >= 0 ? originalRightHand.substring(hashIdx) : "";

          // Preserve quotes if original had them
          if (originalRightHand.startsWith("'")) {
            return `${key}='${strVal}'${comment ? " " + comment : ""}`;
          } else {
            return `${key}="${strVal}"${comment ? " " + comment : ""}`;
          }
        }
      }
      return line;
    });

    return newLines.join("\n");
  }
}
