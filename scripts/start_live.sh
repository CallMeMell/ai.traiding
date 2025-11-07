#!/usr/bin/env bash
# start_live.sh - improved: checks venv, env, deps and chooses free Streamlit port automatically
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# 1) Ensure env/venv and python
python3 -m pip --version >/dev/null 2>&1 || python -m pip --version >/dev/null 2>&1 || {
  echo "[ERROR] pip not found. Run scripts/env-check.py for diagnostics."
  python3 scripts/env-check.py || true
  exit 1
}

# 2) Run env-check (non-fatal, but informative)
python3 scripts/env-check.py || true

# 3) Verify deps; if --auto-install is passed, forward it
AUTO_INSTALL=${1:-""}
if [ "$AUTO_INSTALL" = "--auto-install" ]; then
  python3 scripts/verify-deps.py --install || { echo "[ERROR] verify-deps failed"; exit 1; }
else
  python3 scripts/verify-deps.py || echo "[INFO] Some packages are missing. Run: python3 scripts/verify-deps.py --install"
fi

# 4) Find free port starting at 8501
START_PORT=8501
MAX_PORT=8510
FREE_PORT=""
for ((p=START_PORT; p<=MAX_PORT; p++)); do
  python3 - <<PY >/dev/null 2>&1 || true
import socket, sys
s = socket.socket()
try:
    s.bind(('127.0.0.1',$p))
    s.close()
    print("FREE")
except Exception:
    sys.exit(1)
PY
  if [ $? -eq 0 ]; then
    FREE_PORT=$p
    break
  fi
done

if [ -z "$FREE_PORT" ]; then
  echo "[ERROR] No free port found in range $START_PORT..$MAX_PORT"
  exit 1
fi

echo "[INFO] Using Streamlit port: $FREE_PORT"
# 5) Activate venv if present
if [ -d "venv" ]; then
  echo "[INFO] Activating venv"
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

# 6) Start runner (dry-run by default) and dashboard in background
# Start automation runner in background (dry-run)
python3 -u automation/runner.py &

# Start Streamlit dashboard
streamlit run tools/view_session_app.py --server.port "$FREE_PORT" &
sleep 0.5
echo "[INFO] View Session should be available at http://localhost:$FREE_PORT"
wait
