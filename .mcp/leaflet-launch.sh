#!/usr/bin/env bash
# Launcher for the Leaflet MCP server (github.com/philgebauer/leaflet-mcp-server).
# The package is NOT published to npm and its .gitignore excludes the build output,
# so `npx github:...` ships a broken install. We clone + build from source instead.
# The build is cached in $HOME and rebuilt automatically on a fresh (ephemeral) container.
set -euo pipefail

REPO="https://github.com/philgebauer/leaflet-mcp-server.git"
DIR="${HOME}/.mcp-servers/leaflet-mcp-server"

# docs.js is the file missing from broken installs -> use it as the build sentinel.
if [ ! -f "${DIR}/build/docs.js" ]; then
  rm -rf "${DIR}"
  mkdir -p "$(dirname "${DIR}")"
  # All build noise goes to stderr so it never corrupts the MCP stdio (stdout) channel.
  git clone --depth 1 "${REPO}" "${DIR}" 1>&2
  ( cd "${DIR}" && npm install 1>&2 && npm run build 1>&2 )
fi

exec node "${DIR}/build/index.js"
