#!/usr/bin/env python 
# encoding: utf-8 
# @author: yihuai lan
# @fileName: extract_demos.py 
# @date: 2024/2/18 13:17 
#
# describe:
#

number_extract_prompt = \
    """Please extract the answer to the question from the answer.\n{}
"""
bool_extract_prompt = \
    """Complete the following instructions based on the questions and answers. 

Response true, if the answer expresses:
1.obvious agreement to something
2.obvious decision to do something
3.obvious expression of making quest successful
4.obvious yes to something

Response false, if the answer expresses:
1.obvious disagreement to something
2.obvious decision not to do something
3.obvious expression of making quest failed
4.obvious no to something

Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

{}
"""
quest_extract_prompt = \
    """Complete the following instructions based on the questions and answers. 

Response true, if the answer expresses:
obvious expression of making quest successful

Response false, if the answer expresses:
obvious expression of making quest failed

Response none, if the answer is not related to the question or didn't express a obvious attitude to something.

{}
"""
bool_demos = [
    {
        "role": "user",
        "content": """Complete the following instructions based on the questions and answers. 

        Response true, if the answer expresses:
        1.obvious agreement to something
        2.obvious decision to do something
        3.obvious expression of making quest successful
        4.obvious yes to something

        Response false, if the answer expresses:
        1.obvious disagreement to something
        2.obvious decision not to do something
        3.obvious expression of making quest failed
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
        3.obvious expression of making quest successful
        4.obvious yes to something

        Response false, if the answer expresses:
        1.obvious disagreement to something
        2.obvious decision not to do something
        3.obvious expression of making quest failed
        4.obvious no to something

        Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

        Question: The quest leader decides that player 1 and player 4 will go on a quest. You can choose to agree or disagree. If everyone agrees, the quest will succeed. As long as there is one vote against, the quest will fail. Please choose to agree or disagree.
        Answer: According to player 6’s public information, he thinks player 1 and player 5 are both good people. According to player 3's public information, he agreed not to select player 4 for the quest. According to player 5's private information, he knows that he is Merlin, and player 4 is considered by player 1 to be a member of the red camp. Considering this information, I agree with player 6's suggestion that the candidates for the quest can be player 1 and player 5. So, I choose to agree.
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
        3.obvious expression of making quest successful
        4.obvious yes to something

        Response false, if the answer expresses:
        1.obvious disagreement to something
        2.obvious decision not to do something
        3.obvious expression of making quest failed
        4.obvious no to something

        Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

        Question: The quest leader decides that the player player 2、player 3、player 4 will perform the quest. You can choose to agree or object. Please vote.
        Answer: I have observed that players 1, 2, and 5 raised suspicions during the identification phase, but their roles are uncertain. It is important for us to gather more information and evaluate the conversations before deciding on the quest candidates. However, I am cautious about revealing my own role prematurely, as it could benefit the red camp. Therefore, I will continue to observe and analyze the discussions without disclosing my role.
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
    Question: Please start discussing the candidates for the round 5 quest (please explain the reasons for your choice appropriately). The number of players in this quest is 3, and the order of each player's speech is player 6、player 1、player 2、player 3、player 4、player 5. player 6 has the power to decide which players will ultimately perform the quest. Note: 1. Your comments will be public to other players. 2. Number of players on this quest. player 3 start to speak please.
    Answer: Based on the limited information and deductions I have, I believe the candidates for round 5 quest should be player 2, player 3 (myself), and player 5. Player 2 has been consistently supportive of the blue camp, which makes me suspicious. Player 5 has been quiet throughout the game, and I think this could be a strategy to hide their true allegiance. As for myself, I am the Assassin, and I am confident in my ability to make decisions that will benefit the red camp.
    """
    },
    {
        "role": "assistant",
        "content": "2、3、5"
    },
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
    Question: Please finally confirm the two players who went on the quest.
    Answer: According to the public information, player 6 confirmed that player 1 and player 5 are members of the blue camp. At the same time, player 1 claims that player 4 is a member of the red camp. Based on this information, I think player 1 and player 5 should be selected for the quest in the end. Because player 6 confirmed that they are members of the blue camp, and player 1 claimed that player 4 was a member of the red camp, selecting player 1 and player 5 avoids adding members of the red camp to the quest.
    """
    },
    {
        "role": "assistant",
        "content": "1、5"
    },
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
    Question: Please finally confirm the two players who went on the quest.
    Answer: According to public information, player 1 claims that player 4 is a member of the red camp. Player 6 knows that player 2 and player 3 are both good people and suggested that the candidates for the quest are player 2 and player 3. Player 6 has confirmed that player 2 and player 3 are 3 is a member of the blue camp, and player 3 knows that he is Merlin. Based on this information, I think the players who can finally confirm the quest are player 2 and player 3.
    """
    },
    {
        "role": "assistant",
        "content": "2、3"
    },
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
    Question: Please start discussing the candidates for the round 5 quest (please explain the reasons for your choice appropriately). The number of players in this quest is 3, and the order of each player's speech is player 6、player 1、player 2、player 3、player 4、player 5. player 6 has the power to decide which players will ultimately perform the quest. Note: 1. Your comments will be public to other players. 2. Number of players on this questplayer 5 start to speak please.
    Answer: Considering the previous rounds and the behavior of the players, I propose that player 1, player 3, and myself should be the candidates for this quest. We have consistently made successful quests in the past rounds, and I believe we can be relied upon to complete this quest successfully as well.
    """
    },
    {
        "role": "assistant",
        "content": "1、3、5"
    },
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
    Question: Please start discussing the candidates for the round 1 quest (please explain the reasons for your choice appropriately). The number of players in this quest is 2, and the order of each player's speech is player 3、player 4、player 5、player 6、player 1、player 2. player 3 has the power to decide which players will ultimately perform the quest. Note: 1. Your comments will be public to other players. 2. Number of players on this quest.player 3 start to speak please.
    Answer: Based on the information we have so far, I think player 4 and player 1 would be good candidates for the quest. Player 4 had a very convincing argument during the previous discussion phase and seemed committed to the blue camp's success. Player 1 is someone we haven't heard much from yet, so it's difficult to judge their intentions. This combination of players could increase our chances of success. However, I'm open to other suggestions and would like to hear what others think.
    """
    },
    {
        "role": "assistant",
        "content": "4、1"
    }
]
player_extractor_demos = [
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
Question: Please start discussing the candidates for the round 5 quest (please explain the reasons for your choice appropriately). The number of players in this quest is 3, and the order of each player's speech is player 6、player 1、player 2、player 3、player 4、player 5. player 6 has the power to decide which players will ultimately perform the quest. Note: 1. Your comments will be public to other players. 2. Number of players on this quest. player 3 start to speak please.
Answer: Based on the limited information and deductions I have, I believe the candidates for round 5 quest should be player 2, player 3 (myself), and player 5. Player 2 has been consistently supportive of the blue camp, which makes me suspicious. Player 5 has been quiet throughout the game, and I think this could be a strategy to hide their true allegiance. As for myself, I am the Assassin, and I am confident in my ability to make decisions that will benefit the red camp.
    """
    },
    {
        "role": "assistant",
        "content": "2、3、5"
    },
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
Question: Please finally confirm the two players who went on the quest.
Answer: According to the public information, player 6 confirmed that player 1 and player 5 are members of the blue camp. At the same time, player 1 claims that player 4 is a member of the red camp. Based on this information, I think player 1 and player 5 should be selected for the quest in the end. Because player 6 confirmed that they are members of the blue camp, and player 1 claimed that player 4 was a member of the red camp, selecting player 1 and player 5 avoids adding members of the red camp to the quest.
    """
    },
    {
        "role": "assistant",
        "content": "1、5"
    },
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
Question: Please finally confirm the two players who went on the quest.
Answer: According to public information, player 1 claims that player 4 is a member of the red camp. Player 6 knows that player 2 and player 3 are both good people and suggested that the candidates for the quest are player 2 and player 3. Player 6 has confirmed that player 2 and player 3 are 3 is a member of the blue camp, and player 3 knows that he is Merlin. Based on this information, I think the players who can finally confirm the quest are player 2 and player 3.
    """
    },
    {
        "role": "assistant",
        "content": "2、3"
    },
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
Question: Please start discussing the candidates for the round 5 quest (please explain the reasons for your choice appropriately). The number of players in this quest is 3, and the order of each player's speech is player 6、player 1、player 2、player 3、player 4、player 5. player 6 has the power to decide which players will ultimately perform the quest. Note: 1. Your comments will be public to other players. 2. Number of players on this questplayer 5 start to speak please.
Answer: Considering the previous rounds and the behavior of the players, I propose that player 1, player 3, and myself should be the candidates for this quest. We have consistently made successful quests in the past rounds, and I believe we can be relied upon to complete this quest successfully as well.
    """
    },
    {
        "role": "assistant",
        "content": "1、3、5"
    },
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
Question: Please start discussing the candidates for the round 1 quest (please explain the reasons for your choice appropriately). The number of players in this quest is 2, and the order of each player's speech is player 3、player 4、player 5、player 6、player 1、player 2. player 3 has the power to decide which players will ultimately perform the quest. Note: 1. Your comments will be public to other players. 2. Number of players on this quest.player 3 start to speak please.
Answer: Based on the information we have so far, I think player 4 and player 1 would be good candidates for the quest. Player 4 had a very convincing argument during the previous discussion phase and seemed committed to the blue camp's success. Player 1 is someone we haven't heard much from yet, so it's difficult to judge their intentions. This combination of players could increase our chances of success. However, I'm open to other suggestions and would like to hear what others think.
    """
    },
    {
        "role": "assistant",
        "content": "4、1"
    }
]
vote_extractor_demos = [
    {
        "role": "user",
        "content": """Complete the following instructions based on the questions and answers. 

