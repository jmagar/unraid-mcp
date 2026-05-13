use std::time::Duration;

use anyhow::{anyhow, Context, Result};
use reqwest::Client;
use serde_json::{json, Value};

use crate::config::UnraidConfig;

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
        let client = reqwest::ClientBuilder::new()
            .danger_accept_invalid_certs(cfg.skip_tls_verify)
            .build()
            .context("failed to build HTTP client")?;
        Ok(Self {
            client,
            url: cfg.api_url.clone(),
            api_key: cfg.api_key.clone(),
        })
    }

    async fn query(&self, gql: &str) -> Result<Value> {
        let span = tracing::info_span!("graphql.query", url = %self.url);
        let _guard = span.enter();

        let resp = self
            .client
            .post(&self.url)
            .header("x-api-key", &self.api_key)
            .header("Content-Type", "application/json")
            .json(&json!({ "query": gql }))
            .timeout(Duration::from_secs(30))
            .send()
            .await
            .context("GraphQL request failed — is UNRAID_API_URL reachable?")?;

        let status = resp.status();
        let body: Value = resp
            .json()
            .await
            .context("failed to parse GraphQL response — unexpected non-JSON from upstream")?;

        if !status.is_success() {
            anyhow::bail!("GraphQL HTTP {status}: {body}");
        }
        if let Some(errors) = body.get("errors") {
            anyhow::bail!("GraphQL errors: {errors}");
        }
        let data = body
            .get("data")
            .cloned()
            .ok_or_else(|| anyhow!("GraphQL response missing 'data' field"))?;
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
        let tail_val = tail.unwrap_or(100);
        let q = format!(
            r#"query {{
  docker {{
    logs(id: "{container_id}", tail: {tail_val}) {{
      logLineUrl
      lines
    }}
  }}
}}"#
        );
        self.query(&q).await
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
        let lines_arg = lines.map(|n| format!(", lines: {n}")).unwrap_or_default();
        let start_arg = start_line
            .map(|n| format!(", startLine: {n}"))
            .unwrap_or_default();
        let q = format!(
            r#"query {{ logFile(path: "{path}"{lines_arg}{start_arg}) {{ path content totalLines startLine }} }}"#
        );
        self.query(&q).await
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
