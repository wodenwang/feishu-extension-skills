#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$ROOT_DIR/skills/feishu-chat-server-api"
DEFAULT_VERSION="$(
  ROOT_DIR="$ROOT_DIR" python3 - <<'PY'
from pathlib import Path
import os, re
text = Path(os.environ["ROOT_DIR"]) / "pyproject.toml"
match = re.search(r'^version = "([^"]+)"$', text.read_text(), re.M)
print(match.group(1) if match else "0.1.0")
PY
)"

VERSION="${1:-$DEFAULT_VERSION}"
CHANGELOG="${2:-Sync latest feishu-chat-server-api from repository}"

if ! command -v clawhub >/dev/null 2>&1; then
  echo "clawhub CLI is required" >&2
  exit 1
fi

clawhub publish "$SKILL_DIR" \
  --slug feishu-chat-server-api \
  --name "Feishu Chat Server API" \
  --version "$VERSION" \
  --changelog "$CHANGELOG" \
  --tags latest
