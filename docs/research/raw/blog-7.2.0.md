*   [Unraid News](https://unraid.net/blog)
    

29 October 2025

Unraid OS 7.2.0 Stable is Now Available
=======================================

Unraid 7.2.0 delivers a **fully responsive web interface, expanded filesystem support, a built-in, open-source API**, **ZFS RAIDZ Expansion,** and much more! 

![7 2 Stable](https://cdn.craft.cloud/481d40bf-939a-4dc1-918d-b4d4b48b7c04/assets/uploads/7.2-Stable.png?width=788&quality=80&fit=crop&s=QslBGEL9Xr_DcPGOHkUC19ATiyuq9Bf_sOXDDtZf5iE)

**Your Server: More Responsive, Secure, and More Flexible than ever.**

Building on months of testing and feedback, this release brings major quality-of-life improvements for new and seasoned users alike. Whether you're upgrading your homelab or deploying at scale, this release brings more control, compatibility, and confidence to every system. 

We want to give a huge thanks to the _over 5,000 beta testers_ that helped bring this release to Stable.

**Fully Responsive WebGUI**
---------------------------

Unraid now adapts seamlessly to any screen size. The redesigned WebGUI ensures smooth operation across desktops, tablets, and mobile devices making it easier than ever to manage your server from anywhere, with any device.

### See the Responsive Webgui in action

**Expand Your RAIDZ Pools and Bring Every Drive With You**
----------------------------------------------------------

### **ZFS RAIDZ Expansion**

You can now expand your single-vdev RAIDZ1/2/3 pools, one drive at a time!

1.  Stop the array
2.  On _**Main → Pool Devices,**_ add a slot to the pool
3.  Select the appropriate drive. _Note: must be at least as large as the smallest drive in the pool._
4.  Start the array

### See How RAIDZ Expansion Works

### **External Drive Support: ext2/3/4, NTFS, exFAT**

Alongside XFS, BTRFS, and the ZFS file systems, Unraid now supports ext2 / ext3 / ext4, NTFS, and exFAT out of the box, making it easier to import data from external sources or legacy systems. 

This means you can _create an array or single device pool with existing drives formatted in Ext2/3/4 or NTFS, and you can format drives in Ext4 or NTFS._  

### Learn How Unraid Handles ext, NTFS, and exFAT Out of the Box

Cyber Weekend is Coming
-----------------------

Don’t miss our biggest sale of the year November 28-December 1st. Subscribe to the [Unraid Digest](https://newsletter.unraid.net/)
 and be the first to know all of the details!

[Subscribe](https://newsletter.unraid.net/)

**Unraid API**
--------------

The [**Unraid API**](https://docs.unraid.net/API/)
 is now integrated directly into Unraid OS, giving developers and power users new ways to interact with their systems.

The new **Notifications panel** is the first major feature built on this foundation, and over time, more of the webGUI will transition to use the API for faster, more dynamic updates.

The API is fully [**open source**](https://github.com/unraid/api)
, providing direct access to system data and functionality for building automations, dashboards, and third‑party integrations. It also supports [**external authentication (OIDC)**](https://docs.unraid.net/API/oidc-provider-setup/)
 for secure, scalable access. 

### See the Unraid API in Action!

Learn More about the Unraid API
-------------------------------

*   #### [Follow along the Unraid API Roadmap](https://docs.unraid.net/API/upcoming-features/)
    
*   #### [See current apps using the Unraid API](https://discord.com/channels/216281096667529216/1375651142704566282)
    

**Additional Improvements and Fixes**
-------------------------------------

### **Storage & Array**

*   Two-device ZFS pools default to mirrors; use RAIDZ1 for future vdev expansion
*   New _File System Status_ shows if drives are mounted and/or empty
*   Exclusive shares now exportable via NFS
*   Restricted special share names (homes, global, printers)
*   Improved SMB config (smb3 directory leases = no) and security settings UX
*   Better handling for parity disks with 1MiB partitions
*   BTRFS mounts more reliably with multiple FS signatures
*   New drives now repartitioned when added to parity-protected arrays
*   Devices in SMART test won’t spin down
*   Cleaner handling of case-insensitive share names and invalid characters
*   ZFS vdevs now display correctly in allocation profiles

### **VM Manager** 

*   Console access now works even when user shares are disabled
*   Single quotes are no longer allowed in the Domains storage path
*   Windows 11 defaults have been updated for better compatibility
*   Cdrom Bus now defaults to IDE for i440fx and SATA for Q35 machines
*   Vdisk locations now display properly in non-English languages
*   You'll now see a warning when adding a second vdisk if you forget to assign a capacity

### **WebGUI**

*   Network and RAM stats now shown in human-readable units
*   Font size and layout fixes
*   Better error protection for PHP-based failures

### Miscellaneous **Improvements**

*   Better logging during plugin installs
*   Added safeguards to protect WebGUI from fatal PHP errors
*   Diagnostics ZIPs are now further anonymized
*   Resolved crash related to Docker container CPU pinning
*   Fixed Docker NAT issue caused by missing br\_netfilter
*   Scheduled mover runs are now properly logged

### **Kernel & Packages**

*   Linux Kernel 6.12.54-Unraid
*   Samba 4.23.2
*   Updated versions of openssl, mesa, kernel-firmware, git, exfatprogs, and more

**Plugin Compatibility Notice**
-------------------------------

To maintain stability with the new responsive WebGUI, the following plugins will be removed during upgrade if present:

*   **Theme Engine**
*   **Dark Theme**
*   **Dynamix Date Time**
*   **Flash Remount**
*   **Outdated versions of Unraid Connect**

Please update all other plugins—**especially Unraid Connect and Nvidia Driver**—before upgrading!

Unraid 7.2.0
------------

Important Release Links

*   #### [Docs](https://docs.unraid.net/unraid-os/release-notes/7.2.0/)
    
    Version 7.2.0 Full Release Notes
    
*   #### [Forum Thread](https://forums.unraid.net/topic/194610-unraid-os-version-720-available/)
    
    Unraid 7.2.0 Forum Thread
    
*   #### [Known Issues](https://docs.unraid.net/unraid-os/release-notes/7.2.0/#known-issues)
    
    See the Known Issues for the Unraid 7.2 series
    
*   #### [Learn More](https://docs.unraid.net/unraid-os/system-administration/maintain-and-update/upgrading-unraid/#standard-upgrade-process)
    
    Ready to Upgrade? Visit your server’s Tools → Update OS page to install Unraid 7.2.0.
    

![Img Pricing 1](https://cdn.craft.cloud/481d40bf-939a-4dc1-918d-b4d4b48b7c04/assets/uploads/img_Pricing-1.jpg?width=1380&height=444&quality=100&fit=crop&s=Vnf0bkINshpmnIRgfMLOisrcLdSH9WP-b54ecTBxNUw)

Pricing
-------

With affordable options starting at just $49, we have a license for everyone.

[Buy Now](https://account.unraid.net/buy)

![Img Trial 2024 02 08 212340 axtg](https://cdn.craft.cloud/481d40bf-939a-4dc1-918d-b4d4b48b7c04/assets/uploads/img_Trial_2024-02-08-212340_axtg.jpg?width=1380&height=444&quality=100&fit=crop&s=-lkAcuBOMgQgFSU_toFAaDf98CS5kxlMWcP7yYA3m7Y)

Try before you buy
------------------

Not sure if Unraid is right for you? Take Unraid for a test drive for 30 days—no credit card required.

[Free Trial](https://unraid.net/getting-started)