use std::process::Command;

use serde_json::Value;
use tempfile::tempdir;

fn unraid_bin() -> &'static str {
    env!("CARGO_BIN_EXE_unraid")
}

fn base_command(data_dir: &std::path::Path) -> Command {
    let mut cmd = Command::new(unraid_bin());
    cmd.env_clear()
        .env("HOME", data_dir)
        .env("PATH", std::env::var("PATH").unwrap_or_default())
        .env("CLAUDE_PLUGIN_DATA", data_dir)
        .env("UNRAID_API_URL", "https://tower.example/graphql")
        .env("UNRAID_API_KEY", "secret")
        .env("UNRAID_MCP_PORT", "0")
        .env("UNRAID_MCP_TOKEN", "mcp-secret");
    cmd
}

#[test]
fn setup_plugin_hook_no_repair_emits_json_contract() {
    let dir = tempdir().unwrap();
    let mut cmd = base_command(dir.path());
    let output = cmd
        .args(["setup", "plugin-hook", "--no-repair"])
        .output()
        .unwrap();

    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    let json: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(json["exit_policy"], "advisory_failure");
    assert_eq!(json["ran_repair"], false);
    assert_eq!(json["no_repair"], true);
    assert!(json["blocking_failures"].as_array().unwrap().is_empty());
    assert!(json["advisory_failures"]
        .as_array()
        .unwrap()
        .iter()
        .any(|failure| failure["code"] == "env_file_missing"));
    assert!(!dir.path().join(".env").exists());
}

#[test]
fn setup_repair_creates_env_file_without_upstream_contact() {
    let dir = tempdir().unwrap();
    let missing = dir.path().join("appdata");
    let mut cmd = base_command(&missing);
    let output = cmd.args(["setup", "repair"]).output().unwrap();

    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    let json: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(json["exit_policy"], "success");
    assert_eq!(json["ran_repair"], true);
    assert_eq!(json["no_repair"], false);

    let env_file = std::fs::read_to_string(missing.join(".env")).unwrap();
    assert!(env_file.contains("UNRAID_API_URL=https://tower.example/graphql"));
    assert!(env_file.contains("UNRAID_API_KEY=secret"));
    assert!(env_file.contains("UNRAID_MCP_TOKEN=mcp-secret"));
}

#[test]
fn plugin_setup_script_delegates_to_binary_setup_command() {
    let script = std::fs::read_to_string("plugins/unraid/hooks/plugin-setup.sh").unwrap();
    assert!(script.contains("unraid setup plugin-hook"));
    assert!(!script.contains("systemctl --user"));
    assert!(!script.contains("docker compose"));
}
