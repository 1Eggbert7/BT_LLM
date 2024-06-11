from furhat_remote_api import FurhatRemoteAPI
import time
from openai import OpenAI
import keyboard  # using module keyboard

client = OpenAI()

# Create an instance of the FurhatRemoteAPI class, providing the address of the robot or the SDK running the virtual robot
furhat = FurhatRemoteAPI("192.168.0.196")

# Get the voices on the robot
voices = furhat.get_voices()

# Set the voice of the robot
voice_name = 'Rachel22k_CO'
furhat.set_voice(name=voice_name)


def listen():
    return furhat.listen()

def record_speech():
    total_listened = ""
    print("Press 'space' to start/continue recording, 'esc' to stop.")

    while True:  # making a loop
        try:  # used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('space'):
                listened = listen()
                print(listened.message)
                total_listened += listened.message + " "

            elif keyboard.is_pressed('enter'):
                print('You Pressed Enter!')
                break
        except:
            break  # if user pressed a key other than the given key the loop will break

    return total_listened


# Example usage:
recorded_text = record_speech()
print("Total listened: ", recorded_text)

# Get the users detected by the robot 
users = furhat.get_users()
#print(users)

# Attend the user closest to the robot
furhat.attend(user="CLOSEST")
#print("Attending to user closest to the robot")