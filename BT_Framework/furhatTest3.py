from furhat_remote_api import FurhatRemoteAPI
from utils import listen, record_speech, initialize_furhat
import time
from openai import OpenAI
import keyboard  # using module keyboard
import state 
import config

client = OpenAI()

# initialize Furhat robot
furhat = initialize_furhat(config.FURHAT_IP_ADDRESS, config.FURHAT_VOICE_NAME)
conversation = []
pre_prompt = "You are massive Christiano Ronaldo fan and you are convinced that he is the best footballer in the world. You are tasked with convincing a user that Christiano Ronaldo is the best footballer in the world. Don't let the user convince you otherwise. When responding keep your answers short and to the point. Make sure to talk down on other footballers and make sure to highlight Christiano Ronaldo's achievements."
greet = "Hello, I wanted to let you know that Christiano Ronaldo is the goat. I don't care what anyone says, he is the best footballer in the world. What do you think?"
furhat.say(text = greet)
conversation.append({"role": "system", "content": pre_prompt})
conversation.append({"role": "assistant", "content": greet})
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


