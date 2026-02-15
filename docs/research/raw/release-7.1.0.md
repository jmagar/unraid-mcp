[Skip to main content](https://docs.unraid.net/unraid-os/release-notes/7.1.0#__docusaurus_skipToContent_fallback)

On this page

This release adds wireless networking, the ability to import TrueNAS and other foreign pools, multiple enhancements to VMs, early steps toward making the webGUI responsive, and more.

Upgrading[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#upgrading "Direct link to Upgrading")

---------------------------------------------------------------------------------------------------------

### Known issues[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#known-issues "Direct link to Known issues")

This release has a potential data-loss issue where the recent "mover empty disk" feature does not handle split levels on shares correctly. Resolved in 7.1.2.

#### Plugins[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#plugins "Direct link to Plugins")

Please upgrade all plugins, particularly Unraid Connect and the Nvidia driver.

For other known issues, see the [7.0.0 release notes](https://docs.unraid.net/unraid-os/release-notes/7.0.0/#known-issues)
.

### Rolling back[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#rolling-back "Direct link to Rolling back")

We are making improvements to how we distribute patches between releases, so the standalone Patch Plugin will be uninstalled from this release. If rolling back to an earlier release we'd recommend reinstalling it. More details to come.

If rolling back earlier than 7.0.0, also see the [7.0.0 release notes](https://docs.unraid.net/unraid-os/release-notes/7.0.0/#rolling-back)
.

Changes vs. [7.0.1](https://docs.unraid.net/unraid-os/release-notes/7.0.1/)
[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#changes-vs-701 "Direct link to changes-vs-701")

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Storage[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#storage "Direct link to Storage")

*   Import foreign ZFS pools such as TrueNAS, Proxmox, Ubuntu, QNAP.
*   Import the largest partition on disk instead of the first.
*   Removing device from btrfs raid1 or zfs single-vdev mirror will now reduce pool slot count.

#### Other storage changes[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#other-storage-changes "Direct link to Other storage changes")

*   Fix: Disabled disks were not shown on the Dashboard.
*   Fix: Initially, only the first pool device spins down after adding a custom spin down setting.
*   Fix: Array Start was permitted if only 2 Parity devices and no Data devices.
*   Fix: The parity check notification often shows the previous parity check and not the current parity check.
*   Fix: Resolved certain instances of _Wrong pool State. Too many wrong or missing devices_ when upgrading.
*   Fix: Not possible to replace a zfs device from a smaller vdev.
*   mover:
    *   Fix: Resolved issue with older share.cfg files that prevented mover from running.
    *   Fix: mover would fail to recreate hard link if parent directory did not already exist.
    *   Fix: mover would hang on named pipes.
    *   Fix: [Using mover to empty an array disk](https://docs.unraid.net/unraid-os/release-notes/7.0.0/#using-mover-to-empty-an-array-disk)
         now only moves top level folders that have a corresponding share.cfg file, also fixed a bug that prevented the list of files _not moved_ from displaying.

### Networking[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#networking "Direct link to Networking")

#### Wireless Networking[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#wireless-networking "Direct link to Wireless Networking")

Unraid now supports WiFi! A hard wired connection is typically preferred, but if that isn't possible for your situation you can now setup WiFi.

For the initial setup you will either need a local keyboard/monitor (boot into GUI mode) or a wired connection. In the future, the USB Creator will be able to configure wireless networking prior to the initial boot.

*   Access the webGUI and visit _**Settings → Network Settings → Wireless wlan0**_
    *   First, enable WiFi
    *   The **Regulatory Region** can generally be left to **Automatic**, but set it to your location if the network you want to connect to is not available
    *   Find your preferred network and click the **Connect to WiFi network** icon
    *   Fill in your WiFi password and other settings, then press **Join this network**
    *   Note: if your goal is to use Docker containers over WiFi, unplug any wired connection before starting Docker

Additional details

*   WPA2/WPA3 and WPA2/WPA3 Enterprise are supported, if both WPA2 and WPA3 are available then WPA3 is used.
*   Having both wired and wireless isn't recommended for long term use, it should be one or the other. But if both connections use DHCP and you (un)plug a network cable while wireless is configured, the system (excluding Docker) should adjust within 45-60 seconds.
*   Wireless chipset support: We expect to have success with modern WiFi adapters, but older adapters may not work. If your WiFi adapter isn't detected, please start a new forum thread and provide your diagnostics so it can be investigated.
*   If you want to use a USB WiFi adapter, see this list of [USB WiFi adapters that are supported with Linux in-kernel drivers](https://github.com/morrownr/USB-WiFi/blob/main/home/USB_WiFi_Adapters_that_are_supported_with_Linux_in-kernel_drivers.md)
    
*   Advanced: New firmware files placed in `/boot/config/firmware/` will be copied to `/lib/firmware/` before driver modules are loaded (existing files will not be overwritten).

Limitations: there are networking limitations when using wireless, as a wlan can only have a single mac address.

*   Only one wireless NIC is supported, wlan0
*   wlan0 is not able to participate in a bond
*   Docker containers
    *   On _**Settings → Docker**_, note that when wireless is enabled, the system will ignore the **Docker custom network type** setting and always use **ipvlan** (macvlan is not possible because wireless does not support multiple mac addresses on a single interface)
    *   _**Settings → Docker**_, **Host access to custom networks** must be disabled
    *   A Docker container's **Network Type** cannot use br0/bond0/eth0
    *   Docker has a limitation that it cannot participate in two networks that share the same subnet. If switching between wired and wireless, you will need to restart Docker and reconfigure all existing containers to use the new interface. We recommend setting up either wired or wireless and not switching.
*   VMs
    *   We recommend setting your VM **Network Source** to **virbr0**, there are no limits to how many VMs you can run in this mode. The VMs will have full network access, the downside is they will not be accessible from the network. You can still access them via VNC to the host.
    *   With some manual configuration, a single VM can be made accessible on the network:
        *   Configure the VM with a static IP address
        *   Configure the same IP address on the ipvtap interface, type: `ip addr add IP-ADDRESS dev shim-wlan0`

#### Other networking changes[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#other-networking-changes "Direct link to Other networking changes")

*   On _**Settings → Network Settings**_, you can now adjust the server's DNS settings without stopping other services first. See the top of the **eth0** section.
*   When configuring a network interface, each interface has an **Info** button showing details for the current connection.
*   When configuring a network interface, the **Desired MTU** field is disabled until you click **Enable jumbo frames**. Hover over the icon for a warning about changing the MTU, in most cases it should be left at the default setting.
*   When configuring multiple network interfaces, by default the additional interfaces will have their gateway disabled, this is a safe default that works on most networks where a single gateway is required. If an additional gateway is enabled, it will be given a higher metric than existing gateways so there are no conflicts. You can override as needed.
*   Old network interfaces are automatically removed from config files when you save changes to _**Settings → Network Settings**_.
*   Fix various issues with DHCP.

### VM Manager[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#vm-manager "Direct link to VM Manager")

#### Nouveau GPU driver[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#nouveau-gpu-driver "Direct link to Nouveau GPU driver")

The Nouveau driver for Nvidia GPUs is now included, disabled by default as we expect most users to want the Nvidia driver instead. To enable it, uninstall the Nvidia driver plugin and run `touch /boot/config/modprobe.d/nouveau.conf` then reboot.

#### VirGL[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#virgl "Direct link to VirGL")

You can now share Intel and AMD GPUs between multiple Linux VMs at the same time using VirGL, the virtual 3D OpenGL renderer. When used this way, the GPU will provide accelerated graphics but will not output on the monitor. Note that this does not yet work with Windows VMs or the standard Nvidia plugin (it does work with Nvidia GPUs using the Nouveau driver though).

To use the virtual GPU in a Linux VM, edit the VM template and set the **Graphics Card** to **Virtual**. Then set the **VM Console Video Driver** to **Virtio(3d)** and select the appropriate **Render GPU** from the list of available GPUs (note that GPUs bound to VFIO-PCI or passed through to other VMs cannot be chosen here, and Nvidia GPUs are available only if the Nouveau driver is enabled).

#### QXL Virtual GPUs[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#qxl-virtual-gpus "Direct link to QXL Virtual GPUs")

To use this feature in a VM, edit the VM template and set the **Graphics Card** to **Virtual** and the **VM Console Video Driver** to **QXL (Best)**, you can then choose how many screens it supports and how much memory to allocate to it.

#### CPU Pinning is optional[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#cpu-pinning-is-optional "Direct link to CPU Pinning is optional")

CPU pinning is now optional, if no cores are pinned to a VM then the OS chooses which cores to use.

From _**Settings → CPU Settings**_ or when editing a VM, press **Deselect All** to unpin all cores for this VM and set the number of vCPUs to 1, increase as needed.

### User VM Templates[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#user-vm-templates "Direct link to User VM Templates")

To create a user template:

*   Edit the VM, choose **Create Modify Template** and give it a name. It will now be stored as a **User Template**, available on the **Add VM** screen.

To use a user template:

*   From the VM listing, press **Add VM**, then choose the template from the **User Templates** area.

Import/Export

*   From the **Add VM** screen, hover over a user template and click the arrow to export the template to a location on the server or download it.
*   On another Unraid system press **Import from file** or **Upload** to use the template.

#### Other VM changes[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#other-vm-changes "Direct link to Other VM changes")

*   When the **Primary** GPU is assigned as passthrough for a VM, warn that it may not work without loading a compatible vBIOS.
*   Fix: Remove confusing _Path does not exist_ message when setting up the VM service
*   Feat: Unraid VMs can now boot into GUI mode, when using the QXL video driver
*   Fix: Could not change VM icon when using XML view

### WebGUI[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#webgui "Direct link to WebGUI")

#### CSS changes[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#css-changes "Direct link to CSS changes")

As a step toward making the webGUI responsive, we have reworked the CSS. For the most part, this should not be noticeable aside from some minor color adjustments. We expect that most plugins will be fine as well, although plugin authors may want to review [this documentation](https://github.com/unraid/webgui/blob/master/emhttp/plugins/dynamix/styles/themes/README.md)
. Responsiveness will continue to be improved in future releases.

If you notice alignment issues or color problems in any official theme, please let us know.

#### nchan out of shared memory issues[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#nchan-out-of-shared-memory-issues "Direct link to nchan out of shared memory issues")

We have made several changes that should prevent this issue, and if we detect that it happens, we restart nginx in an attempt to automatically recover from it.

If your Main page never populates, or if you see "nchan: Out of shared memory" in your logs, please start a new forum thread and provide your diagnostics. You can optionally navigate to _**Settings → Display Settings**_ and disable **Allow realtime updates on inactive browsers**; this prevents your browser from requesting certain updates once it loses focus. When in this state you will see a banner saying **Live Updates Paused**, simply click on the webGUI to bring it to the foreground and re-enable live updates. Certain pages will automatically reload to ensure they are displaying the latest information.

#### Other WebGUI changes[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#other-webgui-changes "Direct link to Other WebGUI changes")

*   Fix: AdBlockers could prevent Dashboard from loading
*   Fix: Under certain circumstances, browser memory utilization on the Dashboard could exponentially grow
*   Fix: Prevent corrupted config file from breaking the Dashboard

Misc[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#misc "Direct link to Misc")

------------------------------------------------------------------------------------------

### Other changes[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#other-changes "Direct link to Other changes")

*   On _**Settings → Date and Time**_ you can now sync your clock with a **PTP** server (we expect most users will continue to use **NTP**)
*   Upgraded to jQuery 3.7.1 and jQuery UI 1.14.1
*   Fix: Visiting boot.php will no longer shutdown the server
*   Fix: On the Docker tab, the dropdown menu for the last container was truncated in certain situations
*   Fix: On _**Settings → Docker**_, deleting a **Docker directory** stored on a ZFS volume now works properly
*   Fix: On boot, custom ssh configuration copied from `/boot/config/ssh/` to `/etc/ssh/` again
*   Fix: File Manager can copy files from a User Share to an Unassigned Disk mount
*   Fix: Remove confusing _Path does not exist_ message when setting up the Docker service
*   Fix: update `rc.messagebus` to correct handling of `/etc/machine-id`
*   Diagnostics
    *   Fix: Improved anonymization of IPv6 addresses in diagnostics
    *   Fix: Improved anonymization of user names in certain config files in diagnostics
    *   Fix: diagnostics could fail due to multibyte strings in syslog
    *   Feat: diagnostics now logs errors in logs/diagnostics.error.log

### Linux kernel[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#linux-kernel "Direct link to Linux kernel")

*   version 6.12.24-Unraid
    
    *   Apply: \[PATCH\] [Revert "PCI: Avoid reset when disabled via sysfs"](https://lore.kernel.org/lkml/20250414211828.3530741-1-alex.williamson@redhat.com/)
        
    *   CONFIG\_NR\_CPUS: increased from 256 to 512
    *   CONFIG\_TEHUTI\_TN40: Tehuti Networks TN40xx 10G Ethernet adapters
    *   CONFIG\_DRM\_XE: Intel Xe Graphics
    *   CONFIG\_UDMABUF: userspace dmabuf misc driver
    *   CONFIG\_DRM\_NOUVEAU: Nouveau (NVIDIA) cards
    *   CONFIG\_DRM\_QXL: QXL virtual GPU
    *   CONFIG\_EXFAT\_FS: exFAT filesystem support
    *   CONFIG\_PSI: Pressure stall information tracking
    *   CONFIG\_PSI\_DEFAULT\_DISABLED: Require boot parameter to enable pressure stall information tracking, i.e., `psi=1`
    *   CONFIG\_ENCLOSURE\_SERVICES: Enclosure Services
    *   CONFIG\_SCSI\_ENCLOSURE: SCSI Enclosure Support
    *   CONFIG\_DRM\_ACCEL: Compute Acceleration Framework
    *   CONFIG\_DRM\_ACCEL\_HABANALABS: HabanaLabs AI accelerators
    *   CONFIG\_DRM\_ACCEL\_IVPU: Intel NPU (Neural Processing Unit)
    *   CONFIG\_DRM\_ACCEL\_QAIC: Qualcomm Cloud AI accelerators
    *   zfs: version 2.3.1
*   Wireless support
    
    *   Atheros/Qualcomm
    *   Broadcom
    *   Intel
    *   Marvell
    *   Microtek
    *   Realtek

### Base distro updates[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#base-distro-updates "Direct link to Base distro updates")

*   aaa\_glibc-solibs: version 2.41
*   adwaita-icon-theme: version 48.0
*   at-spi2-core: version 2.56.1
*   bind: version 9.20.8
*   btrfs-progs: version 6.14
*   ca-certificates: version 20250425
*   cairo: version 1.18.4
*   cifs-utils: version 7.3
*   coreutils: version 9.7
*   dbus: version 1.16.2
*   dbus-glib: version 0.114
*   dhcpcd: version 9.5.2
*   diffutils: version 3.12
*   dnsmasq: version 2.91
*   docker: version 27.5.1
*   e2fsprogs: version 1.47.2
*   elogind: version 255.17
*   elfutils: version 0.193
*   ethtool: version 6.14
*   firefox: version 128.10 (AppImage)
*   floppy: version 5.6
*   fontconfig: version 2.16.2
*   gdbm: version 1.25
*   git: version 2.49.0
*   glib2: version 2.84.1
*   glibc: version 2.41
*   glibc-zoneinfo: version 2025b
*   grep: version 3.12
*   gtk+3: version 3.24.49
*   gzip: version 1.14
*   harfbuzz: version 11.1.0
*   htop: version 3.4.1
*   icu4c: version 77.1
*   inih: version 60
*   intel-microcode: version 20250211
*   iperf3: version 3.18
*   iproute2: version 6.14.0
*   iw: version 6.9
*   jansson: version 2.14.1
*   kernel-firmware: version 20250425\_cf6ea3d
*   kmod: version 34.2
*   less: version 674
*   libSM: version 1.2.6
*   libX11: version 1.8.12
*   libarchive: version 3.7.8
*   libcgroup: version 3.2.0
*   libedit: version 20250104\_3.1
*   libevdev: version 1.13.4
*   libffi: version 3.4.8
*   libidn: version 1.43
*   libnftnl: version 1.2.9
*   libnvme: version 1.13
*   libgpg-error: version 1.55
*   libpng: version 1.6.47
*   libseccomp: version 2.6.0
*   liburing: version 2.9
*   libusb: version 1.0.28
*   libuv: version 1.51.0
*   libvirt: version 11.2.0
*   libXft: version 2.3.9
*   libxkbcommon: version 1.9.0
*   libxml2: version 2.13.8
*   libxslt: version 1.1.43
*   libzip: version 1.11.3
*   linuxptp: version 4.4
*   lvm2: version 2.03.31
*   lzip: version 1.25
*   lzlib: version 1.15
*   mcelog: version 204
*   mesa: version 25.0.4
*   mpfr: version 4.2.2
*   nano: version 8.4
*   ncurses: version 6.5\_20250419
*   nettle: version 3.10.1
*   nghttp2: version 1.65.0
*   nghttp3: version 1.9.0
*   noto-fonts-ttf: version 2025.03.01
*   nvme-cli: version 2.13
*   oniguruma: version 6.9.10
*   openssh: version 10.0p1
*   openssl: version 3.5.0
*   ovmf: version stable202502
*   pam: version 1.7.0
*   pango: version 1.56.3
*   parted: version 3.6
*   patch: version 2.8
*   pcre2: version 10.45
*   perl: version 5.40.2
*   php: version 8.3.19
*   procps-ng: version 4.0.5
*   qemu: version 9.2.3
*   rsync: version 3.4.1
*   samba: version 4.21.3
*   shadow: version 4.17.4
*   spice: version 0.15.2
*   spirv-llvm-translator: version 20.1.0
*   sqlite: version 3.49.1
*   sysstat: version 12.7.7
*   sysvinit: version 3.14
*   talloc: version 2.4.3
*   tdb: version 1.4.13
*   tevent: version 0.16.2
*   tree: version 2.2.1
*   userspace-rcu: version 0.15.2
*   utempter: version 1.2.3
*   util-linux: version 2.41
*   virglrenderer: version 1.1.1
*   virtiofsd: version 1.13.1
*   which: version 2.23
*   wireless-regdb: version 2025.02.20
*   wpa\_supplicant: version 2.11
*   xauth: version 1.1.4
*   xf86-input-synaptics: version 1.10.0
*   xfsprogs: version 6.14.0
*   xhost: version 1.0.10
*   xinit: version 1.4.4
*   xkeyboard-config: version 2.44
*   xorg-server: version 21.1.16
*   xterm: version 398
*   xtrans: version 1.6.0
*   xz: version 5.8.1
*   zstd: version 1.5.7

Patches[​](https://docs.unraid.net/unraid-os/release-notes/7.1.0#patches "Direct link to Patches")

---------------------------------------------------------------------------------------------------

No patches are currently available for this release.

*   [Upgrading](https://docs.unraid.net/unraid-os/release-notes/7.1.0#upgrading)
    *   [Known issues](https://docs.unraid.net/unraid-os/release-notes/7.1.0#known-issues)
        
    *   [Rolling back](https://docs.unraid.net/unraid-os/release-notes/7.1.0#rolling-back)
        
*   [Changes vs. 7.0.1](https://docs.unraid.net/unraid-os/release-notes/7.1.0#changes-vs-701)
    *   [Storage](https://docs.unraid.net/unraid-os/release-notes/7.1.0#storage)
        
    *   [Networking](https://docs.unraid.net/unraid-os/release-notes/7.1.0#networking)
        
    *   [VM Manager](https://docs.unraid.net/unraid-os/release-notes/7.1.0#vm-manager)
        
    *   [User VM Templates](https://docs.unraid.net/unraid-os/release-notes/7.1.0#user-vm-templates)
        
    *   [WebGUI](https://docs.unraid.net/unraid-os/release-notes/7.1.0#webgui)
        
*   [Misc](https://docs.unraid.net/unraid-os/release-notes/7.1.0#misc)
    *   [Other changes](https://docs.unraid.net/unraid-os/release-notes/7.1.0#other-changes)
        
    *   [Linux kernel](https://docs.unraid.net/unraid-os/release-notes/7.1.0#linux-kernel)
        
    *   [Base distro updates](https://docs.unraid.net/unraid-os/release-notes/7.1.0#base-distro-updates)
        
*   [Patches](https://docs.unraid.net/unraid-os/release-notes/7.1.0#patches)