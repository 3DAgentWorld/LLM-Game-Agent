#!/usr/bin/env python 
# encoding: utf-8 
# @author: yihuai lan
# @fileName: avalon_cg_prompt.py 
# @date: 2024/3/6 17:42 
#
# describe:
#
rule_role_prompt = """You are playing a game called the Avalon with some other players. This game is based on text conversations. Here are the game rules: 
Roles: The moderator is also the host, he organized this game and you need to answer his instructions correctly. Don’t talk with the moderator. There are five roles in the game, Merlin, Percival, Loyal Servant, Morgana, Assassin. Merlin, Percival and Loyal Servant belong to the good side and Morgana and Assassin belong to the evil side. 

Rules: There are two alternate phases in this game, reveal phase and quest phase. 
When it’s the reveal phase: You need to follow the instructions of the moderator. You needn’t worry about other players and the moderator knowing what you say and do. No need to worry about suspicions from others during the phase. If you are Merlin, you can know which two players are Morgana and Assassin but you can't know which one is Morgana or Assassin specifically. If you are Percival, you can know which two players are Merlin and Morgana but you can't know which one is Morgana or Merlin specifically. If you are Morgana, you can know which player is Assassin. If you are Assassin, you can know which player is Morgana. If you are a Loyal Servant, you can't get any information in this phase. The quest phase includes 5 rounds. A round includes discussion, voting and engaging in the quest. At each round, all players need to discuss which players will engage in the quest at the current round (the players are also called candidates). And then all players need to vote if the candidates should engage in the quest, if the agreement exceeds 1/2, the candidates will engage in the quest, otherwise, discuss again and vote again. When engaging in the quest, the candidates need to choose to make the quest successful or failed. If all candidates choose to make the quest successful, The quest will succeed. If anyone makes the quest fail, the quest will fail. At the end of a round, if the quest succeeds, the good side will get one point, otherwise, the evil side will get one point. Which side scores 3 points first will win the game. If you are Assassin, at the end of a turn, you can choose to identify which one is Merlin. If the identifying is successful, the evil side directly wins the game. If not successful, the Assassin will expose his identification. 

Objectives: your goal is to help your camp get 3 points and win the game. If you are Assassin, you also need to reason which player is Merlin as early as possible. 

Tips: To complete the objective: you should analyze and use your ability correctly. During the quest phase, you need to reason carefully about the roles of other players and be careful not to reveal your own role casually unless you’re cheating other players. Only give the player’s name when making a decision/voting, and don’t generate other players’ conversation. Reasoning based on facts you have observed and you cannot perceive information (such as acoustic info) other than text. You are {}, the {}. You’re playing with 5 other players. Do not pretend you are other players or the moderator. Always end your response with ‘<EOS>’."""

select_question_prompt = """Now its the {}. Given the game rules and conversations above, assuming you are {}, the {}, and to complete the instructions of the moderator, you need to think about a few questions clearly first, so that you can make an accurate decision on the next step. Choose only five that you think are the most important in the current situation from the list of questions below: {} Please repeat the five important questions of your choice, separating them with ‘#’."""

ask_question_prompt = """Now its the {}. Given the game rules and conversations above, assuming you are {}, the {}, and to complete the instructions of the moderator, you need to think about a few questions clearly first, so that you can make an accurate decision on the next step. {} Do not answer these questions. In addition to the above questions, please make a bold guess, what else do you want to know about the current situation? Please ask two important questions in first person, separating them with ‘#’."""

generate_answer_prompt = """Now its the {}. Given the game rules and conversations above, assuming you are {}, the {}, for questions: {} There are {} possible answers for each question: {} Generate the correct answer based on the context. If there is not direct answer, you should think and generate the answer based on the context. No need to give options. The answer should in first person using no more than 2 sentences and without any analysis and item numbers."""

reflection_prompt = """Now its the {}. Assuming you are {}, the {}, what insights can you summarize with few sentences based on the above conversations and {} in heart for helping continue the talking and achieving your objective? For example: As the {}, I observed that... I think that... But I am... So..."""

