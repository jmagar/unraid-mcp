import * as React from "react"
import {
  ArrowLeft,
  MessageSquare,
  PanelRightClose,
  PanelRightOpen,
  SlidersHorizontal,
} from "lucide-react"
import { CodeBlock } from "@/components/aurora/code-block"
import { Conversation } from "@/components/aurora/ai/conversation"
import {
  PermissionChip,
  type ToolPermission,
} from "@/components/aurora/permissions-dropdown"
import {
  PromptInput,
  type Attachment,
} from "@/components/aurora/prompt-input"
import {
  Sheet,
  SheetBody,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/aurora/sheet"
import { Banner } from "@/components/ui/aurora/banner"
import { Button } from "@/components/ui/aurora/button"
import { StatusIndicator } from "@/components/ui/aurora/status-indicator"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/aurora/tooltip"
import { useCodexAppServer } from "@/protocol"
import {
  ContextRenderer,
  PlanRenderer,
  RequestRenderer,
  SessionContextRenderer,
  TimelineRenderer,
} from "@/renderers"

const PERMISSIONS: ToolPermission[] = [
  {
    id: "commands",
    name: "Commands",
    description: "Command execution requires approval when Codex requests it.",
    state: "ask",
  },
  {
    id: "files",
    name: "File Changes",
    description: "File changes require approval when Codex requests it.",
    state: "ask",
  },
  {
    id: "mcp",
    name: "MCP Writes",
    description: "MCP servers can elicit confirmation before write actions.",
    state: "ask",
  },
]

function connectionTone(status: string) {
  if (status === "connected" || status === "working") return "online" as const
  if (status === "connecting") return "syncing" as const
  if (status === "error") return "error" as const
  return "offline" as const
}

export function App() {
  const {
    state,
    send,
    interrupt,
    answerRequest,
    rejectRequest,
    login,
    dismissNotice,
  } = useCodexAppServer()
  const [open, setOpen] = React.useState(false)
  const [docked, setDocked] = React.useState(
    () => localStorage.getItem("unraid-codex.docked") !== "false",
  )
  const [dockWidth, setDockWidth] = React.useState(() => {
    const stored = localStorage.getItem("unraid-codex.dock-width")
    const saved = stored == null ? Number.NaN : Number(stored)
    return Number.isFinite(saved) ? Math.min(900, Math.max(360, saved)) : 520
  })
  const [viewportWidth, setViewportWidth] = React.useState(() => window.innerWidth)
  const [inspectorOpen, setInspectorOpen] = React.useState(false)
  const [prompt, setPrompt] = React.useState("")
  const [attachments, setAttachments] = React.useState<Attachment[]>([])
  const scrollRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    const onResize = () => setViewportWidth(window.innerWidth)
    window.addEventListener("resize", onResize)
    return () => window.removeEventListener("resize", onResize)
  }, [])

  React.useEffect(() => {
    const node = scrollRef.current
    if (!node) return
    node.scrollTo({ top: node.scrollHeight, behavior: "smooth" })
  }, [state.items, state.requests, state.plan, state.diff, state.notices])

  React.useEffect(() => {
    if (state.requests.length) setOpen(true)
  }, [state.requests.length])

  React.useEffect(() => {
    const root = document.documentElement
    const active = open && docked && window.matchMedia("(min-width: 900px)").matches
    const width = Math.min(dockWidth, Math.max(360, viewportWidth - 420))
    const resizedElements = [
      document.body,
      document.querySelector<HTMLElement>("#header"),
      document.querySelector<HTMLElement>("#menu"),
      document.querySelector<HTMLElement>("#displaybox"),
      document.querySelector<HTMLElement>("#footer"),
    ].filter((element): element is HTMLElement => Boolean(element))
    const previous = resizedElements.map((element) => ({
      element,
      width: element.style.getPropertyValue("width"),
      priority: element.style.getPropertyPriority("width"),
      maxWidth: element.style.getPropertyValue("max-width"),
      maxWidthPriority: element.style.getPropertyPriority("max-width"),
    }))
    root.classList.toggle("unraid-codex-docked", active)
    root.style.setProperty("--unraid-codex-dock-width", `${width}px`)
    if (active) {
      document.body.style.setProperty("width", `calc(100vw - ${width}px)`, "important")
      document.body.style.setProperty("max-width", `calc(100vw - ${width}px)`, "important")
      for (const element of resizedElements.slice(1)) {
        const fixedFooter = element.id === "footer"
        element.style.setProperty(
          "width",
          fixedFooter ? `calc(100vw - ${width}px)` : "100%",
          "important",
        )
        element.style.setProperty(
          "max-width",
          fixedFooter ? `calc(100vw - ${width}px)` : "100%",
          "important",
        )
      }
      requestAnimationFrame(() => window.dispatchEvent(new Event("resize")))
    }
    localStorage.setItem("unraid-codex.docked", String(docked))
    localStorage.setItem("unraid-codex.dock-width", String(dockWidth))
    return () => {
      root.classList.remove("unraid-codex-docked")
      for (const entry of previous) {
        if (entry.width) {
          entry.element.style.setProperty("width", entry.width, entry.priority)
        } else {
          entry.element.style.removeProperty("width")
        }
        if (entry.maxWidth) {
          entry.element.style.setProperty("max-width", entry.maxWidth, entry.maxWidthPriority)
        } else {
          entry.element.style.removeProperty("max-width")
        }
      }
      requestAnimationFrame(() => window.dispatchEvent(new Event("resize")))
    }
  }, [dockWidth, docked, open, viewportWidth])

  const beginResize = React.useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    event.preventDefault()
    event.currentTarget.setPointerCapture(event.pointerId)
    document.body.style.userSelect = "none"
  }, [])

  const resizeDock = React.useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    if (!event.currentTarget.hasPointerCapture(event.pointerId)) return
    const maximum = Math.min(900, window.innerWidth - 420)
    setDockWidth(Math.min(maximum, Math.max(360, window.innerWidth - event.clientX)))
  }, [])

  const finishResize = React.useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId)
    }
    document.body.style.removeProperty("user-select")
  }, [])

  const submit = React.useCallback(
    (value: string, submittedAttachments: Attachment[]) => {
      if (!value.trim()) return
      void send(value.trim(), submittedAttachments)
      setPrompt("")
      setAttachments([])
    },
    [send],
  )

  return (
    <TooltipProvider delayDuration={250}>
      <Sheet open={open} onOpenChange={setOpen} modal={false}>
        {!open ? (
          <Tooltip>
            <TooltipTrigger asChild>
              <SheetTrigger asChild>
                <Button
                  variant="neutral"
                  size="icon"
                  className="uc-launcher"
                  aria-label="Open Codex"
                >
                  <MessageSquare size={22} strokeWidth={1.65} aria-hidden />
                </Button>
              </SheetTrigger>
            </TooltipTrigger>
            <TooltipContent side="left">Open Codex</TooltipContent>
          </Tooltip>
        ) : null}

        <SheetContent
          side="right"
          className="uc-sheet"
          style={{ "--uc-dock-width": `${dockWidth}px` } as React.CSSProperties}
        >
          {docked ? (
            <div
              className="uc-resize-handle"
              role="separator"
              aria-label="Resize Codex panel"
              aria-orientation="vertical"
              aria-valuemin={360}
              aria-valuemax={900}
              aria-valuenow={dockWidth}
              tabIndex={0}
              onPointerDown={beginResize}
              onPointerMove={resizeDock}
              onPointerUp={finishResize}
              onPointerCancel={finishResize}
              onDoubleClick={() => setDockWidth(520)}
              onKeyDown={(event) => {
                if (event.key === "ArrowLeft") setDockWidth((width) => Math.min(900, width + 20))
                if (event.key === "ArrowRight") setDockWidth((width) => Math.max(360, width - 20))
                if (event.key === "Home") setDockWidth(360)
                if (event.key === "End") setDockWidth(900)
              }}
            />
          ) : null}
          <SheetHeader className="uc-header">
            <div className="uc-brand">
              <span className="uc-mark">
                <MessageSquare size={18} strokeWidth={1.65} aria-hidden />
              </span>
              <div className="uc-brand-copy">
                <SheetTitle className="aurora-text-section">Codex</SheetTitle>
                <SheetDescription className="aurora-text-meta">
                  Unraid
                </SheetDescription>
              </div>
            </div>
            <div className="uc-header-actions">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="uc-dock-toggle"
                    aria-label={inspectorOpen ? "Back to conversation" : "Inspect session"}
                    onClick={() => setInspectorOpen((current) => !current)}
                  >
                    {inspectorOpen ? (
                      <ArrowLeft size={17} aria-hidden />
                    ) : (
                      <SlidersHorizontal size={17} aria-hidden />
                    )}
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                  {inspectorOpen ? "Back to conversation" : "Inspect session"}
                </TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="uc-dock-toggle"
                    aria-label={docked ? "Undock Codex" : "Dock Codex to the right"}
                    onClick={() => setDocked((current) => !current)}
                  >
                    {docked ? (
                      <PanelRightClose size={17} aria-hidden />
                    ) : (
                      <PanelRightOpen size={17} aria-hidden />
                    )}
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                  {docked ? "Use as overlay" : "Dock to the right"}
                </TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className="uc-connection">
                    <StatusIndicator
                      tone={connectionTone(state.status)}
                      label={state.statusText}
                      showLabel={false}
                      pulse={state.status === "connecting" || state.status === "working"}
                    />
                  </span>
                </TooltipTrigger>
                <TooltipContent side="bottom">{state.statusText}</TooltipContent>
              </Tooltip>
            </div>
          </SheetHeader>

          <SheetBody className="uc-conversation-shell">
            {inspectorOpen ? (
              <div className="uc-inspector">
                <div className="uc-inspector-heading">
                  <div className="aurora-text-section">Session Inspector</div>
                  <div className="aurora-text-meta">
                    Runtime inventory and policy for the active Codex session.
                  </div>
                </div>
                <SessionContextRenderer state={state} />
              </div>
            ) : (
              <Conversation
                ref={scrollRef}
                className="uc-conversation"
                maxHeight={Number.MAX_SAFE_INTEGER}
                style={{
                  height: "100%",
                  maxHeight: "none",
                  border: 0,
                  borderRadius: 0,
                  boxShadow: "none",
                }}
              >
            {!state.authenticated ? (
              <Banner
                variant="info"
                title="Sign in to Codex"
                description="Use your ChatGPT account in this isolated container."
                action={
                  <Button variant="aurora" size="sm" onClick={() => void login()}>
                    Sign In
                  </Button>
                }
              />
            ) : null}

            {state.deviceLogin ? (
              <div className="uc-device-login">
                <div className="aurora-text-label">Device Code</div>
                <div className="uc-device-code">{state.deviceLogin.userCode}</div>
                <Button
                  variant="aurora"
                  size="sm"
                  onClick={() =>
                    window.open(state.deviceLogin?.verificationUrl, "_blank", "noopener")
                  }
                >
                  Open Sign-In Page
                </Button>
              </div>
            ) : null}

            {state.notices.map((notice) => (
              <Banner
                key={notice.id}
                variant={notice.tone}
                title={notice.title}
                description={notice.description}
                onDismiss={() => dismissNotice(notice.id)}
              />
            ))}

            {!state.items.length &&
            !state.requests.length &&
            !state.plan &&
            !state.diff ? (
              <div className="uc-empty">
                <span className="uc-empty-mark">
                  <MessageSquare size={22} strokeWidth={1.65} aria-hidden />
                </span>
                <div className="aurora-text-section">Codex is ready.</div>
                <div className="aurora-text-body uc-muted">
                  Ask about the server, inspect a workspace, or start a development task.
                </div>
              </div>
            ) : null}

            <TimelineRenderer entries={state.items} />

            {state.plan ? (
              <PlanRenderer plan={state.plan} streaming={Boolean(state.activeTurnId)} />
            ) : null}

            {state.diff ? (
              <CodeBlock
                code={state.diff}
                language="diff"
                filename="Current Turn Diff"
                showLineNumbers
                variant="diff"
              />
            ) : null}

            {state.requests.map((request) => (
              <RequestRenderer
                key={String(request.id)}
                request={request}
                answer={(result) => answerRequest(request, result)}
                reject={(message) => rejectRequest(request, message)}
              />
            ))}
              </Conversation>
            )}
          </SheetBody>

          {!inspectorOpen ? <SheetFooter className="uc-footer">
            {state.tokenUsage ? <ContextRenderer tokenUsage={state.tokenUsage} /> : null}
            <PromptInput
              value={prompt}
              onChange={setPrompt}
              onSubmit={submit}
              onStop={() => void interrupt()}
              attachments={attachments}
              onAddAttachment={(attachment) =>
                setAttachments((current) => [...current, attachment])
              }
              onRemoveAttachment={(id) =>
                setAttachments((current) =>
                  current.filter((attachment) => attachment.id !== id),
                )
              }
              model={state.settings?.model ?? state.config?.model ?? "codex"}
              models={
                state.models.length
                  ? state.models
                      .filter((model) => !model.hidden)
                      .map((model) => ({
                        id: model.model ?? model.id,
                        label: model.displayName ?? model.model ?? model.id,
                      }))
                  : [{ id: "codex", label: "Codex" }]
              }
              isStreaming={Boolean(state.activeTurnId)}
              placeholder="Ask Codex…"
              toolbarStart={
                <Tooltip>
                  <TooltipTrigger asChild>
                    <span>
                      <PermissionChip tools={PERMISSIONS} iconOnly />
                    </span>
                  </TooltipTrigger>
                  <TooltipContent side="top">
                    Write actions ask for approval
                  </TooltipContent>
                </Tooltip>
              }
              slashCommands={[
                { id: "review", label: "/review", description: "Review workspace changes" },
                { id: "plan", label: "/plan", description: "Create an implementation plan" },
                { id: "status", label: "/status", description: "Inspect the current environment" },
              ]}
              mentionItems={[
                { id: "workspace", label: "/workspace", kind: "folder" },
                { id: "instructions", label: "AGENTS.md", kind: "file" },
              ]}
            />
          </SheetFooter> : null}
        </SheetContent>
      </Sheet>
    </TooltipProvider>
  )
}
