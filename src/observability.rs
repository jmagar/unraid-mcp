use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::{Duration, Instant};

/// Shared atomic counters for observability. Wrap in `Arc` so all `AppState`
/// clones share the same counters.
#[derive(Debug, Default)]
pub struct Counters {
    pub requests_total: AtomicU64,
    pub errors_total: AtomicU64,
    pub upstream_calls: AtomicU64,
    pub upstream_errors: AtomicU64,
}

impl Counters {
    pub fn new() -> Arc<Self> {
        Arc::new(Self::default())
    }

    pub fn inc_requests(&self) {
        self.requests_total.fetch_add(1, Ordering::Relaxed);
    }

    pub fn inc_errors(&self) {
        self.errors_total.fetch_add(1, Ordering::Relaxed);
    }

    pub fn inc_upstream(&self) {
        self.upstream_calls.fetch_add(1, Ordering::Relaxed);
    }

    pub fn inc_upstream_err(&self) {
        self.upstream_errors.fetch_add(1, Ordering::Relaxed);
    }

    pub fn snapshot(&self) -> CounterSnapshot {
        CounterSnapshot {
            requests_total: self.requests_total.load(Ordering::Relaxed),
            errors_total: self.errors_total.load(Ordering::Relaxed),
            upstream_calls: self.upstream_calls.load(Ordering::Relaxed),
            upstream_errors: self.upstream_errors.load(Ordering::Relaxed),
        }
    }
}

#[derive(Debug, serde::Serialize)]
pub struct CounterSnapshot {
    pub requests_total: u64,
    pub errors_total: u64,
    pub upstream_calls: u64,
    pub upstream_errors: u64,
}

/// Result of a lightweight upstream health probe.
#[derive(Debug, serde::Serialize)]
pub struct UpstreamHealth {
    pub reachable: bool,
    pub latency_ms: Option<u64>,
    pub error: Option<String>,
}

impl UpstreamHealth {
    pub fn ok(latency: Duration) -> Self {
        Self {
            reachable: true,
            latency_ms: Some(latency.as_millis() as u64),
            error: None,
        }
    }

    pub fn down(err: impl std::fmt::Display) -> Self {
        Self {
            reachable: false,
            latency_ms: None,
            error: Some(err.to_string()),
        }
    }
}

/// Probe upstream with a 1-second timeout via a simple info query.
pub async fn probe_upstream(client: &reqwest::Client, url: &str, api_key: &str) -> UpstreamHealth {
    let started = Instant::now();
    let res = client
        .post(url)
        .header("x-api-key", api_key)
        .header("Content-Type", "application/json")
        .json(&serde_json::json!({ "query": "query { info { time } }" }))
        .timeout(Duration::from_secs(1))
        .send()
        .await;
    match res {
        Ok(r) if r.status().is_success() => UpstreamHealth::ok(started.elapsed()),
        Ok(r) => UpstreamHealth::down(format!("HTTP {}", r.status())),
        Err(e) => UpstreamHealth::down(e),
    }
}
