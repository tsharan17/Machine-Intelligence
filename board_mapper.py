import json

def load_board(board_name):
    with open(f"boards/{board_name}.json") as f:
        return json.load(f)
