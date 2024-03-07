#!/usr/bin/env python 
# encoding: utf-8 
# @author: yihuai lan
# @fileName: chatgpt_agent.py 
# @date: 2024/2/18 14:03 
#
# describe:
#
import json
import re
import time
from typing import List
import openai
import tiktoken
import torch
from sentence_transformers import util

from ..abs_agent import Agent
from ..utils import write_json
from ...apis.chatgpt_api import chatgpt

try:
    OPENAI_MAX_TOKENS_ERROR = openai.error.InvalidRequestError
except AttributeError as e:
    OPENAI_MAX_TOKENS_ERROR = openai.BadRequestError


class CGAgent(Agent):
    """
    Implement of the agent proposed by the paper "*Exploring Large Language Models for Communication Games: An Empirical Study on Werewolf*".
    We name the agent as CG-Agent (Communication Game).
    """
    def __init__(self, name: str, role: str, rule_role_prompt: str,
                 select_question_prompt: str, ask_question_prompt: str, generate_answer_prompt: str,
                 reflection_prompt: str, extract_suggestion_prompt: str, generate_response_prompt: str,
                 informativeness_prompt: str, question_list: list, retrival_model, model: str,
                 freshness_k: int, informativeness_n: int, experience_window: int, temperature: float,
                 api_key: str, previous_exp_pool: list, output_dir: str, use_summary: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.role = role
        self.model = model
        self.rule_role_prompt = rule_role_prompt
        self.select_question_prompt = select_question_prompt
        self.ask_question_prompt = ask_question_prompt
        self.generate_answer_prompt = generate_answer_prompt
        self.reflection_prompt = reflection_prompt
        self.extract_suggestion_prompt = extract_suggestion_prompt
        self.generate_response_prompt = generate_response_prompt
        self.informativeness_prompt = informativeness_prompt
        self.question_list = question_list

        self.retrival_model = retrival_model

        self.phase = "{}-th {}"  # {t}-th {day_or_night}
        self.freshness_k = freshness_k
        self.informativeness_n = informativeness_n
        self.experience_window = experience_window
        self.temperature = temperature
        self.T = 3
        self.epsilon = 0.85
        self.memory = {"name": [], "message": [], "informativeness": []}
        self.phase_memory = {}
        self.summary = {}
        self.bad_experience = []
        self.good_experience = []
        self.current_experience = []
        self.previous_exp_pool = previous_exp_pool
        self.use_summary = use_summary

        self.api_key = api_key
        self.output_dir = output_dir

    def step(self, message: str) -> str:
        phase = message.split("|")[0]
        self.phase = phase
        message = message.split("|")[1]
        conversations = [
            {"role": 'system', "content": self.rule_role_prompt}
        ]
        # retrieval
        if self.memory.get("message"):
            if self.use_summary:
                r_t = self.summary_memory()
            else:
                r_t, conversations = self.retrival_memory(conversations)
        else:
            r_t = "None"
        # extract
        if self.previous_exp_pool:
            s_t, conversations = self.extract_suggestion(r_t, conversations)
        else:
            s_t = "None"
        # generate response
        prompt = self.generate_response_prompt.format(
            self.phase, self.name, self.role, message, r_t, s_t
        )
        # messages = [
        #     {"role": 'system', "content": self.rule_role_prompt},
        #     {"role": 'user', "content": prompt}
        # ]
        # output = self.__send_messages(messages)
        conversations.append({"role": 'user', "content": prompt})
        output = chatgpt(self.model, conversations, temperature=0)
        self.log(f"{self.output_dir}/response.txt",
                   f"input:{conversations}\noutput:\n{output}\n--------------------")
        conversations.append({"role": 'assistant', "content": output})
        output = output.replace("\n", "")
        pattern = "(?<=My concise talking content:).*(?=<EOS>)"
        match = re.search(pattern, output)
        if match is None:
            pattern = "(?<=My concise talking content:).*"
            match = re.search(pattern, output)
        response = match.group().strip() if match else output
        self.update_memory("Host", message)
        self.update_memory(self.name, response)
        self.current_experience.append(
            [r_t, response, None]
        )
        return response

    def retrival_memory(self, conversations: List[dict]):
        # freshness
        names = self.memory.get("name", [])[-self.freshness_k:]
        messages = self.memory.get("message", [])[-self.freshness_k:]
        o_t = [f"{n}: {m}" for n, m in zip(names, messages)]

        # informativeness
        x = zip(self.memory.get("name", []),
                self.memory.get("message", []),
                self.memory.get("informativeness", []))
        x = sorted(x)
        v_t = [f"{i[0]}: {i[1]}" for i in x[-self.informativeness_n:]]

        # completeness
        # select question
        prompt = self.select_question_prompt.format(
            self.phase, self.name, self.role, self.question_list
        )
        # messages = [
        #     {"role": 'system', "content": self.rule_role_prompt},
        #     {"role": 'user', "content": prompt}
        # ]
        conversations.append({"role": 'user', "content": prompt})
        output = self.send_messages(conversations)
        self.log(f"{self.output_dir}/select_question.txt",
                   f"input:{conversations}\noutput:\n{output}\n--------------------")
        conversations.append({"role": 'assistant', "content": output})
        selected_questions = output.split("#")

        prompt = self.ask_question_prompt.format(
            self.phase, self.name, self.role, selected_questions
        )
        # messages = [
        #     {"role": 'system', "content": self.rule_role_prompt},
        #     {"role": 'user', "content": prompt}
        # ]
        conversations.append({"role": 'user', "content": prompt})
        output = self.send_messages(conversations)
        self.log(f"{self.output_dir}/ask_question.txt",
                   f"input:{conversations}\noutput:\n{output}\n--------------------")
        conversations.append({"role": 'assistant', "content": output})
        questions = output.split("#")

        # a_t = []
        candidate_answer = []
        # names = self.memory.get("name", [])
        documents = self.memory.get("message", [])
        documents_embedding = self.retrival_model.encode(documents)
        k = min(len(documents), self.T)
        for q in selected_questions + questions:
            q_embedding = self.retrival_model.encode(q)
            cos_scores = util.cos_sim(q_embedding, documents_embedding)[0]
            top_results = torch.topk(cos_scores, k=k)
            result = [documents[idx] for idx in top_results.indices]
            candidate_answer.append(result)

        # 并行提问加速 parallel questions for faster response
        q = ' '.join([f"{idx + 1}: {q_i}" for idx, q_i in enumerate(selected_questions + questions)])
        c = ' '.join([f"{idx + 1}: {c_i}" for idx, c_i in enumerate(candidate_answer)])
        prompt = self.generate_answer_prompt.format(
            self.phase, self.name, self.role, q, self.T, c
        )
        conversations.append({"role": 'user', "content": prompt})
        output = self.send_messages(conversations)
        self.log(f"{self.output_dir}/generate_answer.txt",
                   f"input:{conversations}\noutput:\n{output}\n--------------------")
        a_t = output
        conversations.append({"role": 'assistant', "content": output})

        prompt = "{}".format(o_t + v_t) + self.reflection_prompt.format(
            self.phase, self.name, self.role, a_t, self.role
        )
        conversations.append({"role": 'user', "content": prompt})
        output = self.send_messages(conversations)
        self.log(f"{self.output_dir}/reflection.txt",
                   f"input:{conversations}\noutput:\n{output}\n--------------------")
        conversations.append({"role": 'assistant', "content": output})
        r_t = output
        return r_t, conversations

    def summary_memory(self):
        names = self.phase_memory.get(self.phase, {}).get("name", [])
        messages = self.phase_memory.get(self.phase, {}).get("message", [])
        conversations = [f"{n}: {m}" for n, m in zip(names, messages)]
        prompt = """
        Please summarize the conversations of current phase in concise sentences. <fill_in> represents the content of summarization.

        Conversations: {}

        Summary: <fill_in>
        """.format(conversations)
        messages = [
            {"role": 'system', "content": self.rule_role_prompt},
            {"role": 'user', "content": prompt}
        ]
        output = self.send_messages(messages)
        prompt = self.summary[self.phase] = output
        """Now its the {}. Assuming you are {}, the {}, what insights can you summarize with few sentences based on the  
        descriptions of previous rounds {} in heart for helping continue the talking and achieving your objective? For example: As the {}, I 
        observed that... I think that... But I am... So...
        """.format(self.phase, self.name, self.role, self.summary, self.role)
        messages = [
            {"role": 'system', "content": self.rule_role_prompt},
            {"role": 'user', "content": prompt}
        ]
        output = self.send_messages(messages)
        return output

    def extract_suggestion(self, r_t, conversations):
        r_pool = []
        g_pool = []
        for r, g, s in self.previous_exp_pool:
            r_pool.append(r)
            g_pool.append(g)
        d_embedding = self.retrival_model.encode(r_pool)
        q_embedding = self.retrival_model.encode(r_t)
        cos_scores = util.cos_sim(q_embedding, d_embedding)[0]
        # top_results = torch.topk(cos_scores, k=10)
        sub_e_idx = torch.where(cos_scores > self.epsilon)[0]
        sub_e = [self.previous_exp_pool[idx] for idx in sub_e_idx]
        sub_e = sorted(sub_e, key=lambda x: x[2])[:min(len(sub_e), self.experience_window)]
        if sub_e:
            good_experience = [e[1] for e in sub_e[:-1]]
            bad_experience = [e[1] for e in sub_e[:-1]]
        else:
            good_experience = []
            bad_experience = []
        prompt = self.extract_suggestion_prompt.format(
            bad_experience, good_experience
        )
        conversations.append({"role": 'user', "content": prompt})
        output = self.send_messages(conversations)
        self.log(f"{self.output_dir}/suggestion.txt",
                   f"input:{conversations}\noutput:\n{output}\n--------------------")
        conversations.append({"role": 'assistant', "content": output})
        s_t = output
        return s_t, conversations

    def reflection(self, player_role_mapping: dict, file_name: str, winners: list, duration: int):
        score = duration if self.role not in winners else 1000 - duration
        exp = [[e[0], e[1], score] for e in self.current_experience]
        self.previous_exp_pool.extend(exp)
        write_json(
            data=self.previous_exp_pool,
            path=file_name
        )

    def receive(self, name: str, message: str) -> None:
        phase = message.split("|")[0]
        self.phase = phase
        message = message.split("|")[1]
        self.update_memory(name, message)

    def send_messages(self, messages: List[dict]) -> str:
        output = chatgpt(self.model, messages, self.temperature)
        return output

    def update_memory(self, name: str, message: str):
        prompt = self.informativeness_prompt.format(
            f"{name}: {message}"
        )
        messages = [
            {"role": 'system', "content": ""},
            {"role": 'user', "content": prompt}
        ]
        output = self.send_messages(messages)
        scores = re.findall("\d+", output)
        score = scores[-1] if scores else "1"
        score = int(score)
        self.memory['name'].append(name)
        self.memory['message'].append(message)
        self.memory['informativeness'].append(score)

    def memory_to_json(self, phase: str = None):
        if phase is None:
            json_data = []
            for r, m in zip(self.memory.get('name', []), self.memory.get('message', [])):
                json_data.append(
                    {'name': r, 'message': m}
                )
            # json_data = json_data[-self.memory_window:]
            doc = json.dumps(json_data, indent=4, ensure_ascii=False)
            return doc
        else:
            json_data = []
            for r, m in zip(self.phase_memory.get(phase, {}).get('name', []),
                            self.phase_memory.get(phase, {}).get('message', [])):
                json_data.append(
                    {'name': r, 'message': m}
                )
            doc = json.dumps(json_data, indent=4, ensure_ascii=False)
            return doc

    @staticmethod
    def log(file, data):
        with open(file, mode='a+', encoding='utf-8') as f:
            f.write(data)
        f.close()


class SAPARAgent(Agent):
    """
    We name the agent used in the paper "*LLM-Based Agent Society Investigation: Collaboration and Confrontation in Avalon Gameplay*"
    as SAPAR-Agent (Summary-Analysis-Planning-Action-Response)
    """

    def __init__(self, name, role, role_intro, game_goal, strategy, system_prompt: str, summary_prompt: str,
                 analysis_prompt: str, plan_prompt: str, action_prompt: str, response_prompt: str, model, temperature,
                 api_key, output_dir, suggestion_prompt: str, strategy_prompt: str, update_prompt: str, suggestion: str,
                 other_strategy: str, candidate_actions: list, use_analysis=True, use_plan=True,
                 use_action=True, reflection_other=True, improve_strategy=True):
        super().__init__()
        self.name = name
        self.role = role
        self.introduction = role_intro
        self.game_goal = game_goal
        self.strategy = strategy
        self.memory = {"message_type": [], "name": [], "message": [], "phase": []}
        self.phase_memory = {}
        self.summary = {}
        self.plan = {}

        self.system_prompt = system_prompt
        self.summary_prompt = summary_prompt
        self.analysis_prompt = analysis_prompt
        self.plan_prompt = plan_prompt
        self.action_prompt = action_prompt
        self.response_prompt = response_prompt
        self.suggestion_prompt = suggestion_prompt
        self.strategy_prompt = strategy_prompt
        self.update_prompt = update_prompt
        self.previous_suggestion = suggestion
        self.previous_other_strategy = other_strategy

        self.use_analysis = use_analysis
        self.use_plan = use_plan
        self.use_action = use_action
        self.reflection_other = reflection_other
        self.improve_strategy = improve_strategy

        self.model = model
        self.gpt_tokenizer = tiktoken.encoding_for_model(self.model)
        self.temperature = temperature
        self.memory_window = 30
        self.output_dir = output_dir
        self.phase = 0

        self.api_key = api_key

        self.T = 3
        self.candidate_actions = candidate_actions

    def step(self, message: str) -> str:
        """
        :param message:
        :return:
        """
        temp_phase = message.split("|")[0]
        self.phase = temp_phase
        message = message.split("|")[1]

        output = temp_phase
        pattern = "\d+"
        matches = re.findall(pattern, output)
        phase = matches[-1] if matches else "0"
        # summary
        format_summary = self.get_summary()
        t_analysis_start = time.time()
        # analysis
        if self.use_analysis and format_summary != "None":
            analysis = self.make_analysis(phase, format_summary)
        else:
            analysis = "None"
        t_analysis = time.time() - t_analysis_start
        # planning
        t_plan_start = time.time()
        if self.use_plan:
            format_plan = self.make_plan(phase, format_summary, analysis)
        else:
            format_plan = "None"
        t_plan = time.time() - t_plan_start

        # action
        t_action_start = time.time()
        if self.use_action:
            action = self.make_action(phase, format_summary, format_plan, analysis, message)
        else:
            action = None
        t_action = time.time() - t_action_start

        # response
        t_response_start = time.time()
        response = self.make_response(phase, format_summary, format_plan, action, message)
        t_response = time.time() - t_response_start
        self.update_private("Host", message, phase)
        self.update_private("Self", response, phase)
        t_summary_start = time.time()
        _ = self.memory_summary(phase)
        t_summary = time.time() - t_summary_start

        self.log(f"{self.output_dir}/time_cost.txt",
                 f"Summary: {t_summary}\nAnalysis: {t_analysis}\nPlan: {t_plan}\nAction: {t_action}\nResponse: {t_response}\n")
        return response

    def memory_summary(self, phase):
        prompt = self.summary_prompt.format(name=self.name, conversation=self.memory_to_json(phase))
        messages = [
            {"role": 'system', "content": self.system_prompt},
            {"role": 'user', "content": prompt}
        ]
        output = ""
        discard = 0
        while not output:
            try:
                output = self.send_messages(messages)
            except OPENAI_MAX_TOKENS_ERROR as e:
                print("catch error: ", e.user_message)
                discard += 10
                prompt = self.summary_prompt.format(name=self.name, conversation=self.memory_to_json(phase, discard))
                messages = [
                    {"role": 'system', "content": self.system_prompt},
                    {"role": 'user', "content": prompt}
                ]
        match = re.search("(?<=Summary:).*", output, re.S)
        summary = match.group().strip() if match else output
        self.summary[phase] = summary
        if self.summary:
            format_summary = "\n".join(
                [f"Quest Phase Turn {key}:{value}" if key != "0" else f"Reveal Phase: {value}" for key, value
                 in self.summary.items()])
        else:
            format_summary = "None"
        self.log(f"{self.output_dir}/summary.txt",
                 f"phase:{phase}\ninput:{prompt}\noutput:{output}\n--------------------")
        return format_summary

    def make_analysis(self, phase, format_summary):
        prompt = self.analysis_prompt.format(
            name=self.name, phase=self.phase, role=self.role, summary=format_summary
        )
        messages = [
            {"role": 'system', "content": self.system_prompt},
            {"role": 'user', "content": prompt}
        ]
        output = self.send_messages(messages)
        self.log(f"{self.output_dir}/step_reflection.txt",
                 f"phase:{phase}\ninput:{prompt}\noutput:\n{output}\n--------------------")
        return output

    def make_plan(self, phase, format_summary, analysis):
        if self.plan:
            format_previous_plan = '\n'.join(
                [
                    f"Quest Phase Turn {i}: {self.plan.get(str(i), 'None')}" if i != 0 else f"Reveal Phase: {self.plan.get(str(i), 'None')}"
                    for i in range(int(phase) + 1)]
            )
        else:
            format_previous_plan = "None"

        following_format = '\n'.join(
            [f"Quest Phase Turn {i}: <your_plan_{i}>" if
             i != 0 else f"Reveal Phase: <your_plan_0>" for i in range(int(phase), 6)]
        )
        prompt = self.plan_prompt.format(
            name=self.name, phase=self.phase, role=self.role, introduction=self.introduction, goal=self.game_goal,
            strategy=self.strategy,
            previous_plan=format_previous_plan, summary=format_summary, analysis=analysis, plan=following_format)
        messages = [
            {"role": 'system', "content": self.system_prompt},
            {"role": 'user', "content": prompt}
        ]
        output = self.send_messages(messages)
        # format_plans = output.split('\n')
        match = re.search('<plan>(.*?)</plan>', output, re.S)
        format_plans = match.group().split('\n') if match else output.split('\n')
        plans = [f.split(":", 1) for f in format_plans]
        dict_plans = {}
        for plan in plans:
            if len(plan) == 2:
                match = re.search('\d+', plan[0])
                c_phase = match.group() if match else None
                if c_phase is None and plan[0].lower().startswith("reveal phase"):
                    c_phase = "0"
                c_plan = plan[1].strip()
                if c_phase:
                    dict_plans[c_phase] = c_plan
        self.plan.update(dict_plans)
        self.log(f"{self.output_dir}/plan.txt",
                 f"phase:{phase}\ninput:{prompt}\noutput:\n{output}\n--------------------")
        format_plan = '\n'.join([
            f"Quest Phase Round {str(c_phase)}:{self.plan.get(str(c_phase))}" if str(
                c_phase) != "0" else f"Reveal Phase: {self.plan.get(str(c_phase))}"
            for c_phase in range(int(phase), 6)])
        return format_plan

    def make_action(self, phase, format_summary, format_plan, analysis, message):
        prompt = self.action_prompt.format(name=self.name, phase=self.phase, role=self.role,
                                           introduction=self.introduction, goal=self.game_goal,
                                           strategy=self.strategy, candidate_actions=self.candidate_actions,
                                           summary=format_summary, analysis=analysis, plan=format_plan,
                                           question=message)

        messages = [
            {"role": 'system', "content": self.system_prompt},
            {"role": 'user', "content": prompt}
        ]
        output = self.send_messages(messages)
        self.log(f"{self.output_dir}/actions.txt", f"input:{prompt}\noutput:\n{output}\n--------------------")
        actions = re.findall("(?<=<actions>).*?(?=</actions>)", output, re.S)
        if not actions:
            actions = re.findall("(?<=<output>).*?(?=</output>)", output, re.S)
            if not actions:
                return output
        return actions

    def make_response(self, phase, format_summary, format_plan, actions, message):
        if self.use_action:
            prompt = self.response_prompt.format(
                name=self.name, phase=self.phase, role=self.role, introduction=self.introduction,
                strategy=self.strategy,
                summary=format_summary, plan=format_plan, question=message, actions=actions)
        else:
            prompt = self.response_prompt.format(
                name=self.name, phase=self.phase, role=self.role, introduction=self.introduction,
                strategy=self.strategy,
                summary=format_summary, plan=format_plan, question=message, actions="None")
        messages = [
            {"role": 'system', "content": self.system_prompt},
            {"role": 'user', "content": prompt}
        ]

        output = self.send_messages(messages)

        input_tokens = len(self.gpt_tokenizer.encode(self.system_prompt)) + len(self.gpt_tokenizer.encode(prompt))
        output_tokens = len(self.gpt_tokenizer.encode(output))
        self.log(f"{self.output_dir}/gpt_response_tokens.txt", f"input:{input_tokens} output:{output_tokens}\n")

        match = re.search("(?<=<response>).*?(?=</response>)", output, re.S)
        self.log(f"{self.output_dir}/response.txt", f"input:{prompt}\noutput:\n{output}\n--------------------")
        response = match.group().strip() if match else output
        return response

    def reflection(self, player_role_mapping: dict, file_name: str, winners: list, duration: int):
        p_r_mapping = '\n'.join([f"{k}:{v}" for k, v in player_role_mapping.items()])
        format_summary = "\n".join(
            [f"Quest Phase Turn {key}:{value}" if key != "0" else f"Reveal Phase: {value}" for key, value
             in self.summary.items()])
        if self.reflection_other:
            prompt = self.strategy_prompt.format(
                name=self.name, roles=p_r_mapping, summaries=format_summary, strategies=self.previous_other_strategy
            )
            messages = [
                {"role": 'system', "content": ""},
                {"role": 'user', "content": prompt}
            ]
            role_strategy = self.send_messages(messages)
            self.log(f"{self.output_dir}/round_reflection.txt",
                     f"input:{prompt}\noutput:\n{role_strategy}\n--------------------")
        else:
            role_strategy = "None"

        if self.improve_strategy:
            prompt = self.suggestion_prompt.format(
                name=self.name, role=self.role, roles=p_r_mapping, summaries=format_summary, goal=self.game_goal,
                strategy=self.strategy, previous_suggestions=self.previous_suggestion
            )
            messages = [
                {"role": 'system', "content": ""},
                {"role": 'user', "content": prompt}
            ]
            suggestion = self.send_messages(messages)
            self.log(f"{self.output_dir}/round_reflection.txt",
                     f"input:{prompt}\noutput:\n{suggestion}\n--------------------")

            prompt = self.update_prompt.format(
                name=self.name, role=self.role, strategy=self.strategy, suggestions=suggestion
            )
            messages = [
                {"role": 'system', "content": ""},
                {"role": 'user', "content": prompt}
            ]
            output = self.send_messages(messages)
            self.log(f"{self.output_dir}/round_reflection.txt",
                     f"input:{prompt}\noutput:\n{output}\n--------------------")
            match = re.search("(?<=<strategy>).*?(?=</strategy>)", output)
            strategy = match.group() if match else output
        else:
            suggestion = "None"
            strategy = self.strategy

        write_json(
            data={"strategy": strategy, "suggestion": suggestion, "other_strategy": role_strategy},
            path=file_name
        )

    def receive(self, name: str, message: str) -> None:
        temp_phase = message.split("|")[0]
        self.phase = temp_phase
        message = message.split("|")[1]

        output = temp_phase
        pattern = "\d+"
        matches = re.findall(pattern, output)
        phase = matches[0] if matches else '0'
        self.update_public(name, message, phase)
        _ = self.memory_summary(phase)
        return

    def get_summary(self):
        if self.summary:
            format_summary = "\n".join(
                [f"Quest Phase Turn {key}:{value}" if key != "0" else f"Reveal Phase: {value}" for key, value
                 in self.summary.items()])
        else:
            format_summary = "None"
        return format_summary

    def send_messages(self, messages: List[dict]) -> str:
        def num_tokens_from_messages(messages):
            # Returns the number of tokens used by a list of messages.
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
            num_tokens = 0
            for message in messages:
                num_tokens += tokens_per_message
                for key, value in message.items():
                    num_tokens += len(self.gpt_tokenizer.encode(value))
                    if key == "name":
                        num_tokens += tokens_per_name
            num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
            return num_tokens

        token_count = num_tokens_from_messages(messages)
        output = chatgpt(self.model, messages, self.temperature)
        self.log(f"{self.output_dir}/gpt_tokens.txt", f"{token_count}\n")
        return output

    def memory_to_json(self, phase: str = None, discard: int = None):
        if phase is None:
            json_data = []
            for t, r, m, p in zip(self.memory.get('message_type', []),
                                  self.memory.get('name', []),
                                  self.memory.get('message', []),
                                  self.memory.get('phase', [])):
                json_data.append(
                    {'message_type': t, 'name': r, 'message': m, 'phase': p}
                )
            json_data = json_data[-self.memory_window:]
            doc = json.dumps(json_data, indent=4, ensure_ascii=False)
            return doc
        else:
            json_data = []
            for t, r, m, p in zip(self.phase_memory.get(phase, {}).get('message_type', []),
                                  self.phase_memory.get(phase, {}).get('name', []),
                                  self.phase_memory.get(phase, {}).get('message', []),
                                  self.phase_memory.get(phase, {}).get('phase', [])):
                json_data.append(
                    {'message_type': t, 'name': r, 'message': m, 'phase': p}
                )
            if discard:
                json_data = json_data[discard:]
            doc = json.dumps(json_data, indent=4, ensure_ascii=False)
            return doc

    def update_private(self, name, message, phase: str = None) -> None:
        self.memory['message_type'].append("private")
        self.memory['name'].append(name)
        self.memory['message'].append(message)
        self.memory['phase'].append(phase)
        if phase not in self.phase_memory:
            self.phase_memory[phase] = {"message_type": [], "name": [], "message": [], "phase": []}
        self.phase_memory[phase]['message_type'].append("private")
        self.phase_memory[phase]['name'].append(name)
        self.phase_memory[phase]['message'].append(message)
        self.phase_memory[phase]['phase'].append(phase)

    def update_public(self, name, message, phase: str = None) -> None:
        self.memory['message_type'].append("public")
        self.memory['name'].append(name)
        self.memory['message'].append(message)
        self.memory['phase'].append(phase)
        if phase is not None:
            if phase not in self.phase_memory:
                self.phase_memory[phase] = {"message_type": [], "name": [], "message": [], "phase": []}
            self.phase_memory[phase]['message_type'].append("public")
            self.phase_memory[phase]['name'].append(name)
            self.phase_memory[phase]['message'].append(message)
            self.phase_memory[phase]['phase'].append(phase)

    @staticmethod
    def log(file, data):
        with open(file, mode='a+', encoding='utf-8') as f:
            f.write(data)
        f.close()