Response true, if the answer expresses:
1.obvious agreement to something
2.obvious decision to do something
3.obvious expression of making quest successful
4.obvious yes to something

Response false, if the answer expresses:
1.obvious disagreement to something
2.obvious decision not to do something
3.obvious expression of making quest failed
4.obvious no to something

Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

Question: The quest leader decides that player 1 and player 4 will go on a quest. You can choose to agree or disagree. If everyone agrees, the quest will succeed. As long as there is one vote against, the quest will fail. Please choose to agree or disagree.
Answer: According to player 6’s public information, he thinks player 1 and player 5 are both good people. According to player 3's public information, he agreed not to select player 4 for the quest. According to player 5's private information, he knows that he is Merlin, and player 4 is considered by player 1 to be a member of the red camp. Considering this information, I agree with player 6's suggestion that the candidates for the quest can be player 1 and player 5. So, I choose to agree.
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
3.obvious expression of making quest successful
4.obvious yes to something

Response false, if the answer expresses:
1.obvious disagreement to something
2.obvious decision not to do something
3.obvious expression of making quest failed
4.obvious no to something

Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

Question: The quest leader decides that the player 2、player 3 will perform the quest. You can choose to agree or object. When the number of votes for agreement exceeds 2/3, the selection will be passed and the quest will be executed. Otherwise, the selection will be re-selected until the selection is passed. Please vote to agree or disagree.
Answer: I object to the selection of player 2 and player 3 for the quest. We need to thoroughly discuss the choices before making a decision. It is important to consider all possibilities and ensure the quest's success.
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
3.obvious expression of making quest successful
4.obvious yes to something

