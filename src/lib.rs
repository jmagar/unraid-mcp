pub mod app;
pub mod config;
pub mod graphql;
pub mod logging;
pub mod mcp;
pub mod observability;
pub mod token_limit;

#[cfg(any(test, feature = "test-support"))]
#[doc(hidden)]
pub mod testing {
    use std::sync::Arc;

    use crate::{
        app::UnraidService,
        config::{McpConfig, UnraidConfig},
        graphql::UnraidClient,
        mcp::{AppState, AuthPolicy},
        observability::Counters,
    };

    fn stub_service() -> UnraidService {
        let client = UnraidClient::new(&UnraidConfig {
            api_url: "http://localhost:1/graphql".into(),
            api_key: "test".into(),
            skip_tls_verify: true,
        })
        .expect("stub client should build");
        UnraidService::new(client)
    }

    pub fn loopback_state() -> AppState {
        AppState {
            config: McpConfig::default(),
            auth_policy: AuthPolicy::LoopbackDev,
            service: stub_service(),
            counters: Counters::new(),
        }
    }

    pub fn bearer_state(token: &str) -> AppState {
        AppState {
            config: McpConfig {
                api_token: Some(token.to_string()),
                ..McpConfig::default()
            },
            auth_policy: AuthPolicy::Mounted { auth_state: None },
            service: stub_service(),
            counters: Counters::new(),
        }
    }

    pub async fn oauth_state(data_dir: &std::path::Path) -> AppState {
        let (state, _) = oauth_state_with_auth_state(data_dir).await;
        state
    }

    pub async fn oauth_state_with_auth_state(
        data_dir: &std::path::Path,
    ) -> (AppState, Arc<lab_auth::state::AuthState>) {
        let auth_state = Arc::new(build_auth_state(data_dir).await);
        let state = AppState {
            config: McpConfig {
                auth: crate::config::AuthConfig {
                    public_url: Some("https://unraid.example.com".to_string()),
                    ..Default::default()
                },
                ..McpConfig::default()
            },
            auth_policy: AuthPolicy::Mounted {
                auth_state: Some(auth_state.clone()),
            },
            service: stub_service(),
            counters: Counters::new(),
        };
        (state, auth_state)
    }

    pub async fn build_auth_state(data_dir: &std::path::Path) -> lab_auth::state::AuthState {
        let vars: Vec<(String, String)> = vec![
            ("UNRAID_MCP_AUTH_MODE".into(), "oauth".into()),
            (
                "UNRAID_MCP_PUBLIC_URL".into(),
                "https://unraid.example.com".into(),
            ),
            (
                "UNRAID_MCP_GOOGLE_CLIENT_ID".into(),
                "test-client-id".into(),
            ),
            (
                "UNRAID_MCP_GOOGLE_CLIENT_SECRET".into(),
                "test-client-secret".into(),
            ),
            (
                "UNRAID_MCP_AUTH_ADMIN_EMAIL".into(),
                "admin@example.com".into(),
            ),
            (
                "UNRAID_MCP_AUTH_SQLITE_PATH".into(),
                data_dir.join("auth.db").to_str().unwrap().into(),
            ),
            (
                "UNRAID_MCP_AUTH_KEY_PATH".into(),
                data_dir.join("auth-jwt.pem").to_str().unwrap().into(),
            ),
        ];

        let auth_config = lab_auth::config::AuthConfigBuilder::new()
            .env_prefix("UNRAID_MCP")
            .session_cookie_name("unraid_mcp_session")
            .scopes_supported(vec!["unraid:read".into(), "unraid:admin".into()])
            .default_scope("unraid:read")
            .resource_path("/mcp")
            .build_from_sources(vars)
            .expect("test auth config should build");

        lab_auth::state::AuthState::new(auth_config)
            .await
            .expect("test auth state should init")
    }

    // ── test-support wrappers over internal APIs (for integration tests) ──

    /// Build a loopback `AppState` whose upstream client points at `url`
    /// (e.g. a wiremock mock server), instead of the default `localhost:1` stub.
    pub fn state_with_upstream(url: &str) -> AppState {
        let client = UnraidClient::new(&UnraidConfig {
            api_url: url.to_string(),
            api_key: "test".into(),
            skip_tls_verify: true,
        })
        .expect("stub client should build");
        AppState {
            config: McpConfig::default(),
            auth_policy: AuthPolicy::LoopbackDev,
            service: UnraidService::new(client),
            counters: Counters::new(),
        }
    }

    /// Drive the `unraid` tool dispatch by name + args without the transport layer.
    /// The typed error is flattened to its display string for assertions.
    pub async fn execute_tool(
        state: &AppState,
        name: &str,
        args: serde_json::Value,
    ) -> Result<serde_json::Value, String> {
        crate::mcp::tools::execute_tool(state, name, args)
            .await
            .map_err(|e| e.to_string())
    }

    /// Wrapper over the internal `paginate_array` for unit/integration testing.
    pub fn paginate_array(
        data: serde_json::Value,
        path: &[&str],
        limit: usize,
        offset: usize,
        filter: Option<String>,
    ) -> serde_json::Value {
        crate::mcp::tools::paginate::paginate_array(data, path, limit, offset, filter)
    }

    pub fn string_arg(args: &serde_json::Value, name: &str) -> Option<String> {
        crate::mcp::tools::arg_helpers::string_arg(args, name)
    }

    pub fn i64_arg(args: &serde_json::Value, name: &str) -> anyhow::Result<Option<i64>> {
        crate::mcp::tools::arg_helpers::i64_arg(args, name)
    }

    pub fn usize_arg(args: &serde_json::Value, name: &str) -> anyhow::Result<Option<usize>> {
        crate::mcp::tools::arg_helpers::usize_arg(args, name)
    }

    pub fn allowed_hosts(config: &McpConfig) -> Vec<String> {
        crate::mcp::host_filter::allowed_hosts(config)
    }

    pub fn allowed_origins(config: &McpConfig) -> Vec<String> {
        crate::mcp::host_filter::allowed_origins(config)
    }
}
