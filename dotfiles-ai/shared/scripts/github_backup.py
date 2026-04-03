#!/usr/bin/env python3
"""
GitHub Backup and Synchronization Script

Automatically backs up the Agent AI Skills System to GitHub and manages synchronization.
This ensures the system is version-controlled and available across all environments.
"""

import os
import sys
import json
import subprocess
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GitHubBackup:
    def __init__(self, base_path: str = "/home/cbwinslow/dotfiles/ai"):
        self.base_path = Path(base_path)
        self.repo_url = "https://github.com/cbwinslow/agent-ai-skills-system.git"
        self.backup_dir = Path.home() / "backups" / "ai-skills-system"
        self.local_repo_path = self.base_path
        
        # Files and directories to include in backup
        self.include_patterns = [
            "agents/",
            "frameworks/",
            "skills/",
            "tools/",
            "configs/",
            "packages/",
            "scripts/",
            "docs/",
            "global_rules/",
            "*.md",
            "*.yaml",
            "*.yml",
            "*.py",
            "*.sh",
            "requirements.txt",
            "setup.py"
        ]
        
        # Files and directories to exclude
        self.exclude_patterns = [
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".git/",
            ".vscode/",
            ".idea/",
            "*.log",
            "*.tmp",
            "node_modules/",
            "*.db",
            "*.sqlite",
            "backups/",
            "test_results/",
            "*.swp",
            "*.swo"
        ]
    
    def check_git_status(self) -> bool:
        """Check if the directory is a git repository and is clean."""
        try:
            # Check if it's a git repo
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.info("Directory is not a git repository. Initializing...")
                return self.init_git_repo()
            
            # Check if working directory is clean
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                logger.warning("Working directory has untracked changes:")
                logger.warning(result.stdout)
                return False
            else:
                logger.info("✓ Git repository is clean")
                return True
                
        except Exception as e:
            logger.error(f"Error checking git status: {e}")
            return False
    
    def init_git_repo(self) -> bool:
        """Initialize a new git repository."""
        try:
            logger.info("Initializing git repository...")
            
            # Initialize repository
            subprocess.run(["git", "init"], cwd=self.local_repo_path, check=True)
            
            # Create .gitignore
            gitignore_content = self._generate_gitignore()
            with open(self.local_repo_path / ".gitignore", 'w') as f:
                f.write(gitignore_content)
            
            # Add remote origin
            subprocess.run(
                ["git", "remote", "add", "origin", self.repo_url],
                cwd=self.local_repo_path,
                check=True
            )
            
            # Create initial commit
            subprocess.run(["git", "add", "."], cwd=self.local_repo_path, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit: Agent AI Skills System"],
                cwd=self.local_repo_path,
                check=True
            )
            
            logger.info("✓ Git repository initialized")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to initialize git repository: {e}")
            return False
        except Exception as e:
            logger.error(f"Error initializing git repository: {e}")
            return False
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore content."""
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Dependencies
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
*.log.*
logs/

# Temporary files
*.tmp
*.temp
.tmp/

# Database files
*.db
*.sqlite
*.sqlite3

# Backup files
backups/
*.bak
*.backup

# Test results
test_results/
htmlcov/
.pytest_cache/

# Environment files (keep .env.example)
.env
.env.local
.env.development
.env.test
.env.production

# Node.js (if any)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Letta specific
letta.log
letta.db
'''
    
    def create_backup(self) -> bool:
        """Create a backup of the current system."""
        try:
            logger.info("Creating backup...")
            
            # Create backup directory with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copy files to backup
            for pattern in self.include_patterns:
                if pattern.endswith('/'):
                    # Directory pattern
                    src_dir = self.local_repo_path / pattern.rstrip('/')
                    if src_dir.exists():
                        dst_dir = backup_path / pattern.rstrip('/')
                        shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
                        logger.info(f"✓ Backed up directory: {pattern}")
                else:
                    # File pattern
                    for file_path in self.local_repo_path.glob(pattern):
                        if file_path.is_file():
                            dst_path = backup_path / file_path.relative_to(self.local_repo_path)
                            dst_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file_path, dst_path)
                            logger.info(f"✓ Backed up file: {pattern}")
            
            # Create backup manifest
            manifest = {
                "timestamp": timestamp,
                "backup_path": str(backup_path),
                "included_patterns": self.include_patterns,
                "excluded_patterns": self.exclude_patterns,
                "git_status": self._get_git_status()
            }
            
            with open(backup_path / "backup_manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"✓ Backup created at: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def _get_git_status(self) -> Dict[str, Any]:
        """Get current git status information."""
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True
            )
            current_branch = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            # Get latest commit hash
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True
            )
            commit_hash = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            # Get remote URL
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True
            )
            remote_url = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            return {
                "branch": current_branch,
                "commit": commit_hash,
                "remote": remote_url
            }
            
        except Exception as e:
            logger.warning(f"Could not get git status: {e}")
            return {"error": str(e)}
    
    def commit_changes(self, message: Optional[str] = None) -> bool:
        """Commit changes to the local repository."""
        try:
            logger.info("Committing changes...")
            
            # Generate commit message if not provided
            if not message:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"Auto-commit: Agent AI Skills System update ({timestamp})"
            
            # Add all changes
            subprocess.run(["git", "add", "."], cwd=self.local_repo_path, check=True)
            
            # Create commit
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.local_repo_path,
                check=True
            )
            
            logger.info("✓ Changes committed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to commit changes: {e}")
            return False
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            return False
    
    def push_to_github(self) -> bool:
        """Push changes to GitHub."""
        try:
            logger.info("Pushing to GitHub...")
            
            # Check if remote exists
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error("No remote origin found. Please set up remote repository first.")
                return False
            
            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error("Could not determine current branch")
                return False
            
            current_branch = result.stdout.strip()
            
            # Push to GitHub
            subprocess.run(
                ["git", "push", "-u", "origin", current_branch],
                cwd=self.local_repo_path,
                check=True
            )
            
            logger.info("✓ Changes pushed to GitHub successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to push to GitHub: {e}")
            return False
        except Exception as e:
            logger.error(f"Error pushing to GitHub: {e}")
            return False
    
    def pull_from_github(self) -> bool:
        """Pull latest changes from GitHub."""
        try:
            logger.info("Pulling from GitHub...")
            
            # Check if there are local changes
            if not self.check_git_status():
                logger.warning("Local changes detected. Please commit or stash them first.")
                return False
            
            # Pull from GitHub
            subprocess.run(["git", "pull", "origin", "main"], cwd=self.local_repo_path, check=True)
            
            logger.info("✓ Changes pulled from GitHub successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to pull from GitHub: {e}")
            return False
        except Exception as e:
            logger.error(f"Error pulling from GitHub: {e}")
            return False
    
    def create_release(self, version: str, description: str = "") -> bool:
        """Create a new release on GitHub."""
        try:
            logger.info(f"Creating release {version}...")
            
            # Create git tag
            subprocess.run(["git", "tag", "-a", version, "-m", description], cwd=self.local_repo_path, check=True)
            
            # Push tag to GitHub
            subprocess.run(["git", "push", "origin", version], cwd=self.local_repo_path, check=True)
            
            logger.info(f"✓ Release {version} created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create release: {e}")
            return False
        except Exception as e:
            logger.error(f"Error creating release: {e}")
            return False
    
    def sync_with_github(self) -> bool:
        """Full synchronization with GitHub."""
        logger.info("=" * 60)
        logger.info("Agent AI Skills System - GitHub Synchronization")
        logger.info("=" * 60)
        
        # Create backup first
        if not self.create_backup():
            logger.error("❌ Backup creation failed. Aborting sync.")
            return False
        
        # Check git status
        if not self.check_git_status():
            # Commit changes if there are any
            if not self.commit_changes("Auto-commit: System update before sync"):
                logger.error("❌ Failed to commit changes. Aborting sync.")
                return False
        
        # Pull latest changes from GitHub
        if not self.pull_from_github():
            logger.error("❌ Failed to pull from GitHub. Aborting sync.")
            return False
        
        # Push local changes to GitHub
        if not self.push_to_github():
            logger.error("❌ Failed to push to GitHub. Aborting sync.")
            return False
        
        logger.info("=" * 60)
        logger.info("🎉 GitHub synchronization complete!")
        logger.info("=" * 60)
        
        return True
    
    def setup_github_actions(self) -> bool:
        """Setup GitHub Actions for automated workflows."""
        try:
            logger.info("Setting up GitHub Actions...")
            
            # Create .github/workflows directory
            workflows_dir = self.local_repo_path / ".github" / "workflows"
            workflows_dir.mkdir(parents=True, exist_ok=True)
            
            # Create CI/CD workflow
            ci_workflow = workflows_dir / "ci.yml"
            ci_content = '''name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -e packages/agent_memory
    
    - name: Run validation
      run: python scripts/validate_system.py
    
    - name: Run tests
      run: pytest tests/ -v
    
    - name: Check code quality
      run: |
        black --check .
        flake8 .
        mypy . --ignore-missing-imports

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: echo "Deployment logic here"
'''
            
            with open(ci_workflow, 'w') as f:
                f.write(ci_content)
            
            # Create backup workflow
            backup_workflow = workflows_dir / "backup.yml"
            backup_content = '''name: Daily Backup

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:  # Allow manual triggering

jobs:
  backup:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Create backup
      run: python scripts/github_backup.py --create-backup
    
    - name: Upload backup to storage
      uses: actions/upload-artifact@v3
      with:
        name: daily-backup
        path: backups/
'''
            
            with open(backup_workflow, 'w') as f:
                f.write(backup_content)
            
            logger.info("✓ GitHub Actions workflows created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup GitHub Actions: {e}")
            return False
    
    def create_documentation(self) -> bool:
        """Create comprehensive documentation for GitHub."""
        try:
            logger.info("Creating GitHub documentation...")
            
            # Create CONTRIBUTING.md
            contributing_path = self.local_repo_path / "CONTRIBUTING.md"
            contributing_content = '''# Contributing to Agent AI Skills System

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/ai-skills-system.git
   cd ai-skills-system
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e packages/agent_memory
   ```
4. Run tests:
   ```bash
   pytest tests/
   ```

## Code Style

- Use Black for code formatting
- Use Flake8 for linting
- Use MyPy for type checking
- Follow PEP 8 guidelines

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run validation:
```bash
python scripts/validate_system.py
```

## Pull Request Guidelines

1. Create feature branches from `develop`
2. Write clear commit messages
3. Update documentation for new features
4. Ensure all tests pass
5. Squash commits before merging

## Issue Reporting

When reporting issues, please include:
- System information (OS, Python version)
- Steps to reproduce
- Expected vs actual behavior
- Any error messages
'''
            
            with open(contributing_path, 'w') as f:
                f.write(contributing_content)
            
            # Create CODE_OF_CONDUCT.md
            code_of_conduct_path = self.local_repo_path / "CODE_OF_CONDUCT.md"
            code_of_conduct_content = '''# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity and
orientation.

## Our Standards

Examples of behavior that contributes to a positive environment for our
community include:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback
* Accepting responsibility and apologizing to those affected by our mistakes,
  and learning from the experience
* Focusing on what is best not just for us as individuals, but for the overall
  community

Examples of unacceptable behavior include:

* The use of sexualized language or imagery, and sexual attention or advances of
  any kind
* Trolling, insulting or derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or email address,
  without their explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

## Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

Community leaders have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned to this Code of Conduct, and will communicate reasons for moderation
decisions when appropriate.

## Scope

This Code of Conduct applies within all community spaces, and also applies when
an individual is officially representing the community in public spaces.
Examples of representing our community or organization include using the
official e-mail address, posting via an official social media account, or
acting as an appointed representative at an online or offline event.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders responsible for enforcement at
support@agentmemory.org. All complaints will be reviewed and investigated and will result in a
response that is deemed necessary and appropriate to the circumstances. The
community is obligated to maintain confidentiality with regard to the reporter
of an incident. Further details of specific enforcement policies may be posted
separately.

Community leaders who do not follow or enforce the Code of Conduct in good
faith may face temporary or permanent repercussions as determined by other
members of the community leadership.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.0, available at
[https://www.contributor-covenant.org/version/2/0/code_of_conduct.html][v2.0].

Community Impact Guidelines were inspired by [Mozilla's code of conduct
enforcement ladder][Mozilla CoC].

For answers to common questions about this code of conduct, see the FAQ at
[https://www.contributor-covenant.org/faq][FAQ]. Translations are available at
[https://www.contributor-covenant.org/translations][translations].

[homepage]: https://www.contributor-covenant.org
[v2.0]: https://www.contributor-covenant.org/version/2/0/code_of_conduct.html
[Mozilla CoC]: https://github.com/mozilla/diversity
[FAQ]: https://www.contributor-covenant.org/faq
[translations]: https://www.contributor-covenant.org/translations
'''
            
            with open(code_of_conduct_path, 'w') as f:
                f.write(code_of_conduct_content)
            
            logger.info("✓ GitHub documentation created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create documentation: {e}")
            return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub backup and synchronization for Agent AI Skills System")
    parser.add_argument("--create-backup", action="store_true", help="Create backup only")
    parser.add_argument("--sync", action="store_true", help="Full synchronization with GitHub")
    parser.add_argument("--commit", help="Commit changes with message")
    parser.add_argument("--push", action="store_true", help="Push to GitHub")
    parser.add_argument("--pull", action="store_true", help="Pull from GitHub")
    parser.add_argument("--release", help="Create release (format: v1.0.0)")
    parser.add_argument("--setup-actions", action="store_true", help="Setup GitHub Actions")
    parser.add_argument("--setup-docs", action="store_true", help="Setup documentation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    backup = GitHubBackup()
    
    if args.create_backup:
        success = backup.create_backup()
        sys.exit(0 if success else 1)
    
    elif args.sync:
        success = backup.sync_with_github()
        sys.exit(0 if success else 1)
    
    elif args.commit:
        success = backup.commit_changes(args.commit)
        sys.exit(0 if success else 1)
    
    elif args.push:
        success = backup.push_to_github()
        sys.exit(0 if success else 1)
    
    elif args.pull:
        success = backup.pull_from_github()
        sys.exit(0 if success else 1)
    
    elif args.release:
        success = backup.create_release(args.release, f"Release {args.release}")
        sys.exit(0 if success else 1)
    
    elif args.setup_actions:
        success = backup.setup_github_actions()
        sys.exit(0 if success else 1)
    
    elif args.setup_docs:
        success = backup.create_documentation()
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()