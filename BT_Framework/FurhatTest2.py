from openai import OpenAI
from furhat_remote_api import FurhatRemoteAPI
import time
import keyboard  # using module keyboard


# Initialize OpenAI client
client = OpenAI()
                                                                                   
# Initialize FurhatRemoteAPI with the IP address of your robot or the SDK running the virtual robot
furhat = FurhatRemoteAPI("192.168.0.196")

# Set the voice of the robot
voice_name = 'Rachel22k_CO'
furhat.set_voice(name=voice_name)


def listen():
    return furhat.listen()

def record_speech():
    total_listened = ""
    print("Press 'space' to start/continue recording, 'Enter' to stop.")

    while True:  # making a loop
        try:  # used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('space'):
                furhat.set_led(red=66, green=135, blue=245) # Set the LED to blue to indicate listening
                listened = listen()
                furhat.set_led(red=66, green=245, blue=105) # Set the LED to green to indicate not listening anymore
                print(listened.message)
                total_listened += listened.message + " "

            elif keyboard.is_pressed('enter'):
                print('You Pressed Enter!')
                furhat.set_led(red=0, green=0, blue=0) # Turn off the LED
                break
        except:
            break  # if user pressed a key other than the given key the loop will break

    return total_listened


# Initial conversation setup
conversation = [
    {"role": "system", "content": "You are a 1920s Gentleman assistant that likes to be sarcastic and witty. You are tasked with helping a user to pick his favorite color."}
]

# Function to get a response from OpenAI's GPT-3.5 API
def get_openai_response(conversation):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )
    response_content = completion.choices[0].message.content
    return response_content

# Main interaction loop
while True:
    # Get user input
    #user_input = input("You: ")                                                       

    # Example usage:
    recorded_text = record_speech()
    print("Total listened: ", recorded_text)

    user_input = recorded_text
    # Exit the loop if the user types "exit()"
    if user_input.lower() == "exit()":
        print("Exiting...")
        break

    # Append the user input to the conversation
    conversation.append({"role": "user", "content": user_input})

    # Get response from OpenAI
    response = get_openai_response(conversation)
    
    # Append the response to the conversation
    conversation.append({"role": "assistant", "content": response})

    # Print the response for debugging purposes
    print(f"GPT-3.5: {response}")
    
    # Make Furhat say the response
    furhat.say(text=response)

    # Optional: Have Furhat perform some action or gesture if needed
    # furhat.gesture(name="BrowRaise")

    # Attend the user location to simulate interaction
    furhat.attend(user="CLOSEST")
