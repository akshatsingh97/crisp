#!/bin/sh
# Crisp SessionStart hook (Claude Code and Codex).
#
# Settings (Claude Code reads them from the plugin options in /config;
# Codex and other tools read the environment variables):
#   mode:  always | on-demand    CLAUDE_PLUGIN_OPTION_MODE  or CRISP_MODE   (default: always)
#   level: lite | strict | off   CLAUDE_PLUGIN_OPTION_LEVEL or CRISP_LEVEL  (default: lite)
#
# Output: the rule block for the model. In Claude Code, the first session after
# install also shows the user one line that says how to change the mode.

MODE="${CLAUDE_PLUGIN_OPTION_MODE:-${CRISP_MODE:-always}}"
LEVEL="${CLAUDE_PLUGIN_OPTION_LEVEL:-${CRISP_LEVEL:-lite}}"
DIR="$(cd "$(dirname "$0")" && pwd)/context"

[ "$LEVEL" = "off" ] && exit 0

if [ "$MODE" = "on-demand" ]; then
  CONTEXT="$(cat "$DIR/on-demand.md" 2>/dev/null)"
  NOTICE="Crisp is installed in on-demand mode. It changes answers only when you ask. Run /crisp:level lite to turn it on for a session."
elif [ "$LEVEL" = "strict" ]; then
  CONTEXT="$(cat "$DIR/lite.md" "$DIR/strict.md" 2>/dev/null)"
  NOTICE="Crisp is on and applies to every answer. To use it only when you ask, set Crisp mode to on-demand in /config. To turn it off for this session, run /crisp:level off."
else
  CONTEXT="$(cat "$DIR/lite.md" 2>/dev/null)"
  NOTICE="Crisp is on and applies to every answer. To use it only when you ask, set Crisp mode to on-demand in /config. To turn it off for this session, run /crisp:level off."
fi

[ -z "$CONTEXT" ] && exit 0

json_escape() {
  awk 'BEGIN { ORS = "" }
       { gsub(/\\/, "\\\\"); gsub(/"/, "\\\""); gsub(/\t/, "\\t"); gsub(/\r/, "");
         if (NR > 1) printf "\\n"; print }'
}

MARKER=""
if [ -n "$CLAUDE_PLUGIN_DATA" ]; then
  MARKER="$CLAUDE_PLUGIN_DATA/notice-shown-$MODE"
fi

if [ -n "$MARKER" ] && [ ! -f "$MARKER" ] && mkdir -p "$CLAUDE_PLUGIN_DATA" 2>/dev/null && : > "$MARKER" 2>/dev/null; then
  printf '{"systemMessage":"%s","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' \
    "$(printf '%s' "$NOTICE" | json_escape)" \
    "$(printf '%s' "$CONTEXT" | json_escape)"
else
  printf '%s\n' "$CONTEXT"
fi
exit 0
