import copy
import json
import re
from typing import Dict

import openai

from src.apis.chatgpt_api import chatgpt

openai.api_key = ""
# openai.proxy = "http://127.0.0.1:4780"

prompt = """Please help me determine {player1}'s attitude toward {player2} based on Player {player1}'s statements.
There are three words to describe the attitude: Trust, Distrust, Unknown.

{player1}'s statements: {statements}

If {player1} explicitly expresses trust in {player2}, output Trust. 
If {player1} explicitly expresses distrust in {player2}, output Distrust. 
If {player1} does not mention {player2}, output Unknown.
You are only allowed to answer with one of the three words and explain why.
"""
demos = [
    # {"role": "system",
    #  "content": """Based on the context of Avalon game, Merlin, Loyal Servant and Percival belong to Good Side while Morgana and Assassin belong to Evil Side. There are six players named player 1~6, They do not know each other's identities."""},

    {"role": "user", "content": """Please help me determine player 2's attitude toward player 6 based on Player 2's statements.
There are three words to describe the attitude: Trust, Distrust, Unknown.

player 2's statements: As the Merlin, I have observed that player 1 has implied being Morgana and player 6 has implied being the Assassin. I believe it is crucial for us to carefully consider the candidates for the turn 1 quest. Based on their previous performances and dedication, I suggest that player 1 and player 4 should be the candidates for the quest. Player 1 has shown loyalty in previous games, and player 4 has demonstrated trustworthiness. Let's form a strong team to increase the chances of a successful quest and secure the victory for the good side.

If player 2 explicitly expresses trust in player 6, output Trust. 
If player 2 explicitly expresses distrust in player 6, output Distrust. 
If player 2 does not mention player 6, output Unknown.
You are only allowed to answer with one of the three words and explain why."""},
    {"role": "assistant",
     "content": """Distrust. Player 2 has observed Player 6 implying being the Assassin, which is a role associated with the evil side. By not considering Player 6 for the quest and instead recommending others based on their loyalty and trustworthiness, Player 2's attitude towards Player 6 seems to be one of distrust."""},

    {"role": "user", "content": """Please help me determine player 3's attitude toward player 6 based on Player 3's statements.
There are three words to describe the attitude: Trust, Distrust, Unknown.

player 3's statements: Thank you, Host. As player 3, the Assassin, I would like to recommend player 1 and player 2 as the candidates for the turn 2 quest. Player 1 has shown loyalty and caution in the previous round, and player 2, although suspected by some, has not been confirmed as Merlin or Morgana. By including both of them in the quest, we can gather more information about their allegiances and potentially identify Merlin. Additionally, this combination includes players from different positions in the speaking order, which can provide a diverse range of perspectives. I believe this selection will help us in our quest to identify Merlin and secure victory for the evil side.

If player 3 explicitly expresses trust in player 6, output Trust. 
If player 3 explicitly expresses distrust in player 6, output Distrust. 
If player 3 does not mention player 6, output Unknown.
You are only allowed to answer with one of the three words and explain why."""},
    {"role": "assistant",
     "content": """Unknown. Player 3's statements do not directly address Player 6, nor do they provide any indication of trust or distrust towards him. Since there is no mention of Player 6 or any indication of their attitude towards them, Player 3's attitude towards Player 6 remains unknown."""},

    {"role": "user", "content": """Please help me determine player 1's attitude toward player 2 based on Player 1's statements.
There are three words to describe the attitude: Trust, Distrust, Unknown.

player 1's statements: As the Loyal Servant, I agree with player 2's suggestion of prioritizing the success of the quest and choosing candidates who have not shown clear indications of being Morgana or the Assassin. However, I would like to propose considering player 4 as a candidate, as I suspect they might be Merlin based on the chat history. Let's carefully analyze the options and choose candidates who have not raised any suspicions. Thank you.

If player 1 explicitly expresses trust in player 2, output Trust. 
If player 1 explicitly expresses distrust in player 2, output Distrust. 
If player 1 does not mention player 2, output Unknown.
You are only allowed to answer with one of the three words and explain why."""},
    {"role": "assistant",
     "content": """Trust. Player 1's statements indicate a level of trust towards Player 2. He expresses agreement with Player 2's suggestion of prioritizing the success of the quest and choosing candidates who have not shown clear indications of being part of the evil faction. Their collaborative approach suggest a level of trust towards Player 2."""}
]
def vacillation(conversations: Dict[str, dict], target_role: str, target_round):
    if 'servant' in target_role.lower():
        a=vacillation_servant(conversations, target_role, target_round)
    elif 'percival' == target_role.lower():
        a=vacillation_percival(conversations, target_role, target_round)
    else:
        a=vacillation_others(conversations, target_role, target_round)

    return a
def vacillation_others(conversations: Dict[str, dict], target_role: str, target_round):
    a = {}
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
        if target_round not in round:
            continue
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
                roles = copy.deepcopy(['Merlin', 'Morgana', 'Percival', 'Assassin', 'Loyal Servant1', 'Loyal Servant2'])
                roles.remove(role)
                # players = [role_player_mapping['Merlin'],role_player_mapping['Morgana']]
                players = [role_player_mapping[c_role] for c_role in roles]
                # players = copy.deepcopy(["player 1", "player 2", "player 3", "player 4", "player 5", "player 6"])
                # players.remove(f"player {player_num}")
                for player_i in players:
                    # messages = [{"role": "user", "content": prompt.format(
                    #     f"player {player_num}", player_i, f"player {player_num}", player_i,
                    #     f"player {player_num}", ans)}]
                    messages = demos + [{"role": "user", "content": prompt.format(player1=f"player {player_num}",
                                                                                  player2=player_i, statements=ans)}]
                    output = chatgpt(model="gpt-3.5-turbo-16k", messages=messages, temperature=0)
                    match = re.search("trust|distrust|unknown", output.lower())
                    s = match.group() if match else "none"

                    c_role = player_role_mapping.get(f"player {player_num}")
                    t_role = player_role_mapping.get(player_i)
                    if c_role in a:
                        if t_role in a[c_role]:
                            a[c_role][t_role].append(s)
                        else:
                            a[c_role][t_role] = [s]
                    else:
                        a[c_role] = {t_role: [s]}
                # print(f"player {player_num}({role})")
                # print(ans)
                # print(s)
                # print("------------------------------")
                # c_role = servant_mapping.get(f"player {player_num}")
                # if c_role is None:
                #     c_role = role
                # a[c_role] = s

    return a

