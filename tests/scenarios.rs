//! Scenario-driven integration tests.
//!
//! Mounts the same mock router used by `examples/mock_unraid.rs` onto a wiremock
//! server, then drives the real MCP dispatch (`execute_tool`) for every action
//! across every scenario. This doubles as the safety net proving
//! `mock::classify_query` routes each *real* query from `graphql.rs` correctly:
//! if a query were misrouted, the action would get the wrong (or an `errors`)
//! payload and the dispatch would fail.

use serde_json::{json, Value};
use unraid_mcp::mock::{Scenario, SCENARIOS};
use unraid_mcp::testing::{execute_tool, state_with_upstream};
use wiremock::{Mock, MockServer, Request, Respond, ResponseTemplate};

/// wiremock responder that classifies each incoming GraphQL query and replies
/// with the active scenario's canned payload — exactly like the standalone server.
struct ScenarioResponder {
    scenario: Scenario,
}

impl Respond for ScenarioResponder {
    fn respond(&self, request: &Request) -> ResponseTemplate {
        let body: Value = serde_json::from_slice(&request.body).unwrap_or(Value::Null);
        let query = body.get("query").and_then(Value::as_str).unwrap_or("");
        ResponseTemplate::new(200).set_body_json(self.scenario.respond(query))
    }
}

async fn mock_server_for(scenario: &str) -> MockServer {
    let server = MockServer::start().await;
    Mock::given(wiremock::matchers::method("POST"))
        .respond_with(ScenarioResponder {
            scenario: Scenario::load(scenario).expect("known scenario"),
        })
        .mount(&server)
        .await;
    server
}

use unraid_mcp::testing::upstream_action_calls as action_calls;

/// Does any string anywhere in the JSON tree contain `needle`?
fn tree_contains(value: &Value, needle: &str) -> bool {
    match value {
        Value::String(s) => s.contains(needle),
        Value::Array(a) => a.iter().any(|v| tree_contains(v, needle)),
        Value::Object(o) => o.values().any(|v| tree_contains(v, needle)),
        _ => false,
    }
}

#[tokio::test]
async fn every_mutation_dispatches() {
    // Mutations are write-scoped but execute_tool runs under LoopbackDev (no auth),
    // so this exercises dispatch + the typed round-trip for the write surface.
    let server = mock_server_for("healthy").await;
    let state = state_with_upstream(&server.uri());
    for (action, args) in unraid_mcp::testing::mutation_action_calls() {
        let result = execute_tool(&state, "unraid", args).await;
        assert!(
            result.is_ok(),
            "mutation `{action}` should dispatch ok, got: {result:?}"
        );
    }
}

#[tokio::test]
async fn every_action_dispatches_in_every_scenario() {
    for scenario in SCENARIOS {
        let server = mock_server_for(scenario).await;
        let state = state_with_upstream(&server.uri());

        for (action, args) in action_calls() {
            let result = execute_tool(&state, "unraid", args).await;
            assert!(
                result.is_ok(),
                "scenario `{scenario}` action `{action}` should dispatch ok, got: {result:?}"
            );
        }
    }
}

#[tokio::test]
async fn degraded_surfaces_disabled_disk() {
    let server = mock_server_for("degraded").await;
    let state = state_with_upstream(&server.uri());

    let array = execute_tool(&state, "unraid", json!({ "action": "array" }))
        .await
        .expect("array ok");
    assert!(
        tree_contains(&array, "DISK_DSBL"),
        "degraded array should report a disabled disk: {array}"
    );

    let notes = execute_tool(&state, "unraid", json!({ "action": "notifications" }))
        .await
        .expect("notifications ok");
    assert!(
        tree_contains(&notes, "Disk disabled"),
        "degraded notifications should include the disk-disabled alert: {notes}"
    );
}

#[tokio::test]
async fn disk_failing_surfaces_smart_failure() {
    let server = mock_server_for("disk-failing").await;
    let state = state_with_upstream(&server.uri());

    // The Unraid `DiskSmartStatus` enum is only {OK, UNKNOWN} — there is no
    // `FAILING` value. A failing disk surfaces as UNKNOWN SMART status plus an
    // ALERT notification, so we assert on both real signals.
    let disks = execute_tool(&state, "unraid", json!({ "action": "disks" }))
        .await
        .expect("disks ok");
    assert!(
        tree_contains(&disks, "UNKNOWN"),
        "disk-failing disks should report a non-OK (UNKNOWN) SMART status: {disks}"
    );

    let notes = execute_tool(&state, "unraid", json!({ "action": "notifications" }))
        .await
        .expect("notifications ok");
    assert!(
        tree_contains(&notes, "FAILING SMART status"),
        "disk-failing should raise a SMART-failure alert notification: {notes}"
    );
}

#[tokio::test]
async fn parity_running_surfaces_in_progress_check() {
    let server = mock_server_for("parity-running").await;
    let state = state_with_upstream(&server.uri());

    let array = execute_tool(&state, "unraid", json!({ "action": "array" }))
        .await
        .expect("array ok");
    assert!(
        tree_contains(&array, "152 MB/s"),
        "parity-running array should report a running check speed: {array}"
    );
}

#[tokio::test]
async fn healthy_inherits_baseline_for_unoverridden_actions() {
    // `info` is never overridden, so it must be identical across scenarios.
    let healthy = mock_server_for("healthy").await;
    let degraded = mock_server_for("degraded").await;

    let h_info = execute_tool(
        &state_with_upstream(&healthy.uri()),
        "unraid",
        json!({ "action": "info" }),
    )
    .await
    .expect("healthy info ok");
    let d_info = execute_tool(
        &state_with_upstream(&degraded.uri()),
        "unraid",
        json!({ "action": "info" }),
    )
    .await
    .expect("degraded info ok");

    assert_eq!(h_info, d_info, "info should be inherited unchanged");
}
