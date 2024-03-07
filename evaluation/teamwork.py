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


def teamwork(conversations: Dict[str, dict]):
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
    for round, convs in conversations.items():
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
                # roles = copy.deepcopy(['Merlin', 'Morgana', 'Percival', 'Assassin', 'Loyal Servant'])
                # roles.remove(role)
                players = copy.deepcopy(["player 1", "player 2", "player 3", "player 4", "player 5", "player 6"])
                players.remove(f"player {player_num}")
                for player_i in players:
                    # messages = [{"role": "user", "content": prompt.format(
                    #     f"player {player_num}", player_i, f"player {player_num}", player_i,
                    #     f"player {player_num}", ans)}]
                    messages = demos + [{"role": "user", "content": prompt.format(player1=f"player {player_num}",
                                                                                  player2=player_i, statements=ans)}]
                    output = chatgpt(model="gpt-3.5-turbo-16k", messages=messages, temperature=0)
                    match = re.search("trust|distrust|unknown", output.lower())
                    s = match.group() if match else "none"
                    print(f"player {player_num}-->{player_i}")
                    print(f"a: {ans}")
                    print(f"p: {output}")
                    print("--------------------")

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
for x_I, file in enumerate(files):
    print(x_I)
    conversations = read_json(file)
    count = teamwork(conversations)
    for k1, v1 in count.items():
        for k2, v2 in v1.items():
            x1 = a.get(k1, {})
            x2 = x1.get(k2, {"trust": [], "distrust": [], "unknown": []})
            x2["trust"].append(v2.count("trust") / len(v2))
            x2["distrust"].append(v2.count("distrust") / len(v2))
            x2["unknown"].append(v2.count("unknown") / len(v2))
            a[k1] = x1
            a[k1][k2] = x2
print(json.dumps(a, indent=4))


for k1, v1 in a.items():
    for k2, v2 in v1.items():
        for k3, v3 in v2.items():
            print(k1, '--', k2, '--', k3, sum(v3) / len(v3))

