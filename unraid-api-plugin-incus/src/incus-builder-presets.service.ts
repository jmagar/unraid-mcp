import { Injectable } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { BuilderPreset, BuilderPresetInput } from "./config.entity.js";

/**
 * Saveable distrobuilder presets (distro/release/packages), persisted as a
 * small JSON array at <stateDir>/builder-presets.json. Read-modify-write on
 * every call — this file is tiny and rarely touched, no in-memory cache.
 */
@Injectable()
export class IncusBuilderPresetsService {
  constructor(private readonly config: ConfigService) {}

  private get filePath(): string {
    const dir = this.config.get<string>("incus.stateDir", "/mnt/user/appdata/incus");
    return join(dir, "builder-presets.json");
  }

  async list(): Promise<BuilderPreset[]> {
    return this.readAll();
  }

  async save(input: BuilderPresetInput): Promise<BuilderPreset> {
    const presets = await this.readAll();
    const preset: BuilderPreset = {
      name: input.name,
      distro: input.distro,
      release: input.release,
      packages: input.packages,
    };
    const idx = presets.findIndex((p) => p.name === input.name);
    if (idx >= 0) {
      presets[idx] = preset;
    } else {
      presets.push(preset);
    }
    await this.writeAll(presets);
    return preset;
  }

  async remove(name: string): Promise<boolean> {
    const presets = await this.readAll();
    const next = presets.filter((p) => p.name !== name);
    if (next.length === presets.length) return false;
    await this.writeAll(next);
    return true;
  }

  private async readAll(): Promise<BuilderPreset[]> {
    try {
      const data = await readFile(this.filePath, "utf-8");
      return JSON.parse(data);
    } catch {
      return [];
    }
  }

  private async writeAll(presets: BuilderPreset[]): Promise<void> {
    await mkdir(dirname(this.filePath), { recursive: true });
    await writeFile(this.filePath, JSON.stringify(presets, null, 2), "utf-8");
  }
}
