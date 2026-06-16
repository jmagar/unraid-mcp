use anyhow::Result;
use serde_json::Value;

use crate::graphql::UnraidClient;

/// Thin, intentional typed seam between the CLI / MCP front-ends and
/// [`UnraidClient`]. Each method is a verbatim pass-through to the client by
/// design — there is deliberately no business logic here.
///
/// Where the actual work lives:
/// - data retrieval (GraphQL queries) → `graphql.rs`
/// - pagination, argument validation, action dispatch → `mcp/tools.rs`
///
/// Keeping this seam lets both front-ends share one typed `Service` surface
/// without coupling them to the raw HTTP client.
#[derive(Clone)]
pub struct UnraidService {
    client: UnraidClient,
}

impl UnraidService {
    pub fn new(client: UnraidClient) -> Self {
        Self { client }
    }

    /// Expose raw HTTP client fields for health probing (url, api_key).
    pub fn raw_client_parts(&self) -> (&reqwest::Client, &str, &str) {
        self.client.raw_client()
    }

    pub async fn array(&self) -> Result<Value> {
        self.client.array().await
    }

    pub async fn disks(&self) -> Result<Value> {
        self.client.disks().await
    }

    pub async fn docker(&self) -> Result<Value> {
        self.client.docker().await
    }

    pub async fn docker_logs(&self, id: &str, tail: Option<i64>) -> Result<Value> {
        self.client.docker_logs(id, tail).await
    }

    pub async fn vms(&self) -> Result<Value> {
        self.client.vms().await
    }

    pub async fn server(&self) -> Result<Value> {
        self.client.server().await
    }

    pub async fn info(&self) -> Result<Value> {
        self.client.info().await
    }

    pub async fn shares(&self) -> Result<Value> {
        self.client.shares().await
    }

    pub async fn notifications(&self) -> Result<Value> {
        self.client.notifications().await
    }

    pub async fn log_files(&self) -> Result<Value> {
        self.client.log_files().await
    }

    pub async fn log_file(
        &self,
        path: &str,
        lines: Option<i64>,
        start_line: Option<i64>,
    ) -> Result<Value> {
        self.client.log_file(path, lines, start_line).await
    }

    pub async fn services(&self) -> Result<Value> {
        self.client.services().await
    }

    pub async fn network(&self) -> Result<Value> {
        self.client.network().await
    }

    pub async fn ups(&self) -> Result<Value> {
        self.client.ups().await
    }

    pub async fn ups_config(&self) -> Result<Value> {
        self.client.ups_config().await
    }

    pub async fn metrics(&self) -> Result<Value> {
        self.client.metrics().await
    }

    pub async fn plugins(&self) -> Result<Value> {
        self.client.plugins().await
    }

    pub async fn parity_history(&self) -> Result<Value> {
        self.client.parity_history().await
    }

    pub async fn vars(&self) -> Result<Value> {
        self.client.vars().await
    }

    pub async fn registration(&self) -> Result<Value> {
        self.client.registration().await
    }

    pub async fn flash(&self) -> Result<Value> {
        self.client.flash().await
    }

    pub async fn online(&self) -> Result<Value> {
        self.client.online().await
    }

    pub async fn system_time(&self) -> Result<Value> {
        self.client.system_time().await
    }

    pub async fn installed_unraid_plugins(&self) -> Result<Value> {
        self.client.installed_unraid_plugins().await
    }

    pub async fn is_sso_enabled(&self) -> Result<Value> {
        self.client.is_sso_enabled().await
    }

    pub async fn public_oidc_providers(&self) -> Result<Value> {
        self.client.public_oidc_providers().await
    }

    pub async fn oidc_providers(&self) -> Result<Value> {
        self.client.oidc_providers().await
    }

    pub async fn oidc_configuration(&self) -> Result<Value> {
        self.client.oidc_configuration().await
    }

    pub async fn api_keys(&self) -> Result<Value> {
        self.client.api_keys().await
    }

    pub async fn api_key_possible_roles(&self) -> Result<Value> {
        self.client.api_key_possible_roles().await
    }

    pub async fn api_key_possible_permissions(&self) -> Result<Value> {
        self.client.api_key_possible_permissions().await
    }

    pub async fn get_available_auth_actions(&self) -> Result<Value> {
        self.client.get_available_auth_actions().await
    }

    pub async fn get_api_key_creation_form_schema(&self) -> Result<Value> {
        self.client.get_api_key_creation_form_schema().await
    }

    pub async fn config(&self) -> Result<Value> {
        self.client.config().await
    }

    pub async fn settings(&self) -> Result<Value> {
        self.client.settings().await
    }

    pub async fn display(&self) -> Result<Value> {
        self.client.display().await
    }

    pub async fn customization(&self) -> Result<Value> {
        self.client.customization().await
    }

    pub async fn internal_boot_context(&self) -> Result<Value> {
        self.client.internal_boot_context().await
    }

    pub async fn me(&self) -> Result<Value> {
        self.client.me().await
    }

