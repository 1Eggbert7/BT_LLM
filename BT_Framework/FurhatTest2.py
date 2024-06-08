from openai import OpenAI
from furhat_remote_api import FurhatRemoteAPI
import time

# Initialize OpenAI client
client = OpenAI()

# Initialize FurhatRemoteAPI with the IP address of your robot or the SDK running the virtual robot
furhat = FurhatRemoteAPI("192.168.0.103")

# Set the voice of the robot
voice_name = 'Rachel22k_CO'
furhat.set_voice(name=voice_name)

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
    user_input = input("You: ")
    
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
