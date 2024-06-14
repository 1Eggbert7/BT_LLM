import os
from config import LLM, FURHAT_IP_ADDRESS, FURHAT_VOICE_NAME, FURHAT, VERSION
import time

# Define the folder and file path
folder_name = "Transkript of Conversation"
file_name = "transcripts.txt"
file_path = os.path.join(folder_name, file_name)

# Define your transcript string
transcript = "Version: " + VERSION + "\n" + time.strftime("%c")
transcript += """
User:  Good day sir
Press 'space' to start/continue recording, 'Enter' to stop.
can I have a grilled tomato and mushroom to set up please
You Pressed Enter!
Tree is initialized and furhat is used
Is it ambiguous?:  True
Assistant:  It seems like you're requesting a "grilled tomato and mushroom bruschetta." I can prepare that for you. Would you like anything else with it?
Press 'space' to start/continue recording, 'Enter' to stop.
no
You Pressed Enter!
Is it ambiguous?:  False
Is it Known?:  True
var_KnowNo:  ['bacon and egg sandwich', 'grilled tomato and mushroom bruschetta']
Assistant:  I'm sorry, I'm not sure what you mean. Could you specify your request with one of the following options?
Option 1: bacon and egg sandwich
Option 2: grilled tomato and mushroom bruschetta
Or do you want me to do something else?
Press 'space' to start/continue recording, 'Enter' to stop.
option 2
You Pressed Enter!
Is it ambiguous?:  False
Is it Known?:  True
var_KnowNo:  ['grilled tomato and mushroom bruschetta', 'an option not listed here']
Assistant:  I'm sorry, I'm not sure what you mean. Could you specify your request with one of the following options? 
Option 1: grilled tomato and mushroom bruschetta
Option 2: an option not listed here
Or do you want me to do something else?
Press 'space' to start/continue recording, 'Enter' to stop.
1
can you get angry
You Pressed Enter!
Is it ambiguous?:  True
Assistant:  I'm here to assist you with known sequences like cooking and cleaning tasks. If you have a specific request related to those, feel free to let me know so I can help you accordingly.
Press 'space' to start/continue recording, 'Enter' to stop.
anyone else wants to he doesn't deserve you
You Pressed Enter!
"""

# Create the folder if it doesn't exist
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Append the transcript to the file
with open(file_path, "a") as file:
    file.write(transcript + "\n")

print(f"Transcript saved to {file_path}")
