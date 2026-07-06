#!/bin/bash
# incus-preflight.sh — verify the host can actually run incusd BEFORE we start it.
# Prints a clear pass/fail report. Non-zero exit = do not start the daemon.
# Nothing here mutates the system; it only inspects.

PREFIX="/usr/local/incus"
FAIL=0
say() { printf '  %-22s %s\n' "$1" "$2"; }

echo "== Incus preflight =="

# 1) glibc >= 2.38 (incusd requires libc6 >= 2.38)
GLIBC="$(ldd --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+' | head -1)"
if [ -n "$GLIBC" ] && awk "BEGIN{exit !($GLIBC >= 2.38)}"; then
  say "glibc $GLIBC" "OK (>= 2.38)"
else
  say "glibc ${GLIBC:-unknown}" "FAIL — incusd needs >= 2.38"; FAIL=1
fi

# 2) Host-provided standard libs the bundle does NOT ship (relies on host).
#    We only bundle the incus-specific closure; these must exist on Unraid.
for lib in libselinux.so.1 libseccomp.so.2 libsqlite3.so.0 libudev.so.1 \
           libcap.so.2 libacl.so.1 libdbus-1.so.3 libfuse3.so.4 \
           libgcc_s.so.1 libbsd.so.0 libaudit.so.1; do
  if ldconfig -p 2>/dev/null | grep -q "$lib" || \
     find /lib /lib64 /usr/lib /usr/lib64 -name "$lib" 2>/dev/null | grep -q .; then
    say "$lib" "found"
  else
    say "$lib" "MISSING — bundle it into ${PREFIX}/lib"; FAIL=1
  fi
done

# 3) Confirm our bundled loader resolves for incusd (catches any lib we missed).
if command -v ldd >/dev/null; then
  MISS="$(LD_LIBRARY_PATH="${PREFIX}/lib" ldd "${PREFIX}/libexec/incus/incusd" 2>/dev/null | awk '/not found/{print $1}')"
  if [ -z "$MISS" ]; then say "incusd link" "all resolved"; else
    say "incusd link" "UNRESOLVED: $MISS"; FAIL=1; fi
fi

# 4) cgroup v2 (incus 7.x prefers unified hierarchy).
CG="$(stat -fc %T /sys/fs/cgroup 2>/dev/null)"
if [ "$CG" = "cgroup2fs" ]; then say "cgroup" "v2 (unified) OK"
else say "cgroup" "v1/hybrid ($CG) — works but deprecated"; fi

# 5) user namespaces (needed for unprivileged containers).
if [ "$(cat /proc/sys/kernel/unprivileged_userns_clone 2>/dev/null || echo 1)" = "1" ]; then
  say "userns" "enabled"
else
  say "userns" "disabled — only privileged containers will work"
fi

# 6) subuid/subgid + uid-mapping helpers (unprivileged containers).
if command -v newuidmap >/dev/null && command -v newgidmap >/dev/null; then
  say "uidmap" "newuidmap/newgidmap present"
else
  say "uidmap" "absent — bundle uidmap for unprivileged containers"
fi

echo ""
[ "$FAIL" = 0 ] && echo "PREFLIGHT: PASS" || echo "PREFLIGHT: FAIL (see above)"
exit $FAIL
