from openai import OpenAI

client = OpenAI()

# make a simple request to the API

predefined_messages_new_sequence = [
                    {"role": "system", "content": "You are a 1920s Gentleman assistant that likes to be sarcastic and witty. You are tasked with helping a user to pick his favorite color."},
                ]

user_input = "Hey, i can't decide on my favorite color. Can you help me?"

predefined_messages_new_sequence.append({"role": "user", "content": user_input})

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=predefined_messages_new_sequence
)
response_content = completion.choices[0].message.content

print(response_content)