# Changelog

## learning-opportunities + orient: GitHub Copilot CLI support

**New:**
- `plugin.json` manifest at the root of `learning-opportunities/` and `orient/` so GitHub Copilot CLI (`copilot plugin install ...`) can load them
- README updated with Copilot CLI install instructions
- Existing `.claude-plugin/marketplace.json` is reused — Copilot CLI also reads marketplaces from `.claude-plugin/`, so no separate marketplace file is needed

**Not yet ported:**
- `learning-opportunities-auto` — Copilot CLI's `postToolUse` event does not process hook output, so `additionalContext` injection (the mechanism the auto plugin relies on) is not directly available. A Copilot-native port would likely use the `notification` event instead and is tracked as a follow-up.

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
