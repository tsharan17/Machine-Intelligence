def clean_command(text: str) -> str:
    text = text.lower().strip()

    fillers = ["thank you", "please", "uh", "um"]
    for f in fillers:
        text = text.replace(f, "")

    replacements = {
        "five": "5",
        "ten": "10",
        "twice": "2 times",
        "thrice": "3 times"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text.strip()
