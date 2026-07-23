import * as React from "react"
import { Check, ChevronRight, Copy, XCircle } from "lucide-react"
import { Action } from "@/components/aurora/ai/action"
import { Actions } from "@/components/aurora/ai/actions"
import { Agent } from "@/components/aurora/ai/agent"
import { Checkpoint } from "@/components/aurora/ai/checkpoint"
import { Context } from "@/components/aurora/ai/context"
import { Image as AuroraImage } from "@/components/aurora/ai/image"
import {
  Message,
  MessageContent,
} from "@/components/aurora/ai/message"
import { Plan } from "@/components/aurora/ai/plan"
import { Reasoning } from "@/components/aurora/ai/reasoning"
import { Response } from "@/components/aurora/ai/response"
import { AskUserQuestion } from "@/components/aurora/ask-user-question"
import { CodeBlock } from "@/components/aurora/code-block"
import { PermissionPrompt } from "@/components/aurora/permission-prompt"
import { Terminal, type TerminalLine } from "@/components/aurora/terminal"
import { ToolCalls, type ToolCall } from "@/components/aurora/tool-calls"
import { Banner } from "@/components/ui/aurora/banner"
import { Badge } from "@/components/ui/aurora/badge"
import { Button } from "@/components/ui/aurora/button"
import { Collapsible } from "@/components/ui/aurora/collapsible"
import {
  DescriptionItem,
  DescriptionList,
} from "@/components/ui/aurora/description-list"
import { Input } from "@/components/ui/aurora/input"
import { Progress } from "@/components/ui/aurora/progress"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/aurora/select"
import type {
  JsonObject,
  ServerRequest,
  TimelineItem,
} from "@/protocol"

function formatJson(value: unknown): string {
  if (typeof value === "string") return value
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return String(value)
  }
}

function compactValue(value: unknown): string {
  if (value == null) return "Not set"
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value)
  }
  if (Array.isArray(value)) return value.map(compactValue).join(", ")
  const enabled = Object.entries(value as JsonObject)
    .filter(([, entry]) => entry === true)
    .map(([key]) => key)
  return enabled.length ? enabled.join(", ") : formatJson(value)
}

function InventoryBadges({ values }: { values: string[] }) {
  return (
    <span className="uc-badge-list">
      {values.map((value) => (
        <Badge key={value} tone="neutral" fill="outline" size="sm">
          {value}
        </Badge>
      ))}
    </span>
  )
}

