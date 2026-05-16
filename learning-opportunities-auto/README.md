# learning-opportunities-auto

A companion plugin for [learning-opportunities](../learning-opportunities/) that automatically detects good moments to offer learning exercises. Instead of relying on the agent to notice opportunities on its own, this plugin uses post-commit hooks to nudge the agent to make the offer.

**Requires:** The `learning-opportunities` plugin must also be installed.

**Works with:** Claude Code, Codex, and GitHub Copilot CLI.

## How It Works

The hook fires after every shell tool use and checks whether the command was a `git commit`. After a successful commit, it nudges the agent to consider whether the work that was just committed is a good fit for a learning exercise — the `learning-opportunities` skill handles deciding what kind of exercise to offer based on the nature of the changes.

It respects the same session limits as the skill: no more than 2 offers per session, and it stops if the user declines.

### Copilot CLI design

Copilot CLI's `PostToolUse` event does not process hook stdout, so the plugin uses a **two-hook handshake**:

1. **`PostToolUse`** detects the `git commit` (matching both `bash` and `powershell` tool invocations) and writes a per-session marker file under TMPDIR
2. **`Stop`** / **`SubagentStop`** read the marker and, if present, emit `{"decision":"block","reason":"<nudge>"}`. Copilot honors the block by forcing one synthetic agent turn whose prompt is the nudge text, which the agent surfaces to the user as a one-line question.

The marker is deleted **before** the block JSON is written, so the synthetic turn's own `Stop` event finds no marker and exits silently — no loop is possible.

The hook scripts are inlined directly in `hooks.copilot.json` for both bash and PowerShell, so no env-var path resolution is needed and the plugin works on macOS, Linux, and Windows without extra setup.

## Installation

1. Make sure you've already installed `learning-opportunities` from this marketplace.

2. Install this plugin:

   **Claude Code:**
   ```
   /plugin install learning-opportunities-auto@learning-opportunities
   /plugin reload
   ```

   **Codex:**
   ```
   codex plugin install learning-opportunities-auto@learning-opportunities
   ```

   **GitHub Copilot CLI:**
   ```
   copilot plugin install learning-opportunities-auto@learning-opportunities
   ```

## Windows Setup (Claude Code)

On native Windows, Claude Code runs hooks using `cmd.exe` by default, which cannot execute bash scripts. Set the `CLAUDE_CODE_GIT_BASH_PATH` environment variable to point at your Git for Windows bash installation:

```
CLAUDE_CODE_GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe
```

You can set this as a system environment variable, or add it to your shell profile before launching Claude Code.

This is a [known friction point](https://github.com/anthropics/claude-code/issues/16602) in Claude Code's Windows hook support. GitHub Copilot CLI and Codex do not require this — Copilot ships native PowerShell execution and uses the inlined PowerShell variant of the hook on Windows automatically.

## Hook files at a glance

| Platform | Manifest read by client | Hook config |
|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` | `hooks/hooks.json` → `hooks/post-tool-use.sh` |
| Codex | `.codex-plugin/plugin.json` | `hooks.codex.json` → `hooks/post-tool-use.sh` |
| GitHub Copilot CLI | `plugin.json` (root) | `hooks.copilot.json` (inlined bash + PowerShell) |

The Copilot hook config is generated from `scripts/generate-copilot-hooks.py` at the repo root — edit the cleartext scripts in that file and re-run to update `hooks.copilot.json`.

## License

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
