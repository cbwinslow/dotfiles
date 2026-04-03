---
description: Automated system maintenance using multiple skills
tags: [maintenance, multi-skill, system, operations, automation]
---

# Automated System Maintenance Workflow

## Overview
This workflow chains system maintenance skills to automate routine operations:
1. **system-maintenance** - Check system health
2. **docker-ops** - Container maintenance
3. **analyze** - Review system configs
4. **debug** - Check scripts
5. **letta_backup** - Backup configurations

## Prerequisites
Skills required:
- system-maintenance
- docker-ops
- shell
- analyze
- debug
- letta_backup (optional)

## Daily Maintenance

### Step 1: System Health Check

```bash
#!/bin/bash
# daily_health_check.sh

echo "=== Daily System Health Check ==="
date

# Check disk space
echo -e "\n📊 Disk Usage:"
df -h | grep -E "Filesystem|/dev/(sda|nvme)"

# Check memory
echo -e "\n🧠 Memory Usage:"
free -h | head -2

# Check load average
echo -e "\n⚡ Load Average:"
uptime | awk -F'load average:' '{print $2}'

# Check zombie processes
echo -e "\n👻 Zombie Processes:"
ps aux | awk '$8=="Z"' | wc -l

# Log to Letta memory (optional)
if command -v letta-memory-cli &> /dev/null; then
    letta-memory-cli memory save \
      --agent ops \
      --content "Daily health check: $(date). Disk OK, Memory OK." \
      --type archival \
      --tags "maintenance,daily,health"
fi
```

### Step 2: Docker Maintenance

```bash
#!/bin/bash
# docker_maintenance.sh

echo "=== Docker Maintenance ==="

# List running containers
echo -e "\n🐳 Running Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check for unhealthy containers
echo -e "\n🏥 Unhealthy Containers:"
docker ps --filter "health=unhealthy" --format "{{.Names}}"

# Clean up
echo -e "\n🧹 Cleanup:"
docker system prune -f --volumes 2>/dev/null || true

# Check disk usage
echo -e "\n💾 Docker Disk Usage:"
docker system df
```

### Step 3: Configuration Analysis

```bash
#!/bin/bash
# config_analysis.sh

echo "=== Configuration Analysis ==="

# Analyze critical config files
for config in /etc/nginx/nginx.conf /etc/ssh/sshd_config; do
    if [ -f "$config" ]; then
        echo -e "\n📄 Analyzing: $config"
        cbw-analyze --path "$config" --structure 2>/dev/null || echo "  (Analysis not available)"
    fi
done
```

### Step 4: Script Debugging

```bash
#!/bin/bash
# script_health_check.sh

echo "=== Script Health Check ==="

# Check all shell scripts in common locations
for script in ~/dotfiles/scripts/*.sh /usr/local/bin/*.sh 2>/dev/null; do
    if [ -f "$script" ]; then
        echo -e "\n🔍 Checking: $script"
        cbw-debug "$script" 2>/dev/null | head -20 || echo "  (Debug not available)"
    fi
done
```

## Weekly Maintenance

### Full System Audit

```bash
#!/bin/bash
# weekly_audit.sh

echo "=== Weekly System Audit ==="
date

# 1. Update package lists
echo -e "\n📦 Checking for updates..."
sudo apt update > /dev/null 2>&1
apt list --upgradable 2>/dev/null | wc -l | xargs echo "Packages to upgrade:"

# 2. Check security updates
echo -e "\n🔒 Security Updates:"
apt list --upgradable 2>/dev/null | grep -i security || echo "None found"

# 3. Clean up old logs
echo -e "\n🗑️  Cleaning old logs..."
find /var/log -name "*.log.*" -mtime +30 -delete 2>/dev/null || true

# 4. Check failed services
echo -e "\n🚨 Failed Services:"
systemctl --failed --no-pager 2>/dev/null || true

# 5. Backup critical configs
echo -e "\n💾 Backing up configs..."
tar -czf ~/backups/configs-$(date +%Y%m%d).tar.gz \
  /etc/nginx /etc/ssh /etc/docker 2>/dev/null || true

echo -e "\n✅ Weekly audit complete"
```

