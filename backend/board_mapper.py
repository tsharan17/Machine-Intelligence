import json
from pathlib import Path

BOARDS_DIR = Path(__file__).parent / "pin_profiles"

BOARD_ALIASES = {
    "esp32":        "esp32",
    "esp32dev":     "esp32",
    "arduino":      "arduino_uno",
    "arduino_uno":  "arduino_uno",
    "uno":          "arduino_uno",
}


def load_board(board_name: str) -> dict:
    """
    Load a board pin profile from pin_profiles/<board_name>.json.
    Supports name aliases.

    Returns the parsed board profile dict.
    Raises FileNotFoundError if profile does not exist.
    """

    normalized = BOARD_ALIASES.get(board_name.lower(), board_name.lower())
    path = BOARDS_DIR / f"{normalized}.json"

    if not path.exists():
        available = [p.stem for p in BOARDS_DIR.glob("*.json")]
        raise FileNotFoundError(
            f"[BOARD MAPPER] Board '{board_name}' not found. "
            f"Available profiles: {available}"
        )

    with open(path, "r") as f:
        return json.load(f)