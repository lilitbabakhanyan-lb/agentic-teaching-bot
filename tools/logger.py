from datetime import datetime


def log(state: dict, message: str):
    state.setdefault("logs", []).append(f"{datetime.now().isoformat(timespec='seconds')} - {message}")
