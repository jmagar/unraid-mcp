import { registerAs } from "@nestjs/config";
import { Field, InputType, ObjectType } from "@nestjs/graphql";
import { Exclude, Expose } from "class-transformer";
import { IsArray, IsBoolean, IsOptional, IsString } from "class-validator";

/**
 * Mirrors the shell `incus.cfg` so the daemon-side init and the API agree on
 * one policy. The persister reads/writes this; the array-start script also
 * reads incus.cfg. incus.cfg is canonical for lifecycle; this exposes the
 * same knobs over GraphQL for the UI, kept in sync via IncusConfigSyncService.
 */
@Exclude()
@ObjectType()
export class IncusConfig {
  @Expose()
  @Field(() => Boolean, { description: "Autostart incusd on array start" })
  @IsBoolean()
  enabled!: boolean;

  @Expose()
  @Field(() => String, { description: "Persistent daemon state dir (on the array)" })
  @IsString()
  stateDir!: string;

  @Expose()
  @Field(() => String, { description: "Storage driver: zfs|dir" })
  @IsString()
  storageDriver!: string;

  @Expose()
  @Field(() => String, { description: "ZFS pool/dataset (ignored for dir driver)" })
  @IsString()
  storageSource!: string;

  @Expose()
  @Field(() => String, { description: "Incus storage pool name" })
  @IsString()
  storagePoolName!: string;

  @Expose()
  @Field(() => String, { description: "Jail bridge name" })
  @IsString()
  jailBridge!: string;

  @Expose()
  @Field(() => String, { description: "CIDR for the jail bridge" })
  @IsString()
  jailSubnet!: string;

  @Expose()
  @Field(() => Boolean, { description: "NAT the jail subnet to the Internet" })
  @IsBoolean()
  jailNat!: boolean;

  @Expose()
  @Field(() => String, { description: "IPv6 address for the jail bridge, or 'none'" })
  @IsString()
  jailIpv6!: string;

  @Expose()
  @Field(() => String, { description: "Name of the LAN-ban network ACL" })
  @IsString()
  aclName!: string;

  @Expose()
  @Field(() => String, { description: "CIDRs the jail may NOT reach (comma-separated)" })
  @IsString()
  aclBlock!: string;

  @Expose()
  @Field(() => String, { description: "CIDRs explicitly allowed despite ACL_BLOCK (comma-separated)" })
  @IsString()
  aclAllow!: string;

  @Expose()
  @Field(() => String, { description: "Default egress action: allow|drop" })
  @IsString()
  aclDefaultEgress!: string;

  @Expose()
  @Field(() => String, { description: "Default ingress action: allow|drop" })
  @IsString()
  aclDefaultIngress!: string;

  @Expose()
  @Field(() => String, { description: "Profile applied to new jails" })
  @IsString()
  jailProfile!: string;

  @Expose()
  @Field(() => String, { description: "Default image for new jails" })
  @IsString()
  jailImage!: string;

  @Expose()
  @Field(() => Boolean, { description: "Allow nested docker/incus inside the jail" })
  @IsBoolean()
  jailNesting!: boolean;

  @Expose()
  @Field(() => String, { description: "CPU cap per jail (empty = no cap)" })
  @IsString()
  jailCpu!: string;

  @Expose()
  @Field(() => String, { description: "Memory cap per jail (empty = no cap)" })
  @IsString()
  jailMemory!: string;

  @Expose()
  @Field(() => String, { description: "Host dir holding per-jail workspaces" })
  @IsString()
  jailWorkspaceRoot!: string;

  @Expose()
  @Field(() => String, { description: "In-jail agent user uid" })
  @IsString()
  jailAgentUid!: string;

  @Expose()
  @Field(() => String, { description: "In-jail agent user gid" })
  @IsString()
  jailAgentGid!: string;

  @Expose()
  @Field(() => String, { description: "Comma-separated host:container[:ro] bind-mount triples" })
  @IsString()
  jailBindMounts!: string;

  @Expose()
  @Field(() => String, { description: "Tailscale auth key to auto-join new jails with (empty = disabled)" })
  @IsString()
  tsAuthKey!: string;
}

export const configFeature = registerAs<IncusConfig>("incus", () => ({
  enabled: false,
  stateDir: "/mnt/user/appdata/incus",
  storageDriver: "dir",
  storageSource: "nvme/incus",
  storagePoolName: "default",
  jailBridge: "agentbr0",
  jailSubnet: "198.18.0.1/24",
  jailNat: true,
  jailIpv6: "none",
  aclName: "agent-block-lan",
  aclBlock: "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,169.254.0.0/16",
  aclAllow: "",
  aclDefaultEgress: "allow",
  aclDefaultIngress: "drop",
  jailProfile: "agent-jail",
  jailImage: "images:debian/trixie/cloud",
  jailNesting: false,
  jailCpu: "2",
  jailMemory: "4GiB",
  jailWorkspaceRoot: "/srv/agent-jails",
  jailAgentUid: "1000",
  jailAgentGid: "1000",
  jailBindMounts: "",
  tsAuthKey: "",
}));

/**
 * Input mirror of IncusConfig for the updateIncusConfig mutation — all fields
 * optional (partial update). Every field needs an explicit class-validator
 * decorator: unraid-api's global ValidationPipe runs in whitelist mode, which
 * silently rejects ("property X should not exist") any input property that
 * isn't backed by a validator, regardless of the @Field() GraphQL decorator.
 */
