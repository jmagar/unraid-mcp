#!/usr/bin/env python3
import asyncio
import json
import logging
from unraid_client import UnraidClient, UnraidApiError

"""
Example script demonstrating how to use the UnraidClient to interact with an Unraid server.
Before running this script, make sure you have:
1. Set up your .env file with UNRAID_API_URL and UNRAID_API_KEY
2. Enabled the Unraid API on your server using 'unraid-api developer'
3. Created an API key using 'unraid-api apikey --create'
"""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("example_usage")

async def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

async def safe_api_call(coroutine, section_name):
    """Safely execute an API call and handle exceptions"""
    print(f"\n=== {section_name} ===")
    try:
        return await coroutine
    except UnraidApiError as e:
        print(f"API Error in {section_name}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in {section_name}: {e}")
        return None

async def main():
    # Initialize the client
    try:
        client = UnraidClient()
        print("Unraid client initialized")
    except Exception as e:
        print(f"Failed to initialize client: {e}")
        return
    
    # Example 1: Get system information
    system_info = await safe_api_call(client.get_system_info(), "System Information")
    if system_info:
        try:
            print(f"Unraid Version: {system_info['versions']['unraid']}")
            print(f"Hostname: {system_info['os']['hostname']}")
            print(f"CPU: {system_info['cpu']['brand']} ({system_info['cpu']['cores']} cores)")
            print(f"Memory: {system_info['memory']['total'] / (1024**3):.2f} GB")
        except KeyError as e:
            print(f"Missing expected data in system_info: {e}")
    
    # Example 2: Get array status
    array_status = await safe_api_call(client.get_array_status(), "Array Status")
    if array_status:
        try:
            print(f"Array State: {array_status['state']}")
            if 'disks' in array_status:
                print(f"Number of array disks: {len(array_status['disks'])}")
        except KeyError as e:
            print(f"Missing expected data in array_status: {e}")
    
    # Get disk information
    disks = await safe_api_call(client.get_disks(), "Disk Information")
    if disks:
        try:
            print(f"Found {len(disks)} disks")
            for i, disk in enumerate(disks[:2]):  # Show first 2 disks only
                print(f"Disk {i+1}: {disk.get('name', 'Unknown')}, "
                      f"Size: {disk.get('size', 'Unknown')}, "
                      f"Temp: {disk.get('temperature', 'Unknown')}°C")
        except Exception as e:
            print(f"Error processing disk information: {e}")
    
    # Example 3: Get Docker containers
    containers = await safe_api_call(client.get_docker_containers(), "Docker Containers")
    if containers:
        try:
            print(f"Found {len(containers)} containers")
            for i, container in enumerate(containers[:3]):  # Show first 3 containers only
                names = container.get('names', ['Unknown'])
                name = names[0] if names else 'Unknown'
                print(f"Container {i+1}: {name}, Status: {container.get('state', 'Unknown')}")
        except Exception as e:
            print(f"Error processing container information: {e}")
    
    # Example 4: Get VMs
    vms_data = await safe_api_call(client.get_vms(), "Virtual Machines")
    if vms_data:
        try:
            if 'domain' in vms_data:
                vms = vms_data['domain'] if isinstance(vms_data['domain'], list) else [vms_data['domain']]
                print(f"Found {len(vms)} VMs")
                for i, vm in enumerate(vms[:3]):  # Show first 3 VMs only
                    print(f"VM {i+1}: {vm.get('name', 'Unknown')}, State: {vm.get('state', 'Unknown')}")
            else:
                print("No VMs found or unexpected response format")
        except Exception as e:
            print(f"Error processing VM information: {e}")
    
    # Example 5: Get shares
    shares = await safe_api_call(client.get_shares(), "Network Shares")
    if shares:
        try:
            print(f"Found {len(shares)} shares")
            for i, share in enumerate(shares[:3]):  # Show first 3 shares only
                print(f"Share {i+1}: {share.get('name', 'Unknown')}, "
                      f"Size: {share.get('size', 'Unknown')}, "
                      f"Used: {share.get('used', 'Unknown')}")
        except Exception as e:
            print(f"Error processing share information: {e}")
    
    # Example 6: Get notifications
    notifications = await safe_api_call(client.get_notifications(limit=5), "Notifications")
    if notifications:
        try:
            if 'list' in notifications:
                print(f"Found {len(notifications['list'])} unread notifications")
                for i, notification in enumerate(notifications['list'][:3]):  # Show first 3 notifications only
                    print(f"Notification {i+1}: {notification.get('title', 'Unknown')} - "
                          f"{notification.get('importance', 'Unknown')}")
            else:
                print("No notifications found or unexpected response format")
        except Exception as e:
            print(f"Error processing notification information: {e}")
    
    # Example 7: Get current user
    user = await safe_api_call(client.get_current_user(), "Current User")
    if user:
        try:
            print(f"User: {user.get('name', 'Unknown')}")
            roles = user.get('roles', [])
            print(f"Roles: {', '.join(roles) if roles else 'None'}")
        except Exception as e:
            print(f"Error processing user information: {e}")
    
    # Example 8: Get parity history
    parity_history = await safe_api_call(client.get_parity_history(), "Parity Check History")
    if parity_history:
        try:
            if not parity_history:
                print("No parity check history found")
            else:
                for i, check in enumerate(parity_history[:3]):  # Show first 3 parity checks only
                    print(f"Check {i+1}: Date: {check.get('date', 'Unknown')}, "
                          f"Status: {check.get('status', 'Unknown')}, "
                          f"Errors: {check.get('errors', 'Unknown')}")
        except Exception as e:
            print(f"Error processing parity history: {e}")
    
    print("\nExample script completed")

if __name__ == "__main__":
    asyncio.run(main()) 