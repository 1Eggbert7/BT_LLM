# utils.py
# Alexander Leszczynski
# 14-06-2024 

from furhat_remote_api import FurhatRemoteAPI
import keyboard
import time
import os
from config import BASELINE
import state


def format_conversation(conversation):
        """
        This function formats the conversation to be used in the LLM call.
        """
        # The format should be User: <user_input> Assistant: <assistant_response> User: <user_input> ...
        formatted_conversation = ""
        for i, message in enumerate(conversation):
            if i % 2 == 0:
                formatted_conversation += f"Assistant: {message['content']}\n"
            else:
                formatted_conversation += f"User: {message['content']}\n"
        return formatted_conversation

def initialize_furhat(ip_address, voice_name):
    """
    This function initializes the Furhat robot with the given IP address and voice name.
    """
    
    furhat = FurhatRemoteAPI(ip_address)
    furhat.set_face(mask="adult", character = "Titan")
    furhat.set_voice(name=voice_name)
    # attend closest user
    furhat.attend(user="CLOSEST")
    return furhat

def listen(furhat):
    """
    This function listens to the user and returns the message as a string.
    """
    return furhat.listen()

def record_speech(furhat):
    """
    This function records the speech of the user and returns it as a string.
    """
    total_listened = ""
    time.sleep(2) # else the enter key will be detected in the next loop
    print("Press 'space' to start/continue recording, 'Enter' to stop.")
    furhat.set_led(red=66, green=66, blue=66)  # Set the LED to blue to indicate recording mode

    while True:
        try:
            if keyboard.is_pressed('space'):
                furhat.set_led(red=66, green=135, blue=245)  # Set the LED to blue to indicate listening
                listened = listen(furhat)
                furhat.set_led(red=66, green=245, blue=105)  # Set the LED to green to indicate not listening anymore
                print("User: " + listened.message)
                total_listened += listened.message + " "
            
            elif keyboard.is_pressed('a'): # for again
                furhat.set_led(red=66, green=66, blue=66)  # Set the LED to gray to indicate standby mode
                furhat.say(text = "I am sorry. I did not get that. Can you please repeat?")
                #save it to the transcript
                print("Assistant: " + "I am sorry. I did not get that. Can you please repeat?")
                state.var_transcript += "Assistant: " + "I am sorry. I did not get that. Can you please repeat?" + "\n"
                time.sleep(2)
                # delete listened
                total_listened = ""

            elif keyboard.is_pressed('enter'):
                print('You Pressed Enter!')
                furhat.set_led(red=0, green=0, blue=0)  # Turn off the LED
                break
            elif keyboard.is_pressed('esc'):
                print('You Pressed Esc!')
                total_listened = "esc"
                furhat.set_led(red=0, green=0, blue=0)  # Turn off the LED
                break
        except:
            break  # if user pressed a key other than the given key the loop will break

    return total_listened

def speak(furhat, text):
    """
    This function makes the Furhat speak the given text.
    """
    furhat.say(text = text)

def save_transcript(transcript):
    """
    This function saves the transcript to a file in the 'Transkript of Conversation' folder.
    If the folder or file does not exist, it creates them.
    """
    folder_name = "Transkript of Conversation"
    file_name = "transcripts.txt"
    file_path = os.path.join(folder_name, file_name)

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Append the transcript to the file
    with open(file_path, "a") as file:
        file.write(transcript + "\n")

    print(f"Transcript saved to {file_path}")

def count_turns(formatted_conversation):
    # Split the conversation into lines
    lines = formatted_conversation.splitlines()
    
    # Initialize a counter for the turns
    turn_count = 0
    
    # Loop through the lines and count if a line starts with 'User' or 'Assistant'
    for line in lines:
        if line.startswith("User") or line.startswith("Assistant"):
            turn_count += 1
    
    return turn_count
