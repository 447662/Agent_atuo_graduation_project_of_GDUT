#!/usr/bin/env bash
set -euo pipefail
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/plugins/gdut-thesis-workflow/skills"
DEST_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$DEST_DIR"
cp -R "$SRC_DIR"/* "$DEST_DIR"/
echo "Installed GDUT thesis workflow skills to: $DEST_DIR"
