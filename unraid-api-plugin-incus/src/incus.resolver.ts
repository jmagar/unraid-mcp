import { Resolver, Query, Mutation, Args, registerEnumType } from "@nestjs/graphql";
import { ForbiddenException } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { IncusService } from "./incus.service.js";
import { Jail } from "./config.entity.js";

enum JailAction {
  start = "start",
  stop = "stop",
  restart = "restart",
  freeze = "freeze",
  unfreeze = "unfreeze",
}
registerEnumType(JailAction, { name: "JailAction", description: "Jail lifecycle actions" });

@Resolver()
export class IncusResolver {
  constructor(
    private readonly incus: IncusService,
    private readonly config: ConfigService,
  ) {}

  @Query(() => Boolean, { description: "Is incusd reachable over its unix socket?" })
  async incusHealthy(): Promise<boolean> {
    return this.incus.ping();
  }

  @Query(() => [Jail], { description: "List all agent jails" })
  async jails(): Promise<Jail[]> {
    return this.incus.listJails();
  }

  @Mutation(() => Boolean, { description: "Launch a new LAN-banned agent jail" })
  async launchJail(
    @Args("name") name: string,
    @Args("image", { nullable: true }) image?: string
  ): Promise<boolean> {
    await this.incus.launchJail(name, { image });
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
    // H5 fix: validate hostPath is under the configured workspace root
    const wsRoot = this.config.get<string>("incus.workspaceRoot", "/srv/agent-jails");
    const resolved = hostPath.replace(/\/+$/, "");
    if (!resolved.startsWith(wsRoot)) {
      throw new ForbiddenException(`hostPath must be under the workspace root (${wsRoot})`);
    }
    await this.incus.setWorkspace(name, hostPath);
    return true;
  }

  @Mutation(() => Boolean)
  async deleteJail(@Args("name") name: string): Promise<boolean> {
    await this.incus.deleteJail(name);
    return true;
  }
}
