use anyhow::Result;
use serde_json::Value;

use crate::graphql::UnraidClient;

/// Business service layer. All logic lives here.
/// CLI and MCP are thin shims that call into this.
#[derive(Clone)]
pub struct UnraidService {
    client: UnraidClient,
}

impl UnraidService {
    pub fn new(client: UnraidClient) -> Self {
        Self { client }
    }

    /// Expose raw HTTP client fields for health probing (url, api_key).
    pub fn raw_client_parts(&self) -> (&reqwest::Client, &str, &str) {
        self.client.raw_client()
    }

    pub async fn array(&self) -> Result<Value> {
        self.client.array().await
    }

    pub async fn disks(&self) -> Result<Value> {
        self.client.disks().await
    }

    pub async fn docker(&self) -> Result<Value> {
        self.client.docker().await
    }

    pub async fn docker_logs(&self, id: &str, tail: Option<i64>) -> Result<Value> {
        self.client.docker_logs(id, tail).await
    }

    pub async fn vms(&self) -> Result<Value> {
        self.client.vms().await
    }

    pub async fn server(&self) -> Result<Value> {
        self.client.server().await
    }

    pub async fn info(&self) -> Result<Value> {
        self.client.info().await
    }

    pub async fn shares(&self) -> Result<Value> {
        self.client.shares().await
    }

    pub async fn notifications(&self) -> Result<Value> {
        self.client.notifications().await
    }

    pub async fn log_files(&self) -> Result<Value> {
        self.client.log_files().await
    }

    pub async fn log_file(
        &self,
        path: &str,
        lines: Option<i64>,
        start_line: Option<i64>,
    ) -> Result<Value> {
        self.client.log_file(path, lines, start_line).await
    }

    pub async fn services(&self) -> Result<Value> {
        self.client.services().await
    }

    pub async fn network(&self) -> Result<Value> {
        self.client.network().await
    }

    pub async fn ups(&self) -> Result<Value> {
        self.client.ups().await
    }

    pub async fn ups_config(&self) -> Result<Value> {
        self.client.ups_config().await
    }

    pub async fn metrics(&self) -> Result<Value> {
        self.client.metrics().await
    }

    pub async fn plugins(&self) -> Result<Value> {
        self.client.plugins().await
    }

    pub async fn parity_history(&self) -> Result<Value> {
        self.client.parity_history().await
    }

    pub async fn vars(&self) -> Result<Value> {
        self.client.vars().await
    }

    pub async fn registration(&self) -> Result<Value> {
        self.client.registration().await
    }

    pub async fn flash(&self) -> Result<Value> {
        self.client.flash().await
    }

    pub async fn rclone(&self) -> Result<Value> {
        self.client.rclone().await
    }

    pub async fn remote_access(&self) -> Result<Value> {
        self.client.remote_access().await
    }

    pub async fn connect(&self) -> Result<Value> {
        self.client.connect().await
    }
}
