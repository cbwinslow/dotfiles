"""
Server Management Skills for Letta Server

Provides comprehensive Letta server management capabilities.
These skills replace standalone server management scripts.
"""

import os
import json
import logging
import subprocess
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import shutil
import tarfile
from pathlib import Path

logger = logging.getLogger(__name__)


def check_server_health() -> Dict[str, Any]:
    """
    Monitor Letta server health and status.
    
    Returns:
        Health status information
    """
    try:
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "server_status": "unknown",
            "database_status": "unknown",
            "api_status": "unknown",
            "memory_usage": {},
            "disk_usage": {},
            "issues": [],
            "recommendations": []
        }
        
        # Check Letta server API
        try:
            letta_url = os.getenv("LETTA_SERVER_URL", "http://localhost:8283")
            api_key = os.getenv("LETTA_API_KEY")
            
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            response = requests.get(f"{letta_url}/health", headers=headers, timeout=10)
            
            if response.status_code == 200:
                health_status["server_status"] = "healthy"
                health_status["api_status"] = "healthy"
            else:
                health_status["server_status"] = "unhealthy"
                health_status["api_status"] = f"error_{response.status_code}"
                health_status["issues"].append(f"API returned status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            health_status["server_status"] = "unhealthy"
            health_status["api_status"] = "connection_failed"
            health_status["issues"].append(f"API connection failed: {e}")
        
        # Check PostgreSQL database
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=os.getenv("PG_HOST", "localhost"),
                port=int(os.getenv("PG_PORT", 5432)),
                database=os.getenv("PG_DBNAME", "letta"),
                user=os.getenv("PG_USER", "cbwinslow"),
                password=os.getenv("PG_PASSWORD", "123qweasd"),
            )
            
            # Test database connection
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            
            health_status["database_status"] = "healthy"
            
        except Exception as e:
            health_status["database_status"] = "unhealthy"
            health_status["issues"].append(f"Database connection failed: {e}")
        
        # Check Docker containers (if using Docker)
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=letta"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "letta" in result.stdout:
                health_status["docker_status"] = "running"
            else:
                health_status["docker_status"] = "not_running"
                health_status["issues"].append("Letta Docker container not running")
                
        except Exception as e:
            health_status["docker_status"] = "unknown"
            health_status["issues"].append(f"Docker check failed: {e}")
        
        # Determine overall status
        if health_status["issues"]:
            health_status["status"] = "unhealthy"
            health_status["recommendations"].append("Review and fix reported issues")
        else:
            health_status["status"] = "healthy"
            health_status["recommendations"].append("Server is operating normally")
        
        logger.info(f"Server health check completed: {health_status['status']}")
        return health_status
        
    except Exception as e:
        logger.error(f"Failed to check server health: {e}")
        raise


