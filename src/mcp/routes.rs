use std::sync::Arc;
use std::time::Instant;

use axum::{
    extract::State,
    http::{HeaderValue, Method, StatusCode},
    response::{IntoResponse, Json},
    routing::get,
    Router,
};
use serde_json::json;
use tower_http::{
    cors::{Any, CorsLayer},
    limit::RequestBodyLimitLayer,
};

use crate::observability::probe_upstream;

use super::host_filter::allowed_origins;
use super::rmcp_server::{streamable_http_config, streamable_http_service};
use super::{build_auth_layer, AppState, AuthPolicy};

const MCP_BODY_LIMIT_BYTES: usize = 65_536;

pub fn router(state: AppState) -> Router {
    let rmcp_config = streamable_http_config(&state.config);
    let mcp_service =
        Router::new().nest_service("/mcp", streamable_http_service(state.clone(), rmcp_config));

    let resource_url = match &state.auth_policy {
        AuthPolicy::Mounted { .. } => state
            .config
            .auth
            .public_url
            .as_deref()
            .map(|u| Arc::<str>::from(format!("{}/mcp", u.trim_end_matches('/')))),
        AuthPolicy::LoopbackDev => None,
    };

    let authenticated = if let Some(layer) = build_auth_layer(
        &state.auth_policy,
        state.config.api_token.as_deref().map(Arc::<str>::from),
        resource_url,
    ) {
        mcp_service.layer(layer)
    } else {
        mcp_service
    };

    let oauth_router: Option<Router> = if let AuthPolicy::Mounted {
        auth_state: Some(ref state_arc),
    } = state.auth_policy
    {
        let auth_state = state_arc.as_ref().clone();
        let path_based_discovery = Router::new()
            .route(
                "/mcp/.well-known/oauth-authorization-server",
                get(lab_auth::metadata::authorization_server_metadata),
            )
            .route(
                "/mcp/.well-known/openid-configuration",
                get(lab_auth::metadata::authorization_server_metadata),
            )
            .route(
                "/mcp/.well-known/oauth-protected-resource",
                get(lab_auth::metadata::protected_resource_metadata),
            )
            .with_state(auth_state.clone());
        Some(lab_auth::routes::router(auth_state).merge(path_based_discovery))
    } else {
        None
    };

    let base: Router<()> = Router::new()
        .merge(authenticated)
        .route("/health", get(health))
        .route("/status", get(status))
        .with_state(state.clone());

    let combined = match oauth_router {
        Some(oauth) => base.merge(oauth),
        None => base,
    };

    combined
        .fallback(|| async { (StatusCode::NOT_FOUND, Json(json!({"error": "not_found"}))) })
        .layer(RequestBodyLimitLayer::new(MCP_BODY_LIMIT_BYTES))
        .layer(cors_layer(&state.config))
}

fn cors_layer(config: &crate::config::McpConfig) -> CorsLayer {
    let origins: Vec<HeaderValue> = allowed_origins(config)
        .into_iter()
        .filter_map(|o| o.parse::<HeaderValue>().ok())
        .collect();
    CorsLayer::new()
        .allow_origin(origins)
        .allow_methods([Method::POST, Method::GET])
        .allow_headers(Any)
}

/// GET /health — always returns 200; status is "ok" or "degraded".
/// No authentication required. Performs a lightweight upstream probe (1s timeout).
async fn health(State(state): State<AppState>) -> impl IntoResponse {
    let started = Instant::now();
    let (client, url, key) = state.service.raw_client_parts();
    let upstream = probe_upstream(client, url, key).await;
    let status_str = if upstream.reachable { "ok" } else { "degraded" };
    let latency = started.elapsed().as_millis();
    Json(json!({
        "status": status_str,
        "version": env!("CARGO_PKG_VERSION"),
        "upstream": upstream,
        "latency_ms": latency,
    }))
}

/// GET /status — full runtime state. Requires valid auth when auth is mounted.
async fn status(State(state): State<AppState>) -> impl IntoResponse {
    let snap = state.counters.snapshot();
    let (_, url, _) = state.service.raw_client_parts();
    Json(json!({
        "status": "ok",
        "server": {
            "version": env!("CARGO_PKG_VERSION"),
            "pid": std::process::id(),
        },
        "config": {
            "host": state.config.host,
            "port": state.config.port,
            "auth_mode": format!("{:?}", state.auth_policy),
            "upstream_url": url,
        },
        "counters": snap,
    }))
}
