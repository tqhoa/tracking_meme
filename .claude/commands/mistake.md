Record a mistake or pitfall to avoid repeating.

Steps:
1. Create file: 60-Mistakes/YYYY-MM-DD-{kebab-slug}.md
2. Frontmatter:
   ```yaml
   ---
   type: mistake
   status: active
   date: YYYY-MM-DD
   tags: []
   ---
   ```
3. Sections: ## What Happened, ## Root Cause, ## How to Avoid, ## Detection
4. Append to MEMORY.md under ## Known Mistakes:
   `[YYYY-MM-DD] {mistake} — {how to avoid}`
5. Append relevant detail to .claude/memory/tools/ or .claude/memory/domain/ file

Format for mistake entries: "NEVER do X because Y, instead do Z"
Report: file created, memory updated.
