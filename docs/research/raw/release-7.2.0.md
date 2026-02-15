[Skip to main content](https://docs.unraid.net/unraid-os/release-notes/7.2.0#__docusaurus_skipToContent_fallback)

On this page

The Unraid webGUI is now responsive! The interface automatically adapts to different screen sizes, making it usable on mobile devices, tablets, and desktop monitors alike. The Unraid API is now built in, and the release also brings RAIDZ expansion, Ext2/3/4, NTFS and exFAT support, and the (optional) ability to login to the webGUI via SSO, among other features and bug fixes.

Note that some plugins may have visual issues in this release; please give plugin authors time to make adjustments. Plugin authors, please see this post describing [how to update your plugins to make them responsive](https://forums.unraid.net/topic/192172-responsive-webgui-plugin-migration-guide/)
.

Upgrading[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#upgrading "Direct link to Upgrading")

---------------------------------------------------------------------------------------------------------

For step-by-step instructions, see [Upgrading Unraid](https://docs.unraid.net/unraid-os/system-administration/maintain-and-update/upgrading-unraid/)
. Questions about your [license](https://docs.unraid.net/unraid-os/troubleshooting/licensing-faq/#license-types--features)
?

### Known issues[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#known-issues "Direct link to Known issues")

#### Plugins[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#plugins "Direct link to Plugins")

The Theme Engine, Dark Theme, Dynamix Date Time, and Flash Remount plugins are incompatible and will be automatically uninstalled, as will outdated versions of Unraid Connect.

Please upgrade all plugins, particularly Unraid Connect and the Nvidia driver, before updating. Note that some plugins may have visual issues in this release; please give plugin authors time to make adjustments.

For other known issues, see the [7.1.4 release notes](https://docs.unraid.net/unraid-os/release-notes/7.1.4/#known-issues)
.

### Rolling back[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#rolling-back "Direct link to Rolling back")

If rolling back earlier than 7.1.4, also see the [7.1.4 release notes](https://docs.unraid.net/unraid-os/release-notes/7.1.4/#rolling-back)
.

Changes vs. [7.1.4](https://docs.unraid.net/unraid-os/release-notes/7.1.4/)
[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#changes-vs-714 "Direct link to changes-vs-714")

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Storage[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#storage "Direct link to Storage")

#### ZFS RAIDZ expansion[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#zfs-raidz-expansion "Direct link to ZFS RAIDZ expansion")

You can now expand your single-vdev RAIDZ1/2/3 pools, one drive at a time. For detailed instructions, see [RAIDZ expansion](https://docs.unraid.net/unraid-os/release-notes/7.2.0/warn/)
.

*   With the array running, on **_Main → Pool Devices_**, select the pool name to view the details
*   In the **Pool Status** area, check for an **Upgrade Pool** button. If one exists, you'll need to click that before continuing. Note that upgrading the pool will limit your ability to downgrade to earlier releases of Unraid (7.1 should be OK, but not 7.0)
*   Stop the array
*   On **_Main → Pool Devices_**, add a slot to the pool
*   Select the appropriate drive (must be at least as large as the smallest drive in the pool)
*   Start the array

#### Enhancements[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#enhancements "Direct link to Enhancements")

*   Fix: There will now be an "invalid expansion" warning if the pool needs to be upgraded first
*   Improvement: Better defaults for ZFS RAIDZ vdevs

#### Ext2/3/4, NTFS, and exFAT Support[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#ext234-ntfs-and-exfat-support "Direct link to Ext2/3/4, NTFS, and exFAT Support")

Unraid now supports Ext2/3/4, NTFS, and exFAT drive formats in addition to XFS, BTRFS, and ZFS.

Use case: say you are a content creator with a box full of hard drives containing all of your historical videos. When first creating an array (or after running **_Tools → New Config_**), add all of your existing data drives (blank, or with data in a supported drive format) to the array. Any parity drives will be overwritten but the data drives will retain their data. You can enjoy parity protection, share them on the network, and take full advantage of everything Unraid has to offer.

Critical note: you can continue adding filled data drives to the array up until you start the array with a parity drive installed. Once a parity drive has been added, any new data drives will be zeroed out when they are added to the array.

To clarify, Unraid has always worked this way; what is new is that Unraid now supports additional drive formats.

Additionally, you can create single drive pools using the new formats as well.

*   Improved the usability of the **File System Type** dropdown as the list of available options is growing

#### Warn about deprecated file systems[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#warn-about-deprecated-file-systems "Direct link to Warn about deprecated file systems")

The **_Main_** page will now warn if any array or pool drives are formatted with ReiserFS; these drives need to be migrated to another filesystem ASAP as they will not be usable in a future release of Unraid (likely Unraid 7.3). Similarly, it will warn if there are drives formatted in a deprecated version of XFS; those need to be migrated before 2030. See [Converting to a new file system type](https://docs.unraid.net/unraid-os/using-unraid-to/manage-storage/file-systems/#converting-to-a-new-file-system-type)
 in the docs for details.

#### Other storage changes[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#other-storage-changes "Direct link to Other storage changes")

*   Improvement: Two-device ZFS pools are mirrored by default, but you can make them RAIDZ1 if you plan to expand that vdev in the future
*   Improvement: Add **File system status** to **DeviceInfo** page, showing whether a drive is mounted/unmounted and empty/not empty
*   Fix: Display issue on Main page when two pools are named similarly
*   Fix: [glibc bug](https://github.com/openzfs/zfs/issues/17629)
     which could lead to data loss with ZFS
*   Fix: BTRFS array disks with multiple filesystem signatures don't mount
*   Fix: Resolved some issues for parity disks with existing 1MiB aligned partitions
*   Fix: When stopping array, do not attempt 'umount' on array devices that are not mounted
*   Improvement: Exclusive shares may be selected for NFS export
*   Improvement: Disallow shares named `homes`, `global`, and `printers` (these have special meaning in Samba)
*   Fix: Correct handling of case-insensitive share names
*   Fix: Shares with invalid characters in names could not be deleted or modified
*   Fix: Improvements to reading from/writing to SMB Security Settings
*   Improvement: A top-level `lost+found` directory will not be shared
*   Fix: In smb.conf, set `smb3 directory leases = no` to avoid issues with the current release of Samba
*   Fix: Restore comments in default `/etc/modprobe.d/*.conf` files
*   Fix: Windows fails to create a new folder for a share with primary=ZFS pool and secondary=EXT4 array disk
*   Fix: New devices added to an existing array with valid parity should be repartitioned
*   Fix: Do not spin down devices for which SMART self-test is in progress
*   Fix: New array device not available for shares until the array is restarted
*   Fix: ZFS allocation profile always shows one vdev only

### Networking[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#networking "Direct link to Networking")

#### Other networking changes[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#other-networking-changes "Direct link to Other networking changes")

*   Feature: IPv6 Docker custom networks now support Unique Local Addresses (ULA) in addition to the more standard Global Unicast Addresses (GUA), assuming your router provides both subnets when the Unraid host gets an IPv6 address via DHCP or SLAAC. To use, assign a custom static IP from the appropriate subnet to the container.
*   Fix: The **_Settings → Network Settings → Interface Rules_** page sometimes showed the wrong network driver (was just a display issue)

### VM Manager[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#vm-manager "Direct link to VM Manager")

*   Feature: Save PCI hardware data, warn if hardware used by VM changes
*   Feature: Support virtual sound cards in VMs

#### Other VM changes[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#other-vm-changes "Direct link to Other VM changes")

*   Improvement: Enhance multi-monitor support, automatically enabling spicevmc when needed
*   Feature: Upgrade to noVNC v1.6
*   Removed historical OpenElec and LibreElec VM templates
*   Fix: VM Console did not work when user shares were disabled
*   Fix: Don't allow single quotes in Domains storage path
*   Fix: Change Windows 11 VM defaults
*   Fix: Unable to view vdisk locations in languages other than English
*   Fix: No capacity warning when editing a VM to add a 2nd vdisk
*   Fix: Cdrom Bus: select IDE for i440 and SATA for q35

### Unraid API[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#unraid-api "Direct link to Unraid API")

The Unraid API is now built into Unraid! The new Notifications panel is the first major feature to use it, over time the entire webGUI will be updated to use it.

The Unraid API is fully open source: [https://github.com/unraid/api](https://github.com/unraid/api)
. Get started in the [API docs](https://docs.unraid.net/API/)
.

The Unraid Connect plugin adds functionality which communicates with our cloud servers; it remains completely optional.

#### Other Unraid API changes[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#other-unraid-api-changes "Direct link to Other Unraid API changes")

*   dynamix.unraid.net 4.25.3 - [see changes](https://github.com/unraid/api/releases)
    

### WebGUI[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#webgui "Direct link to WebGUI")

#### Responsive CSS[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#responsive-css "Direct link to Responsive CSS")

The Unraid webGUI is now responsive! Most screens should now work as well on your phone as they do on your desktop monitor.

#### Login to the webGUI via SSO[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#login-to-the-webgui-via-sso "Direct link to Login to the webGUI via SSO")

Login to the Unraid webGUI using Single Sign-On (SSO) with your Unraid.net account or any other OIDC-compliant provider. For details on this _optional_ feature, see [OIDC Provider Setup](https://docs.unraid.net/API/oidc-provider-setup/)
 in the Docs.

#### Other WebGUI changes[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#other-webgui-changes "Direct link to Other WebGUI changes")

*   Feature: Add new notifications management view, access via the bell in the upper right corner of the webGUI
*   Feature: Add progress indicator to Docker / Plugin / VM popup window
*   Feature: Show countdown timer on login page when locked out due to too many incorrect login attempts
*   Feature: Add _Force Install_ button to bypass version checks when manually installing plugins
*   Feature: Add **_Tools → Open Terminal_** page; can access it by searching for "terminal". Can optionally remove Terminal button from toolbar via **_Settings → Display Settings → Show Terminal Button in header_**
*   Feature: **_Users → Root → SSH authorized keys_** now supports more formats (thanks [wandercone](https://github.com/wandercone)
    )
*   Feature: Added a welcome screen for new systems, shown after setting the root password
*   Fix: Re-enable smart test buttons after completion of test
*   Fix: Prevent webGUI from crashing when dynamix.cfg is corrupt, log any issues
*   Fix: `blob:` links shouldn't be considered external
*   Feature: Differentiate between Intel E-Cores and P-Cores on the Dashboard
*   Feature: Dashboard now gets CPU usage stats from the Unraid API
*   Fix: Dashboard: More than 1TB of RAM was not reported correctly
*   Chore: Change charting libraries on the Dashboard
*   Fix: Prevent Firefox from showing resend/cancel popup when starting array (thanks [dkaser](https://github.com/dkaser)
    )
*   Fix: File Manager: stop spinner and show error when it fails (thanks [poroyo](https://github.com/poroyo)
    )
*   Feature: Speed up rendering of Plugins and Docker pages
*   Fix: Prevent issues when clicking an external link from within a changelog
*   Improvement: Show RAM and network speed in human-readable units
*   Fix: On _**Settings → Display Settings → Font size**_, remove extreme options that break the webGUI

Misc[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#misc "Direct link to Misc")

------------------------------------------------------------------------------------------

*   Feature: Do not execute `go` script when in safe mode, create `/boot/config/go.safemode` script if needed
*   Improvement: Require authentication on `http://localhost`. This improves security and allows Tailscale Funnel to work with the webGUI. Note that when booting in GUI mode, you will now need to login again to access the webGUI.
*   Feature: Add favicon and web app manifest support
*   Feature: License key upgrades are installed automatically, without needing to restart the array
*   Feature: Thunderbolt devices will be auto-authorized when connected
*   Feature: Improvements to custom udev rules and scripts, at boot:
    *   `/boot/config/udev/*.rules` are copied to `/etc/udev/rules.d/`
    *   `/boot/config/udev/*.sh` are copied to `/etc/udev/scripts/` where they can be used by your custom udev rules
*   Fix: Remove support for nonworking ipv6.hash.myunraid.net URLs
*   Fix: Docker custom network creation failed when IPv6 was enabled
*   Fix: Resolve issues with high CPU load due to nchan and lsof
*   Improvement: Removed option to disable live updates on inactive browsers; should no longer be needed
*   Improvement: Better messaging around mover and "dangling links"
*   Fix: Prevent errors related to _searchLink_ when installing plugins
*   Fix: PHP warnings importing WireGuard tunnels
*   Improvement: _Europe/Kiev_ timezone renamed to _Europe/Kyiv_ to align with the IANA Time Zone Database
*   Improvement: Enhance Discord notification agent; enable/disable the agent to get the updates (thanks [mgutt](https://github.com/mgutt)
    )
*   Fix: Further anonymization of diagnostics.zip
*   Improvement: Protect WebGUI from fatal PHP errors
*   Improvement: Adjust logging during plugin installs
*   Fix: CPU Pinning for Docker containers could crash in certain instances
*   Fix: Docker NAT failure due to missing br\_netfilter
*   Fix: Scheduled mover runs not logged

### Linux kernel[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#linux-kernel "Direct link to Linux kernel")

*   version 6.12.54-Unraid
    *   built-in: CONFIG\_EFIVAR\_FS: EFI Variable filesystem
    *   CONFIG\_INTEL\_RAPL: Intel RAPL support via MSR interface
    *   CONFIG\_NLS\_DEFAULT: change from "iso8859-1" to "utf8"
    *   Added eMMC support:
        *   CONFIG\_MMC: MMC/SD/SDIO card support
        *   CONFIG\_MMC\_BLOCK: MMC block device driver
        *   CONFIG\_MMC\_SDHCI: Secure Digital Host Controller Interface support
        *   CONFIG\_MMC\_SDHCI\_PCI: SDHCI support on PCI bus
        *   CONFIG\_MMC\_SDHCI\_ACPI: SDHCI support for ACPI enumerated SDHCI controllers
        *   CONFIG\_MMC\_SDHCI\_PLTFM: SDHCI platform and OF driver helper

### Base distro updates[​](https://docs.unraid.net/unraid-os/release-notes/7.2.0#base-distro-updates "Direct link to Base distro updates")

*   aaa\_glibc-solibs: version 2.42
*   adwaita-icon-theme: version 48.1
*   at-spi2-core: version 2.58.1
*   bash: version 5.3.003
*   bind: version 9.20.13
*   btrfs-progs: version 6.17
*   ca-certificates: version 20251003
*   cifs-utils: version 7.4
*   coreutils: version 9.8
*   cryptsetup: version 2.8.1
*   curl: version 8.16.0
*   e2fsprogs: version 1.47.3
*   ethtool: version 6.15
*   exfatprogs: version 1.3.0
*   fontconfig: version 2.17.1
*   freetype: version 2.14.0
*   gdbm: version 1.26
*   gdk-pixbuf2: version 2.44.3
*   git: version 2.51.1
*   glib2: version 2.86.0
*   glibc: version 2.42 (build 2)
*   gnutls: version 3.8.10
*   grub: version 2.12
*   gtk+3: version 3.24.51
*   harfbuzz: version 12.1.0
*   intel-microcode: version 20250812
*   iproute2: version 6.17.0
*   inih: version 61
*   inotify-tools: version 4.25.9.0
*   iputils: version 20250605
*   iw: version 6.17
*   json-glib: version 1.10.8
*   kbd: version 2.9.0
*   kernel-firmware: version 20251018\_8b4de42
*   krb5: version 1.22.1
*   less: version 685
*   libXfixes: version 6.0.2
*   libXpresent: version 1.0.2
*   libXres: version 1.2.3
*   libarchive: version 3.8.2
*   libdrm: version 2.4.127
*   libedit: version 20251016\_3.1
*   libevdev: version 1.13.5
*   libffi: version 3.5.2
*   libgpg-error: version 1.56
*   libjpeg-turbo: version 3.1.2
*   libnftnl: version 1.3.0
*   libnvme: version 1.15
*   libpng: version 1.6.50
*   libssh: version 0.11.3
*   libtiff: version 4.7.1
*   libtirpc: version 1.3.7
*   libunwind: version 1.8.3
*   liburing: version 2.12
*   libusb: version 1.0.29
*   libwebp: version 1.6.0
*   libvirt: version 11.7.0
*   libxkbcommon: version 1.11.0
*   libxml2: version 2.14.6
*   libzip: version 1.11.4
*   lsof: version 4.99.5
*   lvm2: version 2.03.35
*   mcelog: version 207
*   mesa: version 25.2.5
*   nano: version 8.6
*   ncurses: version 6.5\_20250816
*   nettle: version 3.10.2
*   nghttp2: version 1.67.1
*   nghttp3: version 1.12.0
*   noto-fonts-ttf: version 2025.10.01
*   nvme-cli: version 2.15
*   openssh: version 10.2p1
*   openssl: version 3.5.4
*   ovmf: version unraid202502
*   p11-kit: version 0.25.10
*   pam: version 1.7.1
*   pcre2: version 10.46
*   pango: version 1.56.4
*   pciutils: version 3.14.0
*   perl: version 5.42.0
*   php: version 8.3.26-x86\_64-1\_LT with gettext extension
*   pixman: version 0.46.4
*   rclone: version 1.70.1-x86\_64-1\_SBo\_LT.tgz
*   readline: version 8.3.001
*   samba: version 4.23.2
*   shadow: version 4.18.0
*   smartmontools: version 7.5
*   spirv-llvm-translator: version 21.1.1
*   sqlite: version 3.50.4
*   sudo: version 1.9.17p2
*   sysstat: version 12.7.8
*   sysvinit: version 3.15
*   tdb: version 1.4.14
*   tevent: version 0.17.1
*   userspace-rcu: version 0.15.3
*   util-linux: version 2.41.2
*   wayland: version 1.24.0
*   wireguard-tools: version 1.0.20250521
*   wireless-regdb: version 2025.10.07
*   xdpyinfo: version 1.4.0
*   xdriinfo: version 1.0.8
*   xfsprogs: version 6.16.0
*   xkeyboard-config: version 2.46
*   xorg-server: version 21.1.18
*   xterm: version 402
*   zfs: version zfs-2.3.4\_6.12.54\_Unraid-x86\_64-2\_LT

*   [Upgrading](https://docs.unraid.net/unraid-os/release-notes/7.2.0#upgrading)
    *   [Known issues](https://docs.unraid.net/unraid-os/release-notes/7.2.0#known-issues)
        
    *   [Rolling back](https://docs.unraid.net/unraid-os/release-notes/7.2.0#rolling-back)
        
*   [Changes vs. 7.1.4](https://docs.unraid.net/unraid-os/release-notes/7.2.0#changes-vs-714)
    *   [Storage](https://docs.unraid.net/unraid-os/release-notes/7.2.0#storage)
        
    *   [Networking](https://docs.unraid.net/unraid-os/release-notes/7.2.0#networking)
        
    *   [VM Manager](https://docs.unraid.net/unraid-os/release-notes/7.2.0#vm-manager)
        
    *   [Unraid API](https://docs.unraid.net/unraid-os/release-notes/7.2.0#unraid-api)
        
    *   [WebGUI](https://docs.unraid.net/unraid-os/release-notes/7.2.0#webgui)
        
*   [Misc](https://docs.unraid.net/unraid-os/release-notes/7.2.0#misc)
    *   [Linux kernel](https://docs.unraid.net/unraid-os/release-notes/7.2.0#linux-kernel)
        
    *   [Base distro updates](https://docs.unraid.net/unraid-os/release-notes/7.2.0#base-distro-updates)