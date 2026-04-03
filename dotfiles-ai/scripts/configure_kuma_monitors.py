#!/usr/bin/env python3
"""
Uptime Kuma Monitor Configuration Script
Uses uptime-kuma-api to add all homelab service monitors
"""

from uptime_kuma_api import UptimeKumaApi, MonitorType, IncidentStyle
import sys

# Kuma connection settings
KUMA_URL = "http://localhost:3001"
KUMA_USERNAME = "admin"  # Change after first setup
KUMA_PASSWORD = "admin123"  # Change after first setup

# Services to monitor
SERVICES = [
    {
        "name": "Gitea Git Server",
        "type": MonitorType.HTTP,
        "url": "http://192.168.4.101:3002",
        "interval": 60,
        "max_retries": 3,
        "description": "Self-hosted Git service"
    },
    {
        "name": "Uptime Kuma",
        "type": MonitorType.HTTP,
        "url": "http://192.168.4.101:3001",
        "interval": 60,
        "max_retries": 3,
        "description": "Self-monitoring"
    },
    {
        "name": "Docker Registry",
        "type": MonitorType.HTTP,
        "url": "http://192.168.4.101:5000/v2/",
        "interval": 60,
        "max_retries": 3,
        "description": "Private container registry"
    },
    {
        "name": "code-server VS Code",
        "type": MonitorType.HTTP,
        "url": "http://192.168.4.101:8080",
        "interval": 60,
        "max_retries": 3,
        "description": "VS Code in browser"
    },
    {
        "name": "OpenWebUI",
        "type": MonitorType.HTTP,
        "url": "http://192.168.4.101:3000",
        "interval": 60,
        "max_retries": 3,
        "description": "AI chat interface"
    },
    {
        "name": "n8n Workflow",
        "type": MonitorType.HTTP,
        "url": "http://192.168.4.101:5678",
        "interval": 60,
        "max_retries": 3,
        "description": "Workflow automation"
    },
    {
        "name": "OpenClaw Gateway",
        "type": MonitorType.HTTP,
        "url": "http://192.168.4.101:18789",
        "interval": 60,
        "max_retries": 3,
        "description": "AI agent gateway"
    },
    {
        "name": "MySQL Database",
        "type": MonitorType.PORT,
        "hostname": "192.168.4.101",
        "port": 3306,
        "interval": 60,
        "max_retries": 3,
        "description": "MySQL database server"
    },
    {
        "name": "Server Ping",
        "type": MonitorType.PING,
        "hostname": "192.168.4.101",
        "interval": 60,
        "max_retries": 3,
        "description": "Server availability"
    }
]

def setup_monitors():
    """Connect to Kuma and add all monitors"""
    
    print(f"Connecting to Uptime Kuma at {KUMA_URL}...")
    
    try:
        api = UptimeKumaApi(KUMA_URL)
        api.login(KUMA_USERNAME, KUMA_PASSWORD)
        print(f"✓ Logged in as {KUMA_USERNAME}")
        
        # Get existing monitors to avoid duplicates
        existing_monitors = api.get_monitors()
        existing_names = {m.get('name') for m in existing_monitors}
        
        print(f"\nFound {len(existing_monitors)} existing monitors")
        
        added = 0
        skipped = 0
        
        for service in SERVICES:
            name = service['name']
            
            if name in existing_names:
                print(f"⚠ Skipping {name} - already exists")
                skipped += 1
                continue
            
            print(f"\n→ Adding {name}...")
            
            try:
                # Build monitor parameters
                monitor_params = {
                    'type': service['type'],
                    'name': name,
                    'interval': service.get('interval', 60),
                    'maxretries': service.get('max_retries', 3),
                }
                
                # Add type-specific parameters
                if service['type'] == MonitorType.HTTP:
                    monitor_params['url'] = service.get('url')
                elif service['type'] == MonitorType.PORT:
                    monitor_params['hostname'] = service.get('hostname')
                    monitor_params['port'] = service.get('port')
                elif service['type'] == MonitorType.PING:
                    monitor_params['hostname'] = service.get('hostname')
                
                result = api.add_monitor(**monitor_params)
                print(f"  ✓ Created (ID: {result.get('monitorID', 'N/A')})")
                added += 1
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
        
        print(f"\n=== Summary ===")
        print(f"Added: {added}")
        print(f"Skipped (duplicates): {skipped}")
        print(f"Total: {added + skipped}")
        
        api.disconnect()
        print("\n✓ Done! Access your dashboard at http://192.168.4.101:3001")
        
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Kuma is running: sudo systemctl status uptime-kuma")
        print("2. Check if admin account exists: ls -la /var/lib/uptime-kuma/")
        print("3. If empty, visit http://192.168.4.101:3001 to create admin account first")
        sys.exit(1)

def setup_notifications():
    """Configure notification channels"""
    print("\n=== Notification Setup ===")
    print("To add notifications, edit this script and uncomment the notification setup")
    print("\nSupported notification types:")
    print("- Email (SMTP)")
    print("- Discord webhook")
    print("- Telegram bot")
    print("- Slack webhook")
    print("- Pushover")
    print("- ntfy")
    print("\nExample SMTP notification:")
    print("""
    # Add to setup_monitors() after login:
    # api.add_notification(
    #     name="Email Alerts",
    #     type=NotificationType.SMTP,
    #     smtpHost="smtp.gmail.com",
    #     smtpPort=587,
    #     smtpUsername="your-email@gmail.com",
    #     smtpPassword="app-password",
    #     smtpFrom="alerts@yourdomain.com",
    #     smtpTo="your-email@gmail.com",
    #     isDefault=True
    # )
    """)

if __name__ == "__main__":
    print("=" * 60)
    print("Uptime Kuma Monitor Configuration")
    print("=" * 60)
    print()
    
    # Update credentials
    print("IMPORTANT: Update KUMA_USERNAME and KUMA_PASSWORD in this script")
    print("           to match your admin account credentials!")
    print()
    
    setup_monitors()
    setup_notifications()
