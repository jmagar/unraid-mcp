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
}
