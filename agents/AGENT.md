## Memory

Long-term memory lives only in the `memory` MCP server. Never persist memory to files.

**Recall**
- At session start, `memory_search` with tags: the project tag (repo/directory name) and `general`.
- Once the kind of work is clear, `memory_search` with that work-type tag for Ray's preferences. Repeat if it changes.

**Store** with `memory_store`, and tell Ray briefly: project decisions (with the why), context not in the code or git, Ray's preferences and corrections.

Tags are recall addresses, not keywords — use only:
- one scope tag: the project name, or `general` if true across projects (e.g. Ray's machines, tools, setup);
- for Ray's preferences that hold across projects, also `preference` + one work type: `coding`, `science`, `writing`, `language`, `travel`.

Ask before storing personal information (home, workplace, health, family, finances). Never store secrets, transient task state, or verbatim chat.
If the server is unavailable, say so.
