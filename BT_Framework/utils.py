# utils.py
# Alexander Leszczynski
# 11-06-2024 

from furhat_remote_api import FurhatRemoteAPI
import keyboard


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
    furhat = FurhatRemoteAPI(ip_address)
    furhat.set_voice(name=voice_name)
    return furhat

def listen(furhat):
    return furhat.listen()

def record_speech(furhat):
    total_listened = ""
    print("Press 'space' to start/continue recording, 'Enter' to stop.")

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