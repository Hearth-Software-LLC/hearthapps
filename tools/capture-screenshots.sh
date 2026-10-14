#!/usr/bin/env bash
#
# Runs each Hearth app's own scripts/screenshots.sh (light and dark) for the screens the website
# shows, and logs everything to tools/screenshots.log. Needs Xcode; takes a few minutes per app
# because each one builds for the Simulator first.
#
#   bash ~/Developer/hearthapps/tools/capture-screenshots.sh
#
set -uo pipefail
DEV="$HOME/Developer"
LOG="$DEV/hearthapps/tools/screenshots.log"
: > "$LOG"

run() {
  app="$1"; shift
  echo "=== $app: $*" | tee -a "$LOG"
  ( cd "$DEV/$app" && bash scripts/screenshots.sh "$@" ) 2>&1 | tee -a "$LOG"
  echo "=== $app finished with status ${PIPESTATUS[0]}" | tee -a "$LOG"
}

run bigtable-ios plan grocery recipe
run suffice overview budget activity
run sated today trends coach
run caloma home chores calendar
run hearken today reader path

echo "ALL DONE" | tee -a "$LOG"
