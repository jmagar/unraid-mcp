#!/bin/bash
# Shared, side-effect-free validation for containment-sensitive config. Source
# this file after incus.cfg/defaults and call validate_containment_config before
# accepting a candidate as known-good or applying it to Incus.

path_is_safe_storage() {
  case "$1" in /srv/*|/mnt/*) return 0 ;; *) return 1 ;; esac
}

validate_containment_config() {
  local workspace resolved_workspace item host target mode extra resolved_host config_root old_ifs
  workspace="${JAIL_WORKSPACE_ROOT:-/srv/agent-jails}"
  path_is_safe_storage "$workspace" || {
    echo "workspace root must be beneath /srv or /mnt: $workspace" >&2
    return 1
  }
  resolved_workspace="$(readlink -m "$workspace")" || return 1
  path_is_safe_storage "$resolved_workspace" || {
    echo "workspace root resolves outside /srv or /mnt: $resolved_workspace" >&2
    return 1
  }

  [ -z "${JAIL_BIND_MOUNTS:-}" ] && return 0
  config_root="$(readlink -m /boot/config/plugins/incus/bind-mounts)" || return 1
  old_ifs="$IFS"
  IFS=,
  for item in $JAIL_BIND_MOUNTS; do
    IFS=: read -r host target mode extra <<<"$item"
    IFS="$old_ifs"
    if [ -z "$host" ] || [ -z "$target" ] || [ -n "$extra" ]; then
      echo "invalid bind mount '$item' (expected host:container[:ro|rw])" >&2
      return 1
    fi
    mode="${mode:-ro}"
    case "$host" in /*) ;; *) echo "bind source must be absolute: $host" >&2; return 1 ;; esac
    case "$target" in /*) ;; *) echo "bind target must be absolute: $target" >&2; return 1 ;; esac
    case "$host:$target" in *[!A-Za-z0-9_./:-]*) echo "unsupported character in bind mount: $item" >&2; return 1 ;; esac
    case "$mode" in ro|rw) ;; *) echo "bind mode must be ro or rw: $item" >&2; return 1 ;; esac
    [ -e "$host" ] || { echo "bind source does not exist: $host" >&2; return 1; }
    resolved_host="$(readlink -f "$host")" || return 1
    case "$resolved_host" in
      /srv/*|/mnt/*) ;;
      "$config_root"|"$config_root"/*)
        [ "$mode" = "ro" ] || {
          echo "config bind mounts must be read-only: $item" >&2
          return 1
        }
        ;;
      *)
        echo "bind source resolves outside /srv, /mnt, or ${config_root}: $host" >&2
        return 1
        ;;
    esac
    IFS=,
  done
  IFS="$old_ifs"
}
