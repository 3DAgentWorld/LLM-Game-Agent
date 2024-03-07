#!/usr/bin/env python 
# encoding: utf-8 
# @author: yihuai lan
# @fileName: abs_agent.py 
# @date: 2024/2/18 14:04 
#
# describe:
#

from abc import abstractmethod


class Agent:
    name = None
    role = None

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.role = kwargs.get('role')

    @abstractmethod
    def step(self, message: str) -> str:
        """
        interact with the agent.
        :param message: input to the agent
        :return: response of the agent
        """
        pass

    @abstractmethod
    def receive(self, name: str, message: str) -> None:
        """
        receive the message from other agents.
        :param name: name of the agent which send the message
        :param message: content of the agent receives.
        :return:
        """
        pass

    @classmethod
    def init_instance(cls, **kwargs):
        return cls(**kwargs)
