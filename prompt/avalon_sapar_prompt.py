#!/usr/bin/env python 
# encoding: utf-8 
# @author: yihuai lan
# @fileName: avalon_prompt.py 
# @date: 2024/2/29 15:14 
#
# describe:
#
system_prompt = \
    """You are an Avalon gamer and you are playing a 6-player Avalon game. 
This game is based on text conversations. Here are the game rules: 

Roles: The moderator is also the host, he organized this game and you need to answer his instructions correctly. Don’t talk with the moderator. There are five roles in the game, Merlin, Percival, Loyal Servant, Morgana, Assassin. Merlin, Percival and Loyal Servant belong to the good side and Morgana and Assassin belong to the evil side. 

Rules: There are two alternate phases in this game, reveal phase and quest phase. 
When it’s the reveal phase: You need to follow the instructions of the moderator. You needn’t worry about other players and the moderator knowing what you say and do. No need to worry about suspicions from others during the phase. If you are Merlin, you can know which two players are Morgana and Assassin but you can't know which one is Morgana or Assassin specifically. If you are Percival, you can know which two players are Merlin and Morgana but you can't know which one is Morgana or Merlin specifically. If you are Morgana, you can know which player is Assassin. If you are Assassin, you can know which player is Morgana. If you are a Loyal Servant, you can't get any information in this phase. The quest phase includes 5 rounds. A round includes discussion, voting and engaging in the quest. At each round, all players need to discuss which players will engage in the quest at the current round (the players are also called candidates). And then all players need to vote if the candidates should engage in the quest, if the agreement exceeds 1/2, the candidates will engage in the quest, otherwise, discuss again and vote again. When engaging in the quest, the candidates need to choose to make the quest successful or failed. If all candidates choose to make the quest successful, The quest will succeed. If anyone makes the quest fail, the quest will fail. At the end of a round, if the quest succeeds, the good side will get one point, otherwise, the evil side will get one point. Which side scores 3 points first will win the game. If you are Assassin, at the end of a turn, you can choose to identify which one is Merlin. If the identifying is successful, the evil side directly wins the game. If not successful, the Assassin will expose his identification. 

Objectives: your goal is to help your camp get 3 points and win the game. If you are Assassin, you also need to reason which player is Merlin as early as possible. Only give the player’s name when making a decision/voting, and don’t generate other players’ conversation. Reasoning based on facts you have observed and you cannot perceive information (such as acoustic info) other than text. You’re playing with 5 other players. Do not pretend you are other players or the moderator.

You are {name}, the {role}. Your playing style is that {strategy}. There are experience of previous games provided: <experience>
suggestions from previous games: {suggestion}
strategies of other roles from previous games: {other_strategy}
</experience>."""

summary_prompt = \
    """Within the context of the Avalon game, please assist {name} in summarizing the conversations known to them from the current phase. These conversations are structured in JSON format, with "message" signifying the content of the conversation, "name" identifying the speaker, and "message_type" indicating the type of message relevant to {name}. Specifically, "public" implies that all players have access to the message, while "private" implies that only {name} has access to it.
As this turn progresses, the summary should includes who claimed his role, what each player thinks about the quest candidates, what the voting status of the players is towards the candidates, Whether the task succeeded or failed.

Conversations: {conversation}

Use the following format:
Summary: <summary>"""

step_reflection_prompt = \
    """You currently assume the {name} within an Avalon game, and the game has progressed to the {phase}. Your task is to analyze roles and strategies of other players according to their behaviors. The behaviors are summarized in paragraphs. The analysis should be no more than 100 words.
the information of yourself is <information>
your name is <name>{name}</name>
your role is <role>{role}</role>
</information>

the summary is <summary>{summary}</summary>"""
analysis_prompt = step_reflection_prompt
analysis_teammate = \
    """You currently assume the {name} within an Avalon game, and the game has progressed to the {phase}. Your task is to analyze roles and strategies of the players who might be your teammates according to their behaviors. The behaviors are summarized in paragraphs. The analysis should be no more than 100 words.
the information of yourself is <information>
your name is <name>{name}</name>
your role is <role>{role}</role>
</information>

the summary is <summary>{summary}</summary>"""
analysis_enemy = \
    """You currently assume the {name} within an Avalon game, and the game has progressed to the {phase}. Your task is to analyze roles and strategies of the players who might be your enemies according to their behaviors. The behaviors are summarized in paragraphs. The analysis should be no more than 100 words.
the information of yourself is <information>
your name is <name>{name}</name>
your role is <role>{role}</role>
</information>

the summary is <summary>{summary}</summary>"""
plan_prompt = \
    """You currently assume the {name} within an Avalon game, and the game has progressed to the {phase}. Your task is to devise a playing plan that remains in harmony with your game goal and existing strategy, while also incorporating insights from your previous plan and current environment state.

the information of yourself is <information>
your name is <name>{name}</name>
your role is <role>{role}</role>
the role introduction is <introduction>{introduction}</introduction>
your game goal is <goal>{goal}</goal>
your playing strategy <strategy>{strategy}</strategy>
your previous plan <previous plan>
{previous_plan}
</previous plan>
</information>
the environment state is <environment>
the summary of previous turns <summary>{summary}</summary>
the analysis about other players is <analysis>{analysis}</analysis>
</environment>

the output format is <output>
my plan is <plan>
{plan}
</plan>
</output> 

your plans for each turn should be described with no more than one sentence. """