@InputType()
export class IncusConfigInput {
  @Field(() => Boolean, { nullable: true }) @IsOptional() @IsBoolean() enabled?: boolean;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() stateDir?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() storageDriver?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() storageSource?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() storagePoolName?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() jailBridge?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() jailSubnet?: string;
  @Field(() => Boolean, { nullable: true }) @IsOptional() @IsBoolean() jailNat?: boolean;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() jailIpv6?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() aclName?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() aclBlock?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() aclAllow?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() aclDefaultEgress?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() aclDefaultIngress?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() jailProfile?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() jailImage?: string;
  @Field(() => Boolean, { nullable: true }) @IsOptional() @IsBoolean() jailNesting?: boolean;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() jailCpu?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() jailMemory?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() jailWorkspaceRoot?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() jailAgentUid?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() jailAgentGid?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() jailBindMounts?: string;
  @Field(() => String, { nullable: true }) @IsOptional() @IsString() tsAuthKey?: string;
}

@ObjectType()
export class Jail {
  @Field(() => String) name!: string;
  @Field(() => String) status!: string;
  @Field(() => String, { nullable: true }) ipv4?: string;
  @Field(() => Number, { nullable: true, description: "Cumulative CPU time consumed, in nanoseconds" })
  cpuUsageNs?: number;
  @Field(() => Number, { nullable: true, description: "Current memory usage, in bytes" })
  memoryUsageBytes?: number;
  @Field(() => Number, { nullable: true, description: "Memory limit, in bytes (0 = uncapped)" })
  memoryTotalBytes?: number;
}

@ObjectType()
export class JailDetail {
  @Field(() => String) name!: string;
  @Field(() => [String], { description: "Incus profiles applied, in order" }) profiles!: string[];
  @Field(() => String, { nullable: true }) imageOs?: string;
  @Field(() => String, { nullable: true }) imageRelease?: string;
  @Field(() => String, { nullable: true }) imageDescription?: string;
  @Field(() => String, { nullable: true, description: "Incus storage pool backing the root disk" })
  storagePool?: string;
  @Field(() => String, { nullable: true }) networkBridge?: string;
  @Field(() => String, { nullable: true, description: "Effective CPU limit (core count), resolved from profile or override" })
  cpuLimit?: string;
  @Field(() => Boolean, { description: "True if cpuLimit is an instance-level override, not the profile's own value" })
  cpuLimitIsOverride!: boolean;
  @Field(() => String, { nullable: true, description: "Effective memory limit, resolved from profile or override" })
  memoryLimit?: string;
  @Field(() => Boolean, { description: "True if memoryLimit is an instance-level override, not the profile's own value" })
  memoryLimitIsOverride!: boolean;
  @Field(() => String, { nullable: true, description: "Effective host path bind-mounted at /workspace" })
  workspaceHostPath?: string;
  @Field(() => Boolean, { description: "True if workspaceHostPath is an instance-level override, not the profile's own value" })
  workspaceIsOverride!: boolean;
}

@ObjectType()
export class HomebrewInstallStatus {
  @Field(() => String) id!: string;
  @Field(() => String) formula!: string;
  @Field(() => String, { description: "running | success | failed" }) status!: string;
  @Field(() => String) message!: string;
}

@ObjectType()
export class BuilderPreset {
  @Field(() => String) name!: string;
  @Field(() => String) distro!: string;
  @Field(() => String) release!: string;
  @Field(() => [String]) packages!: string[];
}

@InputType()
export class BuilderPresetInput {
  @Field(() => String) @IsString() name!: string;
  @Field(() => String) @IsString() distro!: string;
  @Field(() => String) @IsString() release!: string;
  @Field(() => [String]) @IsArray() @IsString({ each: true }) packages!: string[];
}

@ObjectType()
export class ImageBuildStatus {
  @Field(() => String) id!: string;
  @Field(() => String, { description: "queued|running|success|failed" }) status!: string;
  @Field(() => String, { description: "Alias the built image is/will be imported under" }) alias!: string;
  @Field(() => String) distro!: string;
  @Field(() => String) release!: string;
  @Field(() => [String]) packages!: string[];
  @Field(() => String, { description: "Tail of the distrobuilder build log" }) logTail!: string;
  @Field(() => String, { nullable: true, description: "Error message, present when status is failed" })
  error?: string;
}

@ObjectType()
export class ImageRecord {
  @Field(() => String) alias!: string;
  @Field(() => String) distro!: string;
  @Field(() => String) release!: string;
  @Field(() => [String]) packages!: string[];
  @Field(() => Boolean) isMaster!: boolean;
  @Field(() => String, { nullable: true, description: "Alias of the master image this was built as a variant of" })
  basedOn?: string;
  @Field(() => String, { description: "ISO timestamp of when the image was built" }) createdAt!: string;
}

@ObjectType()
export class PackageSearchResult {
  @Field(() => String, { description: "apt | npm | pypi | brew" }) ecosystem!: string;
  @Field(() => String) name!: string;
  @Field(() => String, { nullable: true }) description?: string;
  @Field(() => String, { nullable: true }) version?: string;
}

@ObjectType()
export class PackageSearchError {
  @Field(() => String) ecosystem!: string;
  @Field(() => String) message!: string;
}

@ObjectType()
export class PackageSearchResponse {
  @Field(() => [PackageSearchResult]) results!: PackageSearchResult[];
  @Field(() => [PackageSearchError], { description: "Sources that failed — results from other sources still come back" })
  errors!: PackageSearchError[];
}
