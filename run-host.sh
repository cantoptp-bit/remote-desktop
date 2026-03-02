#!/usr/bin/env bash
# Run the remote desktop host on this Mac (so another PC can control it).
set -e
cd "$(dirname "$0")"
if [[ ! -d .venv ]]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate
if ! python -c "import mss, cv2, pyautogui" 2>/dev/null; then
  echo "Installing dependencies..."
  pip install -r requirements.txt
fi
PORT="${1:-8765}"
echo "Host listening on port $PORT. Connect from client with: python -m client.main <this_mac_ip> $PORT"
exec python -m host.main "$PORT"
