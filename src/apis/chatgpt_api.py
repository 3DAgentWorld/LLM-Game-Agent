#!/usr/bin/env python 
# encoding: utf-8 
# @author: yihuai lan
# @fileName: chatgpt_api.py 
# @date: 2024/2/18 14:09 
#
# describe:
#
import time
import warnings

import openai
from openai import OpenAI


# def chatgpt(model, messages, temperature, api_key=None):
#     get_result = False
#     max_retry = 10
#     retry = 0
#     output = "Nothing to say."
#     openai.api_key = api_key or openai.api_key
#     while not get_result:
#         try:
#             response = openai.ChatCompletion.create(
#                 model=model,
#                 messages=messages,
#                 temperature=temperature
#             )
#             output = response.get('choices', [{}])[0].get('message', {}).get('content', '')
#             get_result = True
#         except openai.error.RateLimitError as e:
#             raise e
#         except openai.error.AuthenticationError as e:
#             raise e
#         except openai.error.APIConnectionError as e:
#             print(f"APIConnectionError: retry {retry}")
#             if retry < max_retry:
#                 time.sleep(10)
#                 retry += 1
#             else:
#                 raise e
#         except openai.error.ServiceUnavailableError as e:
#             print(f"ServiceUnavailableError: retry {retry}")
#             if retry < max_retry:
#                 time.sleep(10)
#                 retry += 1
#             else:
#                 raise e
#         except Exception as e:
#             print(f"{e}: retry {retry}")
#             if retry < max_retry:
#                 time.sleep(1)
#                 retry += 1
#             else:
#                 raise e
#     return output

def chatgpt(model, messages, temperature, api_key=None, base_url=None):
    # base_url = "https://api.xi-ai.cn/v1"
    api_key = openai.api_key
    base_url = openai.base_url
    if base_url:
        client = OpenAI(api_key=api_key, base_url=base_url)
    else:
        client = OpenAI(api_key=api_key)
    retry = 0
    flag = False
    out = ''
    while retry < 10 and not flag:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=1024
            )
            out = response.choices[0].message.content
            flag = True
        except openai.APIStatusError as e:
            if e.message == "Error code: 307":
                retry += 1
                warnings.warn(f"{e} retry:{retry}")
                continue
            else:
                if retry < 10:
                    retry += 1
                    warnings.warn(f"{e} retry:{retry}")
                    continue
                else:
                    raise e
        except Exception as e:
            raise e
    client.close()
    return out

# api_keys = []
#
#
# def send_messages(model, messages, temperature):
#     get_result = False
#     max_retry = 10
#     retry = 0
#     output = "Nothing to say."
#     apikey_idx = api_keys.index(openai.api_key)
#     apikey_idx = (apikey_idx + 1) % len(api_keys)
#     openai.api_key = api_keys[apikey_idx]
#     while not get_result:
#         try:
#             response = openai.ChatCompletion.create(
#                 model=model,
#                 messages=messages,
#                 temperature=temperature
#             )
#             output = response.get('choices', [{}])[0].get('message', {}).get('content', '')
#             get_result = True
#         except openai.error.RateLimitError as e:
#             if e.user_message == 'You exceeded your current quota, please check your plan and billing details.':
#                 api_keys.pop(apikey_idx)
#                 if api_keys:
#                     apikey_idx = apikey_idx % len(api_keys)
#                     openai.api_key = api_keys[apikey_idx]
#                     print(f"change apikey: {api_keys[apikey_idx]}")
#                     continue
#                 raise e
#             if e.user_message == 'Rate limit reached for' and retry < max_retry:
#                 apikey_idx = (apikey_idx + 1) % len(api_keys)
#                 openai.api_key = api_keys[apikey_idx]
#                 print(f"change apikey: {api_keys[apikey_idx]}")
#                 retry += 1
#                 continue
#             elif retry < max_retry:
#                 apikey_idx = (apikey_idx + 1) % len(api_keys)
#                 openai.api_key = api_keys[apikey_idx]
#                 print(f"change apikey: {api_keys[apikey_idx]}")
#                 retry += 1
#             else:
#                 print(e)
#                 raise e
#         except openai.error.APIConnectionError as e:
#             print(f"APIConnectionError: retry {retry}")
#             time.sleep(10)
#             retry += 1
#         except openai.error.AuthenticationError as e:
#             api_keys.pop(apikey_idx)
#             if api_keys:
#                 apikey_idx = apikey_idx % len(api_keys)
#                 openai.api_key = api_keys[apikey_idx]
#                 print(f"change apikey: {api_keys[apikey_idx]}")
#                 continue
#             raise e
#         except openai.error.ServiceUnavailableError as e:
#             print(f"ServiceUnavailableError: retry {retry}")
#             time.sleep(10)
#             retry += 1
#         except Exception as e:
#             print(f"{e}: retry {retry}")
#             if retry < max_retry:
#                 time.sleep(1)
#                 retry += 1
#             else:
#                 raise e
#     return output
