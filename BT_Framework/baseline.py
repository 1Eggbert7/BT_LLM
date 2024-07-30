# baseline.py
# Alexander Leszczynski
# 30-07-2024

from prompts import BASELINE_PROMPT
from config import FURHAT, LLM
from utils import record_speech
import state
import keyboard
from openai import OpenAI

def run_baseline():
    global conversation
    client = OpenAI()

    conversation = {"role": "user", "content": BASELINE_PROMPT}
    print("You can start chatting with the model now. Press 'esc' to end the conversation.")
    while True:
        if not LLM: 
            print("LLM is not enabled.")
            break
        if FURHAT:
            user_input = record_speech(state.var_furhat)
            conversation.append({"role": "user", "content": user_input})
        else:
            user_input = input("User: ")
            conversation.append({"role": "user", "content": user_input})

        if user_input == "esc": #  not sure if this will work because its just a small window where the user can type 
            break

        completion = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = conversation
        )
        model_response = completion.choices[0].message.content
        response_contains_json = check_json(model_response)
        conversation.append({"role": "assistant", "content": model_response})
        if response_contains_json:
            print("response contains json detected!!!")
            print("Assistant: ", "Alright I will create that sequence for you.")
            break
        response_reached_end = check_end(model_response)
        if response_reached_end:
            print("response reached end detected!!!")
            print("Assistant: ", model_response)
            break
        print("Assistant: ", model_response)
        
def check_json(response):
    # check if the response contains '{' and '}' to determine if it is a JSON response
    return "{" in response and "}" in response

def check_end(response):
    # check if the response contains "Ok, I will now proceed with the sequence" in lowercase
    return "ok, i will now proceed with the sequence" in response.lower()