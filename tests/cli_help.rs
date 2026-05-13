use std::process::Command;

#[test]
fn help_lists_sessions_command() {
    let output = Command::new(env!("CARGO_BIN_EXE_syslog"))
        .arg("--help")
        .output()
        .unwrap();

    let stderr = String::from_utf8(output.stderr).unwrap();
    assert!(
        stderr.contains("syslog sessions"),
        "help output should list the sessions command, got:\n{stderr}"
    );
}

#[test]
fn ai_cli_add_and_query_commands_emit_json() {
    let dir = tempfile::tempdir().unwrap();
    let db_path = dir.path().join("cli-ai.db");
    let transcript = dir.path().join("session.jsonl");
    std::fs::write(
        &transcript,
        "{\"sessionId\":\"cli-1\",\"content\":\"hello cli transcript\"}\n",
    )
    .unwrap();

    let add = run_ai_command(&db_path, ["ai", "add", "--file"], Some(&transcript));
    assert!(add.status.success(), "ai add failed: {add:?}");
    let add_json: serde_json::Value = serde_json::from_slice(&add.stdout).unwrap();
    assert_eq!(add_json["ingested"], 1);

    let search = run_ai_command(&db_path, ["ai", "search", "hello", "--json"], None);
    assert!(search.status.success(), "ai search failed: {search:?}");
    let search_json: serde_json::Value = serde_json::from_slice(&search.stdout).unwrap();
    assert_eq!(search_json["sessions"].as_array().unwrap().len(), 1);

    for args in [
        &["ai", "blocks", "--json"][..],
        &["ai", "tools", "--json"][..],
        &["ai", "projects", "--json"][..],
        &["sessions", "--json"][..],
    ] {
        let output = run_command(&db_path, args);
        assert!(output.status.success(), "{args:?} failed: {output:?}");
        serde_json::from_slice::<serde_json::Value>(&output.stdout).unwrap();
    }

    let cwd = std::env::current_dir().unwrap();
    let context = run_command(
        &db_path,
        &[
            "ai",
            "context",
            "--project",
            cwd.to_str().unwrap(),
            "--json",
        ],
    );
    assert!(context.status.success(), "ai context failed: {context:?}");
    serde_json::from_slice::<serde_json::Value>(&context.stdout).unwrap();
}

fn run_ai_command<const N: usize>(
    db_path: &std::path::Path,
    args: [&str; N],
    trailing_path: Option<&std::path::Path>,
) -> std::process::Output {
    let mut command = Command::new(env!("CARGO_BIN_EXE_syslog"));
    command.env("SYSLOG_MCP_DB_PATH", db_path);
    for arg in args {
        command.arg(arg);
    }
    if let Some(path) = trailing_path {
        command.arg(path);
        command.arg("--json");
    }
    command.output().unwrap()
}

fn run_command(db_path: &std::path::Path, args: &[&str]) -> std::process::Output {
    let mut command = Command::new(env!("CARGO_BIN_EXE_syslog"));
    command.env("SYSLOG_MCP_DB_PATH", db_path);
    command.args(args);
    command.output().unwrap()
}
