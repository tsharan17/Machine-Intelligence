import re


def clean_command(text: str) -> str:
    """
    Normalizes a voice-transcribed command string:
    - Lowercases and strips whitespace
    - Removes filler words (uh, um, please, thank you)
    - Converts word-numbers to digits (five → 5, twice → 2 times)
    - Collapses extra whitespace
    """

    text = text.lower().strip()

    # Remove filler words
    fillers = ["thank you", "please", "uh,", "um,", "uh", "um", "okay,", "okay", "ok,", "ok"]
    for filler in fillers:
        text = text.replace(filler, "")

    # Word → digit replacements (whole words only)
    replacements = {
        r"\bone\b":    "1",
        r"\btwo\b":    "2",
        r"\bthree\b":  "3",
        r"\bfour\b":   "4",
        r"\bfive\b":   "5",
        r"\bsix\b":    "6",
        r"\bseven\b":  "7",
        r"\beight\b":  "8",
        r"\bnine\b":   "9",
        r"\bten\b":    "10",
        r"\bonce\b":   "1 time",
        r"\btwice\b":  "2 times",
        r"\bthrice\b": "3 times",
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text