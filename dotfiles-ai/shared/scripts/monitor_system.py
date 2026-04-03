#!/usr/bin/env python3
"""
System Monitoring Script

Monitors the health and status of the Agent AI Skills System.
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SystemMonitor:
    def __init__(self, base_path: str = "/home/cbwinslow/dotfiles/ai"):
        self.base_path = Path(base_path)
        self.config_path = self.base_path / "system_config.json"
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health."""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "components": {},
            "issues": [],
            "recommendations": []
        }
        
        # Check Agent memory package
        try:
            import agent_memory
            health_report["components"]["agent_memory"] = {"status": "healthy", "version": "1.0.0"}
        except ImportError:
            health_report["components"]["agent_memory"] = {"status": "failed", "error": "Package not installed"}
            health_report["issues"].append("Agent memory package not installed")
        
        # Check PostgreSQL connection
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=os.getenv("PG_HOST", "localhost"),
                port=int(os.getenv("PG_PORT", 5432)),
                database=os.getenv("PG_DBNAME", "letta"),
                user=os.getenv("PG_USER", "cbwinslow"),
                password=os.getenv("PG_PASSWORD", "123qweasd"),
            )
            conn.close()
            health_report["components"]["postgresql"] = {"status": "healthy"}
        except Exception as e:
            health_report["components"]["postgresql"] = {"status": "failed", "error": str(e)}
            health_report["issues"].append(f"PostgreSQL connection failed: {e}")
        
        # Check Letta server
        try:
            import requests
            letta_url = os.getenv("LETTA_SERVER_URL", "http://localhost:8283")
            response = requests.get(f"{letta_url}/health", timeout=5)
            if response.status_code == 200:
                health_report["components"]["letta_server"] = {"status": "healthy"}
            else:
                health_report["components"]["letta_server"] = {"status": "warning", "status_code": response.status_code}
                health_report["issues"].append(f"Letta server returned status: {response.status_code}")
        except Exception as e:
            health_report["components"]["letta_server"] = {"status": "failed", "error": str(e)}
            health_report["issues"].append(f"Letta server not accessible: {e}")
        
        # Check agent configurations
        agents_dir = self.base_path / "agents"
        if agents_dir.exists():
            agent_configs = list(agents_dir.glob("*/config.yaml"))
            health_report["components"]["agents"] = {
                "status": "healthy", 
                "count": len(agent_configs),
                "agents": [p.parent.name for p in agent_configs]
            }
        else:
            health_report["components"]["agents"] = {"status": "failed", "error": "Agents directory not found"}
            health_report["issues"].append("Agents directory not found")
        
        # Determine overall status
        failed_components = [k for k, v in health_report["components"].items() if v["status"] == "failed"]
        if failed_components:
            health_report["status"] = "critical"
            health_report["recommendations"].append("Fix failed components before using the system")
        elif health_report["issues"]:
            health_report["status"] = "warning"
            health_report["recommendations"].append("Review and address warnings")
        else:
            health_report["status"] = "healthy"
            health_report["recommendations"].append("System is ready for use")
        
        return health_report
    
    def generate_report(self) -> str:
        """Generate human-readable health report."""
        health = self.check_system_health()
        
        report = f"""
Agent AI Skills System - Health Report
{'='*50}
Timestamp: {health['timestamp']}
Overall Status: {health['status'].upper()}

Components:
"""
        
        for component, status in health["components"].items():
            status_icon = "✓" if status["status"] == "healthy" else "⚠" if status["status"] == "warning" else "✗"
            report += f"  {status_icon} {component}: {status['status']}
"
            if "error" in status:
                report += f"    Error: {status['error']}
"
            if "count" in status:
                report += f"    Count: {status['count']}
"
        
        if health["issues"]:
            report += f"
Issues Found ({len(health['issues'])}):
"
            for i, issue in enumerate(health["issues"], 1):
                report += f"  {i}. {issue}
"
        
        if health["recommendations"]:
            report += f"
Recommendations:
"
            for i, rec in enumerate(health["recommendations"], 1):
                report += f"  {i}. {rec}
"
        
        return report
    
    def save_health_report(self) -> bool:
        """Save health report to file."""
        try:
            health = self.check_system_health()
            report_path = self.base_path / "logs" / "health_report.json"
            report_path.parent.mkdir(exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(health, f, indent=2)
            
            logger.info(f"✓ Health report saved to {report_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to save health report: {e}")
            return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor Agent AI Skills System health")
    parser.add_argument("--report", action="store_true", help="Generate and display health report")
    parser.add_argument("--save", action="store_true", help="Save health report to file")
    parser.add_argument("--check", action="store_true", help="Quick health check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    monitor = SystemMonitor()
    
    if args.report:
        report = monitor.generate_report()
        print(report)
    
    if args.save:
        monitor.save_health_report()
    
    if args.check:
        health = monitor.check_system_health()
        print(f"System Status: {health['status']}")
        if health['issues']:
            print(f"Issues: {len(health['issues'])}")
            for issue in health['issues'][:3]:  # Show first 3 issues
                print(f"  - {issue}")
    
    if not any([args.report, args.save, args.check]):
        parser.print_help()


if __name__ == "__main__":
    main()
