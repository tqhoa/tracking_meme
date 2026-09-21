Flush current session to persistent memory.

Steps:
1. Summarize what was done this session (3-5 bullets)
2. Append new lessons to MEMORY.md under ## Recent Sessions with [YYYY-MM-DD] prefix
3. Append new decisions to MEMORY.md under ## Architectural Decisions if any
4. Append new mistakes to MEMORY.md under ## Known Mistakes if any
5. Update ## Open Threads — close resolved, add new
6. If any project in 10-Projects/ was touched: update its State section
7. Count lines in MEMORY.md — if > 180, archive oldest entries:
   - Move entries older than 30 days to .claude/memory/archive/MEMORY-YYYY-MM-DD.md
   - Keep routing table and recent 30 days in MEMORY.md

Report: what was saved, what was archived, current MEMORY.md line count.
