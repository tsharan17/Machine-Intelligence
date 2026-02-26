import json
from pathlib import Path

BOARDS_DIR = Path("pin_profiles")


def load_board(board_name: str):

    path = BOARDS_DIR / f"{board_name}.json"

    if not path.exists():
        raise FileNotFoundError(f"Board not found: {board_name}")

    with open(path, "r") as f:
        return json.load(f)