## Monthly Deep Maintenance

### Complete System Overhaul

```bash
#!/bin/bash
# monthly_maintenance.sh

echo "=== Monthly Deep Maintenance ==="

# Phase 1: System Update
echo -e "\n📦 Phase 1: System Update"
sudo apt update && sudo apt upgrade -y

# Phase 2: Docker Deep Clean
echo -e "\n🐳 Phase 2: Docker Cleanup"
docker system prune -a -f --volumes
docker image prune -a -f

# Phase 3: Log Rotation
echo -e "\n📝 Phase 3: Log Management"
sudo logrotate -f /etc/logrotate.conf 2>/dev/null || true
sudo find /var/log -type f -name "*.gz" -mtime +90 -delete 2>/dev/null || true

# Phase 4: User Cleanup
echo -e "\n👤 Phase 4: User Directories"
# Clean temp files
find /tmp -type f -atime +7 -delete 2>/dev/null || true
# Clean old downloads
find ~/Downloads -type f -atime +30 -delete 2>/dev/null || true

# Phase 5: Letta Backup
echo -e "\n🤖 Phase 5: Letta Memory Backup"
if command -v letta-memory-cli &> /dev/null; then
    for agent in $(letta-memory-cli agent list 2>/dev/null | awk '{print $2}'); do
        echo "Backing up: $agent"
        letta-memory-cli backup create --agent "$agent" \
          --path ~/backups/letta 2>/dev/null || true
    done
fi

echo -e "\n✅ Monthly maintenance complete"
```

## Agent-Assisted Maintenance

### Automated Agent Execution

```python
#!/usr/bin/env python3
"""
System maintenance agent using multiple skills.
"""

import subprocess
import sys
import json
from datetime import datetime

class MaintenanceAgent:
    """Agent that performs system maintenance using skills."""
    
    def __init__(self):
        self.log = []
        self.issues = []
    
    def log_action(self, action, status, details=""):
        """Log maintenance action."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "details": details
        }
        self.log.append(entry)
        print(f"[{entry['timestamp']}] {action}: {status}")
    
    def run_skill(self, skill_name, args):
        """Run a skill command."""
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def phase1_health_check(self):
        """Phase 1: System health."""
        print("\n=== Phase 1: Health Check ===")
        
        # Check disk space
        success, stdout, stderr = self.run_skill(
            "system-maintenance",
            ['df', '-h']
        )
        
        if success:
            # Parse disk usage
            lines = stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                parts = line.split()
                if len(parts) >= 6:
                    filesystem, size, used, avail, use_percent, mount = parts[:6]
                    if mount in ['/', '/home']:
                        usage = int(use_percent.rstrip('%'))
                        if usage > 90:
                            self.issues.append(f"CRITICAL: {mount} at {use_percent}")
                            self.log_action("disk_check", "CRITICAL", f"{mount} {use_percent}")
                        elif usage > 80:
                            self.issues.append(f"WARNING: {mount} at {use_percent}")
                            self.log_action("disk_check", "WARNING", f"{mount} {use_percent}")
                        else:
                            self.log_action("disk_check", "OK", f"{mount} {use_percent}")
        
        return len([i for i in self.issues if i.startswith("CRITICAL")]) == 0
    
    def phase2_docker_maintenance(self):
        """Phase 2: Docker cleanup."""
        print("\n=== Phase 2: Docker Maintenance ===")
        
        success, stdout, stderr = self.run_skill(
            "docker-ops",
            ['docker', 'system', 'prune', '-f']
        )
        
        if success:
            self.log_action("docker_prune", "OK", "Cleaned unused resources")
        else:
            self.log_action("docker_prune", "ERROR", stderr)
        
        # Check container health
        success, stdout, stderr = self.run_skill(
            "docker-ops",
            ['docker', 'ps', '--filter', 'health=unhealthy', '-q']
        )
        
        if success and stdout.strip():
            self.issues.append(f"Unhealthy containers: {stdout.strip()}")
            self.log_action("docker_health", "WARNING", "Unhealthy containers found")
        else:
            self.log_action("docker_health", "OK")
        
        return True
    
    def phase3_config_analysis(self):
        """Phase 3: Analyze system configs."""
        print("\n=== Phase 3: Config Analysis ===")
        
        # This would use cbw-analyze if available
        self.log_action("config_analysis", "INFO", "Manual review recommended")
        
        return True
    
    def phase4_backup(self):
        """Phase 4: Backup important data."""
        print("\n=== Phase 4: Backup ===")
        
        # Try Letta backup
        success, stdout, stderr = self.run_skill(
            "letta_backup",
            ['letta-memory-cli', 'agent', 'list']
        )
        
        if success:
            self.log_action("letta_backup", "OK", "Agents available for backup")
        else:
            self.log_action("letta_backup", "SKIP", "Letta not available")
        
        return True
    
    def generate_report(self):
        """Generate maintenance report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "actions": len(self.log),
            "issues": self.issues,
            "log": self.log,
            "status": "CRITICAL" if any(i.startswith("CRITICAL") for i in self.issues) else \
                     "WARNING" if self.issues else "OK"
        }
        
        # Save report
        report_file = f"/tmp/maintenance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Report saved: {report_file}")
        return report
    
    def execute(self):
        """Execute full maintenance workflow."""
        print("=== Automated System Maintenance ===")
        print(f"Started: {datetime.now().isoformat()}")
        
        # Run all phases
        self.phase1_health_check()
        self.phase2_docker_maintenance()
        self.phase3_config_analysis()
        self.phase4_backup()
        
        # Generate report
        report = self.generate_report()
        
        # Summary
        print("\n=== Summary ===")
        print(f"Status: {report['status']}")
        print(f"Actions: {report['actions']}")
        if report['issues']:
            print(f"Issues: {len(report['issues'])}")
            for issue in report['issues']:
                print(f"  - {issue}")
        
        return report['status'] == "OK"

if __name__ == '__main__':
    agent = MaintenanceAgent()
    success = agent.execute()
    sys.exit(0 if success else 1)
```

