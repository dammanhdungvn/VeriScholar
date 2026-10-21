#!/usr/bin/env bash
export GITHUB_PERSONAL_ACCESS_TOKEN=$(gh auth token 2>/dev/null)
exec npx -y @modelcontextprotocol/server-github "$@"
