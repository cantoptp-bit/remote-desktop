# Remote Desktop (custom app)

A simple remote desktop application: **host** runs on the PC you want to control, **client** runs on your MacBook (or another PC). Same-LAN TCP + JPEG streaming and mouse/keyboard forwarding.

## Setup

- **Python 3.9+** on both machines.
- Install dependencies (from the `remote-desktop` folder):

  ```bash
  pip install -r requirements.txt
  ```

### Run on Mac (all commands)

From your Mac terminal, run these in order (use a **virtual environment** so you don’t need admin):

```bash
cd /Users/michael/test/remote-desktop
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then:

- **To control another PC:** start the **client** (replace with the other PC’s IP):
  ```bash
  python -m client.main 192.168.1.100
  ```
- **To let another PC control this Mac:** start the **host**:
  ```bash
  python -m host.main
  ```

Grant **Screen Recording** and **Accessibility** (Input Monitoring) when macOS asks. Press **q** or **Escape** in the client window to quit.

## Usage

### 1. On the PC you want to control (Windows or Mac)

Run the **host** (listens on port 8765 by default):

```bash
cd remote-desktop
python -m host.main
```

Optional: custom port:

```bash
python -m host.main 9000
```

Note the machine’s IP (e.g. `192.168.1.100`).

### 2. On your MacBook (controller)

Run the **client** and connect to the host’s IP:

```bash
cd remote-desktop
python -m client.main 192.168.1.100
```

With a custom port:

```bash
python -m client.main 192.168.1.100 9000
```

- The remote screen appears in a window. Use mouse and keyboard in that window to control the host.
- Press **q** or **Escape** in the client window to quit.

### 3. Saved computers (no need to type the IP each time)

Add computers to a list, then pick one when you run the client:

```bash
# Add a computer (name + IP, optional port)
python -m client.main add "Office PC" 192.168.1.100
python -m client.main add "Living Room" 192.168.1.101 8765

# List saved computers
python -m client.main list

# Run client with no args: choose from the list
python -m client.main
```

The list is stored in `computers.json` in the project folder. You can still connect by IP: `python -m client.main 192.168.1.100`.

## Project layout

```
remote-desktop/
├── README.md
├── requirements.txt
├── shared/
│   └── protocol.py       # Message framing (frame vs input)
├── host/
│   ├── main.py           # TCP server, capture + input loops
│   ├── capture.py        # mss screen capture, JPEG encode
│   └── input_injector.py # Receive events, pyautogui inject
└── client/
    ├── main.py           # TCP client, display + input
    ├── display.py        # Receive JPEG, show in OpenCV
    └── input_sender.py   # Mouse/keyboard → send to host
```

## Requirements

- **Same LAN** (no discovery or relay; use the host’s local IP).
- **Host**: grant screen capture and accessibility/input permissions when prompted (macOS/Windows).
- **Client**: focus the OpenCV window so key presses are sent to the host.

## Running tests

With dependencies installed (e.g. in the project venv):

```bash
cd remote-desktop
source .venv/bin/activate
python -m unittest discover -s tests -v
```

Without cv2/pyautogui (e.g. system Python), protocol and integration tests still run; display and input-injector tests are skipped.

## Bidirectional control

To control your Mac from the Windows PC: run the **host** on the Mac and the **client** on the Windows PC, then connect to the Mac’s IP from the Windows client.
