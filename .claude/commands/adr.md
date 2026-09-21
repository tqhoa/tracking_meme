Create an Architecture Decision Record (ADR).

Steps:
1. Ask for: decision title (if not provided in args)
2. Create file: 50-Decisions/YYYY-MM-DD-{kebab-slug}.md
3. Use frontmatter:
   ```yaml
   ---
   type: decision
   status: active
   date: YYYY-MM-DD
   tags: []
   ---
   ```
4. Sections: ## Context, ## Decision, ## Consequences, ## Alternatives Considered
5. Append one-liner to MEMORY.md under ## Architectural Decisions:
   `[YYYY-MM-DD] {Decision title} — {one sentence summary}`
6. Update Index.md Decisions table

Report: file created, MEMORY.md updated.