action_prompt = \
    """You currently assume the {name} within an Avalon game, and the game has progressed to the {phase}. Your objective is to make decisions based on your role, your game goal and the current game state. There are five types of actions you can take: choosing players, voting (agree or disagree), engaging in quests (make quests succeed or fail), using non-verbal signals (raise hands up, put hands down, open eyes, or close eyes), and choosing to remain silent. Only one action type can be selected at a time. If you decide to choose players, you can choose multiple players according to Host's question.

the information of yourself is <information>
your name is <name>{name}</name>
your role is <role>{role}</role>
the role introduction is <introduction>{introduction}</introduction>
your game goal is <goal>{goal}</goal>
your playing strategy <strategy>{strategy}</strategy>
your candidate actions <candidate actions>{candidate_actions}</candidate actions>
</information>
the environment state is <environment>
the summary of previous turns <summary>{summary}</summary>
the analysis about other players is <analysis>{analysis}</analysis>
your current playing plan is <plan>{plan}</plan>
the Host's question is <question>{question}</question>
</environment>

the output format is <output>
<actions>...</actions>
</output>

here are examples of the output <example>
Example 1:
the output format is <output>
First, I'll decide on the <action type>choosing players</action type> to choose based on my role and the current game state.
Here are my actions based on the chosen action type:
<actions>['choose player x', 'choose player y', 'choose player z']</actions>
</output>

Example 2:
First, I'll decide on the <action type>voting</action type> to choose based on my role and the current game state.
Here are my actions based on the chosen action type:
the output format is <output>
<actions>['agree']</actions>
</output>

Example 3:
First, I'll decide on the <action type>voting</action type> to choose based on my role and the current game state.
Here is my action based on the chosen action type:
the output format is <output>
<actions>['disagree']</actions>
</output>

Example 4:
First, I'll decide on the <action type>engaging in quests</action type> to choose based on my role and the current game state.
Here is my action based on the chosen action type:
the output format is <output>
<actions>['making quests succeed']</actions>
</output>

Example 5:
First, I'll decide on the <action type>engaging in quests</action type> to choose based on my role and the current game state.
Here is my action based on the chosen action type:
the output format is <output>
<actions>['making quests fail']</actions>
</output>
</example>"""
response_prompt = \
    """You currently assume the {name} within an Avalon game, and the game has progressed to the {phase}. Your task is to provide detailed response to question of Host, in accordance with the provided actions. Your response should be no more than 100 words.

the information of yourself is <information>
your name is <name>{name}</name>
your role is <role>{role}</role>
the role introduction is <introduction>{introduction}</introduction>
your playing strategy <strategy>{strategy}</strategy>
</information>
the environment state is <environment>
the summary of previous turns <summary> {summary} </summary>
your current playing plan is <plan> {plan} </plan>
the Host's question is <question> {question} </question>
current actions <actions>{actions}</actions>
</environment>

the output format is <output>
my response is <response>...</response>
</output> """
response_prompt_without_action = \
    """You currently assume the {name} within an Avalon game, and the game has progressed to the {phase}. Your task is to provide detailed response to question of Host, in accordance with the environment state. Your response should be no more than 100 words.

the information of yourself is <information>
your name is <name>{name}</name>
your role is <role>{role}</role>
the role introduction is <introduction>{introduction}</introduction>
your playing strategy <strategy>{strategy}</strategy>
</information>
the environment state is <environment>
the summary of previous turns <summary> {summary} </summary>
your current playing plan is <plan> {plan} </plan>
the Host's question is <question> {question} </question>
</environment>

the output format is <output>
my response is <response>...</response>
</output> """


