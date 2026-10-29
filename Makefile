# Set up Claude Code on this machine with the shared rules, skills and memory.
# Uses the folder Claude Code uses: $CLAUDE_CONFIG_DIR if set (host), else ~/.claude (Mac)
# Details and overrides: bin/setup-claude.sh

.PHONY: setup rules skills memory check help
setup:      ## everything below (default)
	@bin/setup-claude.sh all
rules:      ## CLAUDE.md -> agents/AGENT.md, built-in auto-memory off
	@bin/setup-claude.sh rules
skills:     ## link every skill in skills/
	@bin/setup-claude.sh skills
memory:     ## register the shared memory server (asks for its key if needed)
	@bin/setup-claude.sh memory
check:      ## test the memory server and key without changing anything
	@bin/setup-claude.sh check
help:
	@grep -E '^[a-z]+:.*## ' Makefile | sed 's/:.*## /\t/'
