# Git Workflow & Branch Strategy

This document describes the Git workflow for managing the AI agent dotfiles repository.

## Branch Strategy

### Main Branches

- **`main`** — Production-ready, always deployable. All releases tagged from this branch.
- **`develop`** — Integration branch for features. CI/CD runs on both main and develop.

### Supporting Branches

- **`feature/<name>`** — New features (e.g., `feature/new-skill-category`)
- **`release/<version>`** — Release preparation (e.g., `release/1.1.0`)
- **`hotfix/<issue>`** — Emergency fixes (e.g., `hotfix/security-patch`)

## Versioning

We use **Semantic Versioning** (MAJOR.MINOR.PATCH):

- **MAJOR** — Breaking changes to agent configs/skills structure
- **MINOR** — New agents, major skill additions, new frameworks
- **PATCH** — Bug fixes, documentation updates, minor improvements

Current version: **1.0.0** (defined in `dotfiles/ai/VERSION`)

## Release Process

### Automated (CI/CD)

On merge to `main`:

1. All GitHub Actions workflows run:
   - `chezmoi.yml` — configuration validation
   - `skills-ci.yml` — agent structure, skill tests, SKILL.md coverage
   - `security-scan.yml` — secret scanning, YAML validation
2. If all jobs pass:
   - `release.yml` workflow triggers (on version tag push)
   - Auto-generates GitHub Release with changelog
   - Updates VERSION file with commit SHA and build date
   - Creates deploy badge

### Manual Release

```bash
# 1. Ensure develop is up-to-date
git checkout develop
git pull origin develop

# 2. Merge to main (via PR or direct)
git checkout main
git merge develop --no-edit

# 3. Bump version in dotfiles/ai/VERSION
#    Edit VERSION file: VERSION=1.1.0

# 4. Update CHANGELOG.md with new section

# 5. Commit and push
git add dotfiles/ai/VERSION dotfiles/ai/CHANGELOG.md
git commit -m "chore: bump version to 1.1.0"
git push origin main

# 6. Create annotated tag
git tag -a v1.1.0 -m "Release 1.1.0 - New features"
git push origin v1.1.0

# 7. Release workflow auto-creates GitHub Release
```

## Workflow Management with Git Worktrees

The `worktree-manager.sh` script allows you to work on multiple branches simultaneously without stashing:

```bash
# List worktrees
./scripts/worktree-manager.sh list

# Create worktree for feature development
./scripts/worktree-manager.sh create develop my-devel
# Creates ~/.local/share/chezmoi-worktrees/my-devel

# Switch to worktree (cd's automatically)
./scripts/worktree-manager.sh checkout my-devel

# Sync worktree with remote
./scripts/worktree-manager.sh sync my-devel

# Remove worktree when done
./scripts/worktree-manager.sh remove my-devel
```

Benefits:
- Work on multiple branches in parallel
- No need to stash/unstash changes
- Each worktree has its own chezmoi apply state
- Easy experimentation with different agent configs

## Branch Protection Rules

Configure on GitHub (Settings → Branches → Branch protection rules):

### `main` branch
- ✅ Require pull request before merging
- ✅ Require status checks (all CI workflows must pass):
  - `chezmoi.yml/validate`
  - `skills-ci.yml/validate-structure`
  - `skills-ci.yml/test-skills`
  - `skills-ci.yml/skill-md-coverage`
  - `security-scan.yml/trufflehog`
  - `security-scan.yml/yaml-validation`
- ✅ Require linear history (squash merge disabled)
- ✅ Require conversation resolution (no unresolved PR comments)
- ✅ Restrict pushes (only specific users/bots can push)

### `develop` branch
- ✅ Require pull request before merging
- ✅ Require status checks (at least `chezmoi.yml/validate`)
- ✅ Allow pushes from maintainers

## CI/CD Workflows

### 1. Chezmoi Validation (`chezmoi.yml`)
Runs on every push to any branch.

Steps:
- Setup chezmoi
- Run `chezmoi diff` (dry-run to check for conflicts)
- Run `chezmoi verify` (chekmoi internal validation)
- Run `chezmoi doctor` (system health check)
- Scan for obvious secrets in config files

### 2. Skills CI (`skills-ci.yml`)
Runs on `main` and `develop` when AI agent files change.

