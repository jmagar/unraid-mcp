[Skip to main content](https://docs.unraid.net/unraid-connect/remote-access#__docusaurus_skipToContent_fallback)

On this page

Unlock secure, browser-based access to your Unraid WebGUI from anywhere with remote access. This feature is ideal for managing your server when you're away from home - no complicated networking or VPN Tunnel setup is required. For more advanced needs, such as connecting to Docker containers or accessing network drives, a VPN Tunnel remains the recommended solution.

Security reminder

Before enabling remote access, ensure your root password is strong and unique. Update it on the **Users** page if required. Additionally, keep your Unraid OS updated to the latest version to protect against security vulnerabilities. [Learn more about updating Unraid here](https://docs.unraid.net/unraid-os/system-administration/maintain-and-update/upgrading-unraid/)
.

Remote access through Unraid Connect provides:

*   **Convenience** - Quickly access your server’s management interface from anywhere, using a secure, cloud-managed connection.
*   **Security** - Dynamic access modes limit exposure by only allowing access to the internet when necessary, which helps reduce risks from automated attacks.
*   **Simplicity** - No need for manual port forwarding or VPN client setup for basic management tasks.

tip

For full network access or advanced use cases, consider setting up [Tailscale](https://docs.unraid.net/unraid-os/system-administration/secure-your-server/tailscale/)
 or a VPN solution.

* * *

Initial setup[​](https://docs.unraid.net/unraid-connect/remote-access#initial-setup "Direct link to Initial setup")

--------------------------------------------------------------------------------------------------------------------

To enable remote access:

1.  In the Unraid WebGUI, navigate to _**Settings → Management Access**_.
2.  Check the **HTTPS port** (default: 443). If this port is in use (e.g., by Docker), select an unused port above 1000 (like 3443, 4443, or 5443).
3.  Click **Apply** if you changed any settings.
4.  Under **CA-signed certificate file**, click **Provision** to generate a trusted certificate.

Your Unraid server will be ready to accept secure remote connections via the WebGUI, using the configured port and a trusted certificate.

* * *

Choosing a remote access type[​](https://docs.unraid.net/unraid-connect/remote-access#choosing-a-remote-access-type "Direct link to Choosing a remote access type")

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

Unraid Connect offers two modes:

*   Dynamic remote access
*   Static remote access

**Dynamic remote access** provides secure, on-demand access to your WebGUI.

*   **Access is enabled only when you need it.** The WebGUI remains closed to the internet by default, minimizing the attack surface.
*   **Works with UPnP or manual port forwarding.**
*   **Automatically opens and closes access** through the Connect dashboard or API, with sessions limited by time for added security.

**Static remote access** keeps your WebGUI continuously available from the internet.

*   **Server is always accessible from the internet** on the configured port.
*   **Higher risk:** The WebGUI is exposed to WAN traffic at all times, increasing potential vulnerability.

| Feature | Dynamic remote access | Static remote access |
| --- | --- | --- |
| WebGUI open to internet | Only when enabled | Always |
| Attack surface | Minimized | Maximized |
| Automation | Auto open/close via Connect | Manual setup, always open |
| UPnP support | Yes | Yes |
|     | **Recommended for most** |     |

Dynamic remote access setup[​](https://docs.unraid.net/unraid-connect/remote-access#dynamic-remote-access-setup "Direct link to Dynamic remote access setup")

--------------------------------------------------------------------------------------------------------------------------------------------------------------

To set up dynamic remote access:

1.  In _**Settings → Management Access → Unraid API**_, select a dynamic option from the Remote Access dropdown:
    
    *   **Dynamic - UPnP:** Uses UPnP to open and close a random port automatically (requires UPnP enabled on your router).
    *   **Dynamic - Manual port forward:** Requires you to forward the selected port on your router manually.
2.  Navigate to [Unraid Connect](https://connect.myunraid.net/)
    , and go to the management or server details page.
    
3.  The **Dynamic remote access** card will show a button if your server isn’t currently accessible from your location.
    
4.  Click the button to enable WAN access. If using UPnP, a new port forward lease is created (typically for 30 minutes) and auto-renewed while active.
    
5.  The card will display the current status and UPnP state.
    
6.  After 10 minutes of inactivity - or if you click **Disable remote access** - internet access is automatically revoked. UPnP leases are removed as well.
    

* * *

Using UPnP (Universal Plug and Play)[​](https://docs.unraid.net/unraid-connect/remote-access#using-upnp-universal-plug-and-play "Direct link to Using UPnP (Universal Plug and Play)")

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

UPnP automates port forwarding, simplifying remote access without requiring manual router configuration.

To configure UPnP:

1.  **Enable UPnP on your router.** Ensure that your router supports UPnP and verify that it is enabled in the router settings.
    
2.  **Enable UPnP in Unraid.** Navigate to _**Settings → Management Access**_ and change **Use UPnP** to **Yes**.
    
3.  **Select UPnP in Unraid Connect.** On the Unraid Connect settings page, choose the remote access option as UPnP (select either Dynamic or Always On) and then click **Apply**.
    
4.  **Verify port forwarding (Always On only).** Click the **Check** button. If successful, you'll see the message, "Your Unraid Server is reachable from the Internet."
    
    For Dynamic forwarding, you need to click **Enable Dynamic Remote Access** in [Unraid Connect](https://connect.myunraid.net/)
     to allow access.
    

Troubleshooting

If the setting changes from UPnP to Manual Port Forward upon reloading, Unraid might not be able to communicate with your router. Double-check that UPnP is enabled and consider updating your router's firmware.

* * *

Using manual port forwarding[​](https://docs.unraid.net/unraid-connect/remote-access#using-manual-port-forwarding "Direct link to Using manual port forwarding")

-----------------------------------------------------------------------------------------------------------------------------------------------------------------

Manual port forwarding provides greater control and is compatible with most routers.

To configure manual port forwarding:

1.  **Choose a WAN port:** Pick a random port number above 1000 (for example, 13856 or 48653), rather than using the default 443.
    
2.  **Apply settings in Unraid:** Click **Apply** to save the port you selected.
    
3.  **Configure your router:** Set up a port forwarding rule on your router, directing your chosen WAN port to your server’s HTTPS port. The Unraid interface provides the correct ports and IP address.
    
    Some routers may require the WAN port and HTTPS port to match. If so, use the same high random number for both.
    
4.  **Verify port forwarding (Always On only):** Press the **Check** button. If everything is correct, you’ll see “Your Unraid Server is reachable from the Internet.”
    
    For dynamic forwarding, ensure to click **Enable Dynamic Remote Access** in [Unraid Connect](https://connect.myunraid.net/)
     to enable access.
    
5.  **Access your server:** Log in to [Unraid Connect](https://connect.myunraid.net/)
     and click the **Manage** link to connect to your server remotely.
    

* * *

Enabling secure local access[​](https://docs.unraid.net/unraid-connect/remote-access#enabling-secure-local-access "Direct link to Enabling secure local access")

-----------------------------------------------------------------------------------------------------------------------------------------------------------------

Secure local access ensures that all connections to your Unraid WebGUI, even within your home or office network, are encrypted using HTTPS, thereby safeguarding any sensitive information, such as login credentials and configuration data.

Benefits of secure local access include:

*   **Encryption** - All data exchanged between your browser and the server is protected.
*   **Consistency** - Use the same secure URL for both local and remote access.
*   **Compliance** - Adheres to security best practices for protecting administrative interfaces.

To enable secure local access:

1.  Go to _**Settings → Management Access**_.
2.  In the **CA-signed certificate** section, check for DNS Rebinding warnings.
    *   If no warnings show, set **Use SSL/TLS** to **Strict**.
    *   If warnings are present, review [DNS Rebinding Protection](https://docs.unraid.net/unraid-os/system-administration/secure-your-server/securing-your-connection/#dns-rebinding-protection)
        .

important

With SSL/TLS set to Strict, client devices must resolve your server’s DNS name. If your Internet connection fails, access to the WebGUI may be lost. See [Accessing your server when DNS is down](https://docs.unraid.net/unraid-os/system-administration/secure-your-server/securing-your-connection/#accessing-your-server-when-dns-is-down)
 for recovery steps.

*   [Initial setup](https://docs.unraid.net/unraid-connect/remote-access#initial-setup)
    
*   [Choosing a remote access type](https://docs.unraid.net/unraid-connect/remote-access#choosing-a-remote-access-type)
    
*   [Dynamic remote access setup](https://docs.unraid.net/unraid-connect/remote-access#dynamic-remote-access-setup)
    
*   [Using UPnP (Universal Plug and Play)](https://docs.unraid.net/unraid-connect/remote-access#using-upnp-universal-plug-and-play)
    
*   [Using manual port forwarding](https://docs.unraid.net/unraid-connect/remote-access#using-manual-port-forwarding)
    
*   [Enabling secure local access](https://docs.unraid.net/unraid-connect/remote-access#enabling-secure-local-access)