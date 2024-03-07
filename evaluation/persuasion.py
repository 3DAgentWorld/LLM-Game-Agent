import json
import re
from typing import Dict
import openai

from src.apis.chatgpt_api import chatgpt

openai.api_key = ""
# openai.proxy = "http://127.0.0.1:4780"

prompt = """Please help me determine whether the speaker ({}) is recommending himself as a candidate according to his speaking.

his speaking:{}

Output True if he is.
Output False if he is not.
"""


def persuasion(conversations: Dict[str, dict], side):
    a = {}
    for round, convs in conversations.items():
        servant_players = []
        for vo in convs:
            c_keys = vo.keys()
            for k in c_keys:
                if k.startswith("player") or k[0].isdigit():
                    match = re.search("(?<=\().*?(?=\))", k)
                    role = match.group() if match else None
                    match = re.search("\d+", k)
                    player_num = match.group() if match else None
                    if role == "Loyal Servant":
                        if player_num not in servant_players:
                            servant_players.append(player_num)
        servant_players = sorted(servant_players)
        servant_mapping = {f"player {player}": f"Loyal Servant{r_idx + 1}" for r_idx, player in
                           enumerate(servant_players)}
        for idx, c in enumerate(convs):
            if c.get("Host", "").startswith("Please start discussing the candidates for"):
                c_keys = c.keys()
                for k in c_keys:
                    if k.startswith("player") or k[0].isdigit():
                        match = re.search("(?<=\().*?(?=\))", k)
                        role = match.group() if match else None
                        match = re.search("\d+", k)
                        player_num = match.group() if match else None
                if side == "good" and role not in ['Merlin', 'Percival', 'Loyal Servant']:
                    continue
                if side == "evil" and role in ['Merlin', 'Percival', 'Loyal Servant']:
                    continue

                ques = c.get('Host')
                ans = c.get(f"player {player_num}({role})")
                messages = [{"role": "user", "content": prompt.format(f"player {player_num}", ans)}]
                output = chatgpt(model="gpt-3.5-turbo-16k", messages=messages, temperature=0)
                print(f"a:{ans}")
                print(f"p:{output}")
                print("--------------------------------")
                if "true" in output.lower():
                    recommend = True
                else:
                    recommend = False
                ques = ""
                c_idx = idx + 1
                while c_idx < len(convs):
                    c = convs[c_idx]
                    if c.get("Host", "").startswith("The quest leader decides that"):
                        ques = c.get("Host", "")
                        break
                    else:
                        c_idx += 1
                candidates = re.findall("(?<=player )\d+", ques)
                if player_num in candidates:
                    engagement = True
                else:
                    engagement = False
                c_role = servant_mapping.get(f"player {player_num}")
                if c_role is None:
                    c_role = role
                if c_role in a:
                    if recommend:
                        a[c_role]["total"] += 1
                        a[c_role]["recommend"] += 1
                        a[c_role]["engagement"] += int(engagement)
                    else:
                        a[c_role]["total"] += 1
                else:
                    if recommend:
                        a[c_role] = {"total": 1, "recommend": 1, "engagement": int(engagement)}
                    else:
                        a[c_role] = {"total": 1, "recommend": 0, "engagement": 0}

    return a


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
file_len = len(files)
a = {}
b = {}
for x, file in enumerate(files):
    print(x)
    conversations = read_json(file)
    count = persuasion(conversations, "evil")
    for k, v in count.items():
        if k in a:
            if v.get("total"):
                a[k].append(v.get("recommend", 0) / v.get("total"))
            else:
                a[k].append(0)
        else:
            if v.get("total"):
                a[k] = [v.get("recommend", 0) / v.get("total")]
            else:
                a[k] = [0]

        if k in b:
            if v.get("recommend"):
                b[k].append(v.get("engagement", 0) / v.get("recommend"))
            else:
                b[k].append(0)
        else:
            if v.get("recommend"):
                b[k] = [v.get("engagement", 0) / v.get("recommend")]
            else:
                b[k] = [0]
for k, v in a.items():
    print(k, sum(v) / file_len)

for k, v in b.items():
    print(k, sum(v) / file_len)
