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
            ["online"] => Self::Online,
            ["system-time"] | ["system", "time"] => Self::SystemTime,
            ["installed-unraid-plugins"] | ["installed-plugins"] => Self::InstalledUnraidPlugins,
            ["is-sso-enabled"] | ["sso"] => Self::IsSsoEnabled,
            ["public-oidc-providers"] => Self::PublicOidcProviders,
            ["oidc-providers"] => Self::OidcProviders,
            ["oidc-configuration"] | ["oidc-config"] => Self::OidcConfiguration,
            ["api-keys"] => Self::ApiKeys,
            ["api-key-possible-roles"] | ["possible-roles"] => Self::ApiKeyPossibleRoles,
            ["api-key-possible-permissions"] | ["possible-permissions"] => {
                Self::ApiKeyPossiblePermissions
            }
            ["get-available-auth-actions"] | ["auth-actions"] => Self::GetAvailableAuthActions,
            ["get-api-key-creation-form-schema"] | ["api-key-form-schema"] => {
                Self::GetApiKeyCreationFormSchema
            }
            ["config"] => Self::Config,
            ["settings"] => Self::Settings,
            ["display"] => Self::Display,
            ["customization"] => Self::Customization,
            ["internal-boot-context"] | ["boot-context"] => Self::InternalBootContext,
            ["me"] => Self::Me,
            ["owner"] => Self::Owner,
            ["servers"] => Self::Servers,
            ["is-fresh-install"] | ["fresh-install"] => Self::IsFreshInstall,
            ["public-theme"] | ["theme"] => Self::PublicTheme,
            ["network-interfaces"] | ["nics"] => Self::NetworkInterfaces,
            ["time-zone-options"] | ["timezones"] => Self::TimeZoneOptions,
            ["assignable-disks"] => Self::AssignableDisks,
            ["plugin-install-operations"] | ["plugin-ops"] => Self::PluginInstallOperations,
            ["cloud"] => Self::Cloud,
            ["api-key", id] => Self::ApiKey(id.to_string()),
            ["disk", id] => Self::Disk(id.to_string()),
            ["oidc-provider", id] => Self::OidcProvider(id.to_string()),
            ["ups-device", id] | ["ups-device-by-id", id] => Self::UpsDeviceById(id.to_string()),
            ["plugin-install-operation", id] | ["plugin-op", id] => {
                Self::PluginInstallOperation(id.to_string())
            }
            ["validate-oidc-session", token] => Self::ValidateOidcSession(token.to_string()),
            ["get-permissions-for-roles", roles @ ..] if !roles.is_empty() => {
                Self::GetPermissionsForRoles(roles.iter().map(|r| r.to_string()).collect())
            }
            ["recalculate-overview"] => Self::RecalculateOverview,
            ["delete-archived-notifications"] => Self::DeleteArchivedNotifications,
            ["archive-notification", id] => Self::ArchiveNotification(id.to_string()),
            ["create-notification", title, subject, description, importance, rest @ ..] => {
                Self::CreateNotification {
                    title: title.to_string(),
                    subject: subject.to_string(),
                    description: description.to_string(),
                    importance: importance.to_string(),
                    link: rest.first().map(|s| s.to_string()),
                }
            }
            ["vm-start", id] => Self::VmStart(id.to_string()),
            ["vm-stop", id] => Self::VmStop(id.to_string()),
            ["vm-pause", id] => Self::VmPause(id.to_string()),
            ["vm-resume", id] => Self::VmResume(id.to_string()),
            ["vm-force-stop", id] => Self::VmForceStop(id.to_string()),
            ["vm-reboot", id] => Self::VmReboot(id.to_string()),
            ["vm-reset", id] => Self::VmReset(id.to_string()),
            ["docker-start", id] => Self::DockerStart(id.to_string()),
            ["docker-stop", id] => Self::DockerStop(id.to_string()),
            ["docker-pause", id] => Self::DockerPause(id.to_string()),
            ["docker-unpause", id] => Self::DockerUnpause(id.to_string()),
            ["docker-update-container", id] => Self::DockerUpdateContainer(id.to_string()),
            ["docker-remove-container", id] => Self::DockerRemoveContainer(id.to_string()),
            ["docker-update-containers", ids @ ..] if !ids.is_empty() => {
                Self::DockerUpdateContainers(ids.iter().map(|s| s.to_string()).collect())
            }
            ["docker-update-all-containers"] => Self::DockerUpdateAllContainers,
            ["array-set-state", ds] => Self::ArraySetState(ds.to_string()),
            ["array-add-disk-to-array", id] => Self::ArrayAddDiskToArray(id.to_string()),
            ["array-remove-disk-from-array", id] => Self::ArrayRemoveDiskFromArray(id.to_string()),
            ["array-mount-array-disk", id] => Self::ArrayMountArrayDisk(id.to_string()),
            ["array-unmount-array-disk", id] => Self::ArrayUnmountArrayDisk(id.to_string()),
            ["array-clear-array-disk-statistics", id] => {
                Self::ArrayClearArrayDiskStatistics(id.to_string())
            }
            ["parity-check-start", rest @ ..] => Self::ParityCheckStart(
                rest.first()
                    .map(|c| *c == "correct" || *c == "true")
                    .unwrap_or(false),
            ),
            ["parity-check-pause"] => Self::ParityCheckPause,
            ["parity-check-resume"] => Self::ParityCheckResume,
            ["parity-check-cancel"] => Self::ParityCheckCancel,
            ["api-key-create", name] => Self::ApiKeyCreate(name.to_string()),
            ["api-key-add-role", id, role] => Self::ApiKeyAddRole(id.to_string(), role.to_string()),
            ["api-key-remove-role", id, role] => {
                Self::ApiKeyRemoveRole(id.to_string(), role.to_string())
            }
            ["api-key-delete", ids @ ..] if !ids.is_empty() => {
                Self::ApiKeyDelete(ids.iter().map(|s| s.to_string()).collect())
            }
            ["api-key-update", id] => Self::ApiKeyUpdate(id.to_string()),
            ["rclone-create-remote", name, ty] => {
                Self::RcloneCreateRemote(name.to_string(), ty.to_string())
            }
            ["rclone-delete-remote", name] => Self::RcloneDeleteRemote(name.to_string()),
            ["unraid-plugins-install-plugin", url] | ["install-plugin", url] => {
                Self::UnraidPluginsInstallPlugin(url.to_string())
            }
            ["unraid-plugins-install-language", url] | ["install-language", url] => {
                Self::UnraidPluginsInstallLanguage(url.to_string())
            }
            ["onboarding-complete"] => Self::OnboardingComplete,
            ["onboarding-reset"] => Self::OnboardingReset,
            ["archive-notifications", ids @ ..] if !ids.is_empty() => {
                Self::ArchiveNotifications(ids.iter().map(|s| s.to_string()).collect())
            }
            ["unarchive-notifications", ids @ ..] if !ids.is_empty() => {
                Self::UnarchiveNotifications(ids.iter().map(|s| s.to_string()).collect())
            }
            ["unread-notification", id] => Self::UnreadNotification(id.to_string()),
            ["archive-all", rest @ ..] => Self::ArchiveAll(rest.first().map(|s| s.to_string())),
            ["unarchive-all", rest @ ..] => Self::UnarchiveAll(rest.first().map(|s| s.to_string())),
            ["update-server-identity", name] => Self::UpdateServerIdentity(name.to_string()),
            ["connect-sign-out"] => Self::ConnectSignOut,
            ["doctor"] => Self::Doctor,
            ["setup", "check"] => Self::Setup(SetupCommand::Check),
            ["setup", "repair"] => Self::Setup(SetupCommand::Repair),
            ["setup", "install"] => Self::Setup(SetupCommand::Install),
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
