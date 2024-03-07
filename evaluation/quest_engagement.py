import copy
import json
import re
from typing import Dict


def QER(conversations: Dict[str, dict]):
    servant_players = []
    convs = conversations.get("round 1 starts:", [])
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
    servant_mapping = {f"player {player}": f"Loyal Servant{r_idx + 1}" for r_idx, player in
                       enumerate(servant_players)}

    total = len(conversations)
    player_role_mapping = {}
    count = {}
    for turn, convs in conversations.items():
        numbers = []
        for c in convs:
            c_keys = list(c.keys())
            p = None
            for k in c_keys:
                if k.startswith("player") or k[0].isdigit():
                    match = re.search("(?<=\().*?(?=\))", k)
                    role = match.group() if match else None
                    match = re.search("\d+", k)
                    player_num = match.group() if match else None
                    if role and player_num:
                        player_role_mapping[player_num] = role
        for c in convs:
            q = c.get("Host")
            if q is None:
                continue
            if q.startswith("The quest leader decides that"):
                pattern = "(?<=player )\d+"
                numbers = re.findall(pattern, q)
        for n in numbers:
            if f"player {n}" in count:
                count[f"player {n}"]["count"] += 1
            else:
                role = player_role_mapping[n]
                if role == "Loyal Servant":
                    role = servant_mapping[f"player {n}"]
                count[f"player {n}"] = {
                    "name": f"player {n}",
                    "role": role,
                    "count": 1,
                    "total": total
                }

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
all_roles = ["Merlin", "Percival", "Loyal Servant1", "Loyal Servant2", "Morgana", "Assassin"]
for file in files:
    conversations = read_json(file)
    count = QER(conversations)
    all_role_temp = copy.deepcopy(all_roles)
    for k, v in count.items():
        role = v.get("role")
        all_role_temp.remove(role)
        count = v.get("count")
        total = v.get("total")
        if role not in a:
            a[role] = {"count": count, "total": total}
        else:
            a[role]["count"] += count
            a[role]["total"] += total
    for role in all_role_temp:
        if role not in a:
            a[role] = {"count": 0, "total": total}
        else:
            a[role]["total"] += total
for k, v in a.items():
    print(f"{k}: {v.get('count')}/{v.get('total')} {v.get('count') / v.get('total')}")
