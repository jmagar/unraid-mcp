use anyhow::{bail, Result};

use super::{commands::CliCommand, setup::SetupCommand};

impl CliCommand {
    /// Parse CLI arguments into a `(CliCommand, json_mode)` pair.
    ///
    /// Returns an error with a helpful message if the command is unrecognised.
    pub fn parse(args: &[String]) -> Result<(Self, bool)> {
        let json = args.iter().any(|a| a == "--json");
        let rest: Vec<&str> = args
            .iter()
            .filter(|a| a.as_str() != "--json")
            .map(String::as_str)
            .collect();

        let cmd = match rest.as_slice() {
            ["array"] => Self::Array,
            ["disks"] => Self::Disks,
            ["docker"] => Self::Docker,
            ["docker", "logs", id, ..] => Self::DockerLogs {
                id: id.to_string(),
                tail: flag_i64(&rest, "--tail")?,
            },
            ["vms"] => Self::Vms,
            ["server"] => Self::Server,
            ["info"] => Self::Info,
            ["shares"] => Self::Shares,
            ["notifications"] => Self::Notifications,
            ["log-files"] | ["log", "files"] => Self::LogFiles,
            ["log", path, ..] | ["log-file", path, ..] => Self::LogFile {
                path: path.to_string(),
                lines: flag_i64(&rest, "--lines")?,
                start_line: flag_i64(&rest, "--start-line")?,
            },
            ["services"] => Self::Services,
            ["network"] => Self::Network,
            ["ups"] => Self::Ups,
            ["ups-config"] | ["ups", "config"] => Self::UpsConfig,
            ["metrics"] => Self::Metrics,
            ["plugins"] => Self::Plugins,
            ["parity-history"] | ["parity", "history"] => Self::ParityHistory,
            ["vars"] => Self::Vars,
            ["registration"] => Self::Registration,
            ["flash"] => Self::Flash,
            ["rclone"] => Self::Rclone,
            ["remote-access"] | ["remote", "access"] => Self::RemoteAccess,
            ["connect"] => Self::Connect,
            ["doctor"] => Self::Doctor,
            ["setup", "check"] => Self::Setup(SetupCommand::Check),
            ["setup", "repair"] => Self::Setup(SetupCommand::Repair),
            ["setup", "plugin-hook", flags @ ..] => Self::Setup(SetupCommand::PluginHook {
                no_repair: flags.contains(&"--no-repair"),
            }),
            other => bail!(
                "unknown command: {}\n\nRun `unraid --help` for usage.",
                other.join(" ")
            ),
        };
        Ok((cmd, json))
    }
}

fn flag_i64(args: &[&str], flag: &str) -> anyhow::Result<Option<i64>> {
    let Some(pos) = args.iter().position(|a| *a == flag) else {
        return Ok(None);
    };
    let val = args
        .get(pos + 1)
        .ok_or_else(|| anyhow::anyhow!("{flag} requires a value"))?;
    val.parse::<i64>()
        .map(Some)
        .map_err(|_| anyhow::anyhow!("{flag}: expected integer, got {val:?}"))
}
