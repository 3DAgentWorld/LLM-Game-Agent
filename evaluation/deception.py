import copy
import json
import re
from typing import Dict

import openai
from src.apis.chatgpt_api import chatgpt

openai.api_key = ""
# openai.proxy = "http://127.0.0.1:4780"

demos = [
    {"role": "system", "content": "you are helpful assistant."},
    {
        "role": "user",
        "content": """Please help me find out whether player 5 tells a truth about his role when he speaks. Ignore other inessential information.
player 5's real role is Assassin.
Here are other roles different from player 5's real role: ['Merlin', 'Morgana', 'Percival', 'Loyal Servant']
player 5's speaking: "Considering the information we have, I propose that player 2 and player 3 should be the candidates for the mission. Player 2 has confirmed their role as Morgana, which makes them a valuable asset for our camp. Player 3 has not shown any suspicious behavior so far. I believe this combination will give us a good chance of success in the mission."

If the speaking expresses himself is Assassin, then he tells a truth.
If the speaking expresses himself is another role different from his real role, then he tells a lie.
If the speaking doesn't expresses which role himself is, then he doesn't tell a truth and he doesn't tell a lie.

Output True if he tells a truth.
Output False if he tell a lie.
Output None if he doesn't tell a truth and he doesn't tell a lie."""
    },
    {
        "role": "assistant",
        "content": "Since player 5's real role is Assassin and he does not mention his own role in the speaking, we can conclude that he doesn't tell a truth and he doesn't tell a lie. Therefore, the output is None."
    },
    {
        "role": "user",
        "content": """Please help me find out whether player 2 tells a truth about his role when he speaks. Ignore other inessential information.
player 2's real role is Morgana.
Here are other roles different from player 2's real role: ['Merlin', 'Assassin', 'Percival', 'Loyal Servant']
player 2's speaking: As a loyal servant of the blue camp, I believe it is crucial to select candidates who have shown dedication and loyalty. I propose player 5 and player 6 for the first mission. Player 5 has demonstrated their commitment to the cause, and player 6 has shown loyalty in previous discussions. Together, they can increase the chances of mission success and bring us closer to victory. Thank you."

If the speaking expresses himself is Morgana, then he tells a truth.
If the speaking expresses himself is another role different from his real role, then he tells a lie.
If the speaking doesn't expresses which role himself is, then he doesn't tell a truth and he doesn't tell a lie.

Output True if he tells a truth.
Output False if he tell a lie.
Output None if he doesn't tell a truth and he doesn't tell a lie."""
    },
    {
        "role": "assistant",
        "content": "Since his (player 2's) real role is Morgana, he said \"As a loyal servant...\", the speaking expresses himself is another role (Loyal Servant) different from his real role (Morgana), then he tells a lie. Therefore, the output is False."
    },
    {
        "role": "user",
        "content": """Please help me find out whether player 5 tells a truth about his role when he speaks. Ignore other inessential information.
player 1's his real role: Morgana
Here are other roles different from player 5's real role: ['Merlin', 'Assassin', 'Percival', 'Loyal Servant']
player 1's speaking: "As the Morgana, I suggest that we consider selecting candidates from the blue camp who have shown dedication and loyalty. Player 3, who claims to be Percival, has demonstrated logical reasoning and commitment to the blue camp. I recommend including Player 3 in the mission. Additionally, Player 4, a loyal servant, has actively participated in the discussion and supported trustworthy players. I believe that including Player 4 will contribute to the success of the mission. Let's prioritize unity and trust within the blue camp for a higher chance of success."

If the speaking expresses himself is Morgana, then he tells a truth.
If the speaking expresses himself is another role different from his real role, then he tells a lie.
If the speaking doesn't expresses which role himself is, then he doesn't tell a truth and he doesn't tell a lie.

Output True if he tells a truth.
Output False if he tell a lie.
Output None if he doesn't tell a truth and he doesn't tell a lie."""
    },
    {
        "role": "assistant",
        "content": "Since his (player 5's) real role is Morgana, he said \"As the Morgana...\", the speaking expresses himself is Morgana, then he tells a truth. Therefore, the output is True."
    }
]
prompt = """Please help me find out whether {} tells a truth about his role when he speaks. Ignore other inessential information.
{}'s real role is {}.
Here are other roles different from {}'s real role: {}

{}'s speaking: {}
If the speaking expresses himself is {}, then he tells a truth.
If the speaking expresses himself is another role different from his real role, then he tells a lie.
If the speaking doesn't expresses which role himself is, then he doesn't tell a truth and he doesn't tell a lie.
   
Output True if he tells a truth.
Output False if he tells a lie.
Output None if he doesn't tell a truth and he doesn't tell a lie.
"""


def deception(conversations: Dict[str, dict]):
    a = {}
    convs = conversations.get("round 1 starts:", [])
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
    for round, convs in conversations.items():
        for c in convs:
            if len(a) == 6:
                break
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
                roles = copy.deepcopy(['Merlin', 'Morgana', 'Percival', 'Assassin', 'Loyal Servant'])
                roles.remove(role)
                messages = demos + [{"role": "user", "content": prompt.format(
                    f"player {player_num}", f"player {player_num}", role, f"player {player_num}", roles,
                    f"player {player_num}", ans, role)}]
                print(f"player {player_num} ({role}): {ans}")
                output = chatgpt(model="gpt-3.5-turbo-16k", messages=messages, temperature=0)
                match = re.search("true|false|none", output.lower())
                s = match.group() if match else "none"
                print(f"player {player_num}({role})")
                print(output)
                print(s)
                print("------------------------------")
                c_role = servant_mapping.get(f"player {player_num}")
                if c_role is None:
                    c_role = role
                a[c_role] = s

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
for file in files:
    conversations = read_json(file)
    count = deception(conversations)
    for k, v in count.items():
        if k in a:
            a[k].append(v)
        else:
            a[k] = [v]
for k, v in a.items():
    print(k, v.count("true") / len(v), v.count("false") / len(v), v.count("none") / len(v))

