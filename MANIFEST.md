# incus-unraid — staging tree & package manifest

Repackaged from **Debian trixie** Incus **7.0.0-5** (LTS), amd64. Same upstream
as Zabbly; Debian's `incus-base`/`incus-client` split gives a containers-only
runtime with **no bundled QEMU/SeaBIOS/swtpm VM baggage**.

## Layout (everything under a private prefix — no system-path pollution)

    /usr/local/incus/
      bin/incus                     client CLI (libc-only, ~static Go)
      bin/lxcfs                     container /proc virtualization daemon
      libexec/incus/incusd          the daemon (62 MB Go binary)
      libexec/incus/incus-user      per-user socket proxy
      libexec/incus/incus-apparmor-load
      libexec/incus/{startup,shutdown}
      libexec/lxcfs/                lxcfs helper libs
      lib/                          6 BUNDLED incus-specific .so's (see below)
      incus-env.sh                  lib-scoping env (sourced, not run)
      incus-preflight.sh            host capability check (safe, read-only)
    /etc/rc.d/rc.incus              Unraid-style {start|stop|restart|status}

## The safety model (why this won't hurt the box)

1. **No shadowing of host libs.** We bundle ONLY the 6 libraries Unraid lacks
   (`liblxc`, `libcowsql`, `libraft`, `libuv`, `liblz4`, `libapparmor`) into the
   private `lib/`. `incus-env.sh` puts that dir first on `LD_LIBRARY_PATH`, then
   falls through to the host for everything standard (libc, libselinux,
   libseccomp, libsqlite3, libfuse3, ...). Crucially this env is exported ONLY
   into incusd's own process — no other binary on the system sees these .so's.
2. **RAM-boot escape hatch.** Nothing here is installed to persistent OS disk.
   Unraid rebuilds `/usr` from the flash on every boot; a bad state is cleared
   by a reboot. Persistent DATA lives in `$INCUS_DIR` on the array.
3. **Preflight gate.** `rc.incus start` refuses to launch if glibc < 2.38, a
   required host lib is missing, or incusd has any unresolved link. Fails loud,
   changes nothing.
4. **Pure userspace.** Zero kernel modules shipped; relies on the running
   kernel's userns/cgroup2/veth/netfilter.

## Bundled libs (host does NOT provide these)

    liblxc.so.1 -> .1.9.0        LXC runtime (container backend)
    libcowsql.so.0 -> .0.0.1     Incus's raft/SQLite fork (the state DB)
    libraft.so.0 -> .0.0.0       raft consensus (cowsql dep)
    libuv.so.1 -> .1.0.0         async I/O (raft dep)
    liblz4.so.1 -> .1.10.0       compression (raft dep)
    libapparmor.so.1 -> .1.30.7  liblxc NEEDs it even though Unraid has no AppArmor

## Host-provided (verified by preflight, bundle if a check ever fails)

    libc/ld-linux, libgcc_s, libcap, libacl, libudev, libsqlite3, libseccomp,
    libselinux, libdbus-1, libfuse3, libbsd, libaudit

## Open items before this is production-clean

- **uidmap**: `newuidmap`/`newgidmap` + `/etc/subuid`/`/etc/subgid` for
  unprivileged containers. Preflight detects; bundle `uidmap` if Unraid lacks it.
- **Networking**: init with NO managed bridge; attach containers to Unraid's
  existing `br0` so incusd never touches host networking. (`incus admin init`
  preseed — to be written into the .plg.)
- **incus admin init preseed**: storage pool on a dedicated ZFS dataset, not
  pool root.
- This tree is the payload the `.plg` lays down from
  `/boot/config/plugins/incus/` on each array start.
