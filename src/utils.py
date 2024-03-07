#!/usr/bin/env python 
# encoding: utf-8 
# @author: yihuai lan
# @fileName: utils.py 
# @date: 2024/2/18 13:19 
#
# describe:
#

import time
import os
import json
from colorama import Fore
import openai


def print_text_animated(text):
    # print(text)
    for char in text:
        print(char, end="", flush=True)
        time.sleep(0.02)


# COLOR = [Fore.BLUE, Fore.GREEN, Fore.YELLOW, Fore.RED, Fore.LIGHTGREEN_EX, Fore.CYAN]
COLOR = {
    "player 1": Fore.BLUE,
    "player 2": Fore.GREEN,
    "player 3": Fore.YELLOW,
    "player 4": Fore.RED,
    "player 5": Fore.LIGHTGREEN_EX,
    "player 6": Fore.CYAN,
}


def create_dir(dir_path):
    if not os.path.exists(dir_path):
        # os.mkdir(dir_path)
        os.makedirs(dir_path)


def write_data(data, path):
    f = open(path, mode='a+', encoding='utf-8')
    f.write(data)
    f.write('\n')
    f.close()


def write_json(data, path):
    f = open(path, mode='w+', encoding='utf-8')
    json.dump(data, f, indent=4, ensure_ascii=False)
    f.close()


def read_json(path):
    with open(path, mode="r", encoding="utf-8") as f:
        json_data = json.load(f)
        f.close()
    return json_data
