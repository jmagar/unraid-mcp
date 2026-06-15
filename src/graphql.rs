use std::time::Duration;

use anyhow::{Context, Result};
use reqwest::Client;
use serde_json::{json, Value};
use thiserror::Error;

use crate::config::UnraidConfig;

/// Typed classification of a failure talking to the upstream Unraid GraphQL API.
///
/// This is the *routing* contract: the dispatch layer downcasts an [`anyhow::Error`]
/// to this enum to decide how to surface the failure to the MCP caller, instead of
/// matching on message prose. Each variant carries only a category-level message —
/// raw upstream bodies / GraphQL `errors` are logged server-side, never embedded
/// here (see `query_with_vars`), so they cannot leak to the caller or aid schema
/// probing.
#[derive(Debug, Error)]
pub enum UpstreamError {
    /// Could not reach the upstream (connection refused, DNS, TLS handshake, timeout).
    #[error("{0}")]
    Unreachable(String),
    /// Upstream rejected our credentials (HTTP 401/403).
    #[error("{0}")]
    Auth(String),
    /// Any other upstream-side failure (5xx, GraphQL errors, malformed response).
    #[error("{0}")]
    Other(String),
}

#[derive(Clone)]
pub struct UnraidClient {
    client: Client,
    url: String,
    api_key: String,
}

impl UnraidClient {
    pub fn new(cfg: &UnraidConfig) -> Result<Self> {
        if cfg.api_url.is_empty() {
            anyhow::bail!("UNRAID_API_URL is not set");
        }
        if cfg.api_key.is_empty() {
            anyhow::bail!("UNRAID_API_KEY is not set");
        }
        if cfg.skip_tls_verify {
            tracing::warn!(
                "UNRAID_API_SKIP_TLS_VERIFY is enabled: TLS certificate verification is DISABLED. \
                 The API key is sent to an unverified endpoint and is exposed to on-path (MITM) \
                 attackers. Only use this for self-signed certificates on a trusted network."
            );
        }
        let client = reqwest::ClientBuilder::new()
            .danger_accept_invalid_certs(cfg.skip_tls_verify)
            .connect_timeout(Duration::from_secs(5))
            .build()
            .context("failed to build HTTP client")?;
        Ok(Self {
            client,
            url: cfg.api_url.clone(),
            api_key: cfg.api_key.clone(),
        })
    }

    async fn query(&self, gql: &str) -> Result<Value> {
        self.query_with_vars(gql, Value::Null).await
    }

    /// Same as [`query`], but sends GraphQL `variables` alongside the query so
    /// caller-controlled values never have to be interpolated into the query text.
    async fn query_with_vars(&self, gql: &str, variables: Value) -> Result<Value> {
        let span = tracing::info_span!("graphql.query", url = %self.url);
        let _guard = span.enter();

        let resp = match self
            .client
            .post(&self.url)
            .header("x-api-key", &self.api_key)
            .header("Content-Type", "application/json")
            .json(&json!({ "query": gql, "variables": variables }))
            .timeout(Duration::from_secs(30))
            .send()
            .await
        {
            Ok(resp) => resp,
            Err(e) => {
                // Transport-level failure: connection refused, DNS, TLS, timeout.
                // The reqwest error text can carry OS-locale-specific wording, so it
                // is logged server-side; the caller gets a stable category message.
                tracing::warn!(error = %e, "GraphQL request failed at the transport layer");
                let category = if e.is_connect() || e.is_timeout() {
                    "upstream unreachable — is UNRAID_API_URL reachable?"
                } else {
                    "upstream request failed before a response was received"
                };
                return Err(UpstreamError::Unreachable(category.to_string()).into());
            }
        };

        let status = resp.status();

        if status == reqwest::StatusCode::UNAUTHORIZED
            || status == reqwest::StatusCode::FORBIDDEN
        {
            // Read the body only to log it; never return it to the caller.
            let body = resp.text().await.unwrap_or_default();
            tracing::warn!(status = %status, body = %body, "upstream rejected the request (auth)");
            return Err(UpstreamError::Auth("upstream rejected the request — check that UNRAID_API_KEY is correct and has not expired".to_string()).into());
        }

        if !status.is_success() {
            let body = resp.text().await.unwrap_or_default();
            tracing::error!(status = %status, body = %body, "upstream returned a non-success HTTP status");
            return Err(
                UpstreamError::Other(format!("upstream returned HTTP {status}")).into(),
            );
        }

        let body: Value = match resp.json().await {
            Ok(body) => body,
            Err(e) => {
                tracing::error!(error = %e, "failed to parse GraphQL response as JSON");
                return Err(UpstreamError::Other(
                    "upstream returned an unexpected non-JSON response".to_string(),
                )
                .into());
            }
        };

        if let Some(errors) = body.get("errors") {
            // Log the full GraphQL `errors` array server-side; the caller only learns
            // that a GraphQL-level error occurred (no field names / messages leaked).
            tracing::error!(errors = %errors, "upstream returned GraphQL errors");
            return Err(UpstreamError::Other(
                "upstream GraphQL error — see server logs for details".to_string(),
            )
            .into());
        }

        let data = body.get("data").cloned().ok_or_else(|| {
            tracing::error!(body = %body, "GraphQL response missing 'data' field");
            UpstreamError::Other("upstream GraphQL response missing 'data' field".to_string())
        })?;
        tracing::debug!(status = %status, "GraphQL query ok");
        Ok(data)
    }

