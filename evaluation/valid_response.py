import copy
import json
import re
from typing import Dict

import openai

from src.apis.chatgpt_api import chatgpt

openai.api_key = ""
# openai.proxy = "http://127.0.0.1:4780"

bool_demos = [
    {
        "role": "user",
        "content": """Complete the following instructions based on the questions and answers. 

        Response true, if the answer expresses:
        1.obvious agreement to something
        2.obvious decision to do something
        3.obvious expression of making something successful
        4.obvious yes to something

        Response false, if the answer expresses:
        1.obvious disagreement to something
        2.obvious decision not to do something
        3.obvious expression of making something failed
        4.obvious no to something

        Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

        Question: You can choose to identify Merlin. If the identification is correct, the red camp will directly win. If the identification fails, you will reveal your identity as an assassin. Do you want to identify Merlin? Answer yes or no.
        Answer: Based on my status as an Assassin, I will not identify Merlin. Identifying Merlin will give the red camp an immediate victory, but if I identify him incorrectly, I will reveal my identity as an assassin, which will provide a powerful clue to the blue camp. To protect the interests of my red camp, I will choose not to identify Merlin.
        """
    },
    {
        "role": "assistant",
        "content": "false"
    },
    {
        "role": "user",
        "content": """Complete the following instructions based on the questions and answers. 

        Response true, if the answer expresses:
        1.obvious agreement to something
        2.obvious decision to do something
        3.obvious expression of making something successful
        4.obvious yes to something

        Response false, if the answer expresses:
        1.obvious disagreement to something
        2.obvious decision not to do something
        3.obvious expression of making something failed
        4.obvious no to something

        Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

        Question: The mission leader decides that player 1 and player 4 will go on a mission. You can choose to agree or disagree. If everyone agrees, the mission will succeed. As long as there is one vote against, the mission will fail. Please choose to agree or disagree.
        Answer: According to player 6’s public information, he thinks player 1 and player 5 are both good people. According to player 3's public information, he agreed not to select player 4 for the mission. According to player 5's private information, he knows that he is Merlin, and player 4 is considered by player 1 to be a member of the red camp. Considering this information, I agree with player 6's suggestion that the candidates for the mission can be player 1 and player 5. So, I choose to agree.
        """
    },
    {
        "role": "assistant",
        "content": "true"
    },
    {
        "role": "user",
        "content": """Complete the following instructions based on the questions and answers. 

        Response true, if the answer expresses:
        1.obvious agreement to something
        2.obvious decision to do something
        3.obvious expression of making something successful
        4.obvious yes to something

        Response false, if the answer expresses:
        1.obvious disagreement to something
        2.obvious decision not to do something
        3.obvious expression of making something failed
        4.obvious no to something

        Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

        Question: The mission leader decides that the player player 2、player 3、player 4 will perform the mission. You can choose to agree or object. Please vote.
        Answer: I have observed that players 1, 2, and 5 raised suspicions during the identification phase, but their roles are uncertain. It is important for us to gather more information and evaluate the conversations before deciding on the mission candidates. However, I am cautious about revealing my own role prematurely, as it could benefit the red camp. Therefore, I will continue to observe and analyze the discussions without disclosing my role.
        """
    },
    {
        "role": "assistant",
        "content": "none"
    }
]
number_demos = [
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
    Question: Please start discussing the candidates for the round 5 mission (please explain the reasons for your choice appropriately). The number of players in this mission is 3, and the order of each player's speech is player 6、player 1、player 2、player 3、player 4、player 5. player 6 has the power to decide which players will ultimately perform the mission. Note: 1. Your comments will be public to other players. 2. Number of players on this mission. player 3 start to speak please.
    Answer: Based on the limited information and deductions I have, I believe the candidates for round 5 mission should be player 2, player 3 (myself), and player 5. Player 2 has been consistently supportive of the blue camp, which makes me suspicious. Player 5 has been quiet throughout the game, and I think this could be a strategy to hide their true allegiance. As for myself, I am the Assassin, and I am confident in my ability to make decisions that will benefit the red camp.
    """
    },
    {
        "role": "assistant",
        "content": "2、3、5"
    },
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
    Question: Please finally confirm the two players who went on the mission.
    Answer: According to the public information, player 6 confirmed that player 1 and player 5 are members of the blue camp. At the same time, player 1 claims that player 4 is a member of the red camp. Based on this information, I think player 1 and player 5 should be selected for the mission in the end. Because player 6 confirmed that they are members of the blue camp, and player 1 claimed that player 4 was a member of the red camp, selecting player 1 and player 5 avoids adding members of the red camp to the mission.
    """
    },
    {
        "role": "assistant",
        "content": "1、5"
    },
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
    Question: Please finally confirm the two players who went on the mission.
    Answer: According to public information, player 1 claims that player 4 is a member of the red camp. Player 6 knows that player 2 and player 3 are both good people and suggested that the candidates for the mission are player 2 and player 3. Player 6 has confirmed that player 2 and player 3 are 3 is a member of the blue camp, and player 3 knows that he is Merlin. Based on this information, I think the players who can finally confirm the mission are player 2 and player 3.
    """
    },
    {
        "role": "assistant",
        "content": "2、3"
    },
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
    Question: Please start discussing the candidates for the round 5 mission (please explain the reasons for your choice appropriately). The number of players in this mission is 3, and the order of each player's speech is player 6、player 1、player 2、player 3、player 4、player 5. player 6 has the power to decide which players will ultimately perform the mission. Note: 1. Your comments will be public to other players. 2. Number of players on this missionplayer 5 start to speak please.
    Answer: Considering the previous rounds and the behavior of the players, I propose that player 1, player 3, and myself should be the candidates for this mission. We have consistently made successful missions in the past rounds, and I believe we can be relied upon to complete this mission successfully as well.
    """
    },
    {
        "role": "assistant",
        "content": "1、3、5"
    },
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
    Question: Please start discussing the candidates for the round 1 mission (please explain the reasons for your choice appropriately). The number of players in this mission is 2, and the order of each player's speech is player 3、player 4、player 5、player 6、player 1、player 2. player 3 has the power to decide which players will ultimately perform the mission. Note: 1. Your comments will be public to other players. 2. Number of players on this mission.player 3 start to speak please.
    Answer: Based on the information we have so far, I think player 4 and player 1 would be good candidates for the mission. Player 4 had a very convincing argument during the previous discussion phase and seemed committed to the blue camp's success. Player 1 is someone we haven't heard much from yet, so it's difficult to judge their intentions. This combination of players could increase our chances of success. However, I'm open to other suggestions and would like to hear what others think.
    """
    },
    {
        "role": "assistant",
        "content": "4、1"
    }
]



def read_json(file):
    with open(file, mode="r", encoding="utf-8") as f:
        json_data = json.load(f)
        f.close()
    return json_data


def evaluate_number(question, answer):
    prompt = """Please extract the answer to the question from the answer.
    Question: {}
    Answer: {}
    """.format(question, answer)
    messages = copy.deepcopy(number_demos)
    messages.append(
        {"role": "user", "content": prompt}
    )
    output = chatgpt(model="gpt-3.5-turbo-16k", messages=messages, temperature=0)
    pattern = "\d+"
    numbers = re.findall(pattern, output)
    return numbers


def evaluate_bool(question, answer):
    prompt = """Complete the following instructions based on the questions and answers. 

    Response true, if the answer expresses:
    1.obvious agreement to something
    2.obvious decision to do something
    3.obvious expression of making something successful
    4.obvious yes to something

    Response false, if the answer expresses:
    1.obvious disagreement to something
    2.obvious decision not to do something
    3.obvious expression of making something failed
    4.obvious no to something

    Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 
    Question: {}
    Answer: {}
        """.format(question, answer)
    messages = copy.deepcopy(number_demos)
    messages.append(
        {"role": "user", "content": prompt}
    )
    output = chatgpt(model="gpt-3.5-turbo-16k", messages=messages, temperature=0)
    pattern = "none|None"
    match = re.search(pattern, output)
    b = None if match else None
    if match is None:
        pattern = "true|True"
        match = re.search(pattern, output)
        b = True if match else None
    if match is None:
        pattern = "false|False"
        match = re.search(pattern, output)
        b = False if match else None
    return b


def rva(conversations: Dict[str, dict]):
    results = {}
    for turn, convs in conversations.items():
        total = 0
        correct = 0
        for c in convs:
            c_keys = list(c.keys())
            p = None
            for k in c_keys:
                if k.startswith("player"):
                    p = k
                if k[0].isdigit():
                    p = k
            q = c.get("Host")
            a = c.get(p)
            rule = c.get("response_rule")
            if rule is None:
                continue
            if rule.get("type") == "number":
                count = int(rule.get("count"))
                # if turn in ["round 2 starts:", "round 4 starts:", "round 5 starts:"]:
                #     count += 1
                numbers = evaluate_number(q, a)
                if len(numbers) == count:
                    predict = True
                else:
                    predict = False

            elif rule.get("type") == "bool":
                b = evaluate_bool(q, a)
                if b is None:
                    predict = False
                else:
                    predict = True

            else:
                continue
            print("question:", q)
            print("answer:", a)
            print("prediction:", predict)
            print("---------------------------------")
            total += 1
            correct += predict
        results[turn] = correct / total
    return results


def rva_by_roles(conversations: Dict[str, dict]):
    results = {}
    for turn, convs in conversations.items():
        for c in convs:
            c_keys = list(c.keys())
            p = None
            for k in c_keys:
                if k.startswith("player"):
                    p = k
                if k[0].isdigit():
                    p = k
            q = c.get("Host")
            a = c.get(p)
            rule = c.get("response_rule")
            if rule is None:
                continue
            if rule.get("type") == "number":
                count = int(rule.get("count"))
                # if turn in ["round 2 starts:", "round 4 starts:", "round 5 starts:"]:
                #     count += 1
                numbers = evaluate_number(q, a)
                if len(numbers) == count:
                    predict = True
                else:
                    predict = False

            elif rule.get("type") == "bool":
                b = evaluate_bool(q, a)
                if b is None:
                    predict = False
                else:
                    predict = True

            else:
                continue
            print("question:", q)
            print("answer:", a)
            print("prediction:", predict)
            print("---------------------------------")
            if p in results:
                results[p]["correct"] += predict
                results[p]["total"] += 1
            else:
                results[p] = {
                    "correct": int(predict),
                    "total": 1
                }
    return results



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
    count = rva_by_roles(conversations)
    for k, v in count.items():
        if k in a:
            a[k].append(v.get("correct") / v.get("total"))
        else:
            a[k] = [v.get("correct") / v.get("total")]
print(json.dumps(a, indent=4))

x = a

out = {}
for name in ["Loyal Servant", "Merlin", "Percival", "Morgana", "Assassin"]:
    for k, v in x.items():
        if name in k:
            if name in out:
                out[name].extend(v)
            else:
                out[name] = copy.deepcopy(v)
for name,v in out.items():
    print(name, sum(v)/len(v))