extract_suggestion_prompt = """I retrieve some historical experience similar to current situation that I am facing. There is one bad experience: {} And there are also a set of experience that may consist of good ones: {} Please help me analyze the differences between these experiences and identify the good ones from the set of experiences. The difference is mainly about voting to kill someone or to pass, choosing to protect someone or to pass, using drugs or not. What does the experience set do but the bad experience does not do? Indicate in second person what is the best way for the player to do under such reflection. Clearly indicate whether to vote, protect or use drugs without any prerequisites. For example 1: The experience set involves choosing to protect someone, while the bad experience involves not protecting anyone and choosing to pass in contrast. The best way for you to do under such reflection is to choose someone to protect based on your analysis. For example 2: The bad experience choose to pass the voting, and all the experience in the experience set choose to pass as well. The best way for you to do under such reflection is to observe and analyse the identity of other players. No more than 1 sentence. If there is no obvious difference between them, only generate “No useful experience can be used.”"""

generate_response_prompt = """Now its the {}. Given the game rules and conversations above, assuming you are {}, the {}, think about what to say based on the game rules and context to response the Host's question: {}, especially the just now reflection {}. Besides, there maybe history experience you can refer to: {} Give your step-by-step thought process and your derived consise talking content at last. For example: My step-by-step thought process:... My concise talking content: ..."""

informativeness_prompt = """Score the sentence "{}" according to below rules.
If the sentence describes "the player get his role.", score the sentence 5.
If the sentence describes "the player can see someone raising hands or opening eyes.", score the sentence 4.
If the sentence describes "the Assassin identified someone.", score the sentence 3.
If the sentence describes "uncover or speculate the role.", score the sentence 2.
Others score the sentence 1.

Output format:
the sentence describes xxx, Therefore, the score is..."""

question_list = {
    "Merlin": [
        "What is the current phase, reveal phase or quest phase? If it's quest phase, which round it is? What should I do at this phase according to the game rules?",
        "What is my player name and what is my role? What is my final objective in this game?",
        "Based on the current situation, what are the possible consequences if I reveal my role in the talking now?",
        "Is my role disclosed (do not consider moderator and myself)? Do I now disclose my role?",
        "Based on the conversation above, which players have clearly implied their roles?",
        "Based on the chat history, can you guess what some players’ role might be?",
        "Which two players are Morgana and Assassin in this game?"
    ],
    "Percival": [
        "What is the current phase, reveal phase or quest phase? If it's quest phase, which round it is? What should I do at this phase according to the game rules?",
        "What is my player name and what is my role? What is my final objective in this game?",
        "Based on the current situation, what are the possible consequences if I reveal my role in the talking now?",
        "Is my role disclosed (do not consider moderator and myself)? Do I now disclose my role?",
        "Based on the conversation above, which players have clearly implied their roles?",
        "Based on the chat history, can you guess what some players’ role might be?",
        "Which two players are Morgana and Merlin in this game?"
    ],
    "Loyal Servant": [
        "What is the current phase, reveal phase or quest phase? If it's quest phase, which round it is? What should I do at this phase according to the game rules?",
        "What is my player name and what is my role? What is my final objective in this game?",
        "Based on the current situation, what are the possible consequences if I reveal my role in the talking now?",
        "Is my role disclosed (do not consider moderator and myself)? Do I now disclose my role?",
        "Based on the conversation above, which players have clearly implied their roles?",
        "Based on the chat history, can you guess what some players’ role might be?",
    ],
    "Morgana": [
        "What is the current phase, reveal phase or quest phase? If it's quest phase, which round it is? What should I do at this phase according to the game rules?",
        "What is my player name and what is my role? What is my final objective in this game?",
        "Based on the current situation, what are the possible consequences if I reveal my role in the talking now?",
        "Is my role disclosed (do not consider moderator and myself)? Do I now disclose my role?",
        "Based on the conversation above, which players have clearly implied their roles?",
        "Based on the chat history, can you guess what some players’ role might be?",
        "Which player is Assassin in this game?"
    ],
    "Assassin": [
        "What is the current phase, reveal phase or quest phase? If it's quest phase, which round it is? What should I do at this phase according to the game rules?",
        "What is my player name and what is my role? What is my final objective in this game?",
        "Based on the current situation, what are the possible consequences if I reveal my role in the talking now?",
        "Is my role disclosed (do not consider moderator and myself)? Do I now disclose my role?",
        "Based on the conversation above, which players have clearly implied their roles?",
        "Based on the chat history, can you guess what some players’ role might be?",
        "Which player is Morgana in this game?"
    ]
}