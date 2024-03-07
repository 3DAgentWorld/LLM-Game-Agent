#!/usr/bin/env python 
# encoding: utf-8 
# @author: yihuai lan
# @fileName: utils.py 
# @date: 2024/2/18 14:05 
#
# describe:
#
import json
import os


def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


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
