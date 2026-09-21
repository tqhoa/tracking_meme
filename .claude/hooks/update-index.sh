#!/bin/bash
# Log new .md files created since last Index.md update

VAULT_DIR="/Users/mabu/Desktop/self_agents"
INDEX_FILE="$VAULT_DIR/Index.md"
LOG="$VAULT_DIR/.claude/hooks/session.log"

[[ ! -f "$INDEX_FILE" ]] && exit 0

NEW_FILES=$(find "$VAULT_DIR" -name "*.md" -newer "$INDEX_FILE" \
  -not -path "*/.claude/*" \
  -not -name "MEMORY.md" \
  -not -name "CLAUDE.md" \
  -not -name "Index.md" \
  -not -path "*/.git/*" \
  2>/dev/null)

if [[ -n "$NEW_FILES" ]]; then
  echo "[$(date +%Y-%m-%d %H:%M)] New files (Index.md may need update):" >>"$LOG"
  echo "$NEW_FILES" >>"$LOG"
fi
