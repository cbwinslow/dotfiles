#!/usr/bin/env bash
# run_once_01-setup-dirs.sh
# Create the full server directory structure
set -euo pipefail

USER_HOME="${HOME}"

echo "==> Creating directory structure..."

# XDG base directories
for d in .config .local/share .local/state .cache; do
    mkdir -p "${USER_HOME}/${d}"
done

# Top-level working directories
for d in infra docker scripts procedures projects meta dotfiles bin; do
    mkdir -p "${USER_HOME}/${d}"
done

# Infrastructure layout
for d in \
    infra/ansible/{playbooks,roles,inventory,group_vars,host_vars} \
    infra/terraform/{modules,environments/{dev,stage,prod}} \
    infra/k8s/{base,overlays} \
    infra/gitops/{bootstrap,apps} \
    infra/monitoring/{prometheus,grafana,exporters,kuma}; do
    mkdir -p "${USER_HOME}/${d}"
done

# Docker layout
for d in docker/{stacks,templates,bin}; do
    mkdir -p "${USER_HOME}/${d}"
done

for s in traefik postgres monitoring misc openclaw n8n local-ai letta open-webui; do
    mkdir -p "${USER_HOME}/docker/stacks/${s}"
done

# Scripts layout
for d in scripts/{admin,maintenance,meta,ai}; do
    mkdir -p "${USER_HOME}/${d}"
done

# Procedures/runbooks
for d in procedures/{infra,docker,incidents,operations,ai}; do
    mkdir -p "${USER_HOME}/${d}"
done

# Projects
for d in projects/{apps,experiments,tools,ai}; do
    mkdir -p "${USER_HOME}/${d}"
done

# Metadata
for d in meta/{inventory,audit,agents}; do
    mkdir -p "${USER_HOME}/${d}"
done

# AI agent directories (XDG-compliant)
XDG_CONFIG="${USER_HOME}/.config"
XDG_DATA="${USER_HOME}/.local/share"
XDG_STATE="${USER_HOME}/.local/state"
XDG_CACHE="${USER_HOME}/.cache"

for d in \
    "${XDG_CONFIG}/ai-agents"/{providers,profiles,global} \
    "${XDG_DATA}/ai-agents"/{memory,vectorstores,artifacts} \
    "${XDG_STATE}/ai-agents"/{logs,sessions} \
    "${XDG_CACHE}/ai-agents"/{embeddings,tmp}; do
    mkdir -p "$d"
done

# Service data directories
for d in /srv/docker /srv/data /srv/meta; do
    if [[ ! -d "$d" ]]; then
        sudo mkdir -p "$d" 2>/dev/null || true
        sudo chown "${USER}:${USER}" "$d" 2>/dev/null || true
    fi
done

for d in /srv/docker/{traefik,postgres,monitoring,misc}; do
    if [[ ! -d "$d" ]]; then
        sudo mkdir -p "$d" 2>/dev/null || true
        sudo chown "${USER}:${USER}" "$d" 2>/dev/null || true
    fi
done

# Symlinks (idempotent)
[[ ! -e "${USER_HOME}/docker/_data" ]] && ln -s /srv/docker "${USER_HOME}/docker/_data"
[[ ! -e "${USER_HOME}/projects/_data" ]] && ln -s /srv/data "${USER_HOME}/projects/_data"

echo "==> Directory structure created."
