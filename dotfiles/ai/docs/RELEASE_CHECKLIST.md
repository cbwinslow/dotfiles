# Release Checklist

Use this checklist when preparing a new release of the AI Agent Dotfiles.

## Pre-Release

- [ ] All CI workflows passing on `main` branch
- [ ] No critical security alerts in GitHub Security tab
- [ ] VERSION file updated to new version (e.g., `VERSION=1.1.0`)
- [ ] CHANGELOG.md updated with new version section under [Unreleased]
- [ ] All agent configs validated locally (`./scripts/validate_skills.py --agent <name>`)
- [ ] SKILL.md coverage complete (`find dotfiles/ai/shared/skills -type d -exec test -f {}/SKILL.md \; -print`)
- [ ] Documentation updated (GIT_WORKFLOW.md, READMEs)
- [ ] Run `chezmoi apply --dry-run` succeeds without errors
- [ ] Secrets scanning returns clean
- [ ] Update branch protection if needed

## Create Release

1. Ensure `main` branch is up-to-date and CI green
2. Bump version in `dotfiles/ai/VERSION`
3. Move [Unreleased] changes to new version section in `CHANGELOG.md`
4. Commit with message: `chore: release vX.Y.Z`
5. Push to origin: `git push origin main`
6. Create and push annotated tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push origin vX.Y.Z`
7. Wait for `release.yml` workflow to auto-create GitHub Release
8. Verify release assets (notes, badge) are correct

## Post-Release

- [ ] GitHub Release published with correct changelog
- [ ] Deploy badge updated in repo (`.github/badges/skills.json`)
- [ ] VERSION file updated with COMMIT_SHA and BUILD_DATE (automated)
- [ ] Announce release to team/community if applicable
- [ ] Monitor for any issues reported from users

## Hotfix Process (if critical issue found after release)

1. Create branch from `main`: `git checkout -b hotfix/<issue>`
2. Fix the issue, validate, test
3. Commit and push hotfix branch
4. Open PR directly to `main` (bypass develop)
5. After merge, create patch release: `VERSION=X.Y.Z+1`
6. Tag and push: `git tag -a vX.Y.Z+1 && git push origin vX.Y.Z+1`
7. Also merge hotfix back to `develop`: `git checkout develop && git merge --no-ff hotfix/<issue>`

## Branch Protection

Main branch should have:
- Require PR reviews (1 approver)
- Require status checks: all CI jobs must pass
- Require linear history
- Require conversation resolution
- Restrict pushes (maintainers only)

Develop branch:
- Require PR reviews (optional)
- Require at least `chezmoi.yml/validate`
- Allow maintainer pushes

## Rollback

If a release introduces breaking changes:

```bash
# Find last good commit/tag
git log --oneline --tags --simplify-by-decoration

# Create hotfix branch from good tag
git checkout -b hotfix/rollback v1.0.0

# Revert problematic commit(s)
git revert <bad-commit-sha>

# Push, PR to main, tag as patch (1.0.1)
```

---

**Maintained by:** cbwinslow  
**Last Updated:** 2026-04-04  
**Required for:** All contributors and maintainers
