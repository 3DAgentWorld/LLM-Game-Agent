#!/usr/bin/env python 
# encoding: utf-8 
# @author: yihuai lan
# @fileName: abs_extractor.py 
# @date: 2024/2/29 10:26 
#
# describe:
#
from abc import abstractmethod, ABC


class Extractor(ABC):
    extractor_name = None
    log_file = None

    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def extract(self, message: str) -> str:
        """
        :param message:
        :return:
        """
        pass

    def log(self, input_: str, output: str):
        """

        :param input_:
        :param output:
        :return:
        """
        if self.log_file:
            log_str = (f"{self.extractor_name}\n{'-' * 20 + 'input' + '-' * 20}\n{input_}\n"
                       f"{'-' * 20 + 'output' + '-' * 20}\n{output}\n")

            with open(self.log_file, 'a+', encoding='utf-8') as f:
                f.write(log_str)
                f.close()
        return

    @classmethod
    def init_instance(cls, **kwargs):
        return cls(**kwargs)
