from furhat_remote_api import FurhatRemoteAPI
from utils import listen, record_speech, initialize_furhat
import time
from openai import OpenAI
import keyboard  # using module keyboard
import state 
import config
LLM = False
TEST = False
client = OpenAI()

# initialize Furhat robot
furhat = initialize_furhat(config.FURHAT_IP_ADDRESS, config.FURHAT_VOICE_NAME)
conversation = []
pre_prompt = "You are the talking robot head called Furhat. You are part of a demo where you demonstrate what you can do. In the demo, you are to have a normal conversation with a participant of the demo as if you were a real human head."
greet = "Hello, I am Furhat. I am a talking robot head. I am here to have a conversation with you. What would you like to talk about?"

furhat.say(text = "Hello, I am Furhat. I am a talking robot head.")
time.sleep(4.1)
furhat.set_led(red=66, green=66, blue=66)  # Set the LED to blue 
furhat.say(text = "But wait I can do so much more than just talk. For example, i can look left.")
time.sleep(4.3)
furhat.set_led(red=66, green=245, blue=105)  # Set the LED to green
 
furhat.gesture(body={
        "frames": [
            {
                "time": [
                    1.0
                ],
                "params": {
                    "LOOK_LEFT": 1.0
                }
            }
        ],
        "class": "furhatos.gestures.Gesture"
        })

time.sleep(5)

furhat.gesture(body={
    "frames": [
        {
            "time": [
                1.0
            ],
            "params": {
                "reset": True
            }
        }
    ],
    "class": "furhatos.gestures.Gesture"
    })

time.sleep(22)
# Perform a custom gesture look right
furhat.gesture(body={
    "frames": [
        {
            "time": [
                1.0
            ],
            "params": {
                "LOOK_RIGHT": 1.0
            }
        }
    ],
    "class": "furhatos.gestures.Gesture"
    })
furhat.set_led(red=66, green=66, blue=66)  # Set the LED to blue

time.sleep(2)

furhat.say(text = "Or I can look right.")
time.sleep(2)
furhat.set_led(red=66, green=245, blue=105)  # Set the LED to green
# Perform a custom gesture look right
furhat.gesture(body={
    "frames": [
        {
            "time": [
                1.0
            ],
            "params": {
                "LOOK_RIGHT": 1.0
            }
        }
    ],
    "class": "furhatos.gestures.Gesture"
    })


time.sleep(2)
# turn off the LED
furhat.set_led(red=0, green=0, blue=0)  # Turn off the LED


if TEST:

    time.sleep(5)
    # Perform a custom gesture look left
    furhat.gesture(body={
        "frames": [
            {
                "time": [
                    2.0
                ],
                "params": {
                    "LOOK_LEFT": 1.0
                }
            }
        ],
        "class": "furhatos.gestures.Gesture"
        })

    time.sleep(3)
    furhat.say(text = "And I can look right.")

    # Perform a custom gesture look right
    furhat.gesture(body={
        "frames": [
            {
                "time": [
                    4.0
                ],
                "params": {
                    "LOOK_RIGHT": 1.0
                }
            }
        ],
        "class": "furhatos.gestures.Gesture"
        })

    time.sleep(7)
    furhat.say(text = "I can also change my face to look like a different person.")
    furhat.set_face(mask="adult", character = "Isabel")

    time.sleep(3)
    furhat.say(text = "Ah I think i look better now. If only I could sound better too.")
    time.sleep(3)
    furhat.set_voice(name="Emma-Neural")
    furhat.say(text = "Here we go now I sound better too. Or do I?")

    # list all gestures
    gestures = furhat.get_gestures()
    for gesture in gestures:
        print(gesture)

    # get all voices
    #faces = furhat.get_voices()
    #for face in faces:
    #    print(face)

    conversation.append({"role": "system", "content": pre_prompt})
    conversation.append({"role": "assistant", "content": greet})

    if LLM:
        while True:
            # Get user input
            user_input = record_speech(furhat)
            print("User: " + user_input)
            conversation.append({"role": "user", "content": user_input}) 

            if user_input == "esc":
                furhat.say(text = "Alright, that's it. CR7 for life.")
                break   
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation
            )
            response_content = completion.choices[0].message.content
            print("Assistant: " + response_content)
            conversation.append({"role": "assistant", "content": response_content})
            furhat.say(text = response_content)
            time.sleep(2)


