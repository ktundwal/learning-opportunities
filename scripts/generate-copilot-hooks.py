#!/usr/bin/env python3
"""
Generator for learning-opportunities-auto/hooks.copilot.json

We want a single JSON file with inlined bash and PowerShell scripts.
Writing the JSON by hand is error-prone (lots of \" and \n escapes),
so we keep the scripts as clean multi-line strings here and let
json.dumps handle the encoding.

Run this from the repo root after editing any of the scripts below:
    python ./scripts/generate-copilot-hooks.py

Output: learning-opportunities-auto/hooks.copilot.json
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = REPO_ROOT / "learning-opportunities-auto" / "hooks.copilot.json"

# -----------------------------------------------------------------------------
# Nudge message emitted to the agent when a commit is detected and the
# per-session offer count is below the limit. The agent receives this as
# the prompt for one extra synthetic turn (forced by decision:"block"),
# and is expected to surface a single short question to the user.
# Keep this text in sync with hooks/post-tool-use.sh (Claude/Codex version).
# -----------------------------------------------------------------------------
NUDGE = (
    "[learning-opportunities-auto] The user just committed code. Per the "
    "learning-opportunities skill, consider whether this is a good moment "
    "to offer a learning exercise. If the committed work involved new "
    "files, schema changes, architectural decisions, refactors, or "
    "unfamiliar patterns, ask the user (one short sentence) if they would "
    "like a 10-15 minute exercise. Do not start the exercise until they "
    "confirm. If they decline, note it - no more offers this session."
)

# -----------------------------------------------------------------------------
# DETECTOR (PostToolUse) -- bash
#
# Reads the PostToolUse payload from stdin (PascalCase event => snake_case
# fields). If the payload represents a bash or powershell tool call whose
# command contained "git ... commit", touches a per-session marker file
# under TMPDIR. The marker is consumed later by the Stop/SubagentStop hook.
#
# The command-match pattern uses `.*` (matching the original Claude script
# at hooks/post-tool-use.sh) so we correctly handle JSON-escaped quotes
# (e.g. `cd "repo with spaces" && git commit ...`). False positives are
# bounded by the tool_name filter above and the 2-offers-per-session cap
# enforced in the nudger.
# -----------------------------------------------------------------------------
DETECTOR_BASH = r"""set -uo pipefail
INPUT=$(cat)
echo "$INPUT" | grep -Eq '"tool_name":"(bash|powershell)"' || exit 0
echo "$INPUT" | grep -Eq '"command":".*git.*commit' || exit 0
SID=$(echo "$INPUT" | grep -o '"session_id":"[^"]*"' | head -1 | cut -d'"' -f4)
[ -z "$SID" ] && exit 0
SAFE="${SID//[^a-zA-Z0-9_-]/_}"
touch "${TMPDIR:-/tmp}/lo_auto_copilot_${SAFE}.commit"
exit 0
"""

# -----------------------------------------------------------------------------
# DETECTOR (PostToolUse) -- PowerShell
#
# Same logic as the bash version, for Windows. Uses $env:TEMP for the
# marker directory. Pattern uses `.*` to match through JSON-escaped quotes,
# matching the bash detector's behavior.
# -----------------------------------------------------------------------------
DETECTOR_PS = r"""$ErrorActionPreference = 'Stop'
$in = [Console]::In.ReadToEnd()
if ($in -notmatch '"tool_name"\s*:\s*"(bash|powershell)"') { exit 0 }
if ($in -notmatch '"command"\s*:\s*".*git.*commit') { exit 0 }
$m = [regex]::Match($in, '"session_id"\s*:\s*"([^"]+)"')
if (-not $m.Success) { exit 0 }
$sid = $m.Groups[1].Value -replace '[^a-zA-Z0-9_-]', '_'
$tmp = if ($env:TEMP) { $env:TEMP } else { '/tmp' }
$null = New-Item -ItemType File -Path (Join-Path $tmp ("lo_auto_copilot_$sid.commit")) -Force
exit 0
"""

# -----------------------------------------------------------------------------
# NUDGER (Stop / SubagentStop) -- bash
#
# Reads the Stop or SubagentStop payload from stdin. Extracts session_id,
# then checks for the marker that the detector hook would have written if
# a git commit happened during this turn.
#
# IMPORTANT: marker is deleted BEFORE writing the block JSON, so the
# synthetic turn forced by decision:"block" does not loop -- its own Stop
# event will find no marker and exit silently.
# -----------------------------------------------------------------------------
NUDGER_BASH_TEMPLATE = r"""set -uo pipefail
INPUT=$(cat)
SID=$(echo "$INPUT" | grep -o '"session_id":"[^"]*"' | head -1 | cut -d'"' -f4)
[ -z "$SID" ] && exit 0
SAFE="${SID//[^a-zA-Z0-9_-]/_}"
T="${TMPDIR:-/tmp}"
M="$T/lo_auto_copilot_${SAFE}.commit"
C="$T/lo_auto_copilot_${SAFE}.offers"
[ ! -f "$M" ] && exit 0
n=0
[ -f "$C" ] && n=$(cat "$C" 2>/dev/null || echo 0)
if [ "$n" -ge 2 ]; then rm -f "$M"; exit 0; fi
echo $((n+1)) > "$C"
rm -f "$M"
printf '%s' '__BLOCK_JSON__'
exit 0
"""

# -----------------------------------------------------------------------------
# NUDGER (Stop / SubagentStop) -- PowerShell
# -----------------------------------------------------------------------------
NUDGER_PS_TEMPLATE = r"""$ErrorActionPreference = 'Stop'
$in = [Console]::In.ReadToEnd()
$m = [regex]::Match($in, '"session_id"\s*:\s*"([^"]+)"')
if (-not $m.Success) { exit 0 }
$sid = $m.Groups[1].Value -replace '[^a-zA-Z0-9_-]', '_'
$tmp = if ($env:TEMP) { $env:TEMP } else { '/tmp' }
$marker  = Join-Path $tmp ("lo_auto_copilot_$sid.commit")
$counter = Join-Path $tmp ("lo_auto_copilot_$sid.offers")
if (-not (Test-Path $marker)) { exit 0 }
$n = 0
if (Test-Path $counter) {
    try { $n = [int](Get-Content -Raw $counter) } catch { $n = 0 }
}
if ($n -ge 2) { Remove-Item -Force $marker -ErrorAction SilentlyContinue; exit 0 }
Set-Content -Path $counter -Value (($n + 1).ToString()) -NoNewline
Remove-Item -Force $marker -ErrorAction SilentlyContinue
[Console]::Out.Write('__BLOCK_JSON__')
exit 0
"""

def main() -> None:
    block_payload = json.dumps({"decision": "block", "reason": NUDGE}, separators=(",", ":"))
    assert "'" not in block_payload, "block payload must not contain single quotes"
    nudger_bash = NUDGER_BASH_TEMPLATE.replace("__BLOCK_JSON__", block_payload)
    nudger_ps   = NUDGER_PS_TEMPLATE.replace("__BLOCK_JSON__", block_payload)

    detector_entry = {
        "type": "command",
        "bash": DETECTOR_BASH,
        "powershell": DETECTOR_PS,
        "timeoutSec": 5,
    }
    nudger_entry = {
        "type": "command",
        "bash": nudger_bash,
        "powershell": nudger_ps,
        "timeoutSec": 5,
    }

    hooks_config = {
        "version": 1,
        "hooks": {
            "PostToolUse": [detector_entry],
            "Stop":         [nudger_entry],
            "SubagentStop": [nudger_entry],
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(hooks_config, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