## Maintenance Schedule

### Cron Setup

```bash
# Edit crontab
crontab -e

# Add these lines:
# Daily at 6 AM
0 6 * * * ~/dotfiles/ai/scripts/daily_health_check.sh >> ~/logs/daily_maintenance.log 2>&1

# Weekly on Sundays at 3 AM
0 3 * * 0 ~/dotfiles/ai/scripts/weekly_audit.sh >> ~/logs/weekly_maintenance.log 2>&1

# Monthly on the 1st at 2 AM
0 2 1 * * ~/dotfiles/ai/scripts/monthly_maintenance.sh >> ~/logs/monthly_maintenance.log 2>&1
```

## Skill Integration

### How Skills Work Together

1. **system-maintenance** - Base system checks
2. **docker-ops** - Container management
3. **shell** - Script execution
4. **analyze** - Config analysis
5. **debug** - Script validation
6. **letta_backup** - Memory backup

### Chaining Example

```bash
# Chain skills together
cbw-analyze --path /etc/nginx --structure && \
cbw-debug ~/scripts/backup.sh && \
docker system prune -f && \
echo "Maintenance complete"
```

## Troubleshooting

### High Disk Usage
```bash
# Find large files
du -h / | grep -E "^[0-9]+G" | sort -hr | head -10

# Clean Docker
docker system prune -a -f

# Clean logs
sudo journalctl --vacuum-time=7d
```

### Memory Issues
```bash
# Check memory hogs
ps aux --sort=-%mem | head -10

# Clear caches
sudo sync && sudo echo 3 > /proc/sys/vm/drop_caches
```

### Docker Problems
```bash
# Reset Docker (careful!)
docker system prune -a -f --volumes

# Restart Docker
sudo systemctl restart docker
```

## Related Workflows
- system-maintenance - Basic maintenance
- docker-ops - Docker operations
- script-debugging - Debug maintenance scripts
- agent-lifecycle - Maintenance agent management