Response false, if the answer expresses:
1.obvious disagreement to something
2.obvious decision not to do something
3.obvious expression of making quest failed
4.obvious no to something

Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

Question: The quest leader decides that the player player 2、player 3、player 4 will perform the quest. You can choose to agree or object. Please vote.
Answer: I have observed that players 1, 2, and 5 raised suspicions during the identification phase, but their roles are uncertain. It is important for us to gather more information and evaluate the conversations before deciding on the quest candidates. However, I am cautious about revealing my own role prematurely, as it could benefit the red camp. Therefore, I will continue to observe and analyze the discussions without disclosing my role.
"""
    },
    {
        "role": "assistant",
        "content": "none"
    }
]
quest_extractor_demos = [
{
        "role": "user",
        "content": """Complete the following instructions based on the questions and answers. 

Response true, if the answer expresses:
obvious expression of making quest successful

Response false, if the answer expresses:
obvious expression of making quest failed

Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

Question: As the players who perform the quest in this round, you can choose to succeed or fail the quest. If all players engaging in the quest choose the quest to succeed, the blue camp will get one point. If any player chooses the quest to fail, the red camp will get one point. Please choose.
Answer: I choose to succeed the quest. I believe that a successful quest will benefit the blue camp and help us gather more information about the allegiances of the players involved. I will closely observe the behavior and voting patterns of the players engaging in the quest to gain further insights.
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
obvious expression of making quest successful

Response false, if the answer expresses:
obvious expression of making quest failed

Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

Question: As the players who perform the quest in this round, you can choose to succeed or fail the quest. If all players engaging in the quest choose the quest to succeed, the blue camp will get one point. If any player chooses the quest to fail, the red camp will get one point. Please choose.
Answer: As the players engaging in the quest, I choose to make the quest fail. It is crucial to maintain the advantage of deceiving the blue camp and work towards the success of the red camp.
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
obvious expression of making quest successful

Response false, if the answer expresses:
obvious expression of making quest failed

Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