    pub async fn owner(&self) -> Result<Value> {
        self.client.owner().await
    }

    pub async fn servers(&self) -> Result<Value> {
        self.client.servers().await
    }

    pub async fn is_fresh_install(&self) -> Result<Value> {
        self.client.is_fresh_install().await
    }

    pub async fn public_theme(&self) -> Result<Value> {
        self.client.public_theme().await
    }

    pub async fn network_interfaces(&self) -> Result<Value> {
        self.client.network_interfaces().await
    }

    pub async fn time_zone_options(&self) -> Result<Value> {
        self.client.time_zone_options().await
    }

    pub async fn assignable_disks(&self) -> Result<Value> {
        self.client.assignable_disks().await
    }

    pub async fn plugin_install_operations(&self) -> Result<Value> {
        self.client.plugin_install_operations().await
    }

    pub async fn cloud(&self) -> Result<Value> {
        self.client.cloud().await
    }

    pub async fn api_key(&self, id: &str) -> Result<Value> {
        self.client.api_key(id).await
    }

    pub async fn disk(&self, id: &str) -> Result<Value> {
        self.client.disk(id).await
    }

    pub async fn oidc_provider(&self, id: &str) -> Result<Value> {
        self.client.oidc_provider(id).await
    }

    pub async fn ups_device_by_id(&self, id: &str) -> Result<Value> {
        self.client.ups_device_by_id(id).await
    }

    pub async fn plugin_install_operation(&self, id: &str) -> Result<Value> {
        self.client.plugin_install_operation(id).await
    }

    pub async fn validate_oidc_session(&self, token: &str) -> Result<Value> {
        self.client.validate_oidc_session(token).await
    }

    pub async fn get_permissions_for_roles(&self, roles: &[String]) -> Result<Value> {
        self.client.get_permissions_for_roles(roles).await
    }

    pub async fn recalculate_overview(&self) -> Result<Value> {
        self.client.recalculate_overview().await
    }

    pub async fn delete_archived_notifications(&self) -> Result<Value> {
        self.client.delete_archived_notifications().await
    }

    pub async fn archive_notification(&self, id: &str) -> Result<Value> {
        self.client.archive_notification(id).await
    }

    pub async fn create_notification(
        &self,
        title: &str,
        subject: &str,
        description: &str,
        importance: &str,
        link: Option<&str>,
    ) -> Result<Value> {
        self.client
            .create_notification(title, subject, description, importance, link)
            .await
    }

    pub async fn vm_start(&self, id: &str) -> Result<Value> {
        self.client.vm_start(id).await
    }

    pub async fn vm_stop(&self, id: &str) -> Result<Value> {
        self.client.vm_stop(id).await
    }

    pub async fn vm_pause(&self, id: &str) -> Result<Value> {
        self.client.vm_pause(id).await
    }

    pub async fn vm_resume(&self, id: &str) -> Result<Value> {
        self.client.vm_resume(id).await
    }

    pub async fn vm_force_stop(&self, id: &str) -> Result<Value> {
        self.client.vm_force_stop(id).await
    }

    pub async fn vm_reboot(&self, id: &str) -> Result<Value> {
        self.client.vm_reboot(id).await
    }

    pub async fn vm_reset(&self, id: &str) -> Result<Value> {
        self.client.vm_reset(id).await
    }
    pub async fn docker_start(&self, id: &str) -> Result<Value> {
        self.client.docker_start(id).await
    }

    pub async fn docker_stop(&self, id: &str) -> Result<Value> {
        self.client.docker_stop(id).await
    }

    pub async fn docker_pause(&self, id: &str) -> Result<Value> {
        self.client.docker_pause(id).await
    }

    pub async fn docker_unpause(&self, id: &str) -> Result<Value> {
        self.client.docker_unpause(id).await
    }

    pub async fn docker_update_container(&self, id: &str) -> Result<Value> {
        self.client.docker_update_container(id).await
    }

    pub async fn docker_remove_container(
        &self,
        id: &str,
        with_image: Option<bool>,
    ) -> Result<Value> {
        self.client.docker_remove_container(id, with_image).await
    }

    pub async fn docker_update_containers(&self, ids: &[String]) -> Result<Value> {
        self.client.docker_update_containers(ids).await
    }

