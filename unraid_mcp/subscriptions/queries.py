"""GraphQL subscription query strings for snapshot and collect operations."""

SNAPSHOT_ACTIONS = {
    "cpu": """
        subscription { systemMetricsCpu { id percentTotal cpus { percentTotal percentUser percentSystem percentIdle } } }
    """,
    "memory": """
        subscription { systemMetricsMemory { id total used free available active buffcache percentTotal swapTotal swapUsed swapFree percentSwapTotal } }
    """,
    "cpu_telemetry": """
        subscription { systemMetricsCpuTelemetry { id totalPower power temp } }
    """,
    "array_state": """
        subscription { arraySubscription { id state capacity { kilobytes { free used total } } parityCheckStatus { status progress speed errors } } }
    """,
    "parity_progress": """
        subscription { parityHistorySubscription { date status progress speed errors correcting paused running } }
    """,
    "ups_status": """
        subscription { upsUpdates { id name model status battery { chargeLevel estimatedRuntime health } power { inputVoltage outputVoltage loadPercentage } } }
    """,
    "notifications_overview": """
        subscription { notificationsOverview { unread { info warning alert total } archive { info warning alert total } } }
    """,
    "owner": """
        subscription { ownerSubscription { username url avatar } }
    """,
    "server_status": """
        subscription { serversSubscription { id name status guid wanip lanip localurl remoteurl } }
    """,
}

COLLECT_ACTIONS = {
    "notification_feed": """
        subscription { notificationAdded { id title subject description importance type timestamp } }
    """,
    "log_tail": """
        subscription LogTail($path: String!) { logFile(path: $path) { path content totalLines startLine } }
    """,
}
