# Workflow: Repository Audit
# Purpose: Run a comprehensive repository audit covering structure, dependencies, security, and CI/CD

## Overview

This workflow performs a thorough analysis of a codebase to understand its structure, dependencies, security posture, and operational characteristics.

## Steps

### 1. Initial Exploration
- List top-level files and directories
- Identify the project's primary language and framework
- Check for documentation (README, CONTRIBUTING, etc.)

### 2. Dependency Analysis
- Locate and analyze package management files:
  - `package.json` / `package-lock.json` (Node.js)
  - `requirements.txt` / `pyproject.toml` / `poetry.lock` (Python)
  - `Cargo.toml` / `Cargo.lock` (Rust)
  - `go.mod` / `go.sum` (Go)
  - `Gemfile` / `Gemfile.lock` (Ruby)
  - `pom.xml` / `build.gradle` (Java)
- Check for outdated dependencies
- Identify security vulnerabilities in dependencies

### 3. Configuration & Tooling
- Check for CI/CD configuration:
  - `.github/workflows/` (GitHub Actions)
  - `.gitlab-ci.yml` (GitLab CI)
  - `Jenkinsfile`
  - `.circleci/`
- Check for code quality tools:
  - `.eslintrc`, `.prettierrc` (JavaScript)
  - `pyproject.toml` [tool.black], `setup.cfg` (Python)
  - `.rustfmt.toml` (Rust)
- Check for testing configuration:
  - `jest.config.js`, `pytest.ini`, etc.

### 4. Security Scan
- Check for exposed secrets:
  - `.env` files (should be in .gitignore)
  - Hardcoded API keys or tokens
  - Private keys or certificates
- Check `.gitignore` for proper exclusions
- Verify no sensitive files are tracked

### 5. Docker & Infrastructure
- Check for `Dockerfile`, `docker-compose.yml`
- Analyze container configuration
- Check for infrastructure-as-code:
  - Terraform files
  - Kubernetes manifests
  - Helm charts

### 6. Testing & Quality
- Identify test suites and frameworks
- Check test coverage (if configured)
- Look for linting and formatting rules

### 7. Documentation
- Evaluate README completeness
- Check for API documentation
- Look for architecture/decision records

## Output Format

The audit produces a structured report:

```markdown
# Repository Audit Report: <repo-name>

## Executive Summary
- **Language/Framework**: 
- **Primary Purpose**: 
- **Overall Health**: 🟢/🟡/🔴

## Structure
- **Top-level directories**:
- **Source code location**:
- **Test location**:

## Dependencies
- **Package Manager**:
- **Dependency Count**:
- **Outdated Dependencies**:
- **Security Vulnerabilities**:

## CI/CD
- **Platform**:
- **Workflows**:
- **Deployment**:

## Security
- **Secrets Found**: Yes/No (details)
- **Gitignore**: Complete/Incomplete
- **Recommendations**:

## Testing
- **Test Framework**:
- **Coverage**: X%
- **Test Count**:

## Recommendations
1. [Priority] <recommendation>
2. <recommendation>
```

## Usage

Run this workflow when:
- Onboarding to a new codebase
- Evaluating a third-party library
- Preparing for maintenance or refactoring
- Due diligence for acquisitions
