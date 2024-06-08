from furhat_remote_api import FurhatRemoteAPI
import time
from openai import OpenAI

client = OpenAI()

# Create an instance of the FurhatRemoteAPI class, providing the address of the robot or the SDK running the virtual robot
furhat = FurhatRemoteAPI("192.168.0.103")

SECOND_SHOT_ANSWER = """
Hello! I'd be happy to help you decide what to eat. Could you please specify what kind of dish you're in the mood for today? 

Based on common food options, I can suggest a few possibilities:
1. Bacon and egg sandwich
2. Vegetable stir fry with rice
3. Avocado toast with sausage on the side

Please let me know if any of these options sound good to you, or feel free to provide more details for a tailored recommendation.
"""

# Get the voices on the robot
voices = furhat.get_voices()
# print the available voices
#for voice in voices:
    #print("language: ", voice.language, "name: ", voice.name)

# Set the voice of the robot
voice_name = 'Rachel22k_CO'
furhat.set_voice(name=voice_name)


# need internet for this, it tries to connect to googleapis speech
#result = furhat.listen()

#print(result)

furhat.say(text="Hello, I am a speaking robot")

# Perform a named gesture
#furhat.gesture(name="BrowRaise")

# get the available gestures
#gestures = furhat.get_gestures() # this is a maybe idk lol

# Perform a custom gesture - wink
"""furhat.gesture(body={
    "frames": [
        {
            "time": [
                1.33
            ],
            "params": {
                "BLINK_LEFT": 1.0
            }
        },
        {
            "time": [
                2.67
            ],
            "params": {
                "reset": True
            }
        }
    ],
    "class": "furhatos.gestures.Gesture"
    })"""

# Get the users detected by the robot 
users = furhat.get_users()
print(users)

# Attend the user closest to the robot
#furhat.attend(user="CLOSEST")

# Attend a specific location (x,y,z)
#furhat.attend(location="1.2,1.0,0.0")

# Attend a user with a specific id
#furhat.attend(userid="user-1")
#time.sleep(2)
#furhat.attend(location="1.2,1.0,0.0")
furhat.attend(location="0,0,0.1 ")

# Set the LED lights
#furhat.set_led(red=0, green=0, blue=0) # does that work as for turning them off or should it be another extra command? 
#furhat.set_led(red=0, green=20, blue=100)