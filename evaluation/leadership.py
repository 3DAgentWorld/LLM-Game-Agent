import copy
import json
import re
from typing import Dict

import openai

from src.apis.chatgpt_api import chatgpt
from src.games.avalon.extract_demos import vote_extractor_demos, bool_extract_prompt

openai.api_key = ""
# openai.proxy = "http://127.0.0.1:4780"


def leadership(conversations: Dict[str, dict], side):
    a = {}
    for round, convs in conversations.items():
        for idx, c in enumerate(convs):
            if c.get("Host", "").startswith("Please finally confirm"):
                c_keys = list(c.keys())
                leader_role = None
                leader_name = None
                for k in c_keys:
                    if k.startswith("player") or k[0].isdigit():
                        match = re.search("(?<=\().*?(?=\))", k)
                        leader_role = match.group() if match else None
                        match = re.search("\d+", k)
                        leader_name = match.group() if match else None
                if side == "good" and leader_role not in ['Merlin', 'Percival', 'Loyal Servant']:
                    continue
                if side == "evil" and leader_role in ['Merlin', 'Percival', 'Loyal Servant']:
                    continue
                votes = convs[idx + 1:idx + 7]
                all_votes = []
                servant_players = []
                for vo in votes:
                    c_keys = vo.keys()
                    for k in c_keys:
                        if k.startswith("player") or k[0].isdigit():
                            match = re.search("(?<=\().*?(?=\))", k)
                            role = match.group() if match else None
                            match = re.search("\d+", k)
                            player_num = match.group() if match else None
                            if role == "Loyal Servant":
                                servant_players.append(player_num)
                servant_players = sorted(servant_players)
                servant_mapping = {f"player {player}": f"Loyal Servant{r_idx + 1}" for r_idx, player in
                                   enumerate(servant_players)}
                for vo in votes:
                    c_keys = vo.keys()
                    for k in c_keys:
                        if k.startswith("player") or k[0].isdigit():
                            match = re.search("(?<=\().*?(?=\))", k)
                            role = match.group() if match else None
                            match = re.search("\d+", k)
                            player_num = match.group() if match else None
                    ques = vo.get('Host')
                    ans = vo.get(f"player {player_num}({role})")
                    messages = vote_extractor_demos + [{"role": "user", "content": bool_extract_prompt.format(
                        f"Question:{ques}\nAnswer:{ans}"
                    )}]
                    output = chatgpt(model="gpt-3.5-turbo-16k", messages=messages, temperature=0)
                    print(f"a: {ans}")
                    print(f"p: {output}")
                    print("-----------------------")
                    if "true" in output.lower():
                        all_votes.append(True)
                    else:
                        all_votes.append(False)
                role = servant_mapping.get(f"player {leader_name}")
                if role is None:
                    role = leader_role
                if role in a:
                    a[role].append(all_votes.count(True) / len(all_votes))
                else:
                    a[role] = [all_votes.count(True) / len(all_votes)]

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
a = {}
for x, file in enumerate(files):
    print(x)
    conversations = read_json(file)
    count = leadership(conversations, "evil")
    for k, v in count.items():
        if k in a:
            a[k].extend(v)
        else:
            a[k] = copy.deepcopy(v)
for k, v in a.items():
    print(k, sum(v) / len(v))

# Ours
# Assassin 0.3611111111111111
# Morgana 0.5166666666666667
# Percival 0.85
# Loyal Servant1 0.8717948717948718
# Merlin 0.8833333333333332
# Loyal Servant2 0.7619047619047619
# [87.17948717948718, 76.19047619047619, 88.33333333333332, 85, 51.66666666666667, 36.11111111111111]

# Baseline
# Loyal Servant1 0.6333333333333333
# Percival 0.6538461538461539
# Loyal Servant2 0.6025641025641026
# Merlin 0.6458333333333334
# Morgana 0.8
# Assassin 0.8974358974358974
# [63.33333333333333, 60.25641025641026, 64.58333333333334, 65.38461538461539, 80, 89.74358974358974]
