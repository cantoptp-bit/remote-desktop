#!/usr/bin/env bash
# Run the remote desktop client on Mac. Usage: ./run-client.sh [host_ip] [port]
# Example: ./run-client.sh 192.168.1.100
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
HOST="${1:-192.168.1.100}"
PORT="${2:-8765}"
echo "Connecting to $HOST:$PORT (edit this script or pass: ./run-client.sh <ip> [port])"
exec python -m client.main "$HOST" "$PORT"
