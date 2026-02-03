from __future__ import annotations
from pathlib import Path
from datetime import datetime

LOG_PATH = Path("parse_errors.log")

def log_error(message: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOG_PATH.write_text(LOG_PATH.read_text(encoding="utf-8") + f"[{ts}] {message}\n", encoding="utf-8") if LOG_PATH.exists() else LOG_PATH.write_text(f"[{ts}] {message}\n", encoding="utf-8")