def initialize_server(config: Dict[str, Any], database_url: str) -> Dict[str, Any]:
    """
    Setup and configure Letta server.
    
    Args:
        config: Server configuration
        database_url: Database connection string
        
    Returns:
        Setup results
    """
    try:
        setup_result = {
            "timestamp": datetime.now().isoformat(),
            "config": config,
            "database_url": database_url,
            "steps_completed": [],
            "errors": [],
            "warnings": []
        }
        
        # Validate configuration
        required_config_keys = ["host", "port", "api_key"]
        for key in required_config_keys:
            if key not in config:
                setup_result["errors"].append(f"Missing required config key: {key}")
        
        if setup_result["errors"]:
            setup_result["status"] = "failed"
            return setup_result
        
        # Create configuration files
        try:
            # Create Letta configuration
            letta_config = {
                "host": config["host"],
                "port": config["port"],
                "api_key": config["api_key"],
                "database_url": database_url,
                "debug": config.get("debug", False),
                "log_level": config.get("log_level", "INFO")
            }
            
            config_dir = Path("/home/cbwinslow/dotfiles/ai/configs")
            config_dir.mkdir(exist_ok=True)
            
            with open(config_dir / "letta.yaml", "w") as f:
                import yaml
                yaml.dump(letta_config, f, default_flow_style=False)
            
            setup_result["steps_completed"].append("configuration_created")
            
        except Exception as e:
            setup_result["errors"].append(f"Failed to create configuration: {e}")
        
        # Initialize Agent memory system
        try:
            from agent_memory import initialize_memory_system
            initialize_memory_system()
            setup_result["steps_completed"].append("memory_system_initialized")
            
        except Exception as e:
            setup_result["errors"].append(f"Failed to initialize memory system: {e}")
        
        # Start Letta server (if using Docker)
        try:
            docker_compose_path = "/home/cbwinslow/infra/letta/docker-compose.letta.yml"
            if Path(docker_compose_path).exists():
                result = subprocess.run(
                    ["docker-compose", "-f", docker_compose_path, "up", "-d"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    setup_result["steps_completed"].append("docker_server_started")
                else:
                    setup_result["errors"].append(f"Docker compose failed: {result.stderr}")
            
        except Exception as e:
            setup_result["warnings"].append(f"Failed to start Docker server: {e}")
        
        # Verify server is running
        try:
            health = check_server_health()
            if health["status"] == "healthy":
                setup_result["steps_completed"].append("server_verification_passed")
            else:
                setup_result["warnings"].append("Server started but health check shows issues")
                
        except Exception as e:
            setup_result["warnings"].append(f"Server verification failed: {e}")
        
        # Determine final status
        if setup_result["errors"]:
            setup_result["status"] = "failed"
        elif setup_result["warnings"]:
            setup_result["status"] = "warning"
        else:
            setup_result["status"] = "success"
        
        logger.info(f"Server initialization completed: {setup_result['status']}")
        return setup_result
        
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        raise


def backup_server_data(backup_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Create backups of Letta data.
    
    Args:
        backup_path: Path where to store the backup
        
    Returns:
        Backup results
    """
    try:
        backup_result = {
            "timestamp": datetime.now().isoformat(),
            "backup_path": backup_path,
            "files_backed_up": [],
            "database_backed_up": False,
            "size_mb": 0,
            "status": "unknown"
        }
        
        # Set default backup path
        if not backup_path:
            backup_path = f"/home/cbwinslow/backups/letta_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_dir = Path(backup_path)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup database
        try:
            db_backup_path = backup_dir / "database_backup.sql"
            
            # Use pg_dump to backup PostgreSQL database
            pg_dump_cmd = [
                "pg_dump",
                "-h", os.getenv("PG_HOST", "localhost"),
                "-p", str(os.getenv("PG_PORT", "5432")),
                "-U", os.getenv("PG_USER", "cbwinslow"),
                "-d", os.getenv("PG_DBNAME", "letta"),
                "-f", str(db_backup_path)
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = os.getenv("PG_PASSWORD", "123qweasd")
            
            result = subprocess.run(pg_dump_cmd, env=env, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                backup_result["database_backed_up"] = True
                backup_result["files_backed_up"].append(str(db_backup_path))
                
                # Get file size
                size_bytes = db_backup_path.stat().st_size
                backup_result["size_mb"] += size_bytes / (1024 * 1024)
            else:
                backup_result["errors"] = [f"Database backup failed: {result.stderr}"]
                
        except Exception as e:
            backup_result["errors"] = [f"Database backup error: {e}"]
        
        # Backup configuration files
        try:
            config_dir = Path("/home/cbwinslow/dotfiles/ai/configs")
            if config_dir.exists():
                config_backup_path = backup_dir / "configs"
                shutil.copytree(config_dir, config_backup_path, dirs_exist_ok=True)
                backup_result["files_backed_up"].append(str(config_backup_path))
                
                # Get size of config directory
                config_size = sum(f.stat().st_size for f in config_backup_path.rglob('*') if f.is_file())
                backup_result["size_mb"] += config_size / (1024 * 1024)
                
        except Exception as e:
            backup_result["warnings"] = [f"Config backup warning: {e}"]
        
        # Backup memory data
        try:
            memory_backup_path = backup_dir / "memory_data"
            memory_backup_path.mkdir(exist_ok=True)
            
            # Backup memory statistics
            from agent_memory import get_memory_stats
            stats = get_memory_stats()
            
            with open(memory_backup_path / "memory_stats.json", "w") as f:
                json.dump(stats, f, indent=2)
            
            backup_result["files_backed_up"].append(str(memory_backup_path / "memory_stats.json"))
            
        except Exception as e:
            backup_result["warnings"] = [f"Memory backup warning: {e}"]
        
        # Create archive
        try:
            archive_path = f"{backup_path}.tar.gz"
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(backup_path, arcname="letta_backup")
            
            # Remove uncompressed backup directory
            shutil.rmtree(backup_path)
            
            backup_result["archive_path"] = archive_path
            backup_result["status"] = "success"
            
        except Exception as e:
            backup_result["warnings"].append(f"Archive creation warning: {e}")
            backup_result["status"] = "partial"
        
        logger.info(f"Server backup completed: {backup_result['status']}")
        return backup_result
        
    except Exception as e:
        logger.error(f"Failed to backup server data: {e}")
        raise


def restore_server_data(backup_path: str) -> Dict[str, Any]:
    """
    Restore from backups.
    
    Args:
        backup_path: Path to the backup file
        
    Returns:
        Restore results
    """
    try:
        restore_result = {
            "timestamp": datetime.now().isoformat(),
            "backup_path": backup_path,
            "steps_completed": [],
            "errors": [],
            "warnings": []
        }
        
        backup_file = Path(backup_path)
        if not backup_file.exists():
            restore_result["errors"].append(f"Backup file not found: {backup_path}")
            restore_result["status"] = "failed"
            return restore_result
        
        # Create temporary directory for extraction
        temp_dir = Path(f"/tmp/letta_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Extract backup
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(temp_dir)
            
            restore_result["steps_completed"].append("backup_extracted")
            
            # Restore database
            try:
                db_backup_path = temp_dir / "letta_backup" / "database_backup.sql"
                if db_backup_path.exists():
                    # Stop Letta server first
                    docker_compose_path = "/home/cbwinslow/infra/letta/docker-compose.letta.yml"
                    if Path(docker_compose_path).exists():
                        subprocess.run(
                            ["docker-compose", "-f", docker_compose_path, "down"],
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                    
                    # Restore database
                    psql_cmd = [
                        "psql",
                        "-h", os.getenv("PG_HOST", "localhost"),
                        "-p", str(os.getenv("PG_PORT", "5432")),
                        "-U", os.getenv("PG_USER", "cbwinslow"),
                        "-d", os.getenv("PG_DBNAME", "letta"),
                        "-f", str(db_backup_path)
                    ]
                    
                    env = os.environ.copy()
                    env["PGPASSWORD"] = os.getenv("PG_PASSWORD", "123qweasd")
                    
                    result = subprocess.run(psql_cmd, env=env, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        restore_result["steps_completed"].append("database_restored")
                    else:
                        restore_result["errors"].append(f"Database restore failed: {result.stderr}")
                
            except Exception as e:
                restore_result["errors"].append(f"Database restore error: {e}")
            
            # Restore configurations
            try:
                config_backup_path = temp_dir / "letta_backup" / "configs"
                if config_backup_path.exists():
                    config_dir = Path("/home/cbwinslow/dotfiles/ai/configs")
                    shutil.copytree(config_backup_path, config_dir, dirs_exist_ok=True)
                    restore_result["steps_completed"].append("configs_restored")
                    
            except Exception as e:
                restore_result["warnings"].append(f"Config restore warning: {e}")
            
            # Restart Letta server
            try:
                docker_compose_path = "/home/cbwinslow/infra/letta/docker-compose.letta.yml"
                if Path(docker_compose_path).exists():
                    result = subprocess.run(
                        ["docker-compose", "-f", docker_compose_path, "up", "-d"],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.returncode == 0:
                        restore_result["steps_completed"].append("server_restarted")
                    else:
                        restore_result["errors"].append(f"Server restart failed: {result.stderr}")
                
            except Exception as e:
                restore_result["warnings"].append(f"Server restart warning: {e}")
            
            # Verify restore
            try:
                health = check_server_health()
                if health["status"] == "healthy":
                    restore_result["steps_completed"].append("restore_verified")
                else:
                    restore_result["warnings"].append("Restore completed but server health check shows issues")
                    
            except Exception as e:
                restore_result["warnings"].append(f"Restore verification warning: {e}")
            
        finally:
            # Clean up temporary directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        
        # Determine final status
        if restore_result["errors"]:
            restore_result["status"] = "failed"
        elif restore_result["warnings"]:
            restore_result["status"] = "warning"
        else:
            restore_result["status"] = "success"
        
        logger.info(f"Server restore completed: {restore_result['status']}")
        return restore_result
        
    except Exception as e:
        logger.error(f"Failed to restore server data: {e}")
        raise


def get_server_logs(log_level: str = "INFO", limit: int = 100) -> Dict[str, Any]:
    """
    Get server logs for monitoring and debugging.
    
    Args:
        log_level: Minimum log level to include
        limit: Maximum number of log entries to return
        
    Returns:
        Server logs
    """
    try:
        logs = {
            "timestamp": datetime.now().isoformat(),
            "log_level": log_level,
            "limit": limit,
            "entries": [],
            "total_entries": 0
        }
        
        # Get Docker logs if using Docker
        try:
            docker_compose_path = "/home/cbwinslow/infra/letta/docker-compose.letta.yml"
            if Path(docker_compose_path).exists():
                result = subprocess.run(
                    ["docker-compose", "-f", docker_compose_path, "logs", "--tail", str(limit)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    log_lines = result.stdout.strip().split('\n')
                    logs["entries"] = log_lines[-limit:]
                    logs["total_entries"] = len(log_lines)
                    
        except Exception as e:
            logs["warnings"] = [f"Failed to get Docker logs: {e}"]
        
        # Get application logs
        try:
            log_dir = Path("/home/cbwinslow/dotfiles/ai/logs")
            if log_dir.exists():
                log_files = list(log_dir.glob("*.log"))
                for log_file in log_files:
                    with open(log_file, 'r') as f:
                        file_logs = f.readlines()
                        logs["entries"].extend(file_logs[-limit:])
                
                logs["total_entries"] = len(logs["entries"])
                
        except Exception as e:
            logs["warnings"] = logs.get("warnings", []) + [f"Failed to get application logs: {e}"]
        
        logger.info(f"Server logs retrieved: {len(logs['entries'])} entries")
        return logs
        
    except Exception as e:
        logger.error(f"Failed to get server logs: {e}")
        raise