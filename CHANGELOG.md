# Changelog

## learning-opportunities-auto 2.0.0

**New: GitHub Copilot CLI support** (alongside Claude Code and Codex).

Copilot CLI's `postToolUse` event does not process hook output the way Claude Code does, so a direct port of the v1 single-hook design isn't possible. v2 replaces it with a **two-hook handshake** that maps cleanly onto Copilot's native event model:

- **`PostToolUse`** — reads the tool payload, detects `git commit` calls in either `bash` or `powershell` tool invocations, and writes a per-session marker file under TMPDIR
- **`Stop`** and **`SubagentStop`** — read the marker and, if present, emit `{"decision":"block","reason":"<nudge>"}`. Copilot honors the block by forcing one extra agent turn whose prompt is the nudge, which the agent then surfaces to the user as a one-line learning-exercise question
- Marker is deleted **before** the block JSON is emitted, so the synthetic turn's own `Stop` event cannot loop
- Per-session offer limit of 2 (matches the Claude/Codex behavior)
- Marker namespace `lo_auto_copilot_*` is distinct from the Claude/Codex `lo_auto_*` namespace, so the three plugins coexist cleanly

The Copilot hooks are inlined directly in `hooks.copilot.json` for both bash and PowerShell, so no path-resolution env var is required and the plugin works out-of-the-box on macOS, Linux, and Windows.

**Other changes:**
- `plugin.json` at the plugin root for Copilot CLI to discover the manifest
- Marketplace, Claude, and Codex manifest descriptions updated to mention all three platforms
- Original Claude (`hooks/hooks.json`, `hooks/post-tool-use.sh`) and Codex (`hooks.codex.json`) hook files are unchanged — additive only

## learning-opportunities + orient: GitHub Copilot CLI support

**New:**
- `plugin.json` manifest at the root of `learning-opportunities/` and `orient/` so GitHub Copilot CLI (`copilot plugin install ...`) can load them
- README updated with Copilot CLI install instructions
- Existing `.claude-plugin/marketplace.json` is reused — Copilot CLI also reads marketplaces from `.claude-plugin/`, so no separate marketplace file is needed

## orient 1.0.0

Added orient plugin to the learning-opportunities marketplace.

**New:**
- `orient` skill for generating repo-specific orientation files using program comprehension research
- Showboat mode for detailed linear code walkthroughs

## learning-opportunities-auto 1.0.1

**Fixed:**
- Moved hook declaration from inline `plugin.json` format to `hooks/hooks.json`, which is the format Claude Code actually reads at runtime
- Moved `scripts/post-tool-use.sh` to `hooks/post-tool-use.sh` to colocate with hook configuration

## learning-opportunities-auto 1.0.0

Initial release of the automatic hook companion plugin.

**New:**
- `PostToolUse` hook that triggers after `git commit` and nudges Claude to offer a learning exercise when appropriate
- Bash implementation — works on Linux and macOS out of the box; Windows users need to configure `CLAUDE_CODE_GIT_BASH_PATH` (see README)
- Session state tracking: respects the learning-opportunities skill's two-exercise-per-session limit and declined-offer flag

## learning-opportunities 1.0.0

Initial release as a Claude Code plugin.

**New:**
- `learning-opportunities` skill for science-based deliberate practice during AI-assisted coding
- Exercise types: Prediction/Observation/Reflection, Generation/Comparison, Trace the Path, Debug This, Teach It Back, Retrieval Check-in
- Supporting resources: PRINCIPLES.md (learning science foundations), MEASURE-THIS.md (team experiment playbook)
