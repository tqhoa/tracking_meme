#!/bin/bash
# Auto-archive MEMORY.md entries older than 30 days on session stop

VAULT_DIR="/Users/mabu/Desktop/self_agents"
MEMORY_FILE="$VAULT_DIR/MEMORY.md"
ARCHIVE_DIR="$VAULT_DIR/.claude/memory/archive"
LOG="$VAULT_DIR/.claude/hooks/session.log"

[[ ! -f "$MEMORY_FILE" ]] && exit 0

mkdir -p "$ARCHIVE_DIR"

LINE_COUNT=$(wc -l <"$MEMORY_FILE")

if [[ $LINE_COUNT -gt 180 ]]; then
  ARCHIVE_FILE="$ARCHIVE_DIR/MEMORY-$(date +%Y%m%d-%H%M%S).md"
  cp "$MEMORY_FILE" "$ARCHIVE_FILE"
  echo "[$(date +%Y-%m-%d %H:%M)] MEMORY.md archived: $LINE_COUNT lines → $ARCHIVE_FILE" >>"$LOG"
fi

echo "[$(date +%Y-%m-%d %H:%M)] Session ended" >>"$LOG"
