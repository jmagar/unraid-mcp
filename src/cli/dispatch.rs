use anyhow::Result;

use unraid_mcp::app::UnraidService;

use super::commands::CliCommand;
use super::format::print_human;

pub async fn run(service: &UnraidService, cmd: CliCommand, json: bool) -> Result<()> {
    let (label, data) = match cmd {
        CliCommand::Array => ("array", service.array().await?),
        CliCommand::Disks => ("disks", service.disks().await?),
        CliCommand::Docker => ("docker", service.docker().await?),
        CliCommand::DockerLogs { ref id, tail } => {
            ("docker_logs", service.docker_logs(id, tail).await?)
        }
        CliCommand::Vms => ("vms", service.vms().await?),
        CliCommand::Server => ("server", service.server().await?),
        CliCommand::Info => ("info", service.info().await?),
        CliCommand::Shares => ("shares", service.shares().await?),
        CliCommand::Notifications => ("notifications", service.notifications().await?),
        CliCommand::LogFiles => ("log_files", service.log_files().await?),
        CliCommand::LogFile {
            ref path,
            lines,
            start_line,
        } => ("log_file", service.log_file(path, lines, start_line).await?),
        CliCommand::Services => ("services", service.services().await?),
        CliCommand::Network => ("network", service.network().await?),
        CliCommand::Ups => ("ups", service.ups().await?),
        CliCommand::UpsConfig => ("ups_config", service.ups_config().await?),
        CliCommand::Metrics => ("metrics", service.metrics().await?),
        CliCommand::Plugins => ("plugins", service.plugins().await?),
        CliCommand::ParityHistory => ("parity_history", service.parity_history().await?),
        CliCommand::Vars => ("vars", service.vars().await?),
        CliCommand::Registration => ("registration", service.registration().await?),
        CliCommand::Flash => ("flash", service.flash().await?),
        CliCommand::Rclone => ("rclone", service.rclone().await?),
        CliCommand::RemoteAccess => ("remote_access", service.remote_access().await?),
        CliCommand::Connect => ("connect", service.connect().await?),
        // Doctor is intercepted in main.rs before reaching dispatch.
        CliCommand::Doctor => unreachable!("doctor is handled before service construction"),
    };

    if json {
        println!("{}", serde_json::to_string_pretty(&data)?);
    } else {
        print_human(label, &data);
    }
    Ok(())
}
