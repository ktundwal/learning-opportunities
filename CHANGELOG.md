# Changelog

## learning-opportunities 1.0.1

**Fixed:** Discovery loop in `Orientation mode` now also checks `.github/copilot-orientation.md` (the GitHub Copilot CLI project-level path written by orient v1.1.0). Without this, orient and the consumer skill could silently miss each other under Copilot CLI — orient would write the file, the consumer would tell the user to invoke orient. The new path is checked first, so Copilot CLI users get the orient-generated orientation file without falling through to the legacy Codex/Claude paths.

## orient 1.1.0

Quality-of-life improvements to make `orient` work first-class on Windows and on C#/.NET repos, and to amplify (not duplicate) any onboarding investment a repo already has.

**New:**
- **GitHub Copilot CLI write path** — when running under Copilot CLI, `orientation.md` is written to `.github/copilot-orientation.md` (conventional repo-level location, alongside the existing `.codex/` and `.claude/` paths).
- **Step 2.5: Inherit from existing onboarding docs** — before re-deriving anything, orient now reads `.github/copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `CONTRIBUTING.md`, and `docs/` indexes. These become the primary source of truth; Step 3 becomes a sanity check and gap-fill.
- **Prerequisites & secrets** section added to the orientation template — captures required env vars, SDK pins, cloud auth, local services, and platform-specific notes that aren't covered by the package manifest.

**Improved:**
- **C#/.NET detection** — Step 2 signal list now includes `*.slnx` (SLN-XML), `Directory.Packages.props`, and `global.json`. Step 3c gets a new C#/.NET entry-point row covering `Program.cs` (top-level statements or `Main`), ASP.NET Core `WebApplication.CreateBuilder`/`IHostBuilder`, multi-project solution discovery, and SDK/package-pin signals. Also adds Java/Kotlin `main` and Spring Boot entry-point guidance.
- **PowerShell variants** — Step 3b directory walk and Step 3f git-churn analysis now ship both bash and pwsh versions, so Windows users get accurate output without WSL.
- **Expanded directory-tree ignore list** — Step 3b now also excludes `bin/`, `obj/`, `out/`, `dist/`, `target/`, `packages/`, `.vs/`, `TestResults/` so .NET, Java, and Rust repos don't drown the architectural view in build output.

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
