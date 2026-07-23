import * as React from "react"

const STORAGE_THREAD = "unraid-codex.thread-id"
const SOCKET_PATH = "/webterminal/unraid-codex-appserver/ws"

export type JsonObject = Record<string, any>

export interface TimelineItem {
  id: string
  turnId: string
  item: JsonObject
  startedAtMs?: number
  completedAtMs?: number
  progress?: string
}

export interface Notice {
  id: string
  tone: "info" | "warn" | "error" | "success"
  title: string
  description?: string
}

export interface ServerRequest {
  id: string | number
  method: string
  params: JsonObject
}

export interface DeviceLogin {
  verificationUrl: string
  userCode: string
}

export interface CodexState {
  status: "connecting" | "connected" | "working" | "disconnected" | "error"
  statusText: string
  initialized: boolean
  authenticated: boolean
  threadId: string | null
  activeTurnId: string | null
  items: TimelineItem[]
  requests: ServerRequest[]
  notices: Notice[]
  plan: JsonObject | null
  diff: string
  tokenUsage: JsonObject | null
  deviceLogin: DeviceLogin | null
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
}

const INITIAL_STATE: CodexState = {
  status: "connecting",
  statusText: "Connecting to Codex",
  initialized: false,
  authenticated: false,
  threadId: localStorage.getItem(STORAGE_THREAD),
  activeTurnId: null,
  items: [],
  requests: [],
  notices: [],
  plan: null,
  diff: "",
  tokenUsage: null,
  deviceLogin: null,
  thread: null,
  settings: null,
  config: null,
  models: [],
  skills: [],
  mcpServers: [],
  goal: null,
  rateLimits: null,
  permissionProfiles: [],
  hooks: [],
  apps: [],
}

function flattenTurns(thread: JsonObject): TimelineItem[] {
  return (thread.turns ?? []).flatMap((turn: JsonObject) =>
    (turn.items ?? []).map((item: JsonObject) => ({
      id: item.id,
      turnId: turn.id,
      item,
      startedAtMs: turn.startedAt ? turn.startedAt * 1000 : undefined,
      completedAtMs: turn.completedAt ? turn.completedAt * 1000 : undefined,
    })),
  )
}

function upsertTimeline(
  items: TimelineItem[],
  id: string,
  update: Partial<TimelineItem> | ((current: TimelineItem) => TimelineItem),
): TimelineItem[] {
  const index = items.findIndex((entry) => entry.id === id)
  if (index < 0) {
    if (typeof update === "function") return items
    return [...items, { id, turnId: update.turnId ?? "", item: update.item ?? {}, ...update }]
  }
  const copy = items.slice()
  copy[index] =
    typeof update === "function" ? update(copy[index]) : { ...copy[index], ...update }
  return copy
}

function textFromError(error: any): string {
  return error?.message ?? error?.error?.message ?? String(error ?? "Codex request failed.")
}

function contentText(content: JsonObject[] = []): string {
  return content
    .filter((entry) => entry.type === "text")
    .map((entry) => entry.text ?? "")
    .join("\n")
}

async function browserUrlToDataUrl(url: string): Promise<string> {
  if (url.startsWith("data:") || url.startsWith("http:") || url.startsWith("https:")) {
    return url
  }
  const blob = await fetch(url).then((response) => response.blob())
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.addEventListener("load", () => resolve(String(reader.result)))
    reader.addEventListener("error", () => reject(reader.error ?? new Error("Could not read attachment.")))
    reader.readAsDataURL(blob)
  })
}

