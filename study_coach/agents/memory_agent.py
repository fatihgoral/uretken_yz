import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("progress.json")


def save_progress(level: str):
    data = _load()
    data.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": "progress",
        "level": level
    })
    _save(data)


def _load():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
