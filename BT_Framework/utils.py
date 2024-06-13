# utils.py
# Alexander Leszczynski
# 13-06-2024 

from furhat_remote_api import FurhatRemoteAPI
import keyboard
import time


def format_conversation(conversation):
        """
        This function formats the conversation to be used in the LLM call.
        """
        # The format should be User: <user_input> Assistant: <assistant_response> User: <user_input> ...
        formatted_conversation = ""
        for i, message in enumerate(conversation):
            if i % 2 == 0:
                formatted_conversation += f"User: {message['content']}\n"
            else:
                formatted_conversation += f"Assistant: {message['content']}\n"
        return formatted_conversation

def initialize_furhat(ip_address, voice_name):
    """
    This function initializes the Furhat robot with the given IP address and voice name.
    """
    
    furhat = FurhatRemoteAPI(ip_address)
    furhat.set_face(mask="adult", character = "Isabel")
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
                print(listened.message)
                total_listened += listened.message + " "

            elif keyboard.is_pressed('enter'):
                print('You Pressed Enter!')
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