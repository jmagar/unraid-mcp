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
        CliCommand::Online => ("online", service.online().await?),
        CliCommand::SystemTime => ("system_time", service.system_time().await?),
        CliCommand::InstalledUnraidPlugins => (
            "installed_unraid_plugins",
            service.installed_unraid_plugins().await?,
        ),
        CliCommand::IsSsoEnabled => ("is_sso_enabled", service.is_sso_enabled().await?),
        CliCommand::PublicOidcProviders => (
            "public_oidc_providers",
            service.public_oidc_providers().await?,
        ),
        CliCommand::OidcProviders => ("oidc_providers", service.oidc_providers().await?),
        CliCommand::OidcConfiguration => {
            ("oidc_configuration", service.oidc_configuration().await?)
        }
        CliCommand::ApiKeys => ("api_keys", service.api_keys().await?),
        CliCommand::ApiKeyPossibleRoles => (
            "api_key_possible_roles",
            service.api_key_possible_roles().await?,
        ),
        CliCommand::ApiKeyPossiblePermissions => (
            "api_key_possible_permissions",
            service.api_key_possible_permissions().await?,
        ),
        CliCommand::GetAvailableAuthActions => (
            "get_available_auth_actions",
            service.get_available_auth_actions().await?,
        ),
        CliCommand::GetApiKeyCreationFormSchema => (
            "get_api_key_creation_form_schema",
            service.get_api_key_creation_form_schema().await?,
        ),
        CliCommand::Config => ("config", service.config().await?),
        CliCommand::Settings => ("settings", service.settings().await?),
        CliCommand::Display => ("display", service.display().await?),
        CliCommand::Customization => ("customization", service.customization().await?),
        CliCommand::InternalBootContext => (
            "internal_boot_context",
            service.internal_boot_context().await?,
        ),
        CliCommand::Me => ("me", service.me().await?),
        CliCommand::Owner => ("owner", service.owner().await?),
        CliCommand::Servers => ("servers", service.servers().await?),
        CliCommand::IsFreshInstall => ("is_fresh_install", service.is_fresh_install().await?),
        CliCommand::PublicTheme => ("public_theme", service.public_theme().await?),
        CliCommand::NetworkInterfaces => {
            ("network_interfaces", service.network_interfaces().await?)
        }
        CliCommand::TimeZoneOptions => ("time_zone_options", service.time_zone_options().await?),
        CliCommand::AssignableDisks => ("assignable_disks", service.assignable_disks().await?),
        CliCommand::PluginInstallOperations => (
            "plugin_install_operations",
            service.plugin_install_operations().await?,
        ),
        CliCommand::Cloud => ("cloud", service.cloud().await?),
        CliCommand::ApiKey(id) => ("api_key", service.api_key(&id).await?),
        CliCommand::Disk(id) => ("disk", service.disk(&id).await?),
        CliCommand::OidcProvider(id) => ("oidc_provider", service.oidc_provider(&id).await?),
        CliCommand::UpsDeviceById(id) => ("ups_device_by_id", service.ups_device_by_id(&id).await?),
        CliCommand::PluginInstallOperation(id) => (
            "plugin_install_operation",
            service.plugin_install_operation(&id).await?,
        ),
        CliCommand::ValidateOidcSession(token) => (
            "validate_oidc_session",
            service.validate_oidc_session(&token).await?,
        ),
        CliCommand::GetPermissionsForRoles(roles) => (
            "get_permissions_for_roles",
            service.get_permissions_for_roles(&roles).await?,
        ),
        CliCommand::RecalculateOverview => (
            "recalculate_overview",
            service.recalculate_overview().await?,
        ),
        CliCommand::DeleteArchivedNotifications => (
            "delete_archived_notifications",
            service.delete_archived_notifications().await?,
        ),
        CliCommand::ArchiveNotification(id) => (
            "archive_notification",
            service.archive_notification(&id).await?,
        ),
        CliCommand::CreateNotification {
            title,
            subject,
            description,
            importance,
            link,
        } => (
            "create_notification",
            service
                .create_notification(&title, &subject, &description, &importance, link.as_deref())
                .await?,
        ),
        CliCommand::VmStart(id) => ("vm_start", service.vm_start(&id).await?),
        CliCommand::VmStop(id) => ("vm_stop", service.vm_stop(&id).await?),
        CliCommand::VmPause(id) => ("vm_pause", service.vm_pause(&id).await?),
        CliCommand::VmResume(id) => ("vm_resume", service.vm_resume(&id).await?),
        CliCommand::VmForceStop(id) => ("vm_force_stop", service.vm_force_stop(&id).await?),
        CliCommand::VmReboot(id) => ("vm_reboot", service.vm_reboot(&id).await?),
        CliCommand::VmReset(id) => ("vm_reset", service.vm_reset(&id).await?),
        CliCommand::DockerStart(id) => ("docker_start", service.docker_start(&id).await?),
        CliCommand::DockerStop(id) => ("docker_stop", service.docker_stop(&id).await?),
        CliCommand::DockerPause(id) => ("docker_pause", service.docker_pause(&id).await?),
        CliCommand::DockerUnpause(id) => ("docker_unpause", service.docker_unpause(&id).await?),
        CliCommand::DockerUpdateContainer(id) => (
            "docker_update_container",
            service.docker_update_container(&id).await?,
        ),
        CliCommand::DockerRemoveContainer(id) => (
            "docker_remove_container",
            service.docker_remove_container(&id, None).await?,
        ),
        CliCommand::DockerUpdateContainers(ids) => (
            "docker_update_containers",
            service.docker_update_containers(&ids).await?,
        ),
        CliCommand::DockerUpdateAllContainers => (
            "docker_update_all_containers",
            service.docker_update_all_containers().await?,
        ),
        CliCommand::ArraySetState(ds) => ("array_set_state", service.array_set_state(&ds).await?),
        CliCommand::ArrayAddDiskToArray(id) => (
            "array_add_disk_to_array",
            service.array_add_disk_to_array(&id, None).await?,
        ),
        CliCommand::ArrayRemoveDiskFromArray(id) => (
            "array_remove_disk_from_array",
            service.array_remove_disk_from_array(&id, None).await?,
        ),
        CliCommand::ArrayMountArrayDisk(id) => (
            "array_mount_array_disk",
            service.array_mount_array_disk(&id).await?,
        ),
        CliCommand::ArrayUnmountArrayDisk(id) => (
            "array_unmount_array_disk",
            service.array_unmount_array_disk(&id).await?,
        ),
        CliCommand::ArrayClearArrayDiskStatistics(id) => (
            "array_clear_array_disk_statistics",
            service.array_clear_array_disk_statistics(&id).await?,
        ),
        CliCommand::ParityCheckStart(correct) => (
            "parity_check_start",
            service.parity_check_start(correct).await?,
        ),
        CliCommand::ParityCheckPause => ("parity_check_pause", service.parity_check_pause().await?),
        CliCommand::ParityCheckResume => {
            ("parity_check_resume", service.parity_check_resume().await?)
        }
        CliCommand::ParityCheckCancel => {
            ("parity_check_cancel", service.parity_check_cancel().await?)
        }
        CliCommand::ApiKeyCreate(name) => (
            "api_key_create",
            service
                .api_key_create(&name, None, None, &serde_json::Value::Null, None)
                .await?,
        ),
        CliCommand::ApiKeyAddRole(id, role) => (
            "api_key_add_role",
            service.api_key_add_role(&id, &role).await?,
        ),
        CliCommand::ApiKeyRemoveRole(id, role) => (
            "api_key_remove_role",
            service.api_key_remove_role(&id, &role).await?,
        ),
        CliCommand::ApiKeyDelete(ids) => ("api_key_delete", service.api_key_delete(&ids).await?),
        CliCommand::ApiKeyUpdate(id) => (
            "api_key_update",
            service
                .api_key_update(&id, None, None, None, &serde_json::Value::Null)
                .await?,
        ),
        CliCommand::RcloneCreateRemote(name, ty) => (
            "rclone_create_r_clone_remote",
            service
                .rclone_create_r_clone_remote(&name, &ty, serde_json::json!({}))
                .await?,
        ),
        CliCommand::RcloneDeleteRemote(name) => (
            "rclone_delete_r_clone_remote",
            service.rclone_delete_r_clone_remote(&name).await?,
        ),
        CliCommand::UnraidPluginsInstallPlugin(url) => (
            "unraid_plugins_install_plugin",
            service
                .unraid_plugins_install_plugin(&url, None, None)
                .await?,
        ),
        CliCommand::UnraidPluginsInstallLanguage(url) => (
            "unraid_plugins_install_language",
            service
                .unraid_plugins_install_language(&url, None, None)
                .await?,
        ),
        CliCommand::OnboardingComplete => (
            "onboarding_complete_onboarding",
            service.onboarding_complete_onboarding().await?,
        ),
        CliCommand::OnboardingReset => (
            "onboarding_reset_onboarding",
            service.onboarding_reset_onboarding().await?,
        ),
        CliCommand::ArchiveNotifications(ids) => (
            "archive_notifications",
            service.archive_notifications(&ids).await?,
        ),
        CliCommand::UnarchiveNotifications(ids) => (
            "unarchive_notifications",
            service.unarchive_notifications(&ids).await?,
        ),
        CliCommand::UnreadNotification(id) => (
            "unread_notification",
            service.unread_notification(&id).await?,
        ),
        CliCommand::ArchiveAll(imp) => ("archive_all", service.archive_all(imp.as_deref()).await?),
        CliCommand::UnarchiveAll(imp) => (
            "unarchive_all",
            service.unarchive_all(imp.as_deref()).await?,
        ),
        CliCommand::UpdateServerIdentity(name) => (
            "update_server_identity",
            service.update_server_identity(&name, None, None).await?,
        ),
        CliCommand::ConnectSignOut => ("connect_sign_out", service.connect_sign_out().await?),
        // Doctor and setup are intercepted in main.rs before reaching dispatch.
        CliCommand::Doctor | CliCommand::Setup(_) => {
            unreachable!("doctor/setup are handled before service construction")
        }
    };

    if json {
        println!("{}", serde_json::to_string_pretty(&data)?);
    } else {
        print_human(label, &data);
    }
    Ok(())
}
