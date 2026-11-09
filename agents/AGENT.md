## Memory

Long-term memory lives only in the `memory` MCP server. Never persist memory to files.

**Recall**
- At session start, `memory_list` with tag `general` (the index of topic tags), and `memory_search` with the project tag (repo/directory name).
- When the conversation touches a topic in the index, `memory_search` with that topic tag.
- Once the kind of work is clear, `memory_search` with that work-type tag for Ray's preferences. Repeat if it changes.

**Store** with `memory_store`, and tell Ray briefly: project decisions (with the why), context not in the code or git, Ray's preferences and corrections.

Tags are recall addresses, not keywords — use only:
- one scope tag: the project name, or a topic tag for things beyond one project (e.g. `home-network`, `tax`);
- `general` only for index memories: one per topic tag, saying what it covers and when to search it. Creating a topic tag means storing its index memory too;
- for Ray's preferences that hold across projects: `preference` + one work type (`coding`, `science`, `writing`, `language`, `travel`), with no scope tag.

Ask before storing personal information (home, workplace, health, family, finances). Never store secrets, transient task state, or verbatim chat.
If the server is unavailable, say so.