    pub async fn docker_update_all_containers(&self) -> Result<Value> {
        self.client.docker_update_all_containers().await
    }
    pub async fn array_set_state(&self, desired_state: &str) -> Result<Value> {
        self.client.array_set_state(desired_state).await
    }
    pub async fn array_add_disk_to_array(&self, id: &str, slot: Option<i32>) -> Result<Value> {
        self.client.array_add_disk_to_array(id, slot).await
    }
    pub async fn array_remove_disk_from_array(&self, id: &str, slot: Option<i32>) -> Result<Value> {
        self.client.array_remove_disk_from_array(id, slot).await
    }
    pub async fn array_mount_array_disk(&self, id: &str) -> Result<Value> {
        self.client.array_mount_array_disk(id).await
    }
    pub async fn array_unmount_array_disk(&self, id: &str) -> Result<Value> {
        self.client.array_unmount_array_disk(id).await
    }
    pub async fn array_clear_array_disk_statistics(&self, id: &str) -> Result<Value> {
        self.client.array_clear_array_disk_statistics(id).await
    }
    pub async fn parity_check_start(&self, correct: bool) -> Result<Value> {
        self.client.parity_check_start(correct).await
    }
    pub async fn parity_check_pause(&self) -> Result<Value> {
        self.client.parity_check_pause().await
    }
    pub async fn parity_check_resume(&self) -> Result<Value> {
        self.client.parity_check_resume().await
    }
    pub async fn parity_check_cancel(&self) -> Result<Value> {
        self.client.parity_check_cancel().await
    }
    pub async fn api_key_create(
        &self,
        name: &str,
        description: Option<&str>,
        roles: Option<&[String]>,
        permissions: &Value,
        overwrite: Option<bool>,
    ) -> Result<Value> {
        self.client
            .api_key_create(name, description, roles, permissions, overwrite)
            .await
    }
    pub async fn api_key_add_role(&self, api_key_id: &str, role: &str) -> Result<Value> {
        self.client.api_key_add_role(api_key_id, role).await
    }
    pub async fn api_key_remove_role(&self, api_key_id: &str, role: &str) -> Result<Value> {
        self.client.api_key_remove_role(api_key_id, role).await
    }
    pub async fn api_key_delete(&self, ids: &[String]) -> Result<Value> {
        self.client.api_key_delete(ids).await
    }
    pub async fn api_key_update(
        &self,
        id: &str,
        name: Option<&str>,
        description: Option<&str>,
        roles: Option<&[String]>,
        permissions: &Value,
    ) -> Result<Value> {
        self.client
            .api_key_update(id, name, description, roles, permissions)
            .await
    }
    pub async fn rclone_create_r_clone_remote(
        &self,
        name: &str,
        remote_type: &str,
        parameters: Value,
    ) -> Result<Value> {
        self.client
            .rclone_create_r_clone_remote(name, remote_type, parameters)
            .await
    }
    pub async fn rclone_delete_r_clone_remote(&self, name: &str) -> Result<Value> {
        self.client.rclone_delete_r_clone_remote(name).await
    }
    pub async fn unraid_plugins_install_plugin(
        &self,
        url: &str,
        name: Option<&str>,
        forced: Option<bool>,
    ) -> Result<Value> {
        self.client
            .unraid_plugins_install_plugin(url, name, forced)
            .await
    }
    pub async fn unraid_plugins_install_language(
        &self,
        url: &str,
        name: Option<&str>,
        forced: Option<bool>,
    ) -> Result<Value> {
        self.client
            .unraid_plugins_install_language(url, name, forced)
            .await
    }
    pub async fn onboarding_complete_onboarding(&self) -> Result<Value> {
        self.client.onboarding_complete_onboarding().await
    }
    pub async fn onboarding_reset_onboarding(&self) -> Result<Value> {
        self.client.onboarding_reset_onboarding().await
    }
    pub async fn archive_notifications(&self, ids: &[String]) -> Result<Value> {
        self.client.archive_notifications(ids).await
    }
    pub async fn unarchive_notifications(&self, ids: &[String]) -> Result<Value> {
        self.client.unarchive_notifications(ids).await
    }
    pub async fn unread_notification(&self, id: &str) -> Result<Value> {
        self.client.unread_notification(id).await
    }
    pub async fn archive_all(&self, importance: Option<&str>) -> Result<Value> {
        self.client.archive_all(importance).await
    }
    pub async fn unarchive_all(&self, importance: Option<&str>) -> Result<Value> {
        self.client.unarchive_all(importance).await
    }
    pub async fn update_server_identity(
        &self,
        name: &str,
        comment: Option<&str>,
        sys_model: Option<&str>,
    ) -> Result<Value> {
        self.client
            .update_server_identity(name, comment, sys_model)
            .await
    }
    pub async fn configure_ups(&self, config: Value) -> Result<Value> {
        self.client.configure_ups(config).await
    }
    pub async fn update_system_time(&self, input: Value) -> Result<Value> {
        self.client.update_system_time(input).await
    }
    pub async fn update_temperature_config(&self, input: Value) -> Result<Value> {
        self.client.update_temperature_config(input).await
    }
    pub async fn add_plugin(&self, input: Value) -> Result<Value> {
        self.client.add_plugin(input).await
    }
    pub async fn remove_plugin(&self, input: Value) -> Result<Value> {
        self.client.remove_plugin(input).await
    }
    pub async fn connect_sign_out(&self) -> Result<Value> {
        self.client.connect_sign_out().await
    }

    pub async fn rclone(&self) -> Result<Value> {
        self.client.rclone().await
    }

    pub async fn remote_access(&self) -> Result<Value> {
        self.client.remote_access().await
    }

    pub async fn connect(&self) -> Result<Value> {
        self.client.connect().await
    }
}
