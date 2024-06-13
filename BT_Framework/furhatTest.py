from furhat_remote_api import FurhatRemoteAPI
import time
from openai import OpenAI
import keyboard  # using module keyboard

client = OpenAI()

# Create an instance of the FurhatRemoteAPI class, providing the address of the robot or the SDK running the virtual robot
furhat = FurhatRemoteAPI("192.168.0.196")

# get the gestures on the robot
#gestures = furhat.get_gestures()
available_gestures = """
{'duration': 0.96, 'name': 'BigSmile'}
{'duration': 0.4, 'name': 'Blink'}
{'duration': 1.0, 'name': 'BrowFrown'}
{'duration': 1.0, 'name': 'BrowRaise'}
{'duration': 0.4, 'name': 'CloseEyes'}
{'duration': 3.0, 'name': 'ExpressAnger'}
{'duration': 3.0, 'name': 'ExpressDisgust'}
{'duration': 3.0, 'name': 'ExpressFear'}
{'duration': 3.0, 'name': 'ExpressSad'}
{'duration': 3.0, 'name': 'GazeAway'}
{'duration': 1.6, 'name': 'Nod'}
{'duration': 0.96, 'name': 'Oh'}
{'duration': 0.4, 'name': 'OpenEyes'}
{'duration': 2.0, 'name': 'Roll'}
{'duration': 1.2, 'name': 'Shake'}
{'duration': 1.04, 'name': 'Smile'}
{'duration': 0.96, 'name': 'Surprise'}
{'duration': 1.6, 'name': 'Thoughtful'}
{'duration': 0.67, 'name': 'Wink'}
"""
#for gesture in gestures:
    #print(gesture)

# Set the face of the robot
furhat.set_face(mask="adult", character = "Isabel")

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
#recorded_text = record_speech()
#print("Total listened: ", recorded_text)

furhat.set_led(red = 10 , green = 100, blue = 200)
#time.sleep(5)
furhat.set_led(red = 0, green = 0, blue = 0)
#furhat.say(text = recorded_text)
# Get the users detected by the robot 
users = furhat.get_users()
#print(users)

# Attend the user closest to the robot
#furhat.attend(user="CLOSEST")
#print("Attending to user closest to the robot")
# make furhat stop attending to any user
furhat.attend(user="NONE")