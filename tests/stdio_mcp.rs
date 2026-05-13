use std::process::Stdio;

use rmcp::{
    model::CallToolRequestParams,
    service::ServiceExt,
    transport::{ConfigureCommandExt, TokioChildProcess},
};
use serde_json::json;
use tempfile::TempDir;
use tokio::{io::AsyncReadExt, process::Command};

async fn stdio_client(
    db_path: &std::path::Path,
) -> anyhow::Result<(
    rmcp::service::RunningService<rmcp::RoleClient, ()>,
    Option<tokio::process::ChildStderr>,
)> {
    let binary = env!("CARGO_BIN_EXE_syslog");
    let (transport, stderr) = TokioChildProcess::builder(Command::new(binary).configure(|cmd| {
        cmd.arg("mcp")
            .env("SYSLOG_MCP_DB_PATH", db_path)
            .env("SYSLOG_MCP_RETENTION_DAYS", "0")
            .env("SYSLOG_MCP_MAX_DB_SIZE_MB", "0")
            .env("SYSLOG_MCP_RECOVERY_DB_SIZE_MB", "0")
            .env("SYSLOG_MCP_MIN_FREE_DISK_MB", "0")
            .env("SYSLOG_MCP_RECOVERY_FREE_DISK_MB", "0")
            .env("RUST_LOG", "warn")
            .env_remove("SYSLOG_MCP_TOKEN")
            .env_remove("SYSLOG_MCP_API_TOKEN");
    }))
    .stderr(Stdio::piped())
    .spawn()?;
    let service = ().serve(transport).await?;
    Ok((service, stderr))
}

fn text_content_json(result: &rmcp::model::CallToolResult) -> serde_json::Value {
    let value = serde_json::to_value(result).expect("tool result should serialize");
    let text = value["content"][0]["text"]
        .as_str()
        .expect("tool result should contain text content");
    serde_json::from_str(text).expect("tool text content should be JSON")
}

#[tokio::test]
async fn stdio_child_process_lists_tools_and_calls_queries() {
    let temp = TempDir::new().unwrap();
    let db_path = temp.path().join("stdio-mcp.db");
    let (service, stderr) = stdio_client(&db_path).await.unwrap();

    let tools = service.list_tools(Default::default()).await.unwrap();
    let names: Vec<&str> = tools.tools.iter().map(|tool| tool.name.as_ref()).collect();
    assert_eq!(names, vec!["syslog"]);

    let stats = service
        .call_tool(
            CallToolRequestParams::new("syslog")
                .with_arguments(json!({"action": "stats"}).as_object().unwrap().clone()),
        )
        .await
        .unwrap();
    let stats = text_content_json(&stats);
    assert_eq!(stats["total_logs"], 0);

    let search = service
        .call_tool(
            CallToolRequestParams::new("syslog").with_arguments(
                json!({"action": "search", "query": "disk", "limit": 5})
                    .as_object()
                    .unwrap()
                    .clone(),
            ),
        )
        .await
        .unwrap();
    let search = text_content_json(&search);
    assert_eq!(search["count"], 0);

    service.cancel().await.unwrap();

    if let Some(mut stderr) = stderr {
        let mut logs = String::new();
        match tokio::time::timeout(
            std::time::Duration::from_secs(1),
            stderr.read_to_string(&mut logs),
        )
        .await
        {
            Ok(Ok(_)) => {}
            Ok(Err(error)) => panic!("failed to read stdio child stderr: {error}"),
            Err(_) => panic!("stdio child stderr did not close after cancellation"),
        }
        assert!(
            !logs.contains("syslog listener") && !logs.contains("MCP server listening"),
            "stdio mode must not start network services; stderr was: {logs}"
        );
    }
}