export function SessionContextRenderer({
  state,
  onMcpLogin,
  onUpdateSettings,
}: {
  state: {
    thread: JsonObject | null
    settings: JsonObject | null
    config: JsonObject | null
    models: JsonObject[]
    skills: JsonObject[]
    mcpServers: JsonObject[]
    goal: JsonObject | null
    rateLimits: JsonObject | null
    permissionProfiles: JsonObject[]
    hooks: JsonObject[]
    apps: JsonObject[]
    plugins: JsonObject[]
    marketplaceErrors: JsonObject[]
    events: Array<{ method: string; params: JsonObject; at: number }>
    items: TimelineItem[]
  }
  onMcpLogin?: (name: string) => void
  onUpdateSettings?: (settings: JsonObject) => void
}) {
  const config = state.config ?? {}
  const settings = state.settings ?? {}
  const currentModel = settings.model ?? config.model ?? "Codex default"
  const effort = settings.effort ?? config.model_reasoning_effort ?? "default"
  const approval =
    settings.approvalPolicy ?? config.approval_policy ?? config.approvalPolicy ?? "ask"
  const sandbox =
    settings.sandboxPolicy ?? config.sandbox_mode ?? config.sandboxMode ?? "danger-full-access"
  const profile =
    settings.activePermissionProfile?.name ??
    settings.activePermissionProfile?.id ??
    config.permission_profile ??
    "Default"
  const configuredTools = Object.entries(config.tools ?? {})
    .filter(([, enabled]) => enabled !== false)
    .map(([name]) => name)
  const agents = state.items.filter((entry) =>
    ["collabAgentToolCall", "subAgentActivity"].includes(entry.item.type),
  )
  const rateWindow = state.rateLimits?.primary
  const selectedModel = state.models.find(
    (model) => (model.model ?? model.id) === currentModel,
  )
  const effortOptions =
    selectedModel?.supportedReasoningEfforts?.map(
      (option: JsonObject) => option.reasoningEffort ?? option.effort ?? option.value,
    ).filter(Boolean) ?? ["minimal", "low", "medium", "high", "xhigh"]
  const goalPercent =
    state.goal?.tokenBudget && state.goal.tokenBudget > 0
      ? Math.min(100, Math.round((state.goal.tokensUsed / state.goal.tokenBudget) * 100))
      : null

  return (
    <div className="uc-session-context">
      <DescriptionList className="uc-session-summary">
        <DescriptionItem
          label="Model"
          value={
            <div className="uc-setting-controls">
              <Select
                value={String(currentModel)}
                onValueChange={(model) => onUpdateSettings?.({ model })}
              >
                <SelectTrigger aria-label="Session model">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {state.models.filter((model) => !model.hidden).map((model) => (
                    <SelectItem
                      key={model.model ?? model.id}
                      value={model.model ?? model.id}
                    >
                      {model.displayName ?? model.model ?? model.id}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select
                value={String(effort)}
                onValueChange={(nextEffort) =>
                  onUpdateSettings?.({ effort: nextEffort })
                }
              >
                <SelectTrigger aria-label="Reasoning effort">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {effortOptions.map((option: string) => (
                    <SelectItem key={option} value={option}>
                      {option} effort
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          }
          active
        />
        <DescriptionItem
          label="Permissions"
          value={`${compactValue(approval)} · ${compactValue(sandbox)} · ${profile}`}
        />
        <DescriptionItem
          label="Workspace"
          value={settings.cwd ?? state.thread?.cwd ?? "/workspace"}
        />
      </DescriptionList>

      {state.goal ? (
        <Collapsible
          title={
            <span className="uc-collapsible-title">
              Goal
              <Badge tone={state.goal.status === "blocked" ? "warn" : "info"} size="sm">
                {state.goal.status}
              </Badge>
            </span>
          }
          defaultOpen
        >
          <div className="uc-inventory-detail">
            <div className="aurora-text-body">{state.goal.objective}</div>
            {goalPercent != null ? (
              <Progress
                value={state.goal.tokensUsed}
                max={state.goal.tokenBudget}
                showLabel
                label={`${state.goal.tokensUsed.toLocaleString()} / ${state.goal.tokenBudget.toLocaleString()} tokens`}
                size="sm"
              />
            ) : (
              <div className="aurora-text-meta">
                {Number(state.goal.tokensUsed ?? 0).toLocaleString()} tokens used
              </div>
            )}
          </div>
        </Collapsible>
      ) : null}

      <Collapsible
        title={
          <span className="uc-collapsible-title">
            MCP Servers & Tools
            <Badge tone="info" size="sm">{state.mcpServers.length}</Badge>
          </span>
        }
      >
        <div className="uc-inventory-list">
          {state.mcpServers.length ? state.mcpServers.map((server) => {
            const tools = Object.keys(server.tools ?? {})
            const failed = server.startupStatus === "failed" || Boolean(server.startupError)
            return (
              <div className="uc-inventory-row" key={server.name}>
                <div className="uc-inventory-heading">
                  <strong>{server.name}</strong>
                  <Badge tone={failed ? "error" : "success"} dot size="sm">
                    {failed ? "failed" : compactValue(server.authStatus ?? "ready")}
                  </Badge>
                </div>
                <div className="aurora-text-meta">
                  {tools.length} tools · {(server.resources ?? []).length} resources ·{" "}
                  {(server.resourceTemplates ?? []).length} templates
                </div>
                {tools.length ? <InventoryBadges values={tools} /> : null}
                {(server.resources ?? []).length ? (
                  <InventoryBadges
                    values={(server.resources ?? [])
                      .map((resource: JsonObject) => resource.name ?? resource.uri)
                      .filter(Boolean)}
                  />
                ) : null}
                {(server.resourceTemplates ?? []).length ? (
                  <InventoryBadges
                    values={(server.resourceTemplates ?? [])
                      .map(
                        (template: JsonObject) =>
                          template.name ?? template.uriTemplate,
                      )
                      .filter(Boolean)}
                  />
                ) : null}
                {server.authStatus === "notLoggedIn" && onMcpLogin ? (
                  <Button
                    variant="neutral"
                    size="sm"
                    onClick={() => onMcpLogin(server.name)}
                  >
                    Sign in
                  </Button>
                ) : null}
              </div>
            )
          }) : <div className="aurora-text-meta">No MCP servers advertised.</div>}
        </div>
      </Collapsible>

      <Collapsible
        title={
          <span className="uc-collapsible-title">
            Apps & Plugins
            <Badge tone="info" size="sm">
              {state.apps.length + state.plugins.length}
            </Badge>
          </span>
        }
      >
        <div className="uc-inventory-list">
          {state.plugins.map((plugin) => (
            <div className="uc-inventory-row" key={`plugin-${plugin.id}`}>
              <div className="uc-inventory-heading">
                <strong>{plugin.name}</strong>
                <Badge
                  tone={plugin.enabled ? "success" : "neutral"}
                  size="sm"
                >
                  {plugin.enabled ? "plugin enabled" : "plugin disabled"}
                </Badge>
              </div>
              <div className="aurora-text-meta">
                {[plugin.marketplaceName, plugin.localVersion ?? plugin.version]
                  .filter(Boolean)
                  .join(" · ")}
              </div>
              {plugin.keywords?.length ? (
                <InventoryBadges values={plugin.keywords.slice(0, 8)} />
              ) : null}
            </div>
          ))}
          {state.apps.map((app) => (
            <div className="uc-inventory-row" key={`app-${app.id}`}>
              <div className="uc-inventory-heading">
                <strong>{app.name}</strong>
                <Badge
                  tone={app.isAccessible && app.isEnabled ? "success" : "neutral"}
                  size="sm"
                >
                  {app.isAccessible && app.isEnabled ? "app ready" : "app unavailable"}
                </Badge>
              </div>
              {app.description ? (
                <div className="aurora-text-meta">{app.description}</div>
              ) : null}
              {app.pluginDisplayNames?.length ? (
                <InventoryBadges values={app.pluginDisplayNames} />
              ) : null}
              {!app.isAccessible && app.installUrl ? (
                <Button
                  variant="neutral"
                  size="sm"
                  onClick={() =>
                    window.open(app.installUrl, "_blank", "noopener,noreferrer")
                  }
                >
                  Connect app
                </Button>
              ) : null}
            </div>
          ))}
          {!state.apps.length && !state.plugins.length ? (
            <div className="aurora-text-meta">No apps or plugins discovered.</div>
          ) : null}
          {state.marketplaceErrors.map((error, index) => (
            <Banner
              key={`marketplace-error-${index}`}
              variant="warn"
              title="Plugin marketplace unavailable"
              description={error.message ?? formatJson(error)}
            />
          ))}
        </div>
      </Collapsible>

      <Collapsible
        title={
          <span className="uc-collapsible-title">
            Skills
            <Badge tone="info" size="sm">{state.skills.length}</Badge>
          </span>
        }
      >
        <div className="uc-inventory-list">
          {state.skills.length ? state.skills.map((skill) => (
            <div className="uc-inventory-row" key={`${skill.name}-${skill.path}`}>
              <div className="uc-inventory-heading">
                <strong>{skill.name}</strong>
                <Badge tone={skill.enabled ? "success" : "neutral"} size="sm">
                  {skill.enabled ? compactValue(skill.scope) : "disabled"}
                </Badge>
              </div>
              <div className="aurora-text-meta">
                {skill.shortDescription ?? skill.interface?.short_description ?? skill.description}
              </div>
            </div>
          )) : <div className="aurora-text-meta">No skills discovered for this workspace.</div>}
        </div>
      </Collapsible>

      <Collapsible
        title={
          <span className="uc-collapsible-title">
            Runtime
            <Badge tone="neutral" size="sm">
              {state.models.length} models
            </Badge>
          </span>
        }
      >
        <DescriptionList className="uc-runtime-list">
          <DescriptionItem
            label="Models"
            value={<InventoryBadges values={state.models.map((model) => model.id ?? model.model ?? model.slug).filter(Boolean)} />}
          />
          <DescriptionItem
            label="Tools"
            value={configuredTools.length ? <InventoryBadges values={configuredTools} /> : "App-server defaults"}
          />
          <DescriptionItem
            label="Profiles"
            value={
              state.permissionProfiles.length ? (
                <Select
                  value={
                    settings.activePermissionProfile?.id ??
                    config.permission_profile ??
                    state.permissionProfiles.find((entry) => entry.allowed !== false)?.id
                  }
                  onValueChange={(permissions) =>
                    onUpdateSettings?.({ permissions })
                  }
                >
                  <SelectTrigger aria-label="Permission profile">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {state.permissionProfiles
                      .filter((entry) => entry.allowed !== false)
                      .map((entry) => (
                        <SelectItem key={entry.id} value={entry.id}>
                          {entry.name ?? entry.id}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              ) : (
                "Default"
              )
            }
          />
          <DescriptionItem
            label="Personality"
            value={
              <Select
                value={settings.personality ?? config.personality ?? "none"}
                onValueChange={(personality) =>
                  onUpdateSettings?.({ personality })
                }
              >
                <SelectTrigger aria-label="Personality">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  <SelectItem value="friendly">Friendly</SelectItem>
                  <SelectItem value="pragmatic">Pragmatic</SelectItem>
                </SelectContent>
              </Select>
            }
          />
          <DescriptionItem
            label="Hooks"
            value={state.hooks.length
              ? <InventoryBadges values={state.hooks.map((hook) => `${hook.eventName}${hook.enabled ? "" : " (off)"}`)} />
              : "None configured"}
          />
          <DescriptionItem
            label="Agents"
            value={agents.length ? `${agents.length} agent activities in this session` : "No delegated agents yet"}
          />
        </DescriptionList>
      </Collapsible>

      {rateWindow ? (
        <Collapsible title="Account Usage">
          <Progress
            value={rateWindow.usedPercent}
            showLabel
            label={`${Math.round(rateWindow.usedPercent)}% used · ${state.rateLimits?.planType ?? "account plan"}`}
            variant={rateWindow.usedPercent >= 90 ? "warn" : "default"}
          />
        </Collapsible>
      ) : null}

      <Collapsible
        title={
          <span className="uc-collapsible-title">
            Protocol Activity
            <Badge tone="neutral" size="sm">{state.events.length}</Badge>
          </span>
        }
      >
        <div className="uc-protocol-events">
          {state.events.length ? state.events.slice(-20).reverse().map((event, index) => (
            <div className="uc-protocol-event" key={`${event.at}-${event.method}-${index}`}>
              <code>{event.method}</code>
              <time dateTime={new Date(event.at).toISOString()}>
                {new Date(event.at).toLocaleTimeString([], {
                  hour: "numeric",
                  minute: "2-digit",
                  second: "2-digit",
                })}
              </time>
              {Object.keys(event.params).length ? (
                <details>
                  <summary>Payload</summary>
                  <pre>{formatJson(event.params)}</pre>
                </details>
              ) : null}
            </div>
          )) : (
            <div className="aurora-text-meta">No app-server events yet.</div>
          )}
        </div>
      </Collapsible>
    </div>
  )
}

function contentText(content: JsonObject[] = []): string {
  return content
    .filter((entry) => entry.type === "text" || entry.type === "inputText")
    .map((entry) => entry.text ?? "")
    .join("\n")
}

function resultText(item: JsonObject): string {
  if (item.error) return formatJson(item.error)
  if (item.result?.structuredContent) return formatJson(item.result.structuredContent)
  if (item.result?.content) {
    return item.result.content
      .map((entry: JsonObject) => entry.text ?? entry.content ?? formatJson(entry))
      .join("\n")
  }
  if (item.contentItems) {
    return item.contentItems
      .map((entry: JsonObject) => entry.text ?? entry.imageUrl ?? entry.audioUrl ?? "")
      .join("\n")
  }
  return ""
}

function terminalLines(item: JsonObject): TerminalLine[] {
  const lines: TerminalLine[] = [{ text: `$ ${item.command}`, type: "command" }]
  if (item.aggregatedOutput) {
    lines.push(
      ...String(item.aggregatedOutput)
        .split("\n")
        .map((text) => ({
          text,
          type: item.exitCode && item.exitCode !== 0 ? ("error" as const) : ("output" as const),
        })),
    )
  }
  if (item.status === "failed" && !item.aggregatedOutput) {
    lines.push({ text: `Command failed${item.exitCode == null ? "" : ` with exit code ${item.exitCode}`}`, type: "error" })
  }
  return lines
}

function UnraidTerminalItem({ entry }: { entry: TimelineItem }) {
  const item = entry.item
  const [copied, setCopied] = React.useState(false)
  const copyCommand = React.useCallback(async () => {
    try {
      await navigator.clipboard.writeText(item.command ?? "")
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1200)
    } catch {
      setCopied(false)
    }
  }, [item.command])
  const complete = entry.completedAtMs != null
  const failed = item.status === "failed" || (item.exitCode != null && item.exitCode !== 0)

  return (
    <section className="uc-unraid-terminal" aria-label="Command output">
      <div className="uc-unraid-terminal-head">
        <span className="uc-unraid-terminal-kind">EXEC</span>
        <code title={item.command}>{item.command}</code>
        <span
          className={`uc-unraid-terminal-exit ${failed ? "is-error" : ""}`}
        >
          {complete
            ? `exit ${item.exitCode ?? (failed ? 1 : 0)}`
            : "running"}
        </span>
        <Button
          variant="plain"
          size="unstyled"
          className="uc-unraid-terminal-copy"
          onClick={() => void copyCommand()}
          aria-label={copied ? "Copied command" : "Copy command"}
        >
          {copied ? "copied" : "copy"}
        </Button>
      </div>
      <pre>{item.aggregatedOutput || (complete ? "No output" : "Running…")}</pre>
    </section>
  )
}

function UnraidReasoningItem({ entry }: { entry: TimelineItem }) {
  const item = entry.item
  const summary = [...(item.summary ?? []), ...(item.content ?? [])]
    .filter(Boolean)
    .join("\n\n")
  const preview =
    String(item.summary?.[0] ?? item.content?.[0] ?? "Working through the request")
      .replace(/\s+/g, " ")
      .trim()

  return (
    <details className="uc-unraid-thinking" open={!entry.completedAtMs}>
      <summary>
        <ChevronRight size={13} strokeWidth={1.7} aria-hidden />
        <span>Thinking</span>
        <span aria-hidden>—</span>
        <em>{preview}</em>
      </summary>
      <div>{summary}</div>
    </details>
  )
}

function mappedToolCall(entry: TimelineItem): ToolCall {
  const item = entry.item
  const failed = item.status === "failed" || item.status === "error" || Boolean(item.error)
  const completed =
    entry.completedAtMs != null ||
    ["completed", "success", "failed", "error"].includes(item.status)
  return {
    id: item.id,
    tool:
      item.type === "mcpToolCall"
        ? `${item.server}.${item.tool}`
        : item.type === "dynamicToolCall"
          ? [item.namespace, item.tool].filter(Boolean).join(".")
          : item.type === "webSearch"
            ? "web.search"
            : item.tool ?? item.type,
    args: item.arguments ?? (item.query ? { query: item.query } : {}),
    status: failed ? "error" : completed ? "completed" : "running",
    result: entry.progress
      ? [entry.progress, resultText(item)].filter(Boolean).join("\n")
      : resultText(item),
    startedAt: entry.startedAtMs ? new Date(entry.startedAtMs) : undefined,
    completedAt: entry.completedAtMs ? new Date(entry.completedAtMs) : undefined,
  }
}

function MessageItem({ entry }: { entry: TimelineItem }) {
  const item = entry.item
  const user = item.type === "userMessage"
  const markdown = user ? contentText(item.content) : item.text ?? ""
  const [copied, setCopied] = React.useState(false)
  const copyMessage = React.useCallback(async () => {
    try {
      await navigator.clipboard.writeText(markdown)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1200)
    } catch {
      setCopied(false)
    }
  }, [markdown])
  const timestamp = entry.completedAtMs ?? entry.startedAtMs
  return (
    <Message
      role={user ? "user" : "assistant"}
      time={
        timestamp
          ? new Date(timestamp).toLocaleTimeString([], {
              hour: "numeric",
              minute: "2-digit",
            })
          : undefined
      }
      actions={
        markdown ? (
          <Actions>
            <Action
              size="sm"
              aria-label={copied ? "Copied message" : "Copy message"}
              title={copied ? "Copied" : "Copy"}
              onClick={() => void copyMessage()}
            >
              {copied ? <Check size={13} aria-hidden /> : <Copy size={13} aria-hidden />}
            </Action>
          </Actions>
        ) : undefined
      }
    >
      <MessageContent
        tone={user ? "user" : "assistant"}
        streaming={!user && !entry.completedAtMs}
        className={user ? "uc-message-content uc-message-user" : "uc-message-content uc-message-assistant"}
      >
        <Response markdown={markdown} streaming={!user && !entry.completedAtMs} />
      </MessageContent>
    </Message>
  )
}

function PlanItem({ entry }: { entry: TimelineItem }) {
  return (
    <Plan
      title="Plan"
      steps={[
        {
          label: entry.item.text || "Building a plan",
          status: entry.completedAtMs ? "done" : "inprog",
        },
      ]}
      isStreaming={!entry.completedAtMs}
    />
  )
}

function FileChangeItem({ entry }: { entry: TimelineItem }) {
  const changes = entry.item.changes ?? []
  if (!changes.length) {
    return (
      <Banner
        variant="info"
        title="Preparing file changes"
        description="Codex is building the patch."
      />
    )
  }
  return (
    <div className="uc-stack">
      {changes.map((change: JsonObject, index: number) => (
        <CodeBlock
          key={`${change.path}-${index}`}
          code={change.diff ?? ""}
          language="diff"
          filename={change.path}
          showLineNumbers
        />
      ))}
    </div>
  )
}

function CollabItem({ entry }: { entry: TimelineItem }) {
  const item = entry.item
  const states = Object.values(item.agentsStates ?? {}) as JsonObject[]
  const state = states.at(0)
  const status =
    item.status === "failed" || state?.status === "failed"
      ? "blocked"
      : entry.completedAtMs
        ? "completed"
        : "running"
  return (
    <Agent
      name={item.tool ?? "Collaborating Agent"}
      role={item.prompt ?? "Working on a delegated task"}
      status={status}
      model={item.model ?? undefined}
      task={state?.message ?? undefined}
      badge
    />
  )
}

function ImageItem({ entry }: { entry: TimelineItem }) {
  const item = entry.item
  const source =
    item.type === "imageGeneration" && /^(data:|https?:)/.test(item.result ?? "")
      ? item.result
      : item.type === "imageView" && /^(data:|https?:)/.test(item.path ?? "")
        ? item.path
        : undefined
  return (
    <AuroraImage
      src={source}
      alt={item.revisedPrompt ?? item.path ?? "Codex image"}
      status={
        item.status === "failed"
          ? "failed"
          : entry.completedAtMs
            ? "ready"
            : "generating"
      }
      prompt={item.revisedPrompt ?? undefined}
      caption={item.savedPath ?? item.path ?? undefined}
    />
  )
}

export function TimelineRenderer({
  entries,
  theme = "aurora",
}: {
  entries: TimelineItem[]
  theme?: "aurora" | "unraid"
}) {
  return (
    <>
      {entries.map((entry) => {
        const item = entry.item
        switch (item.type) {
          case "userMessage":
          case "agentMessage":
            return <MessageItem key={entry.id} entry={entry} />
          case "hookPrompt":
            return (
              <Message key={entry.id} role="system" className="uc-message-system">
                <MessageContent tone="system" className="uc-message-content uc-message-system-content">
                  <Response
                    markdown={(item.fragments ?? [])
                      .map((fragment: JsonObject) => fragment.text ?? formatJson(fragment))
                      .join("\n")}
                  />
                </MessageContent>
              </Message>
            )
          case "reasoning":
            if (theme === "unraid") {
              return <UnraidReasoningItem key={entry.id} entry={entry} />
            }
            return (
              <Reasoning
                key={entry.id}
                isStreaming={!entry.completedAtMs}
                duration={
                  entry.completedAtMs && entry.startedAtMs
                    ? Math.round((entry.completedAtMs - entry.startedAtMs) / 1000)
                    : undefined
                }
                defaultOpen={false}
              >
                <Response
                  markdown={[...(item.summary ?? []), ...(item.content ?? [])]
                    .filter(Boolean)
                    .join("\n\n")}
                  streaming={!entry.completedAtMs}
                />
              </Reasoning>
            )
          case "plan":
            return <PlanItem key={entry.id} entry={entry} />
          case "commandExecution":
            if (theme === "unraid") {
              return <UnraidTerminalItem key={entry.id} entry={entry} />
            }
            return (
              <Terminal
                key={entry.id}
                title={item.cwd ? `Terminal · ${item.cwd}` : "Terminal"}
                status={
                  item.status === "failed"
                    ? "error"
                    : entry.completedAtMs
                      ? "idle"
                      : "connected"
                }
                lines={terminalLines(item)}
                compact
              />
            )
          case "fileChange":
            return <FileChangeItem key={entry.id} entry={entry} />
          case "mcpToolCall":
          case "dynamicToolCall":
          case "webSearch":
            return <ToolCalls key={entry.id} calls={[mappedToolCall(entry)]} />
          case "collabAgentToolCall":
            return <CollabItem key={entry.id} entry={entry} />
          case "subAgentActivity":
            return (
              <Agent
                key={entry.id}
                name={item.agentPath ?? "Subagent"}
                role={item.kind ?? "Agent activity"}
                status={entry.completedAtMs ? "completed" : "running"}
                task={item.agentThreadId}
                variant="compact"
              />
            )
          case "imageGeneration":
          case "imageView":
            return <ImageItem key={entry.id} entry={entry} />
          case "sleep":
            return (
              <Checkpoint
                key={entry.id}
                label="Waiting"
                description={`Paused for ${Math.round((item.durationMs ?? 0) / 1000)} seconds`}
                status={entry.completedAtMs ? "saved" : "current"}
                variant="compact"
              />
            )
          case "enteredReviewMode":
          case "exitedReviewMode":
            return (
              <Banner
                key={entry.id}
                variant="info"
                title={item.type === "enteredReviewMode" ? "Review started" : "Review completed"}
                description={item.review}
              />
            )
          case "contextCompaction":
            return (
              <Checkpoint
                key={entry.id}
                label="Context compacted"
                status="saved"
                badge
                variant="compact"
              />
            )
          case "approvalResolution":
            return <ApprovalResolutionItem key={entry.id} entry={entry} />
          default:
            return (
              <CodeBlock
                key={entry.id}
                code={formatJson(item)}
                language="json"
                filename={item.type ?? "App-server item"}
              />
            )
        }
      })}
    </>
  )
}

function approvalDetails(method: string, params: JsonObject) {
  const fileChange =
    method === "item/fileChange/requestApproval" ||
    method === "applyPatchApproval"
  const legacy =
    method === "execCommandApproval" ||
    method === "applyPatchApproval"
  const target =
    params.command ??
    params.cmd ??
    params.changes?.map((change: JsonObject) => change.path).join(", ") ??
    params.reason
  const available = params.availableDecisions
  const allowSession =
    legacy ||
    !Array.isArray(available) ||
    available.includes("acceptForSession")

  return {
    fileChange,
    legacy,
    allowSession,
    target: typeof target === "string" ? target : formatJson(target),
    description:
      params.reason ??
      (fileChange
        ? "Codex wants to apply file changes to your system:"
        : "Codex wants to run a command that can modify your system:"),
  }
}

function ApprovalCard({
  method,
  params,
  approved,
  denied,
  session,
  exitCode,
  onAllow,
  onDeny,
}: {
  method: string
  params: JsonObject
  approved?: boolean
  denied?: boolean
  session?: boolean
  exitCode?: number | null
  onAllow?: (always: boolean) => void
  onDeny?: () => void
}) {
  const details = approvalDetails(method, params)
  const [always, setAlways] = React.useState(false)
  const resolved = approved || denied
  return (
    <section
      className={`uc-approval-card${resolved ? " is-resolved" : ""}`}
      aria-label={resolved ? "Approval result" : "Approval needed"}
    >
      <div className="uc-approval-eyebrow">
        {resolved ? (approved ? "Approved" : "Denied") : "Approval Needed"}
      </div>
      {!resolved ? <p>{details.description}</p> : null}
      {details.target ? <code>{details.target}</code> : null}
      {resolved ? (
        <div className={`uc-approval-result${denied ? " is-denied" : ""}`}>
          {approved ? (
            <Check size={14} strokeWidth={2} aria-hidden />
          ) : (
            <XCircle size={14} strokeWidth={1.8} aria-hidden />
          )}
          <span>
            {approved
              ? `Approved${session ? " for this session" : ""}${
                  exitCode == null ? " — command queued" : ` — command ran with exit ${exitCode}`
                }`
              : "Denied — command was not run"}
          </span>
        </div>
      ) : (
        <div className="uc-approval-actions">
          <Button
            variant="rose"
            size="sm"
            filled
            onClick={() => onAllow?.(always)}
          >
            Allow
          </Button>
          <Button variant="neutral" size="sm" onClick={onDeny}>
            Deny
          </Button>
          {details.allowSession ? (
            <label className="uc-approval-always">
              <input
                type="checkbox"
                checked={always}
                onChange={(event) => setAlways(event.target.checked)}
              />
              <span>Always allow</span>
            </label>
          ) : null}
        </div>
      )}
    </section>
  )
}

function ApprovalRequest({
  request,
  answer,
}: {
  request: ServerRequest
  answer: (result: JsonObject) => void
}) {
  const details = approvalDetails(request.method, request.params)
  return (
    <ApprovalCard
      method={request.method}
      params={request.params}
      onAllow={(always) =>
        answer({
          decision: details.legacy
            ? always
              ? "approved_for_session"
              : "approved"
            : always
              ? "acceptForSession"
              : "accept",
        })
      }
      onDeny={() =>
        answer({ decision: details.legacy ? "denied" : "decline" })
      }
    />
  )
}

function ApprovalResolutionItem({ entry }: { entry: TimelineItem }) {
  const item = entry.item
  return (
    <ApprovalCard
      method={item.requestMethod}
      params={item.requestParams ?? {}}
      approved={item.approved}
      denied={!item.approved}
      session={item.session}
      exitCode={item.exitCode}
    />
  )
}

function PermissionsRequest({
  request,
  answer,
}: {
  request: ServerRequest
  answer: (result: JsonObject) => void
}) {
  return (
    <PermissionPrompt
      tool="Additional Permissions"
      action={request.params.reason ?? "Codex requested additional permissions"}
      target={formatJson(request.params.permissions)}
      variant="inline"
      onAllow={() =>
        answer({
          permissions: request.params.permissions,
          scope: "turn",
          strictAutoReview: true,
        })
      }
      onDeny={() =>
        answer({ permissions: {}, scope: "turn", strictAutoReview: true })
      }
      allowLabel="Approve Once"
      denyLabel="Decline"
    />
  )
}

function UserInputRequest({
  request,
  answer,
}: {
  request: ServerRequest
  answer: (result: JsonObject) => void
}) {
  const questions = request.params.questions ?? []
  const [answers, setAnswers] = React.useState<Record<string, { answers: string[] }>>({})
  return (
    <div className="uc-stack">
      {questions.map((question: JsonObject) => (
        <AskUserQuestion
          key={question.id}
          question={question.question}
          type={question.options?.length ? "radio" : "text"}
          options={question.options?.map((option: JsonObject) => ({
            id: option.label,
            label: option.label,
            description: option.description,
          }))}
          onSubmit={(value) => {
            const values = Array.isArray(value) ? value : [value]
            setAnswers((current) => ({
              ...current,
              [question.id]: { answers: values },
            }))
          }}
        />
      ))}
      <div className="uc-request-actions">
        <Button
          variant="aurora"
          size="sm"
          disabled={Object.keys(answers).length !== questions.length}
          onClick={() => answer({ answers })}
        >
          Submit Answers
        </Button>
        <Button variant="neutral" size="sm" onClick={() => answer({ answers: {} })}>
          Cancel
        </Button>
      </div>
    </div>
  )
}

function ElicitationRequest({
  request,
  answer,
}: {
  request: ServerRequest
  answer: (result: JsonObject) => void
}) {
  const schema = request.params.requestedSchema ?? {}
  const [content, setContent] = React.useState<JsonObject>(() =>
    Object.fromEntries(
      Object.entries(schema.properties ?? {}).map(([name, field]: [string, any]) => [
        name,
        field.default ?? (field.type === "boolean" ? false : ""),
      ]),
    ),
  )

  if (request.params.mode === "url") {
    return (
      <div className="uc-request-card">
        <Banner
          variant="info"
          title={`${request.params.serverName ?? "MCP server"} request`}
          description={request.params.message}
        />
        <div className="uc-request-actions">
          <Button
            variant="aurora"
            size="sm"
            onClick={() => window.open(request.params.url, "_blank", "noopener")}
          >
            Open Request
          </Button>
          <Button
            variant="neutral"
            size="sm"
            onClick={() => answer({ action: "accept", content: null, _meta: null })}
          >
            Continue
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => answer({ action: "decline", content: null, _meta: null })}
          >
            Decline
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="uc-request-card">
      <div>
        <div className="aurora-text-section">
          {request.params.serverName ?? "MCP Server"} Request
        </div>
        <div className="aurora-text-body-sm uc-muted">{request.params.message}</div>
      </div>
      {Object.entries(schema.properties ?? {}).map(([name, field]: [string, any]) => (
        <label className="uc-field" key={name}>
          <span className="aurora-text-label">{field.title ?? name}</span>
          {Array.isArray(field.enum) ? (
            <Select
              value={String(content[name] ?? "")}
              onValueChange={(value) => setContent((current) => ({ ...current, [name]: value }))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {field.enum.map((value: unknown) => (
                  <SelectItem key={String(value)} value={String(value)}>
                    {String(value)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : (
            <Input
              type={field.secret ? "password" : ["number", "integer"].includes(field.type) ? "number" : "text"}
              value={String(content[name] ?? "")}
              onChange={(event) =>
                setContent((current) => ({
                  ...current,
                  [name]: ["number", "integer"].includes(field.type)
                    ? Number(event.target.value)
                    : event.target.value,
                }))
              }
            />
          )}
        </label>
      ))}
      <div className="uc-request-actions">
        <Button
          variant="aurora"
          size="sm"
          onClick={() => answer({ action: "accept", content, _meta: null })}
        >
          Submit
        </Button>
        <Button
          variant="neutral"
          size="sm"
          onClick={() => answer({ action: "decline", content: null, _meta: null })}
        >
          Decline
        </Button>
      </div>
    </div>
  )
}

export function RequestRenderer({
  request,
  answer,
  reject,
}: {
  request: ServerRequest
  answer: (result: JsonObject) => void
  reject: (message: string) => void
}) {
  switch (request.method) {
    case "item/commandExecution/requestApproval":
    case "item/fileChange/requestApproval":
    case "execCommandApproval":
    case "applyPatchApproval":
      return <ApprovalRequest request={request} answer={answer} />
    case "item/permissions/requestApproval":
      return <PermissionsRequest request={request} answer={answer} />
    case "item/tool/requestUserInput":
      return <UserInputRequest request={request} answer={answer} />
    case "mcpServer/elicitation/request":
      return <ElicitationRequest request={request} answer={answer} />
    default:
      return (
        <Banner
          variant="warn"
          title="Unsupported app-server request"
          description={request.method}
          action={
            <Button
              variant="neutral"
              size="sm"
              onClick={() => reject(`The Unraid chathead cannot answer ${request.method}.`)}
            >
              Dismiss
            </Button>
          }
        />
      )
  }
}

export function PlanRenderer({
  plan,
  streaming,
}: {
  plan: JsonObject
  streaming: boolean
}) {
  return (
    <Plan
      title={plan.explanation ?? "Current Plan"}
      steps={(plan.plan ?? []).map((step: JsonObject) => ({
        label: step.step,
        status:
          step.status === "completed"
            ? "done"
            : step.status === "in_progress"
              ? "inprog"
              : "pending",
      }))}
      isStreaming={streaming}
    />
  )
}

export function ContextRenderer({ tokenUsage }: { tokenUsage: JsonObject }) {
  const total = tokenUsage.total ?? {}
  return (
    <Context
      variant="compact"
      limit={tokenUsage.modelContextWindow ?? undefined}
      segments={[
        { label: "Input", value: total.inputTokens ?? 0 },
        { label: "Cached", value: total.cachedInputTokens ?? 0 },
        { label: "Output", value: total.outputTokens ?? 0 },
        { label: "Reasoning", value: total.reasoningOutputTokens ?? 0 },
      ]}
    />
  )
}
