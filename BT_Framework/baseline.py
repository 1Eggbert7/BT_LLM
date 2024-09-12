# baseline.py
# Alexander Leszczynski
# 29-08-2024

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
            state.var_transcript += "Assistant: " + "Hello I am Gregory. How can I help you today?" + "\n"
            state.var_turns += 1 # increment the number of turns
        else:
            time.sleep(2)
            speak(state.var_furhat, "That's it for this task. Let's go onto the next one... Hello. How can I help you today?")
            state.var_transcript += "Assistant: " + "That's it for this task. Let's go onto the next one... Hello. How can I help you today?" + "\n"
            state.var_turns += 1 # increment the number of turns
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
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
        else:
            user_input = input("User: ")
            conversation.append({"role": "user", "content": user_input})
            state.var_transcript += "User: " + user_input + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
        
        state.var_turns += 1 # increment the number of turns because the user has responded

        if user_input == "esc": #  not sure if this will work because its just a small window where the user can type 
            #if FURHAT:
                #speak(state.var_furhat, "Let's stop here for now.")
            break

        completion = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = conversation
        )
        model_response = completion.choices[0].message.content
        response_contains_json = check_json(model_response)
        conversation.append({"role": "assistant", "content": model_response})
        state.var_turns += 1 # increment the number of turns because the assistant has responded
        if response_contains_json:
            print("response contains json detected!!!")
            model_response_without_json = model_response.split("Here’s the new sequence in JSON format")[0]
            if check_json(model_response_without_json):
                print("response still contains json!!!")
                model_response_without_json = model_response_without_json.split("{")[0]
                model_response_without_json += "\nI will skip this part where I read the sequence in JSON format out to you."
            # add "I will now make the new recipe for you" to the transcript
            model_response_without_json += "\nI will now make the follow the steps to fulfill this task."
            print("Assistant: ", model_response_without_json)
            #print("Assistant: ", "The sequence is: " + model_response)
            if FURHAT:
                #speak(state.var_furhat, "Alright I will create that sequence for you.")
                speak(state.var_furhat, model_response_without_json)
                #speak(state.var_furhat, "I will actually skip this part where I read the sequence in json format out to you and we can move on to the next task.")   
                state.var_transcript += "Assistant: " + model_response + "\n"
                state.var_transcript += "Time: " + time.strftime("%c") + "\n"           
            break
        response_reached_end = check_end(model_response)
        if response_reached_end:
            #print("response reached end detected!!!")
            print("Assistant: ", model_response)
            if FURHAT:
                speak(state.var_furhat, model_response)
                state.var_transcript += "Assistant: " + model_response + "\n"
                state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            break
        print("Assistant: ", model_response)
        if FURHAT:
            speak(state.var_furhat, model_response)
            state.var_transcript += "Assistant: " + model_response + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
        
def check_json(response): 
    # check if the response contains '{' and '}' to determine if it is a JSON response
    return "{" in response and "}" in response

def check_end(response):
    # check if the response contains "Ok, I will now proceed with the sequence" in lowercase
    #print("is it end?: ", "i will start the task for" in response.lower())
    return "i will start the task for" in response.lower() 