export function useCodexAppServer() {
  const [state, setState] = React.useState<CodexState>(INITIAL_STATE)
  const socketRef = React.useRef<WebSocket | null>(null)
  const nextIdRef = React.useRef(1)
  const reconnectRef = React.useRef<number | null>(null)
  const pendingRef = React.useRef(
    new Map<string, { resolve: (value: any) => void; reject: (error: Error) => void }>(),
  )
  const localRequestRef = React.useRef(
    new Map<string, { resolve: (value: any) => void; reject: (error: Error) => void }>(),
  )
  const threadIdRef = React.useRef<string | null>(INITIAL_STATE.threadId)
  const activeTurnRef = React.useRef<string | null>(null)

  const rpc = React.useCallback((method: string, params: JsonObject = {}) => {
    const socket = socketRef.current
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      return Promise.reject(new Error("Codex app-server is disconnected."))
    }
    const id = nextIdRef.current++
    socket.send(JSON.stringify({ id, method, params }))
    return new Promise<any>((resolve, reject) => {
      pendingRef.current.set(String(id), { resolve, reject })
    })
  }, [])

  const notify = React.useCallback((method: string, params: JsonObject = {}) => {
    const socket = socketRef.current
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ method, params }))
    }
  }, [])

  const addNotice = React.useCallback((notice: Omit<Notice, "id">) => {
    setState((current) => ({
      ...current,
      notices: [...current.notices.slice(-5), { ...notice, id: crypto.randomUUID() }],
    }))
  }, [])

  const handleNotification = React.useCallback(
    (message: JsonObject) => {
      const params = message.params ?? {}
      switch (message.method) {
        case "item/started":
          setState((current) => ({
            ...current,
            items: upsertTimeline(
              params.item.type === "userMessage"
                ? current.items.filter(
                    (entry) =>
                      !(
                        entry.id.startsWith("local-") &&
                        entry.turnId === "pending" &&
                        contentText(entry.item.content) === contentText(params.item.content)
                      ),
                  )
                : current.items,
              params.item.id,
              {
              id: params.item.id,
              turnId: params.turnId,
              item: params.item,
              startedAtMs: params.startedAtMs,
              },
            ),
          }))
          break
        case "item/completed":
          setState((current) => ({
            ...current,
            items: upsertTimeline(current.items, params.item.id, {
              item: params.item,
              completedAtMs: params.completedAtMs,
            }),
          }))
          break
        case "item/agentMessage/delta":
          setState((current) => ({
            ...current,
            items: upsertTimeline(current.items, params.itemId, (entry) => ({
              ...entry,
              item: { ...entry.item, text: `${entry.item.text ?? ""}${params.delta ?? ""}` },
            })),
          }))
          break
        case "item/plan/delta":
          setState((current) => ({
            ...current,
            items: upsertTimeline(current.items, params.itemId, (entry) => ({
              ...entry,
              item: { ...entry.item, text: `${entry.item.text ?? ""}${params.delta ?? ""}` },
            })),
          }))
          break
        case "item/reasoning/summaryTextDelta":
          setState((current) => ({
            ...current,
            items: upsertTimeline(current.items, params.itemId, (entry) => {
              const summary = [...(entry.item.summary ?? [])]
              const index = Math.max(0, summary.length - 1)
              summary[index] = `${summary[index] ?? ""}${params.delta ?? ""}`
              return { ...entry, item: { ...entry.item, summary } }
            }),
          }))
          break
        case "item/reasoning/summaryPartAdded":
          setState((current) => ({
            ...current,
            items: upsertTimeline(current.items, params.itemId, (entry) => ({
              ...entry,
              item: { ...entry.item, summary: [...(entry.item.summary ?? []), ""] },
            })),
          }))
          break
        case "item/reasoning/textDelta":
          setState((current) => ({
            ...current,
            items: upsertTimeline(current.items, params.itemId, (entry) => {
              const content = [...(entry.item.content ?? [])]
              const index = Math.max(0, content.length - 1)
              content[index] = `${content[index] ?? ""}${params.delta ?? ""}`
              return { ...entry, item: { ...entry.item, content } }
            }),
          }))
          break
        case "item/commandExecution/outputDelta":
        case "command/exec/outputDelta":
        case "process/outputDelta":
          setState((current) => ({
            ...current,
            items: upsertTimeline(current.items, params.itemId ?? params.processId, (entry) => ({
              ...entry,
              item: {
                ...entry.item,
                aggregatedOutput: `${entry.item.aggregatedOutput ?? ""}${params.delta ?? ""}`,
              },
            })),
          }))
          break
        case "item/fileChange/patchUpdated":
          setState((current) => ({
            ...current,
            items: upsertTimeline(current.items, params.itemId, (entry) => ({
              ...entry,
              item: { ...entry.item, changes: params.changes },
            })),
          }))
          break
        case "item/mcpToolCall/progress":
          setState((current) => ({
            ...current,
            items: upsertTimeline(current.items, params.itemId, (entry) => ({
              ...entry,
              progress: params.message,
            })),
          }))
          break
        case "turn/plan/updated":
          setState((current) => ({ ...current, plan: params }))
          break
        case "turn/diff/updated":
          setState((current) => ({ ...current, diff: params.diff ?? "" }))
          break
        case "thread/tokenUsage/updated":
          setState((current) => ({ ...current, tokenUsage: params.tokenUsage }))
          break
        case "thread/settings/updated":
          setState((current) => ({ ...current, settings: params.threadSettings ?? params.settings }))
          break
        case "thread/goal/updated":
          setState((current) => ({ ...current, goal: params.goal }))
          break
        case "thread/goal/cleared":
          setState((current) => ({ ...current, goal: null }))
          break
        case "account/rateLimits/updated":
          setState((current) => ({
            ...current,
            rateLimits: params.rateLimits ?? params.snapshot ?? current.rateLimits,
          }))
          break
        case "turn/started":
          activeTurnRef.current = params.turn?.id ?? params.turnId
          setState((current) => ({
            ...current,
            status: "working",
            statusText: "Codex is working",
            activeTurnId: activeTurnRef.current,
          }))
          break
        case "turn/completed":
          activeTurnRef.current = null
          setState((current) => ({
            ...current,
            status: "connected",
            statusText: "Connected",
            activeTurnId: null,
          }))
          break
        case "thread/status/changed":
          if (params.status?.type === "idle") {
            activeTurnRef.current = null
            setState((current) => ({
              ...current,
              status: "connected",
              statusText: "Connected",
              activeTurnId: null,
            }))
          }
          break
        case "account/login/completed":
          if (params.success) {
            setState((current) => ({
              ...current,
              authenticated: true,
              deviceLogin: null,
              status: "connected",
              statusText: "Connected",
            }))
          } else {
            addNotice({ tone: "error", title: "Sign-in failed", description: params.error })
          }
          break
        case "error":
          addNotice({
            tone: "error",
            title: params.willRetry ? "Codex will retry" : "Codex error",
            description: textFromError(params.error),
          })
          break
        case "warning":
        case "guardianWarning":
        case "configWarning":
        case "deprecationNotice":
          addNotice({
            tone: "warn",
            title: message.method === "deprecationNotice" ? "Deprecation notice" : "Codex warning",
            description: params.message ?? params.summary ?? JSON.stringify(params),
          })
          break
        case "thread/compacted":
          addNotice({ tone: "info", title: "Context compacted" })
          break
        case "model/rerouted":
          setState((current) => ({
            ...current,
            settings: current.settings
              ? { ...current.settings, model: params.toModel }
              : current.settings,
          }))
          addNotice({
            tone: "info",
            title: "Model rerouted",
            description: params.reason ?? JSON.stringify(params),
          })
          break
        case "mcpServer/startupStatus/updated":
          setState((current) => ({
            ...current,
            mcpServers: current.mcpServers.map((server) =>
              server.name === (params.server ?? params.name)
                ? { ...server, startupStatus: params.status, startupError: params.error }
                : server,
            ),
          }))
          if (params.status === "failed" || params.error) {
            addNotice({
              tone: "warn",
              title: `${params.server ?? params.name ?? "MCP server"} unavailable`,
              description: params.error,
            })
          }
          break
        case "hook/started":
          addNotice({
            tone: "info",
            title: `Hook started · ${params.run?.eventName ?? "event"}`,
            description: params.run?.statusMessage,
          })
          break
        case "hook/completed":
          addNotice({
            tone: params.run?.status === "failed" ? "warn" : "success",
            title: `Hook ${params.run?.status === "failed" ? "failed" : "completed"}`,
            description: params.run?.statusMessage,
          })
          break
        case "thread/realtime/error":
          addNotice({
            tone: "error",
            title: "Realtime session error",
            description: textFromError(params),
          })
          break
        default:
          break
      }
    },
    [addNotice],
  )

  const handleMessage = React.useCallback(
    (event: MessageEvent) => {
      let message: JsonObject
      try {
        message = JSON.parse(event.data)
      } catch {
        return
      }

      if (Object.hasOwn(message, "id") && !message.method) {
        const pending = pendingRef.current.get(String(message.id))
        if (!pending) return
        pendingRef.current.delete(String(message.id))
        if (message.error) pending.reject(new Error(textFromError(message.error)))
        else pending.resolve(message.result)
        return
      }

      if (Object.hasOwn(message, "id") && message.method) {
        setState((current) => ({
          ...current,
          requests: [...current.requests, message as ServerRequest],
        }))
        return
      }

      handleNotification(message)
    },
    [handleNotification],
  )

  React.useEffect(() => {
    let disposed = false

    async function establishSession() {
      await rpc("initialize", {
        clientInfo: {
          name: "unraid-codex-chathead",
          title: "Unraid Codex",
          version: "0.2.0",
        },
        capabilities: {
          experimentalApi: true,
          requestAttestation: false,
          mcpServerOpenaiFormElicitation: true,
        },
      })
      notify("initialized")

      const [account, models] = await Promise.all([
        rpc("account/read", { refreshToken: false }),
        rpc("model/list", {}).catch(() => ({ data: [] })),
      ])

      let threadId = threadIdRef.current
      let thread: JsonObject | null = null
      if (threadId) {
        try {
          thread = (await rpc("thread/resume", { threadId })).thread
          threadId = thread?.id ?? null
        } catch {
          threadId = null
          localStorage.removeItem(STORAGE_THREAD)
        }
      }
      if (!threadId) {
        const started = (
          await rpc("thread/start", {
            cwd: "/workspace",
            approvalPolicy: {
              granular: {
                sandbox_approval: true,
                rules: true,
                skill_approval: true,
                request_permissions: true,
                mcp_elicitations: true,
              },
            },
            sandbox: "danger-full-access",
            serviceName: "unraid-chathead",
          })
        ).thread
        thread = started
        threadId = started.id
      }
      if (!threadId || disposed) return
      threadIdRef.current = threadId
      localStorage.setItem(STORAGE_THREAD, threadId)

      const [config, skills, hooks, permissionProfiles, mcpServers, apps, goal, rateLimits] =
        await Promise.all([
          rpc("config/read", { cwd: "/workspace", includeLayers: false }).catch(() => null),
          rpc("skills/list", { cwds: ["/workspace"] }).catch(() => ({ data: [] })),
          rpc("hooks/list", { cwds: ["/workspace"] }).catch(() => ({ data: [] })),
          rpc("permissionProfile/list", { cwd: "/workspace", limit: 100 }).catch(() => ({ data: [] })),
          rpc("mcpServerStatus/list", {
            detail: "full",
            threadId,
            limit: 100,
          }).catch(() => ({ data: [] })),
          rpc("app/list", { threadId, limit: 100 }).catch(() => ({ data: [] })),
          rpc("thread/goal/get", { threadId }).catch(() => ({ goal: null })),
          rpc("account/rateLimits/read").catch(() => ({ rateLimits: null })),
        ])
      if (disposed) return

      setState((current) => ({
        ...current,
        status: "connected",
        statusText: account.account ? "Connected" : "Connected. Sign-in required.",
        initialized: true,
        authenticated: Boolean(account.account),
        threadId,
        thread,
        items: thread ? flattenTurns(thread) : current.items,
        config: config?.config ?? null,
        models: models.data ?? [],
        skills: (skills.data ?? []).flatMap((entry: JsonObject) => entry.skills ?? []),
        hooks: (hooks.data ?? []).flatMap((entry: JsonObject) => entry.hooks ?? []),
        permissionProfiles: permissionProfiles.data ?? [],
        mcpServers: mcpServers.data ?? [],
        apps: apps.data ?? [],
        goal: goal.goal ?? null,
        rateLimits: rateLimits.rateLimits ?? null,
      }))
    }

    function connect() {
      if (disposed) return
      setState((current) => ({
        ...current,
        status: "connecting",
        statusText: "Connecting to Codex",
        initialized: false,
      }))
      const protocol = location.protocol === "https:" ? "wss:" : "ws:"
      const socket = new WebSocket(`${protocol}//${location.host}${SOCKET_PATH}`)
      socketRef.current = socket
      socket.addEventListener("message", handleMessage)
      socket.addEventListener("open", () => {
        establishSession().catch((error) => {
          setState((current) => ({
            ...current,
            status: "error",
            statusText: textFromError(error),
          }))
        })
      })
      socket.addEventListener("close", () => {
        if (disposed) return
        activeTurnRef.current = null
        pendingRef.current.forEach(({ reject }) =>
          reject(new Error("Codex app-server disconnected.")),
        )
        pendingRef.current.clear()
        setState((current) => ({
          ...current,
          status: "disconnected",
          statusText: "Disconnected. Retrying.",
          initialized: false,
          activeTurnId: null,
        }))
        reconnectRef.current = window.setTimeout(connect, 2500)
      })
      socket.addEventListener("error", () => {
        setState((current) => ({
          ...current,
          status: "error",
          statusText: "Could not reach Codex.",
        }))
      })
    }

    connect()
    return () => {
      disposed = true
      if (reconnectRef.current) window.clearTimeout(reconnectRef.current)
      socketRef.current?.close()
    }
  }, [handleMessage, notify, rpc])

  const send = React.useCallback(
    async (text: string, attachments: Array<{ type: string; url?: string }> = []) => {
      const threadId = threadIdRef.current
      if (!threadId || !text.trim() || activeTurnRef.current) return
      const optimisticId = `local-${crypto.randomUUID()}`
      setState((current) => ({
        ...current,
        items: [
          ...current.items,
          {
            id: optimisticId,
            turnId: "pending",
            item: {
              id: optimisticId,
              type: "userMessage",
              content: [{ type: "text", text, text_elements: [] }],
            },
            startedAtMs: Date.now(),
            completedAtMs: Date.now(),
          },
        ],
      }))
      try {
        const imageInputs = await Promise.all(
          attachments
            .filter((attachment) => attachment.type === "image" && attachment.url)
            .map(async (attachment) => ({
              type: "image",
              url: await browserUrlToDataUrl(attachment.url!),
            })),
        )
        const input = [
          { type: "text", text, text_elements: [] },
          ...imageInputs,
        ]
        const result = await rpc("turn/start", { threadId, input })
        activeTurnRef.current = result.turn.id
        setState((current) => ({
          ...current,
          status: "working",
          statusText: "Codex is working",
          activeTurnId: result.turn.id,
        }))
      } catch (error) {
        addNotice({ tone: "error", title: "Message failed", description: textFromError(error) })
      }
    },
    [addNotice, rpc],
  )

  const interrupt = React.useCallback(async () => {
    const threadId = threadIdRef.current
    const turnId = activeTurnRef.current
    if (!threadId || !turnId) return
    await rpc("turn/interrupt", { threadId, turnId })
  }, [rpc])

  const answerRequest = React.useCallback((request: ServerRequest, result: JsonObject) => {
    if (request.method.startsWith("mcpApp/")) {
      const pending = localRequestRef.current.get(String(request.id))
      localRequestRef.current.delete(String(request.id))
      setState((current) => ({
        ...current,
        requests: current.requests.filter((entry) => entry.id !== request.id),
      }))
      if (!pending) return
      if (result.decision !== "accept") {
        pending.resolve({
          content: [{ type: "text", text: "The user declined this MCP App action." }],
          isError: true,
        })
        return
      }
      if (request.method === "mcpApp/tool/requestApproval") {
        rpc("mcpServer/tool/call", {
          threadId: threadIdRef.current,
          server: request.params.server,
          tool: request.params.tool,
          arguments: request.params.arguments ?? {},
          _meta: request.params._meta,
        }).then(pending.resolve, pending.reject)
        return
      }
      if (request.method === "mcpApp/openLink/requestApproval") {
        const url = new URL(request.params.url)
        if (!["http:", "https:"].includes(url.protocol)) {
          pending.resolve({ isError: true })
          return
        }
        window.open(url.href, "_blank", "noopener,noreferrer")
        pending.resolve({})
      }
      return
    }
    socketRef.current?.send(JSON.stringify({ id: request.id, result }))
    setState((current) => ({
      ...current,
      requests: current.requests.filter((entry) => entry.id !== request.id),
    }))
  }, [rpc])

  const rejectRequest = React.useCallback((request: ServerRequest, message: string) => {
    socketRef.current?.send(
      JSON.stringify({ id: request.id, error: { code: -32601, message } }),
    )
    setState((current) => ({
      ...current,
      requests: current.requests.filter((entry) => entry.id !== request.id),
    }))
  }, [])

  const login = React.useCallback(async () => {
    try {
      const result = await rpc("account/login/start", { type: "chatgptDeviceCode" })
      setState((current) => ({
        ...current,
        deviceLogin: {
          verificationUrl: result.verificationUrl,
          userCode: result.userCode,
        },
      }))
      window.open(result.verificationUrl, "_blank", "noopener")
    } catch (error) {
      addNotice({ tone: "error", title: "Could not start sign-in", description: textFromError(error) })
    }
  }, [addNotice, rpc])

  const readMcpResource = React.useCallback(
    (server: string, uri: string) =>
      rpc("mcpServer/resource/read", {
        threadId: threadIdRef.current,
        server,
        uri,
      }),
    [rpc],
  )

  const queueMcpAppRequest = React.useCallback(
    (method: string, params: JsonObject) =>
      new Promise<any>((resolve, reject) => {
        const id = `mcp-app-${crypto.randomUUID()}`
        localRequestRef.current.set(id, { resolve, reject })
        setState((current) => ({
          ...current,
          requests: [...current.requests, { id, method, params }],
        }))
      }),
    [],
  )

  const requestMcpAppTool = React.useCallback(
    (server: string, tool: string, args: JsonObject = {}, meta?: JsonObject) =>
      queueMcpAppRequest("mcpApp/tool/requestApproval", {
        server,
        tool,
        arguments: args,
        _meta: meta,
      }),
    [queueMcpAppRequest],
  )

  const requestMcpAppOpenLink = React.useCallback(
    (appName: string, url: string) =>
      queueMcpAppRequest("mcpApp/openLink/requestApproval", { appName, url }),
    [queueMcpAppRequest],
  )

  const dismissNotice = React.useCallback((id: string) => {
    setState((current) => ({
      ...current,
      notices: current.notices.filter((notice) => notice.id !== id),
    }))
  }, [])

  return {
    state,
    send,
    interrupt,
    answerRequest,
    rejectRequest,
    login,
    dismissNotice,
    readMcpResource,
    requestMcpAppTool,
    requestMcpAppOpenLink,
  }
}
