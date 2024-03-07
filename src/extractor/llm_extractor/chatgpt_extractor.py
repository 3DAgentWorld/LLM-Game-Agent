#!/usr/bin/env python 
# encoding: utf-8 
# @author: yihuai lan
# @fileName: chatgpt_extractor.py
# @date: 2024/2/29 10:34 
#
# describe:
#
from typing import List, Tuple

from ..abs_extractor import Extractor
from ...apis.chatgpt_api import chatgpt


class ChatGPTBasedExtractor(Extractor):
    def __init__(self, extractor_name: str, model_name: str, system_prompt: str, extract_prompt: str,
                 temperature: float, few_shot_demos: List[Tuple[str, str]] = None, api_key=None, output_dir=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.extractor_name = extractor_name
        self.model = model_name
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.extract_prompt = extract_prompt
        self.few_shot_demos = few_shot_demos if few_shot_demos else []
        if output_dir:
            self.log_file = f"{output_dir}/extractor.txt"
        self.api_key = api_key

    def extract(self, message: str):
        messages = [{"role": "system", "content": self.system_prompt}]
        for demo in self.few_shot_demos:
            messages.append(demo)
            messages.append(demo)
        instruction = self.extract_prompt.format(message)
        messages.append({"role": 'user', "content": instruction})

        output = chatgpt(self.model, messages, self.temperature,self.api_key)
        self.log(instruction, output)
        return output

    def step(self, message):
        return self.extract(message)