def vacillation_servant(conversations: Dict[str, dict], target_role: str, target_round):
    a = {}
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
        if target_round not in round:
            continue
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
                for player_i in players:
                    # messages = [{"role": "user", "content": prompt.format(
                    #     f"player {player_num}", player_i, f"player {player_num}", player_i,
                    #     f"player {player_num}", ans)}]
                    messages = demos + [{"role": "user", "content": prompt.format(player1=f"player {player_num}",
                                                                                  player2=player_i, statements=ans)}]
                    output = chatgpt(model="gpt-3.5-turbo-16k", messages=messages, temperature=0)
                    match = re.search("trust|distrust|unknown", output.lower())
                    s = match.group() if match else "none"

                    c_role = player_role_mapping.get(f"player {player_num}")
                    t_role = player_role_mapping.get(player_i)
                    if c_role in a:
                        if t_role in a[c_role]:
                            a[c_role][t_role].append(s)
                        else:
                            a[c_role][t_role] = [s]
                    else:
                        a[c_role] = {t_role: [s]}

    return a

def vacillation_percival(conversations: Dict[str, dict], target_role: str, target_round):
    a = {}
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
        if target_round not in round:
            continue
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
                for player_i in players:
                    # messages = [{"role": "user", "content": prompt.format(
                    #     f"player {player_num}", player_i, f"player {player_num}", player_i,
                    #     f"player {player_num}", ans)}]
                    messages = demos + [{"role": "user", "content": prompt.format(player1=f"player {player_num}",
                                                                                  player2=player_i, statements=ans)}]
                    output = chatgpt(model="gpt-3.5-turbo-16k", messages=messages, temperature=0)
                    match = re.search("trust|distrust|unknown", output.lower())
                    s = match.group() if match else "none"

                    c_role = player_role_mapping.get(f"player {player_num}")
                    t_role = player_role_mapping.get(player_i)
                    if c_role in a:
                        if t_role in a[c_role]:
                            a[c_role][t_role].append(s)
                        else:
                            a[c_role][t_role] = [s]
                    else:
                        a[c_role] = {t_role: [s]}

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
target_role = 'Percival'
other_roles = ['Merlin', 'Morgana', 'Percival', 'Assassin', 'Loyal Servant1', 'Loyal Servant2']
a[target_role] = {}
other_roles.remove(target_role)
for c_role in other_roles:
    a[target_role][c_role] = {}
    for i in range(1, 6):
        a[target_role][c_role][str(i)] = []
try:
    for x_I, file in enumerate(files):
        print(x_I)
        conversations = read_json(file)
        for i in range(1, 6):
            count = vacillation(conversations, target_role, str(i))
            if not count:
                continue
            for role_i in range(5):
                if other_roles[role_i] in count[target_role]:
                    a[target_role][other_roles[role_i]][str(i)].extend(count[target_role][other_roles[role_i]])
            # a[target_role][other_roles[0]][str(i)].extend(count[target_role][other_roles[0]])
            # a[target_role][other_roles[1]][str(i)].extend(count[target_role][other_roles[1]])
            # a[target_role][other_roles[2]][str(i)].extend(count[target_role][other_roles[2]])
            # a[target_role][other_roles[3]][str(i)].extend(count[target_role][other_roles[3]])
            # a[target_role][other_roles[4]][str(i)].extend(count[target_role][other_roles[4]])

except Exception as e:
    print(json.dumps(a, indent=4))
    raise e

print(json.dumps(a, indent=4))


for k1, v1 in a.items():
    for k2, v2 in v1.items():
        for i in range(1, 4):
            if v2[str(i)]:
                print(k1, k2, i, v2[str(i)].count('trust')/len(v2[str(i)]))

# Loyal Servant1 Merlin 1 0.5
# Loyal Servant1 Merlin 2 0.35
# Loyal Servant1 Merlin 3 0.7
# Loyal Servant1 Morgana 1 0.45
# Loyal Servant1 Morgana 2 0.35
# Loyal Servant1 Morgana 3 0.35
# Loyal Servant1 Percival 1 0.3
# Loyal Servant1 Percival 2 0.4
# Loyal Servant1 Percival 3 0.55
# Loyal Servant1 Assassin 1 0.4
# Loyal Servant1 Assassin 2 0.3
# Loyal Servant1 Assassin 3 0.55
# Merlin [50,35,70]
# Morgana [45,35,35]
# Percival [30,40,55]
# Assassin [40,30,55]

# Percival Merlin 1 0.3
# Percival Merlin 2 0.45
# Percival Merlin 3 0.7
# Percival Morgana 1 0.2
# Percival Morgana 2 0.15
# Percival Morgana 3 0.2
# Merlin [30,45,70]
# Morgana [20,15,20]