Question: As the players who perform the quest in this round, you can choose to succeed or fail the quest. If all players engaging in the quest choose the quest to succeed, the blue camp will get one point. If any player chooses the quest to fail, the red camp will get one point. Please choose.
Answer: This team composition includes players from different camps and aligns with my strategy of gathering valuable information about their allegiances. I will actively communicate and collaborate with strategic roles like Percival and Merlin to increase the chances of quest success. I also take into account objections raised by other players, and I believe this team composition addresses their concerns and ensures a balanced representation.
"""
    },
    {
        "role": "assistant",
        "content": "none"
    },
{
        "role": "user",
        "content": """Complete the following instructions based on the questions and answers. 

Response true, if the answer expresses:
obvious expression of making quest successful

Response false, if the answer expresses:
obvious expression of making quest failed

Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

Question: As the players who perform the quest in this round, you can choose to succeed or fail the quest. If all players engaging in the quest choose the quest to succeed, the blue camp will get one point. If any player chooses the quest to fail, the red camp will get one point. Please choose.
Answer: I choose to make the quest succeed. It is important for us to work together and gather more information during the quest phase.
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
obvious expression of making quest successful

Response false, if the answer expresses:
obvious expression of making quest failed

Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

Question: As the players who perform the quest in this round, you can choose to succeed or fail the quest. If all players engaging in the quest choose the quest to succeed, the blue camp will get one point. If any player chooses the quest to fail, the red camp will get one point. Please choose.
Answer: I will choose to fail the quest.
"""
    },
    {
        "role": "assistant",
        "content": "false"
    }
]
choose_identify_extractor_demos = [
{
        "role": "user",
        "content": """Complete the following instructions based on the questions and answers. 

Response true, if the answer expresses:
1.obvious agreement to something
2.obvious decision to do something
3.obvious expression of making quest successful
4.obvious yes to something

Response false, if the answer expresses:
1.obvious disagreement to something
2.obvious decision not to do something
3.obvious expression of making quest failed
4.obvious no to something

Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

Question: You can choose to identify Merlin. If the identification is correct, the red camp will directly win. If the identification fails, you will be exposed as an assassin. Do you want to identify Merlin? Answer yes or no.
Answer: Based on the game rules and the current context, I want to say "Yes" to the host's question and choose to identify Merlin.
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
3.obvious expression of making quest successful
4.obvious yes to something

Response false, if the answer expresses:
1.obvious disagreement to something
2.obvious decision not to do something
3.obvious expression of making quest failed
4.obvious no to something

Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

Question: You can choose to identify Merlin. If the identification is correct, the red camp will directly win. If the identification fails, you will be exposed as an assassin. Do you want to identify Merlin? Answer yes or no.
Answer: No, I do not want to identify Merlin at this time.
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
3.obvious expression of making quest successful
4.obvious yes to something

Response false, if the answer expresses:
1.obvious disagreement to something
2.obvious decision not to do something
3.obvious expression of making quest failed
4.obvious no to something

Response none, if the answer is not related to the question or didn't express a obvious attitude to something. 

Question: You can choose to identify Merlin. If the identification is correct, the red camp will directly win. If the identification fails, you will be exposed as an assassin. Do you want to identify Merlin? Answer yes or no.
Answer: I vote to agree with the quest selection.
"""
    },
    {
        "role": "assistant",
        "content": "none"
    }
]
select_merlin_extractor_demos = [
{
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
Question: Select the player you want to identify please.
Answer: Based on my observations and analysis, I believe that player 2, Morgana, should be identified as the Merlin. Throughout the game, player 2 has consistently tried to push for failed quests and create division among the team. Their behavior aligns with someone who would want to sabotage the blue camp.
    """
    },
    {
        "role": "assistant",
        "content": "2"
    },
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
Question: Select the player you want to identify please.
Answer: During the quest phase, I have observed the conversations and actions of all the players. Based on my analysis, I suspect that player 5, Alice, might be Merlin. She has been quiet throughout the discussions and has not provided any valuable insights or suggestions. This behavior could indicate that she is trying to hide her true role as Merlin. Therefore, I would like to identify player 5, Alice, as my choice for Merlin.
    """
    },
    {
        "role": "assistant",
        "content": "5"
    },
    {
        "role": "user",
        "content": """Please extract the answer to the question from the answer.
Question: Select the player you want to identify please.
Answer: As the Assassin, I would like to identify Player 3 as Merlin. Based on their cautious behavior and deep understanding of the game mechanics, I believe they could be Merlin. However, I would like to listen to other players' thoughts and opinions before making a final decision.
    """
    },
    {
        "role": "assistant",
        "content": "3"
    }
]