Jobs:
- **validate-structure** — Validates agent config.yaml schema
- **test-skills** — Matrix test for each agent (parallel)
- **skill-md-coverage** — Ensures all skills have SKILL.md
- **deploy** — Only on main, tags release, updates badge

### 3. Security Scan (`security-scan.yml`)
Runs on every push to main/develop and daily via schedule.

Jobs:
- **trufflehog** — Deep secret scanning with OSS
- **check-secrets** — Gitleaks high-entropy string detection
- **yaml-validation** — Syntax check for all YAML files
- **agent-config-schema** — Schema validation for agent configs

### 4. Release (`release.yml`)
Runs only when a version tag (`v*.*.*`) is pushed.

Steps:
- Generate release notes from CHANGELOG.md
- Create GitHub Release with auto-generated assets
- Update VERSION file with commit SHA and timestamp
- Create deploy badge
- Post notification

## GitHub Community Files

- **`.github/CODEOWNERS`** — Auto-assigns reviewers based on paths
- **`.github/dependabot.yml`** — Auto-updates GitHub Actions, npm, pip deps
- **`.github/ISSUE_TEMPLATE/`** — Structured bug reports and feature requests
- **`.github/pull_request_template.yml`** — PR checklist and guidelines

## Contributor Workflow

1. **Sync your fork/branch:**
   ```bash
   git checkout develop
   git pull origin develop
   ```

2. **Create feature branch:**
   ```bash
   git checkout -b feature/my-new-skill
   ```

3. **Make changes** — edit configs, skills, scripts

4. **Validate locally:**
   ```bash
   chezmoi diff
   chezmoi verify
   ./scripts/worktree-manager.sh sync .
   ```

5. **Commit with conventional message:**
   ```bash
   git commit -m "feat: add commit-style skill for conventional commits"
   ```

6. **Push and open PR:**
   ```bash
   git push -u origin feature/my-new-skill
   # Open PR on GitHub, request review per CODEOWNERS
   ```

7. **CI runs automatically** — fix any failures

8. **Squash and merge** to `develop` (or `main` for hotfixes)

## Hotfix Process

For critical security or production issues:

1. Create branch from `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/security-issue
   ```

2. Fix the issue, following same validation steps

3. PR directly to `main` (bypass develop for speed)

4. After merge, tag immediately:
   ```bash
   git checkout main
   git pull origin main
   VERSION=$(grep '^VERSION=' dotfiles/ai/VERSION | cut -d= -f2)
   # Increment PATCH: 1.0.1 -> 1.0.2
   # Edit VERSION, commit, then:
   git tag -a v1.0.2 -m "Hotfix: security issue"
   git push origin v1.0.2
   ```

5. Backport to `develop`:
   ```bash
   git checkout develop
   git merge --no-ff hotfix/security-issue
   git push origin develop
   ```

## Nightly Maintenance

The `security-scan.yml` workflow runs daily at 6 AM UTC. Results appear in GitHub Security tab.

Additionally, consider setting up:
- **Dependabot** — already configured for weekly updates
- **Renovate** — if you need more control (we could add)

## Monitoring

- **CI Status Badge** —`.github/badges/skills.json` updated on deploy
- **Release RSS** — GitHub releases provide RSS feed
- **Security Alerts** — GitHub sends email for secret scanning

## Rollback Procedure

If a release introduces issues:

```bash
# 1. Find last good commit from git log
git log --oneline --tags --simplify-by-decoration

# 2. Create hotfix branch from good tag
git checkout -b hotfix/rollback v1.0.0

# 3. Revert problematic commit(s)
git revert <bad-commit-sha>

# 4. Push and PR to main with hotfix label
# 5. Tag new patch release (e.g., v1.0.1)
```

## Tools & Aliases

Useful commands:

```bash
# See all branches with latest commit
git branch -av

# See all tags
git tag -l -n --sort=-version:refname

# Check status of all worktrees
git worktree list

# Prune stale worktrees
git worktree prune

# Validate YAML locally (same as CI)
find dotfiles/ai -name "*.yaml" -exec python3 -c "import yaml; yaml.safe_load(open('{}'))" \;

# Run validate_skills.py locally
python3 dotfiles/ai/scripts/validate_skills.py --agent opencode
```

## Further Reading

- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

**Maintained by:** cbwinslow  
**Last Updated:** 2026-04-04  
**Repository:** github.com/cbwinslow/dotfiles
