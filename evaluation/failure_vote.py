import json
from typing import Dict
import re

from src.apis.chatgpt_api import chatgpt
from src.games.avalon.extract_demos import bool_demos, bool_extract_prompt
import openai

openai.api_key = ""
# openai.proxy = "http://127.0.0.1:4780"


def FVR(conversations: Dict[str, dict]):
    count = {}
    for turn, convs in conversations.items():
        for c in convs:
            q = c.get("Host")
            if q is None:
                continue
            if q.startswith("As the players who engage"):
                c_keys = list(c.keys())
                role = None
                player_num = None
                for k in c_keys:
                    if k.startswith("player") or k[0].isdigit():
                        match = re.search("(?<=\().*?(?=\))", k)
                        role = match.group() if match else None
                        match = re.search("\d+", k)
                        player_num = match.group() if match else None
                if role in ["Morgana", "Assassin"]:
                    ques = c.get('Host')
                    ans = c.get(f"player {player_num}({role})")
                    messages = bool_demos + [{"role": "user", "content": bool_extract_prompt.format(
                        f"Question:{ques}\nAnswer:{ans}"
                    )}]
                    output = chatgpt(model="gpt-3.5-turbo-16k", messages=messages, temperature=0)
                    if "true" in output.lower():
                        if role in count:
                            count[role]['total'] += 1
                        else:
                            count[role] = {'total': 1, 'fail': 0}
                    else:
                        if role in count:
                            count[role]['total'] += 1
                            count[role]['fail'] += 1
                        else:
                            count[role] = {'total': 1, 'fail': 1}
                    print(f"answer: {ans}")
                    print(f"prediction: {output}")
                    print("--------------------------------")
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
a = {}
for file in files:
    conversations = read_json(file)
    count = FVR(conversations)
    for k, v in count.items():
        if k in a:
            a[k]["fail"] += v.get('fail')
            a[k]["total"] += v.get('total')
        else:
            a[k] = {"fail": v.get('fail'), 'total': v.get('total')}
for k, v in a.items():
    print(k, v.get('fail')/v.get('total'))

# ours
# Morgana
# [100, 100, 100, 100]
# Assassin
# [100, 78.57142857142857, 65, 68]

# baseline
# Morgana
# [50, 40, 47.058823529411764, 53.84615384615384]
# Assassin
# [11.11111111111111, 17.647058823529413,16.666666666666666, 19.35483870967742]