# incus-unraid — staging tree & package manifest

Repackaged from **Debian trixie** Incus **7.0.0** (LTS), amd64, plus a bundled
`distrobuilder` toolchain for the settings UI's custom image builder. Same
upstream as Zabbly; Debian's `incus-base`/`incus-client` split gives a
containers-only runtime with **no bundled QEMU/SeaBIOS/swtpm VM baggage**.
Current package build: `incus-unraid-7.0.0-40-x86_64-1.txz` (see `incus.plg`'s
`txz`/`md5` entities for the version actually pinned for install).

## Layout (everything under a private prefix — no system-path pollution)

    /usr/local/incus/
      bin/incus                     client CLI (libc-only, ~static Go)
      bin/lxcfs                     container /proc virtualization daemon
      bin/distrobuilder              image builder (18 MB Go binary, Builder tab)
      bin/debootstrap, bin/ar        distrobuilder deps (Debian/derivative rootfs bootstrap)
      bin/mksquashfs, bin/unsquashfs squashfs (image import/export, rootfs unpack)
      bin/nft                        nftables CLI (LAN-ban ACL backend)
      libexec/incus/incusd           the daemon (Go binary)
      libexec/incus/incus-user       per-user socket proxy
      libexec/incus/incus-apparmor-load
      libexec/incus/{startup,shutdown}
      libexec/lxcfs/                 lxcfs helper libs
      lib/                           ~30 BUNDLED .so's (see below)
      share/debootstrap/             debootstrap's per-release scripts (trixie, bookworm, ...)
      incus-env.sh                   lib/PATH-scoping env (sourced, not run)
      incus-preflight.sh             host capability check (safe, read-only)
      MANIFEST.md                    this file, shipped for on-box reference
    /etc/rc.d/rc.incus                symlinked to the plugin's rc.incus script

Also shipped in the same `.txz`, outside `/usr/local/incus/`:

    /usr/lib/x86_64-linux-gnu/lxcfs/liblxcfs.so   lxcfs FUSE module (host loader path, not scoped)
    /usr/local/emhttp/plugins/incus/               settings page, scripts, event hooks, incus.cfg,
                                                     built Vue 3 frontend (web/incus-settings.{js,css})

## The safety model (why this won't hurt the box)

1. **No shadowing of host libs for incusd's own libs.** The Incus-specific
   shared libraries Unraid doesn't ship (`liblxc`, `libcowsql`, `libraft`,
   `libuv`, `liblz4`, `libapparmor`, plus additional deps pulled in by
   `distrobuilder`/`nft`/`mksquashfs`) live in the private `lib/`.
   `incus-env.sh` puts that dir first on `LD_LIBRARY_PATH`, then falls through
   to the host for everything standard (libc, libselinux, libseccomp,
   libsqlite3, libfuse3, ...). This env is exported ONLY into incusd's own
   process (via the wrapper / rc script) — no other binary on the system sees
   these .so's.
2. **RAM-boot escape hatch.** Nothing here is installed to persistent OS disk.
   Unraid rebuilds `/usr` from the flash on every boot; a bad state is cleared
   by a reboot. Persistent DATA lives in `$INCUS_DIR` (`/mnt/user/appdata/incus`
   by default) on the array.
3. **Preflight gate.** `rc.incus start` refuses to launch if glibc < 2.38, a
   required host lib is missing, `unsquashfs`/`nft` aren't on `PATH`, or
   incusd has any unresolved link. Fails loud, changes nothing. See
   `incus-preflight.sh` for the exact checklist.
4. **Pure userspace.** Zero kernel modules shipped; relies on the running
   kernel's userns/cgroup2/veth/netfilter.

## Bundled libs (partial list — host does NOT reliably provide these)

    liblxc.so.1 -> .1.9.0        LXC runtime (container backend)
    libcowsql.so.0 -> .0.0.1     Incus's raft/SQLite fork (the state DB)
    libraft.so.0 -> .0.0.0       raft consensus (cowsql dep)
    libuv.so.1 -> .1.0.0         async I/O (raft dep)
    liblz4.so.1 -> .1.10.0       compression (raft dep)
    libapparmor.so.1 -> .1.30.7  liblxc NEEDs it even though Unraid has no AppArmor
    libnftables.so.1, libnftnl.so.11, libmnl.so.0, libxtables.so.12
                                  nftables CLI deps (LAN-ban ACL)
    libfuse3.so.3.17.2 / .so.4   FUSE (lxcfs, unsquashfs)
    libselinux.so.1, libaudit.so.1, libcap-ng.so.0
                                  bundled as a fallback where the host copy is missing/old
    libzstd.so.1, liblzma.so.5, liblzo2.so.2, libz.so.1
                                  compression backends (mksquashfs, distrobuilder)
    libgmp.so.10, libjansson.so.4, libedit.so.2, libpcre2-8.so.0,
    libmd.so.0, libxxhash.so.0, libtinfo.so.6, libsframe.so.1, libbfd-2.44-system.so
                                  transitive deps of nft/mksquashfs/distrobuilder

Full current list: `tar -tJf packages/incus-unraid-*.txz | grep '/lib/'`.

## Preflight checklist (see `incus-preflight.sh`, source of truth)

    glibc >= 2.38
    libselinux.so.1, libseccomp.so.2, libsqlite3.so.0, libudev.so.1,
      libcap.so.2, libacl.so.1, libdbus-1.so.3, libfuse3.so.4,
      libgcc_s.so.1, libbsd.so.0, libaudit.so.1     (bundled OR host — both checked)
    unsquashfs on PATH        (missing => image/rootfs unpack hangs, not fails)
    nft on PATH                (missing => ACL create/edit hangs, not fails)
    incusd fully link-resolved (ldd re-check against the bundled LD_LIBRARY_PATH)
    cgroup v2 (unified) preferred; v1/hybrid works but is flagged
    user namespaces enabled    (else only privileged containers work)
    newuidmap/newgidmap present (else flagged, not fatal — unprivileged containers degrade)

## Open items

- **uidmap**: `newuidmap`/`newgidmap` + `/etc/subuid`/`/etc/subgid` for
  unprivileged containers. Preflight detects and flags but does not fail the
  gate; bundle `uidmap` if a target box lacks it.
- This tree is the payload the `.plg` lays down from
  `/boot/config/plugins/incus/` on each array start (via `upgradepkg
  --install-new`, gated on the build number in the txz filename changing).
