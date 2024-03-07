import copy
import json
import re
from typing import Dict

import openai

from src.apis.chatgpt_api import chatgpt

openai.api_key = ""
# openai.proxy = "http://127.0.0.1:4780"

prompt_percival = """Please assist me in determining whether {player1} has shared something from his statements.

{player1}'s statements: {statements}

If he mentions any of the following information, we consider it as sharing:
- {player2} is/may be Merlin.
- {player3} is/may be Merlin.
- {player2} is/may be Morgana.
- {player3} is/may be Morgana.

Otherwise, we consider he hasn't shared anything.

Output True if he shared something, otherwise output False.
You are only allowed output True or False without explanation.
"""
prompt_merlin = """Please assist me in determining whether {player1} has shared something from his statements.

{player1}'s statements: {statements}

If he mentions any of the following information, we consider it as sharing:
- {player2} is/may be Assassin.
- {player3} is/may be Assassin.
- {player2} is/may be Morgana.
- {player3} is/may be Morgana.

Otherwise, we consider he hasn't shared anything.

Output True if he shared something, otherwise output False.
You are only allowed output True or False without explanation.
"""


def share(conversations: Dict[str, dict], target_role: str):
    if 'merlin' in target_role.lower():
        a = share_merlin(conversations, target_role)
    elif 'percival' == target_role.lower():
        a = share_percival(conversations, target_role)
    else:
        raise NotImplementedError()

    return a


def share_merlin(conversations: Dict[str, dict], target_role: str):
    a = {target_role: {}}
    convs = conversations.get("round 1 starts:", [])
    servant_players = []
    player_role_mapping = {}
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
    for vo in convs:
        c_keys = vo.keys()
        for k in c_keys:
            if k.startswith("player") or k[0].isdigit():
                match = re.search("(?<=\().*?(?=\))", k)
                role = match.group() if match else None
                match = re.search("\d+", k)
                player_num = match.group() if match else None
                c_role = servant_mapping.get(f"player {player_num}")
                if c_role is None:
                    c_role = role
                player_role_mapping[f"player {player_num}"] = c_role

    role_player_mapping = {v: k for k, v in player_role_mapping.items()}
    for round, convs in conversations.items():
        match = re.search('\d+', round)
        round_i = match.group()
        for c in convs:
            if c.get("Host", "").startswith("Please start discussing the candidates for"):
                c_keys = list(c.keys())
                role = None
                player_num = None
                for k in c_keys:
                    if k.startswith("player") or k[0].isdigit():
                        match = re.search("(?<=\().*?(?=\))", k)
                        role = match.group() if match else None
                        match = re.search("\d+", k)
                        player_num = match.group() if match else None
                ans = c.get(f"player {player_num}({role})")
                if role == 'Loyal Servant':
                    role = servant_mapping[f"player {player_num}"]
                if role != target_role:
                    continue
                roles = copy.deepcopy(['Merlin', 'Morgana', 'Percival', 'Assassin'])
                players = [role_player_mapping[c_role] for c_role in roles]
                # players = copy.deepcopy(["player 1", "player 2", "player 3", "player 4", "player 5", "player 6"])
                # players.remove(f"player {player_num}")
                messages = [{"role": "user", "content": prompt_percival.format(player1=f"player {player_num}",
                                                                               player2=players[0], player3=players[1],
                                                                               statements=ans)}]
                output = chatgpt(model="gpt-3.5-turbo-16k", messages=messages, temperature=0)
                print(f"a: {ans}")
                print(f"p: {output}")
                print("----------------------")
                if 'true' in output.lower():
                    flag = True
                else:
                    flag = False
                if round_i in a[role]:
                    a[role][round_i].append(flag)
                else:
                    a[role][round_i] = [flag]

    return a


def share_percival(conversations: Dict[str, dict], target_role: str):
    a = {target_role: {}}
    convs = conversations.get("round 1 starts:", [])
    servant_players = []
    player_role_mapping = {}
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
    for vo in convs:
        c_keys = vo.keys()
        for k in c_keys:
            if k.startswith("player") or k[0].isdigit():
                match = re.search("(?<=\().*?(?=\))", k)
                role = match.group() if match else None
                match = re.search("\d+", k)
                player_num = match.group() if match else None
                c_role = servant_mapping.get(f"player {player_num}")
                if c_role is None:
                    c_role = role
                player_role_mapping[f"player {player_num}"] = c_role

    role_player_mapping = {v: k for k, v in player_role_mapping.items()}
    for round, convs in conversations.items():
        match = re.search('\d+', round)
        round_i = match.group()
        for c in convs:
            if c.get("Host", "").startswith("Please start discussing the candidates for"):
                c_keys = list(c.keys())
                role = None
                player_num = None
                for k in c_keys:
                    if k.startswith("player") or k[0].isdigit():
                        match = re.search("(?<=\().*?(?=\))", k)
                        role = match.group() if match else None
                        match = re.search("\d+", k)
                        player_num = match.group() if match else None
                ans = c.get(f"player {player_num}({role})")
                if role == 'Loyal Servant':
                    role = servant_mapping[f"player {player_num}"]
                if role != target_role:
                    continue
                roles = copy.deepcopy(['Merlin', 'Morgana'])
                players = [role_player_mapping[c_role] for c_role in roles]
                # players = copy.deepcopy(["player 1", "player 2", "player 3", "player 4", "player 5", "player 6"])
                # players.remove(f"player {player_num}")
                messages = [{"role": "user", "content": prompt_percival.format(player1=f"player {player_num}",
                                                                               player2=players[0], player3=players[1],
                                                                               statements=ans)}]
                output = chatgpt(model="gpt-3.5-turbo-16k", messages=messages, temperature=0)
                print(f"a: {ans}")
                print(f"p: {output}")
                print("----------------------")
                if 'true' in output.lower():
                    flag = True
                else:
                    flag = False
                if round_i in a[role]:
                    a[role][round_i].append(flag)
                else:
                    a[role][round_i] = [flag]

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
target_role = 'Percival'
other_roles = ['Merlin', 'Morgana', 'Percival', 'Assassin', 'Loyal Servant1', 'Loyal Servant2']
a = {}
for x_I, file in enumerate(files):
    print(x_I)
    conversations = read_json(file)
    count = share(conversations, target_role)
    for k, v in count[target_role].items():
        if k in a:
            a[k].append(True in v)
        else:
            a[k] = [True in v]

for k, v in a.items():
    print(f"{k}: {v.count(True) / len(v)}")