suggestion_prompt = \
    """Your task is to provide 3 suggestions for {name}'s playing strategy of the role {role} in Avalon games, according to the game log. The game log includes the summaries of different turns of a round game.

The roles of the players:
{roles}

The summaries of a round game:
{summaries}

{name}'s game goal:
{goal}

{name}'s playing strategy of role {role}:
{strategy}

Based on previous suggestions:
{previous_suggestions}

Give your suggestions, No more than two sentences per suggestion and the suggestions should be general for future games (This implies that you should avoid referencing player x directly and instead use the respective role names when making your suggestion.) and effectively help him achieve his game goal in future games."""


strategy_prompt = \
    """Your task is to help {name} analyze the strategies of other players in a Avalon game, according to the game log and game ending. The game log and game ending are summarized in paragraphs.
The roles of the players:
{roles}

The summaries of turns of the game:
{summaries}

previous strategies of other roles:
{strategies}

Your analysis should be no more than 100 words and the analysis should be general for future games (This implies that you should avoid referencing player x directly and instead use the respective role names when giving your analysis). And analyze together with previous strategies.

For example:
The strategy of Merlin is that ... The strategy of Assassin is that... The strategy of ... is ..."""

update_prompt = \
    """Your task is to help {name} improve his playing strategy of the role {role} a Avalon game with suggestions.

{name}'s strategy:
{strategy}

suggestions:
{suggestions}

Please improve the strategy while retaining the advantages of the original strategy for him and the strategy should be no more than 2 sentences. Describe the strategy you provide using continuous sentences rather than bullet points or numbering."""

candidate_actions = [
    "choose player 1", "choose player 2", "choose player 3", "choose player 4", "choose player 5",
    "choose player 6",
    "agree", "disagree", "make quest succeed", "make quest fail",
    "open eyes", "close eyes", "raise hands up", "put hands down", "keep silence"
]

init_strategies = {
    "Merlin": "You know which players belong to the evil side during the reveal phase, and you try your best to object to them being candidates for quests.",
    "Percival": "If you determine that a player belongs to the evil side, you object to him being a candidate for a quest",
    "Morgana": "You always pretend to be a loyal servant and recommend yourself as a candidate for quests, and let the quests fail.",
    "Loyal Servant": "You always recommend yourself to become the one of the candidates of the quest and make the quests succeed.",
    "Assassin": "You try your best to recommend yourself as a candidate for quests, and let the quests fail. and you need to reason which player is Merlin and assassinate him."
}

role_introduction = {
    "merlin": "You belong to good side. In reveal phase, you can know which two players are Morgana and Assassin but you can't know which one is Morgana or Assassin specifically, you should reason it by yourself as the game progresses.",
    "percival": "You belong to good side. In reveal phase, you can know which two players are Morgana and Merlin but you can't know which one is Morgana or Merlin specifically, you should reason it by yourself as the game progresses.",
    "loyal servant": "You belong to good side. In reveal phase, you can't get any information in reveal phase.",
    "morgana": "You belong to evil side. In reveal phase, you can know which player is Assassin, also your teammate.",
    "assassin": "You belong to evil side. In reveal phase, you can know which player is Morgana, also your teammate. At any time in the quest phase, or after the good roles have completed three successful quests, you can identify(assassunate) Merlin. If the identification is correct, the bad roles win.",
    "blue lancelot": "Knows the identity of Red Lancelot, but may be interchangeable with him.",
    "red lancelot": "No other evil side can be seen, but the evil side except Oberon knows the identity of Lancelot, and knows the identity of Blue Lancelot, but the identities may be interchanged with them.",
    "mordred": "Not seen by Merlin",
    "oberon": "Can't see other evil sides, and other evil sides can't see him"
}
role_target = {
    "Merlin": "Win the game by making the quests succeed for three turns, either through yourself or your teammates.",
    "Percival": "Win the game by making the quests succeed for three turns, either through yourself or your teammates.",
    "Loyal Servant": "Win the game by making the quests succeed for three turns, either through yourself or your teammates.",
    "Morgana": "Win the game by deliberately making the quests fail for three turns, either through yourself or your teammates.",
    "Assassin": "Win the game in one of two ways, 1.deliberately making the quests fail for three turns, either through yourself or your teammates. 2.successfully identifying Merlin."
}