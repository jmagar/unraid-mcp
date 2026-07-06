import { registerAs } from "@nestjs/config";
import { Field, ObjectType } from "@nestjs/graphql";
import { Exclude, Expose } from "class-transformer";
import { IsBoolean, IsString } from "class-validator";

/**
 * Mirrors the shell `incus.cfg` so the daemon-side init and the API agree on
 * one policy. The persister reads/writes this; the array-start script also
 * reads incus.cfg. (v1: incus.cfg is canonical for lifecycle; this exposes the
 * same knobs over GraphQL for the UI. Reconciliation writer is a follow-up.)
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
  @Field(() => String, { description: "Jail bridge name" })
  @IsString()
  jailBridge!: string;

  @Expose()
  @Field(() => String, { description: "CIDRs the jail may NOT reach (comma-separated)" })
  @IsString()
  aclBlock!: string;

  @Expose()
  @Field(() => String, { description: "Default image for new jails" })
  @IsString()
  jailImage!: string;

  @Expose()
  @Field(() => String, { description: "Profile applied to new jails" })
  @IsString()
  jailProfile!: string;
}

export const configFeature = registerAs<IncusConfig>("incus", () => ({
  enabled: false,
  stateDir: "/mnt/user/appdata/incus",
  jailBridge: "agentbr0",
  aclBlock: "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,169.254.0.0/16",
  jailImage: "images:debian/trixie/cloud",
  jailProfile: "agent-jail",
}));

@ObjectType()
export class Jail {
  @Field(() => String) name!: string;
  @Field(() => String) status!: string;
  @Field(() => String, { nullable: true }) ipv4?: string;
}
