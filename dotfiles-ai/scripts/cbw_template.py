#!/usr/bin/env python3
"""
CBW Script Templates - Generate scripts from your indexed patterns
"""

import os
import sys
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')

from unified_memory.queries import search_files_content, get_shell_files


class ScriptTemplateLibrary:
    """Library of script templates extracted from indexed files."""
    
    TEMPLATES = {
        'postgres-backup': {
            'description': 'PostgreSQL database backup script',
            'patterns': ['psql', 'pg_dump', 'backup'],
        },
        'docker-deploy': {
            'description': 'Docker deployment script',
            'patterns': ['docker', 'docker-compose', 'deploy'],
        },
        'api-client': {
            'description': 'API client with curl or httpx',
            'patterns': ['curl', 'httpx', 'requests'],
        },
        'rag-query': {
            'description': 'Query the RAG database',
            'patterns': ['CBW_RAG_DATABASE', 'psql'],
        },
        'python-cli': {
            'description': 'Python CLI tool template',
            'patterns': ['argparse', 'def main', 'if __name__'],
        },
    }
    
    def __init__(self):
        self.templates_dir = os.path.expanduser('~/dotfiles/ai/templates/scripts')
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def generate_template(self, template_name: str) -> str:
        """Generate a script template based on indexed patterns."""
        if template_name not in self.TEMPLATES:
            return None
        
        template_info = self.TEMPLATES[template_name]
        patterns = template_info['patterns']
        
        # Search for relevant code
        code_examples = []
        for pattern in patterns:
            results = search_files_content(pattern, file_extensions=['.sh', '.py'], max_results=5)
            for r in results:
                text = r.get('chunk_text', '')
                lines = text.split('\n')
                for line in lines:
                    if pattern in line and len(line.strip()) > 10:
                        code_examples.append({
                            'code': line.strip(),
                            'file': r['file_path']
                        })
                        break
        
        # Generate template based on type
        if 'postgres' in template_name:
            return self._generate_postgres_template(code_examples)
        elif 'docker' in template_name:
            return self._generate_docker_template(code_examples)
        elif 'api' in template_name:
            return self._generate_api_template(code_examples)
        elif 'python' in template_name:
            return self._generate_python_template(code_examples)
        else:
            return self._generate_generic_template(template_name, code_examples)
    
    def _generate_postgres_template(self, examples: list) -> str:
        """Generate PostgreSQL backup script template."""
        return '''#!/bin/bash
# PostgreSQL Backup Script
# Generated from indexed patterns

set -euo pipefail

# Configuration
PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5432}"
PG_USER="${PG_USER:-postgres}"
PG_DB="${PG_DB:-mydb}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Perform backup
echo "Backing up database $PG_DB..."
PGPASSWORD="$PG_PASSWORD" pg_dump \\
    -h "$PG_HOST" \\
    -p "$PG_PORT" \\
    -U "$PG_USER" \\
    -d "$PG_DB" \\
    -F custom \\
    -f "$BACKUP_DIR/${PG_DB}_${DATE}.dump"

echo "Backup complete: $BACKUP_DIR/${PG_DB}_${DATE}.dump"
'''
    
    def _generate_docker_template(self, examples: list) -> str:
        """Generate Docker deployment template."""
        return '''#!/bin/bash
# Docker Deployment Script
# Generated from indexed patterns

set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
PROJECT_NAME="${PROJECT_NAME:-myproject}"

# Functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

deploy() {
    log "Building and deploying..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d --build
    log "Deployment complete"
}

stop() {
    log "Stopping services..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
}

logs() {
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f
}

# Main
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    stop)
        stop
        ;;
    logs)
        logs
        ;;
    *)
        echo "Usage: $0 {deploy|stop|logs}"
        exit 1
        ;;
esac
'''
    
    def _generate_api_template(self, examples: list) -> str:
        """Generate API client template."""
        return '''#!/bin/bash
# API Client Script
# Generated from indexed patterns

set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://localhost:8080}"
API_KEY="${API_KEY:-}"

# Function to make API calls
api_call() {
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"
    
    local curl_opts=(-s -H "Content-Type: application/json")
    
    if [ -n "$API_KEY" ]; then
        curl_opts+=(-H "Authorization: Bearer $API_KEY")
    fi
    
    if [ -n "$data" ]; then
        curl "$API_BASE_URL$endpoint" "${curl_opts[@]}" -X "$method" -d "$data"
    else
        curl "$API_BASE_URL$endpoint" "${curl_opts[@]}" -X "$method"
    fi
}

# Example usage
get() {
    api_call "GET" "$1"
}

post() {
    api_call "POST" "$1" "$2"
}

# Main
case "${1:-}" in
    get)
        get "$2"
        ;;
    post)
        post "$2" "$3"
        ;;
    *)
        echo "Usage: $0 {get|post} <endpoint> [data]"
        exit 1
        ;;
esac
'''
    
    def _generate_python_template(self, examples: list) -> str:
        """Generate Python CLI template."""
        return '''#!/usr/bin/env python3
"""
Python CLI Tool Template
Generated from indexed patterns
"""

import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='My CLI Tool')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add subcommands here
    cmd_parser = subparsers.add_parser('command', help='Example command')
    cmd_parser.add_argument('input', help='Input file')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.command == 'command':
        logger.info(f"Processing {args.input}")
        # Your code here
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
'''
    
    def _generate_generic_template(self, name: str, examples: list) -> str:
        """Generate generic script template."""
        return f'''#!/bin/bash
# {name.replace('-', ' ').title()} Script
# Generated from indexed patterns

set -euo pipefail

# TODO: Add your script logic here
# Found {len(examples)} relevant code examples in indexed files

echo "Template: {name}"
echo "Modify this script for your needs"
'''
    
    def save_template(self, template_name: str, output_path: str = None):
        """Generate and save a template."""
        template = self.generate_template(template_name)
        
        if not template:
            print(f"Unknown template: {template_name}")
            return None
        
        if not output_path:
            output_path = os.path.join(self.templates_dir, f"{template_name}.sh")
        
        with open(output_path, 'w') as f:
            f.write(template)
        
        os.chmod(output_path, 0o755)
        print(f"Template saved: {output_path}")
        return output_path
    
    def list_templates(self):
        """List available templates."""
        print("Available Templates:")
        print("=" * 50)
        for name, info in self.TEMPLATES.items():
            print(f"  {name:20} - {info['description']}")
    
    def list_saved(self):
        """List saved template files."""
        if os.path.exists(self.templates_dir):
            files = [f for f in os.listdir(self.templates_dir) if f.endswith(('.sh', '.py'))]
            if files:
                print(f"\nSaved templates in {self.templates_dir}:")
                for f in sorted(files):
                    print(f"  - {f}")
            else:
                print(f"\nNo templates saved yet in {self.templates_dir}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='CBW Script Templates')
    parser.add_argument('--list', action='store_true', help='List available templates')
    parser.add_argument('--list-saved', action='store_true', help='List saved templates')
    parser.add_argument('--generate', type=str, help='Generate a template')
    parser.add_argument('--output', type=str, help='Output path for generated template')
    args = parser.parse_args()
    
    lib = ScriptTemplateLibrary()
    
    if args.list:
        lib.list_templates()
    elif args.list_saved:
        lib.list_saved()
    elif args.generate:
        lib.save_template(args.generate, args.output)
    else:
        lib.list_templates()
        print("\nUsage:")
        print("  cbw-template --list")
        print("  cbw-template --generate postgres-backup --output backup.sh")


if __name__ == '__main__':
    main()
