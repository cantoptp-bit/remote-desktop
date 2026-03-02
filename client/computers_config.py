"""
Saved computers list: load/save from computers.json in project root.
Format: [{"name": "Office PC", "host": "192.168.1.100", "port": 8765}, ...]
"""
import json
from pathlib import Path

CONFIG_NAME = "computers.json"


def _config_path():
    root = Path(__file__).resolve().parent.parent
    return root / CONFIG_NAME


def load():
    """Return list of {name, host, port}. Port defaults to 8765 if missing."""
    path = _config_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    out = []
    for entry in data:
        if isinstance(entry, dict) and entry.get("host"):
            out.append({
                "name": entry.get("name", entry["host"]),
                "host": str(entry["host"]).strip(),
                "port": int(entry.get("port", 8765)),
            })
    return out


def save(computers):
    """Write list of {name, host, port} to computers.json."""
    path = _config_path()
    path.write_text(json.dumps(computers, indent=2), encoding="utf-8")


def add(name, host, port=8765):
    """Append a computer and save. Returns updated list."""
    host = str(host).strip()
    computers = load()
    computers.append({"name": name, "host": host, "port": int(port)})
    save(computers)
    return computers