    /// Expose the HTTP client and URL for the health probe.
    pub fn raw_client(&self) -> (&Client, &str, &str) {
        (&self.client, &self.url, &self.api_key)
    }

    // ── queries ───────────────────────────────────────────────────────────────

    pub async fn array(&self) -> Result<Value> {
        self.query(
            r#"query {
  array {
    state
    capacity {
      kilobytes { free used total }
      disks { free used total }
    }
    parityCheckStatus { status running progress speed errors correcting paused }
    parities { id name device size status temp numErrors type isSpinning rotational }
    disks {
      id name device size status temp numErrors numReads numWrites
      fsSize fsFree fsUsed type color isSpinning rotational fsType comment
    }
    caches {
      id name device size status temp numErrors
      fsSize fsFree fsUsed type color isSpinning rotational fsType
    }
  }
}"#,
        )
        .await
    }

    pub async fn disks(&self) -> Result<Value> {
        self.query(
            r#"query {
  disks {
    id device type name vendor size serialNum
    interfaceType smartStatus temperature isSpinning
    partitions { name fsType size }
  }
}"#,
        )
        .await
    }

    pub async fn docker(&self) -> Result<Value> {
        self.query(
            r#"query {
  docker {
    containers {
      id names image state status autoStart autoStartOrder
      ports { privatePort publicPort type ip }
      webUiUrl iconUrl isOrphaned isUpdateAvailable
    }
  }
}"#,
        )
        .await
    }

    pub async fn docker_logs(&self, container_id: &str, tail: Option<i64>) -> Result<Value> {
        let gql = r#"query($id: PrefixedID!, $tail: Int) {
  docker {
    logs(id: $id, tail: $tail) {
      logLineUrl
      lines
    }
  }
}"#;
        self.query_with_vars(
            gql,
            json!({ "id": container_id, "tail": tail.unwrap_or(100) }),
        )
        .await
    }

    pub async fn vms(&self) -> Result<Value> {
        self.query(
            r#"query {
  vms {
    domains { id name state }
  }
}"#,
        )
        .await
    }

    pub async fn server(&self) -> Result<Value> {
        self.query(
            r#"query {
  server { id name comment status wanip lanip localurl remoteurl guid }
}"#,
        )
        .await
    }

    pub async fn info(&self) -> Result<Value> {
        self.query(
            r#"query {
  info {
    time
    os { platform distro release kernel arch hostname fqdn uptime }
    cpu { brand manufacturer cores threads speed speedmax socket }
    memory { layout { size type clockSpeed } }
    versions { core { unraid kernel } }
  }
}"#,
        )
        .await
    }

    pub async fn shares(&self) -> Result<Value> {
        self.query(
            r#"query {
  shares {
    id name free used size cache comment allocator luksStatus
  }
}"#,
        )
        .await
    }

    pub async fn notifications(&self) -> Result<Value> {
        self.query(
            r#"query {
  notifications {
    overview { unread { warning alert info total } archive { warning alert info total } }
    warningsAndAlerts { id title subject description importance type timestamp }
  }
}"#,
        )
        .await
    }

    pub async fn log_files(&self) -> Result<Value> {
        self.query(r#"query { logFiles { name path size modifiedAt } }"#)
            .await
    }

    pub async fn log_file(
        &self,
        path: &str,
        lines: Option<i64>,
        start_line: Option<i64>,
    ) -> Result<Value> {
        let gql = r#"query($path: String!, $lines: Int, $startLine: Int) {
  logFile(path: $path, lines: $lines, startLine: $startLine) {
    path content totalLines startLine
  }
}"#;
        self.query_with_vars(
            gql,
            json!({ "path": path, "lines": lines, "startLine": start_line }),
        )
        .await
    }

    pub async fn services(&self) -> Result<Value> {
        self.query(r#"query { services { id name online version uptime { timestamp } } }"#)
            .await
    }

    pub async fn network(&self) -> Result<Value> {
        self.query(r#"query { network { id accessUrls { type name ipv4 ipv6 } } }"#)
            .await
    }

    pub async fn ups(&self) -> Result<Value> {
        self.query(
            r#"query {
  upsDevices {
    id name model status
    battery { chargeLevel estimatedRuntime health }
    power { inputVoltage outputVoltage loadPercent }
  }
}"#,
        )
        .await
    }

    pub async fn ups_config(&self) -> Result<Value> {
        self.query(
            r#"query {
  upsConfiguration {
    service upsCable upsType device batteryLevel minutes timeout
    killUps nisIp netServer upsName modelName
  }
}"#,
        )
        .await
    }

    pub async fn metrics(&self) -> Result<Value> {
        self.query(
            r#"query {
  metrics {
    cpu { percentTotal cpus { percentTotal percentUser percentSystem percentIdle } }
    memory {
      total used free available percentTotal
      swapTotal swapUsed swapFree percentSwapTotal
    }
    temperature {
      sensors { id name type location current { value unit } warning critical }
      summary { average warningCount criticalCount }
    }
  }
}"#,
        )
        .await
    }

    pub async fn plugins(&self) -> Result<Value> {
        self.query(r#"query { plugins { name version hasApiModule hasCliModule } }"#)
            .await
    }

    pub async fn parity_history(&self) -> Result<Value> {
        self.query(
            r#"query {
  parityHistory { date duration speed status errors progress correcting paused running }
}"#,
        )
        .await
    }

    pub async fn vars(&self) -> Result<Value> {
        self.query(
            r#"query {
  vars {
    version name timeZone comment sysModel
    useSsl port portssl useSsh portssh useTelnet porttelnet
    startArray spindownDelay shareSmbEnabled shareNfsEnabled shareAfpEnabled
    configValid configError regState regTo
    deviceCount flashGuid flashProduct flashVendor
    sbName sbVersion sbUpdated sbState
  }
}"#,
        )
        .await
    }

    pub async fn registration(&self) -> Result<Value> {
        self.query(r#"query { registration { id type state expiration updateExpiration } }"#)
            .await
    }

    pub async fn flash(&self) -> Result<Value> {
        // guid is non-nullable in schema but can be null at runtime — omit it
        self.query(r#"query { flash { id vendor product } }"#).await
    }

    pub async fn rclone(&self) -> Result<Value> {
        self.query(r#"query { rclone { remotes { name type } drives { name } } }"#)
            .await
    }

    pub async fn remote_access(&self) -> Result<Value> {
        self.query(r#"query { remoteAccess { accessType forwardType port } }"#)
            .await
    }

    pub async fn connect(&self) -> Result<Value> {
        self.query(
            r#"query {
  connect {
    id
    dynamicRemoteAccess { enabledType runningType error }
    settings { values { accessType forwardType port } }
  }
}"#,
        )
        .await
    }
}
