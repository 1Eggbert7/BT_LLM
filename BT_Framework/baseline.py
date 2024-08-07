# baseline.py
# Alexander Leszczynski
# 30-07-2024

from prompts import BASELINE_PROMPT
from config import FURHAT, LLM, VERSION
from utils import record_speech, speak
import state
import keyboard
from openai import OpenAI
import time

def run_baseline():
    conversation = []
    client = OpenAI()
    #print("conversation: ", conversation)
    #print the type of conversation
    #print("type of conversation: ", type(conversation))
    if FURHAT:
        state.var_transcript = "Version: " + VERSION + "\n" + time.strftime("%c") + "\n" + "Furhat is being used with Baseline" + "\n"
        if state.var_run == 1:
            speak(state.var_furhat, "Hello I am Gregory. How can I help you today?")
        else:
            time.sleep(2)
            speak(state.var_furhat, "Let's go again... Hello. How can I help you today?")
    conversation.append({"role": "user", "content": BASELINE_PROMPT})
    print("You can start chatting with the model now. Press 'esc' to end the conversation.")
    while True:
        if not LLM: 
            print("LLM is not enabled.")
            break
        state.var_total_llm_calls += 1
        if FURHAT:
            user_input = record_speech(state.var_furhat)
            conversation.append({"role": "user", "content": user_input})
            state.var_transcript += "User: " + user_input + "\n"
        else:
            user_input = input("User: ")
            conversation.append({"role": "user", "content": user_input})
            state.var_transcript += "User: " + user_input + "\n"

        if user_input == "esc": #  not sure if this will work because its just a small window where the user can type 
            break

        completion = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = conversation
        )
        model_response = completion.choices[0].message.content
        response_contains_json = check_json(model_response)
        conversation.append({"role": "assistant", "content": model_response})
        if response_contains_json:
            print("response contains json detected!!!")
            print("Assistant: ", "Alright I will need to create a new sequence to fulfill your request. I'll get right to it.")
            #print("Assistant: ", "The sequence is: " + model_response)
            if FURHAT:
                speak(state.var_furhat, "Alright I will create that sequence for you.")
                speak(state.var_furhat, model_response)    
                state.var_transcript += "Assistant: " + "Alright I will create that sequence for you." + "\n"
                state.var_transcript += "Assistant: " + "The sequence is: " + model_response + "\n"           
            break
        response_reached_end = check_end(model_response)
        if response_reached_end:
            #print("response reached end detected!!!")
            print("Assistant: ", model_response)
            if FURHAT:
                speak(state.var_furhat, model_response)
                state.var_transcript += "Assistant: " + model_response + "\n"
            break
        print("Assistant: ", model_response)
        if FURHAT:
            speak(state.var_furhat, model_response)
            state.var_transcript += "Assistant: " + model_response + "\n"
        
def check_json(response): 
    # check if the response contains '{' and '}' to determine if it is a JSON response
    return "{" in response and "}" in response

def check_end(response):
    # check if the response contains "Ok, I will now proceed with the sequence" in lowercase
    return "ok, i will now proceed with the sequence" in response.lower() or "ok i will now proceed with the sequence" in response.lower()