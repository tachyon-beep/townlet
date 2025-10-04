#!/usr/bin/env bash
# Run the demo storyline end-to-end and prompt operators to open the observer UI.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.venv/bin/activate"
fi

CONFIG_PATH=${CONFIG_PATH:-"${ROOT_DIR}/configs/scenarios/demo_story_arc.yaml"}
TIMELINE_PATH=${TIMELINE_PATH:-"${ROOT_DIR}/configs/scenarios/timelines/demo_story_arc.yaml"}
TICKS=${TICKS:-150}
NARRATION_LEVEL=${NARRATION_LEVEL:-summary}

echo "[demo] Using config: ${CONFIG_PATH}"
echo "[demo] Using timeline: ${TIMELINE_PATH}"
echo "[demo] Tick budget: ${TICKS}"
echo "[demo] Narration level: ${NARRATION_LEVEL}"
echo "[demo] Tip: launch the observer UI in another terminal with:\n  python -m townlet_ui.dashboard --config ${CONFIG_PATH}"
echo

python "${ROOT_DIR}/scripts/demo_run.py" \
  --scenario demo_story_arc \
  --config "${CONFIG_PATH}" \
  --timeline "${TIMELINE_PATH}" \
  --ticks "${TICKS}" \
  --narration-level "${NARRATION_LEVEL}" \
  "$@"
