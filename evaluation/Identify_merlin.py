import json
from typing import Dict


def im(conversations: Dict[str, dict]):
    count = 0
    for turn, convs in conversations.items():
        c = convs[-2]
        if c.get("Host").endswith("the identification is successful."):
            count += 1
    return count


def read_json(file):
    with open(file, mode="r", encoding="utf-8") as f:
        json_data = json.load(f)
        f.close()
    return json_data


files = [
    "playing_log/avalon/battle/battle03-blue-strategy-3-style-specific-0_game_0/process.json",
    "playing_log/avalon/battle/battle03-blue-strategy-3-style-specific-0_game_1/process.json",
    "playing_log/avalon/battle/battle03-blue-strategy-3-style-specific-0_game_2/process.json",
    "playing_log/avalon/battle/battle03-blue-strategy-3-style-specific-0_game_3/process.json",
    "playing_log/avalon/battle/battle03-blue-strategy-3-style-specific-0_game_4/process.json",
    "playing_log/avalon/battle/battle03-blue-strategy-3-style-specific-0_game_5/process.json",
    "playing_log/avalon/battle/battle03-blue-strategy-3-style-specific-0_game_6/process.json",
    "playing_log/avalon/battle/battle03-blue-strategy-3-style-specific-0_game_7/process.json",
    "playing_log/avalon/battle/battle03-blue-strategy-3-style-specific-0_game_8/process.json",
    "playing_log/avalon/battle/battle03-blue-strategy-3-style-specific-0_game_9/process.json"
]
files = [
    "playing_log/avalon/battle/battle03-red-strategy-3-style-specific-0_game_0/process.json",
    "playing_log/avalon/battle/battle03-red-strategy-3-style-specific-0_game_1/process.json",
    "playing_log/avalon/battle/battle03-red-strategy-3-style-specific-0_game_2/process.json",
    "playing_log/avalon/battle/battle03-red-strategy-3-style-specific-0_game_3/process.json",
    "playing_log/avalon/battle/battle03-red-strategy-3-style-specific-0_game_4/process.json",
    "playing_log/avalon/battle/battle03-red-strategy-3-style-specific-0_game_5/process.json",
    "playing_log/avalon/battle/battle03-red-strategy-3-style-specific-0_game_6/process.json",
    "playing_log/avalon/battle/battle03-red-strategy-3-style-specific-0_game_7/process.json",
    "playing_log/avalon/battle/battle03-red-strategy-3-style-specific-0_game_8/process.json",
    "playing_log/avalon/battle/battle03-red-strategy-3-style-specific-0_game_9/process.json"
]
a = 0
for file in files:
    conversations = read_json(file)
    count = im(conversations)
    a += count
print(a)
