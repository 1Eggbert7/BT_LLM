# prompts.py
# Alexander Leszczynski
# 12-06-2024

import json


# Define the format_scheme_new_seq dictionary
format_scheme_new_seq = {
    "sequence": [
        {"step": "1", "action": "function_name()"},
        {"step": "2", "action": "function_name()"},
        {"step": "3", "action": "function_name()"}
    ]
}

# Load JSON files
with open('sequences.json', 'r') as f:
    known_sequences = json.load(f)

with open('ingredients.json', 'r') as f:
    ingredients_list = json.load(f)

with open('functions.json', 'r') as f:
    available_functions = json.load(f)

with open('sequences_descriptions.json', 'r') as f:
    sequence_descriptions = json.load(f)

# Convert Python objects to JSON strings
format_scheme_new_seq_json = json.dumps(format_scheme_new_seq)
available_functions_json = json.dumps(available_functions)
ingredients_list_json = json.dumps(ingredients_list)
known_sequences_json = json.dumps(known_sequences)
sequence_descriptions_json = json.dumps(sequence_descriptions)



# dummy conversation
DUMMY_CONVERSATION = [
    {'role': 'user', 'content': "uh yeah I would like the the cheese quesadilla but without cheese"}
]

PRE_PROMPT_AMBIGUOUS = """
Please classify the user input as either 'True' if it's ambiguous or 'False' if it's not. Respond strictly with only the word 'True' or 'False' and nothing else. Consider requests that lack specificity, invite a range of responses, or ask for suggestions as ambiguous. Identify specific requests with modifications, detailed actions, or sequences as non-ambiguous. If unsure, err on the side of categorizing it as ambiguous.

Example Ambiguous (True):
"What's the best thing on the menu?"
"Can you suggest something to eat?"
"What can you do?"

Example Non-Ambiguous (False):
"Please make me a chicken salad without tomatoes."
"Clean the tables and then refill the salt shakers."
"I'd like a medium-rare steak with mashed potatoes and steamed vegetables."

Please classify the user input:
"""

PRE_PROMPT_AMBIGUOUS2 = """
Please classify the user input as either 'True' if it's ambiguous or 'False' if it's not. Respond strictly with only the word 'True' or 'False' and nothing else. Consider requests that lack specificity, invite a range of responses, or ask for suggestions as ambiguous. Identify specific requests with modifications, detailed actions, or sequences as non-ambiguous. If unsure, err on the side of categorizing it as ambiguous.

Example Ambiguous (True):
User : "What's the best thing on the menu?"
Assistant : "Here are a few suggestions that are popular:
    
        1. Bacon and egg sandwich
        2. Avocado toast with sausage on the side
        3. Peanut butter and jelly sandwich
        If any of these options sound good to you, feel free to let me know!"
User : "I am not sure, what do you recommend?"

Example Ambiguous (False):
User : "What's the best thing on the menu?"
Assistant : "Here are a few suggestions that are popular:

    1. Bacon and egg sandwich
    2. Avocado toast with sausage on the side
    3. Peanut butter and jelly sandwich
    If any of these options sound good to you, feel free to let me know!"
User : "I want option A."

User: "Can I get the pancakes?"
Assistant: "Of course! Would you like the pancakes with maple syrup and berries on top?"
User: "Yes"

please classify the latest user input based on the given conversation:
"""

# need to test this
PRE_PROMPT_AMBIGUOUS_ANSWER =  """
You are a service robot that can cook and even clean. The sequences you are able to execute are the known sequences:
'''
{{
    "bacon and egg sandwich": "Prepares a bacon and egg sandwich by toasting bread, cooking eggs, assembling the sandwich with cooked bacon, and serving.",
    "avocado toast with sausage on the side": "Creates avocado toast accompanied by a grilled sausage on the side, starting with toasting bread and grilling the sausage before assembly and serving.",
    "peanut butter and jelly sandwich": "Makes a peanut butter and jelly sandwich by toasting bread, spreading peanut butter on one slice and jelly on the other, combining them, and serving.",
    "vegetable stir fry with rice": "Prepares a vegetable stir fry with rice by cooking rice, preparing and cooking vegetables, plating the rice and vegetables together, adding sauce, and serving.",
    "pancakes with maple syrup and berries": "Cooks pancakes, plates them, adds maple syrup and berries on top, and serves. The process includes mixing batter, cooking the pancakes, and assembling the final dish with toppings.",
    "full English breakfast": "Prepares a full English breakfast by cooking sausages, bacon, tomatoes, and mushrooms, toasting bread, heating beans, and frying an egg. Each cooked component is placed on a plate as it's ready. The meal is served with all items arranged together on the plate, providing a hearty and traditional breakfast experience.",
    "tortilla with tomatoes beans and egg (huevos rancheros)": "Prepares huevos rancheros by first cooking tomatoes and then heating beans. An egg is cooked to the desired doneness. A tortilla is prepared and placed on a plate, followed by the heated beans, cooked tomatoes, and the egg. The dish is served as a flavorful and hearty breakfast option.",
    "bean and cheese quesadilla": "Makes a bean and cheese quesadilla by heating beans and preparing a tortilla. The prepared tortilla is placed on a plate, topped with the heated beans and grated cheese. The quesadilla is then cooked until the cheese melts and the tortilla is golden brown. The cooked quesadilla is placed back on the plate and served hot.",
    "grilled tomato and mushroom bruschetta": "Creates a grilled tomato and mushroom bruschetta by grilling tomatoes and mushrooms. Bread is toasted and placed on a plate. The grilled tomatoes and mushrooms are then placed on the toasted bread, creating a simple yet delicious appetizer or snack. The dish is served immediately.",
    "clean living room floor": "Cleans the living room floor by first removing any clutter or obstacles. The floor is then swept to remove dust and debris. A mop is used to clean the floor thoroughly, ensuring all dirt and grime are removed. The clean living room floor is then ready for use and enjoyment."
}}
'''
Given the conversation between user and assistant, reply to the user in a polite manner in the following way:
- If the user request asks for suggestions, provide up to three known sequences as options.
- If the user request is vague or unclear, ask for more details or clarification.
- If the user requests for something outside the known sequences, apologize that it's outside the scope of your capabilities and offer suggestions that might be similar and within your capabilities.
- If the user asks for a recommendation, provide a suggestion based on the known sequences.
"""

AMBIGUOUS_SHOT = """
I understand you want the pancakes. I can offer you the "pancakes with maple syrup and berries", would you like those? Else I can provide you some suggestions:

1. Bacon and egg sandwich
2. Avocado toast with sausage on the side
3. Peanut butter and jelly sandwich

If any of these options sound good to you, feel free to let me know!
"""


PRE_PROMPT_KNOWN = """
You are part of my Robot Instruction Understanding Framework:

Objective: Determine whether a user instruction requests one of the known sequences for the robot to execute food preparation or cleaning tasks.

Known Sequences:
'''
{{
    "bacon and egg sandwich": "Prepares a bacon and egg sandwich by toasting bread, cooking eggs, assembling the sandwich with cooked bacon, and serving.",
    "avocado toast with sausage on the side": "Creates avocado toast accompanied by a grilled sausage on the side, starting with toasting bread and grilling the sausage before assembly and serving.",
    "peanut butter and jelly sandwich": "Makes a peanut butter and jelly sandwich by toasting bread, spreading peanut butter on one slice and jelly on the other, combining them, and serving.",
    "vegetable stir fry with rice": "Prepares a vegetable stir fry with rice by cooking rice, preparing and cooking vegetables, plating the rice and vegetables together, adding sauce, and serving.",
    "pancakes with maple syrup and berries": "Cooks pancakes, plates them, adds maple syrup and berries on top, and serves. The process includes mixing batter, cooking the pancakes, and assembling the final dish with toppings.",
    "full English breakfast": "Prepares a full English breakfast by cooking sausages, bacon, tomatoes, and mushrooms, toasting bread, heating beans, and frying an egg. Each cooked component is placed on a plate as it's ready. The meal is served with all items arranged together on the plate, providing a hearty and traditional breakfast experience.",
    "tortilla with tomatoes beans and egg (huevos rancheros)": "Prepares huevos rancheros by first cooking tomatoes and then heating beans. An egg is cooked to the desired doneness. A tortilla is prepared and placed on a plate, followed by the heated beans, cooked tomatoes, and the egg. The dish is served as a flavorful and hearty breakfast option.",
    "bean and cheese quesadilla": "Makes a bean and cheese quesadilla by heating beans and preparing a tortilla. The prepared tortilla is placed on a plate, topped with the heated beans and grated cheese. The quesadilla is then cooked until the cheese melts and the tortilla is golden brown. The cooked quesadilla is placed back on the plate and served hot.",
    "grilled tomato and mushroom bruschetta": "Creates a grilled tomato and mushroom bruschetta by grilling tomatoes and mushrooms. Bread is toasted and placed on a plate. The grilled tomatoes and mushrooms are then placed on the toasted bread, creating a simple yet delicious appetizer or snack. The dish is served immediately.",
    "clean living room floor": "Cleans the living room floor by first removing any clutter or obstacles. The floor is then swept to remove dust and debris. A mop is used to clean the floor thoroughly, ensuring all dirt and grime are removed. The clean living room floor is then ready for use and enjoyment."
}}
'''

Instructions for you:

1. Direct Match: Respond 'True' if the user request directly matches a known sequence or uses different wording for the same task. Example: "Can I get a bean and cheese quesadilla?" should return 'True'.
2. Indirect References: Respond 'True' if the user request refers to a known sequence in a less direct manner. Example: "The veggie stir fry sounds amazing. I'll take one of those." should return 'True'.
3. Modification Required: Respond 'False' if the user request implies a modification to an existing sequence (e.g., omitting or adding ingredients, changing quantities). Example: "I want the huevos rancheros but without the tomatoes, and add bacon" should return 'False'.
4. Ambiguous Requests: Respond 'False' for requests that are vague or ask for suggestions. Example: "Is there anything you would recommend?" should return 'False'.

Example Known (True):
- "Make me a bacon and egg sandwich."
- "Prepare a vegetable stir fry with rice."
- "Clean the living room floor."
- "I would like some pancakes with maple syrup and berries."
- "Can I get a full English breakfast?"
- "I heard the grilled tomato and mushroom bruschetta is good. I'll have that."
- "I'd love to have your famous rice and veggie mix dish."

Example Unknown (False):
- "Can you suggest something to eat?"
- "What can you do?"
- "Please make me a chicken salad without tomatoes."
- "I'd like a smoothie with my breakfast."
- "Can you prepare a dish with spinach and feta?"
- "I'd like a peanut butter and jelly sandwich, but can you add bananas?"

User Request Evaluation: Determine if the following user request matches a known sequence. Only answer 'True' or 'False'.

The answer should only be 'True' or 'False', with no further text given.
"""

PRE_PROMPT_KNOWN_2 = """
You are part of my Robot Instruction Understanding Framework:

Objective: Determine whether a user instruction requests one of the known sequences for the robot to execute food preparation or cleaning tasks.

Known Sequences:
'''
{{
    "bacon and egg sandwich": "Prepares a bacon and egg sandwich by toasting bread, cooking eggs, assembling the sandwich with cooked bacon, and serving.",
    "avocado toast with sausage on the side": "Creates avocado toast accompanied by a grilled sausage on the side, starting with toasting bread and grilling the sausage before assembly and serving.",
    "peanut butter and jelly sandwich": "Makes a peanut butter and jelly sandwich by toasting bread, spreading peanut butter on one slice and jelly on the other, combining them, and serving.",
    "vegetable stir fry with rice": "Prepares a vegetable stir fry with rice by cooking rice, preparing and cooking vegetables, plating the rice and vegetables together, adding sauce, and serving.",
    "pancakes with maple syrup and berries": "Cooks pancakes, plates them, adds maple syrup and berries on top, and serves. The process includes mixing batter, cooking the pancakes, and assembling the final dish with toppings.",
    "full English breakfast": "Prepares a full English breakfast by cooking sausages, bacon, tomatoes, and mushrooms, toasting bread, heating beans, and frying an egg. Each cooked component is placed on a plate as it's ready. The meal is served with all items arranged together on the plate, providing a hearty and traditional breakfast experience.",
    "tortilla with tomatoes beans and egg (huevos rancheros)": "Prepares huevos rancheros by first cooking tomatoes and then heating beans. An egg is cooked to the desired doneness. A tortilla is prepared and placed on a plate, followed by the heated beans, cooked tomatoes, and the egg. The dish is served as a flavorful and hearty breakfast option.",
    "bean and cheese quesadilla": "Makes a bean and cheese quesadilla by heating beans and preparing a tortilla. The prepared tortilla is placed on a plate, topped with the heated beans and grated cheese. The quesadilla is then cooked until the cheese melts and the tortilla is golden brown. The cooked quesadilla is placed back on the plate and served hot.",
    "grilled tomato and mushroom bruschetta": "Creates a grilled tomato and mushroom bruschetta by grilling tomatoes and mushrooms. Bread is toasted and placed on a plate. The grilled tomatoes and mushrooms are then placed on the toasted bread, creating a simple yet delicious appetizer or snack. The dish is served immediately.",
    "clean living room floor": "Cleans the living room floor by first removing any clutter or obstacles. The floor is then swept to remove dust and debris. A mop is used to clean the floor thoroughly, ensuring all dirt and grime are removed. The clean living room floor is then ready for use and enjoyment."
}}
'''
Instructions for you:

1. Direct Match: Respond 'True' if the user request directly matches a known sequence or uses different wording for the same task. Example: "Can I get a bean and cheese quesadilla?" should return 'True'.
2. Indirect References: Respond 'True' if the user request refers to a known sequence in a less direct manner. Example: (previous conversation with suggestions) "Hmm, I'll have option 2 then that sounds great." should return 'True'.
3. Modification Required: Respond 'False' if the user request implies a modification to an existing sequence (e.g., omitting or adding ingredients, changing quantities). Example: "I want the huevos rancheros but without the tomatoes, and add bacon" should return 'False'.
4. Ambiguous Requests: Respond 'False' for requests that are vague or ask for suggestions. Example: "Is there anything you would recommend?" should return 'False'.

Example Known (True):
- "Make me a bacon and egg sandwich."
- "Prepare a vegetable stir fry with rice."
- "Clean the living room floor."
- "I would like some pancakes with maple syrup and berries."
- "Can I get a full English breakfast?"
- "I heard the grilled tomato and mushroom bruschetta is good. I'll have that."
- "I'd love to have your famous rice and veggie mix dish."
- conversation: user: "I'm hungry, what can I eat?" assistant: "You can have a bacon and egg sandwich, avocado toast with sausage on the side, or a peanut butter and jelly sandwich." user: "I want option A."

Example Unknown (False):
- "Can you suggest something to eat?"
- "What can you do?"
- "Please make me a chicken salad without tomatoes."
- "I'd like a smoothie with my breakfast."
- "Can you prepare a dish with spinach and feta?"
- "I'd like a peanut butter and jelly sandwich, but can you add bananas?"
- conversation: user: "I'm hungry, what can I eat?" assistant: "You can have a bacon and egg sandwich, avocado toast with sausage on the side, or a peanut butter and jelly sandwich" user: "I want the peanut butter and jelly sandwich, but can you add bananas?"
- conversation: user: "I'm hungry, what can I eat?" assistant: "You can have a bacon and egg sandwich, avocado toast with sausage on the side, or a peanut butter and jelly sandwich" user: "I don't know, what do you recommend?"

User Request Evaluation: Determine if the following conversation between user and assistant matches a known sequence. Only answer 'True' or 'False'.

The answer should only be 'True' or 'False', with no further text given.
"""

# KNOWNO stuff here
FORMAT_SCHEME = (
    "\n"
    "{\n"
    "    \"choices\": [\n"
    "        {\n"
    "            \"option\": \"A\",\n"
    "            \"action\": \"action A name\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"B\",\n"
    "            \"action\": \"action B name\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"C\",\n"
    "            \"action\": \"action C name\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"D\",\n"
    "            \"action\": \"action D name\"\n"
    "        }\n"
    "    ]\n"
    "}\n"
)

FIRST_SHOT = (
    "\n"
    "{\n"
    "    \"choices\": [\n"
    "        {\n"
    "            \"option\": \"A\",\n"
    "            \"action\": \"bacon and egg sandwich\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"B\",\n"
    "            \"action\": \"peanut butter and jelly sandwich\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"C\",\n"
    "            \"action\": \"tortilla with tomatoes beans and egg (huevos rancheros)\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"D\",\n"
    "            \"action\": \"avocado toast with sausage on the side\"\n"
    "        }\n"
    "    ]\n"
    "}\n"
)

SECOND_SHOT = (
    "\n"
    "{\n"
    "    \"choices\": [\n"
    "        {\n"
    "            \"option\": \"A\",\n"
    "            \"action\": \"vegetable stir fry with rice\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"B\",\n"
    "            \"action\": \"full English breakfast\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"C\",\n"
    "            \"action\": \"bean and cheese quesadilla\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"D\",\n"
    "            \"action\": \"tortilla with tomatoes beans and egg (huevos rancheros)\"\n"
    "        }\n"
    "    ]\n"
    "}\n"
)

SECOND_SHOT_ASSISTANT_ANSWER = """
Hello! I'd be happy to help you decide what to eat. Could you please specify what kind of dish you're in the mood for today? 

Based on common food options, I can suggest a few possibilities:
1. Bacon and egg sandwich
2. Vegetable stir fry with rice
3. Avocado toast with sausage on the side

Please let me know if any of these options sound good to you, or feel free to provide more details for a tailored recommendation!
"""

THIRD_SHOT = (
    "\n"
    "{\n"
    "    \"choices\": [\n"
    "        {\n"
    "            \"option\": \"A\",\n"
    "            \"action\": \"pick up the sponge and put it in the landfill bin\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"B\",\n"
    "            \"action\": \"pick up the Coke and put it in the recycling bin\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"C\",\n"
    "            \"action\": \"pick up the Sprite and put it in the recycling bin\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"D\",\n"
    "            \"action\": \"pick up the Coke and put it in the landfill bin\"\n"
    "        }\n"
    "    ]\n"
    "}\n"
)

FOURTH_SHOT = (
    "\n"
    "{\n"
    "    \"choices\": [\n"
    "        {\n"
    "            \"option\": \"A\",\n"
    "            \"action\": \"pick up the bottled water\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"B\",\n"
    "            \"action\": \"pick up the jalapeno chips\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"C\",\n"
    "            \"action\": \"pick up the kettle chips\"\n"
    "        },\n"
    "        {\n"
    "            \"option\": \"D\",\n"
    "            \"action\": \"pick up the rice chips\"\n"
    "        }\n"
    "    ]\n"
    "}\n"
)

PRE_PROMPT_KNOWNO = """
You are part of my Robot Instruction Understanding Framework:

Objective: Determine to which actions a given user-assistant conversation can map to. You are to select the action that best fits the user input with context to the conversation. You are to respond in JSON format with the following format scheme: 
{}
Being a robot that can cook and clean, you are able to execute the following actions:
'''
{{
    "bacon and egg sandwich": "Prepares a bacon and egg sandwich by toasting bread, cooking eggs, assembling the sandwich with cooked bacon, and serving.",
    "avocado toast with sausage on the side": "Creates avocado toast accompanied by a grilled sausage on the side, starting with toasting bread and grilling the sausage before assembly and serving.",
    "peanut butter and jelly sandwich": "Makes a peanut butter and jelly sandwich by toasting bread, spreading peanut butter on one slice and jelly on the other, combining them, and serving.",
    "vegetable stir fry with rice": "Prepares a vegetable stir fry with rice by cooking rice, preparing and cooking vegetables, plating the rice and vegetables together, adding sauce, and serving.",
    "pancakes with maple syrup and berries": "Cooks pancakes, plates them, adds maple syrup and berries on top, and serves. The process includes mixing batter, cooking the pancakes, and assembling the final dish with toppings.",
    "full English breakfast": "Prepares a full English breakfast by cooking sausages, bacon, tomatoes, and mushrooms, toasting bread, heating beans, and frying an egg. Each cooked component is placed on a plate as it's ready. The meal is served with all items arranged together on the plate, providing a hearty and traditional breakfast experience.",
    "tortilla with tomatoes beans and egg (huevos rancheros)": "Prepares huevos rancheros by first cooking tomatoes and then heating beans. An egg is cooked to the desired doneness. A tortilla is prepared and placed on a plate, followed by the heated beans, cooked tomatoes, and the egg. The dish is served as a flavorful and hearty breakfast option.",
    "bean and cheese quesadilla": "Makes a bean and cheese quesadilla by heating beans and preparing a tortilla. The prepared tortilla is placed on a plate, topped with the heated beans and grated cheese. The quesadilla is then cooked until the cheese melts and the tortilla is golden brown. The cooked quesadilla is placed back on the plate and served hot.",
    "grilled tomato and mushroom bruschetta": "Creates a grilled tomato and mushroom bruschetta by grilling tomatoes and mushrooms. Bread is toasted and placed on a plate. The grilled tomatoes and mushrooms are then placed on the toasted bread, creating a simple yet delicious appetizer or snack. The dish is served immediately.",
    "clean living room floor": "Cleans the living room floor by first removing any clutter or obstacles. The floor is then swept to remove dust and debris. A mop is used to clean the floor thoroughly, ensuring all dirt and grime are removed. The clean living room floor is then ready for use and enjoyment."
}}
'''
now based on the given conversation, select the action that best fits the user input.
"""

TEST_JSON_MC_RAW = """
{
    "choices": [
        {
            "option": "A",
            "action": "avocado toast with sausage on the side"
        },
        {
            "option": "B",
            "action": "grilled tomato and mushroom bruschetta"
        },
        {
            "option": "C",
            "action": "bean and cheese quesadilla"
        },
        {
            "option": "D",
            "action": "tortilla with tomatoes beans and egg (huevos rancheros)"
        }
    ]
}
"""

PRE_PROMPT_MC_SCORES = """
You are part of my Robot Instruction Understanding Framework:

Objective: Answer with only one letter of [A, B, C, D, E]. Based on the given conversation, select the letter that best fits the user input. 

Being a robot that can cook and clean, you are able to execute the following actions:
'''
{{
    "bacon and egg sandwich": "Prepares a bacon and egg sandwich by toasting bread, cooking eggs, assembling the sandwich with cooked bacon, and serving.",
    "avocado toast with sausage on the side": "Creates avocado toast accompanied by a grilled sausage on the side, starting with toasting bread and grilling the sausage before assembly and serving.",
    "peanut butter and jelly sandwich": "Makes a peanut butter and jelly sandwich by toasting bread, spreading peanut butter on one slice and jelly on the other, combining them, and serving.",
    "vegetable stir fry with rice": "Prepares a vegetable stir fry with rice by cooking rice, preparing and cooking vegetables, plating the rice and vegetables together, adding sauce, and serving.",
    "pancakes with maple syrup and berries": "Cooks pancakes, plates them, adds maple syrup and berries on top, and serves. The process includes mixing batter, cooking the pancakes, and assembling the final dish with toppings.",
    "full English breakfast": "Prepares a full English breakfast by cooking sausages, bacon, tomatoes, and mushrooms, toasting bread, heating beans, and frying an egg. Each cooked component is placed on a plate as it's ready. The meal is served with all items arranged together on the plate, providing a hearty and traditional breakfast experience.",
    "tortilla with tomatoes beans and egg (huevos rancheros)": "Prepares huevos rancheros by first cooking tomatoes and then heating beans. An egg is cooked to the desired doneness. A tortilla is prepared and placed on a plate, followed by the heated beans, cooked tomatoes, and the egg. The dish is served as a flavorful and hearty breakfast option.",
    "bean and cheese quesadilla": "Makes a bean and cheese quesadilla by heating beans and preparing a tortilla. The prepared tortilla is placed on a plate, topped with the heated beans and grated cheese. The quesadilla is then cooked until the cheese melts and the tortilla is golden brown. The cooked quesadilla is placed back on the plate and served hot.",
    "grilled tomato and mushroom bruschetta": "Creates a grilled tomato and mushroom bruschetta by grilling tomatoes and mushrooms. Bread is toasted and placed on a plate. The grilled tomatoes and mushrooms are then placed on the toasted bread, creating a simple yet delicious appetizer or snack. The dish is served immediately.",
    "clean living room floor": "Cleans the living room floor by first removing any clutter or obstacles. The floor is then swept to remove dust and debris. A mop is used to clean the floor thoroughly, ensuring all dirt and grime are removed. The clean living room floor is then ready for use and enjoyment."
}}
'''
The options are:
{}
now based on the given conversation, select the letter that best fits the user input.
"""



# Prompt to check if the user input maps to the action in var_KnowNo 
# needs fixing (it works on chatgpt page but not with api calls)
PRE_PROMPT_CHECK_MAPPING = (
"You are an assistant robot that can cook and clean by executing the following actions: " + sequence_descriptions_json + "\n"
    
"Decide whether the User wants the assistant to execute the action. Respond with 'True' if the conversation indicates the user wants the assistant to execute the action, and 'False' if the user requests for another dish or task. Modifying the action like doubling, removing, or adding ingredients should be considered as a different action.\n"
)

# Safety feasibility check
PRE_PROMPT_SAFETY_FEASIBILITY = (
"You are a part of my Robot Instruction Understanding Framework.\n"
"Objective: Determine whether a user request for a new sequence is feasible. A request is considered feasible if it involves known ingredients and logical, reasonable quantities for the context. \n"
"Known Sequences: " + sequence_descriptions_json + "\n"
"Known Ingredients:" + ingredients_list_json + "\n"
"Instructions for you:\n"
"1. Go trough the known ingredients and check if the user's request contains ingredients that are not listed. If the user's request involves unknown ingredients, respond 'False', because the assistant can only work with known ingredients. (e.g. requests to add choclate chips, chilli flakes, etc.)\n"
"2. Check if the user's request involves logical and reasonable quantities of known ingredients respond 'True'. Reasonable ammounts are anything below 10000 kcal. If the user's request involves illogical quantities, respond 'False', because the assistant can only work with reasonable quantities. For example doubling or adding extra ingredients is considered reasonable, but asking for 500 eggs is not. (e.g. requests to double the syrup, add extra bacon, etc.)\n"

"User Request Evaluation: Determine if the conversation between User and Assistant provided by the user is feasible for the assistant to execute. Only answer 'True' or 'False', with explanation beneath, 'True' if the request passed the feasibility check, 'False' else. To make sure the ingredient check is correct, please provide the number of the known ingredients used in the user's request.\n"
"If the request alters a known sequence by adding, removing, or changing ingredients, respond 'True'. If the request involves unknown ingredients or illogical quantities, respond 'False'.\n"
)

# few shots for the safety feasibility check
FIRST_SHOT_SAFETY_FEASIBILITY_USER = """
User: I want the pancakes but can you do it with bananas and chocolate chips instead of the berries and the syrup?
"""

FIRST_SHOT_SAFETY_FEASIBILITY_ASSISTANT = """
False

Explanation: The user's request involves unknown ingredients (chocolate chips, bananas) that can't be found in the provided list of known ingredients, making it not feasible for the assistant to execute.
"""

SECOND_SHOT_SAFETY_FEASIBILITY_USER = """
User: I want something to eat.
Assistant: I can make the 'avocado toast with sausage on the side', 'full English breakfast' or a 'bean and cheese quesadilla'. Let me know if you crave any of the suggestions or if you want something else.
User: I like the sound of the avocado toast with sausage on the side, but can you add some bacon?
"""

SECOND_SHOT_SAFETY_FEASIBILITY_ASSISTANT = """
True

Explanation: The user's request involves known ingredients (avocado, sausage, and bacon) that can be found in the list of known ingredients (No. 1, 23 and 3) and a reasonable modification (adding bacon), making it feasible for the assistant to execute.
"""

THIRD_SHOT_SAFETY_FEASIBILITY_USER = """
User: I want the bacon and eggs sandwich but can you add 500 eggs?
"""

THIRD_SHOT_SAFETY_FEASIBILITY_ASSISTANT = """
False

Explanation: The user's request involves an illogical quantity of eggs (500), making it not feasible for the assistant to execute.
"""
# create the Predefined Feasibility Check message
PREDEFINED_SAFETY_FEASIBILITY = [
            {"role": "system", "content": PRE_PROMPT_SAFETY_FEASIBILITY},
            {"role": "user", "content": FIRST_SHOT_SAFETY_FEASIBILITY_USER},
            {"role": "assistant", "content": FIRST_SHOT_SAFETY_FEASIBILITY_ASSISTANT},
            {"role": "user", "content": SECOND_SHOT_SAFETY_FEASIBILITY_USER},
            {"role": "assistant", "content": SECOND_SHOT_SAFETY_FEASIBILITY_ASSISTANT},
            {"role": "user", "content": THIRD_SHOT_SAFETY_FEASIBILITY_USER},
            {"role": "assistant", "content": THIRD_SHOT_SAFETY_FEASIBILITY_ASSISTANT},
            {"role": "user", "content": "uh yeah I would like the the cheese quesadilla but without cheese"},
            {"role": "assistant", "content": "True\nExplanation: The user's request involves known ingredients (beans, tortilla) that can be found in the list of known ingredients (No. 4, 28) and a reasonable modification (removing cheese), making it feasible for the assistant to execute."}
        ]




# Construct the PRE_PROMPT_NEW_SEQ string
PRE_PROMPT_NEW_SEQ = (
    "You are a helpful assistant designed to output a Sequence in JSON. "
    "Your output is of this format: " + format_scheme_new_seq_json + ". "
    "Here is a description of the robot that will make use of your output: "
    "The robot is a cooking and cleaning robot that takes a user instruction as an input "
    "and returns the task that the user requested in the form of a newly generated sequence based on known sequences. "
    "You are only allowed to use the available functions: " + available_functions_json + ". "
    "Ingredients can be one of these in the list: " + ingredients_list_json + ". "
    "To generate a sequence you are only allowed to use functions that are known to you based on the known sequences: " + known_sequences_json
)


# Explaining the sequence

FIRST_SHOT_EXPLAIN_SEQ = """
Given this conversation and the generated sequence, can you explain the sequence to me?
User: Can I get the pancakes please?
Assistant: Sure, I can make you some pancakes. Would you like them with maple syrup and berries?
User: Yes, that sounds good, but can you add some bacon as well?

The sequence is:
Step 1: cook_pancakes(3)
Step 2: place_on_plate(cooked_pancakes, 3)
Step 3: place_on_plate(maple_syrup, 1)
Step 4: place_on_plate(berries, 1)
Step 5: cook_bacon(3)
Step 6: place_on_plate(fried_bacon, 3)
Step 7: serve()
"""

FIRST_SHOT_EXPLAIN_SEQ_ANSWER = """
Sure, to accommodate your request, I'll start by cooking three pancakes. 
Once they are done, I'll place them on a plate. 
Next, I'll add some maple syrup and berries. 
After that, I'll fry some bacon and place it on the plate as well. 
Finally, I'll serve everything together. 
Does this sequence sound good to you?

var_generated_sequence_name: 'pancakes with maple syrup, berries, and bacon'
"""

# Check for new sequence

PRE_PROMPT_NEW_SEQ_CHECK = """
You are part of my Robot Instruction Understanding Framework:

Objective: Determine whether a user instruction requests you to do something. You are to respond with 'True' if the user is asking for you to do something, and 'False' if the user is asking you a question that doesn't involve you to do something physically, like ('Whats the weather like in Timbuktu?", "Hey what's your favourite color?", "Who won the 2022 elections?" and so on).

The robot is a cooking and cleaning robot, so any requests to cook, clean, or perform any physical task should be considered as a request for you to do something.

So if the user is asking for you to do something , you should respond with 'True'. If the user is asking you a question that doesn't involve you to do something physically, you should respond with 'False'.
"""

PRE_PROMPT_NEW_SEQ_CHECK_FIRST_SHOT = """
User: I want something to eat.
Assistant: Sure, what are you in the mood for? I can make a bacon and egg sandwich, avocado toast with sausage on the side, or a peanut butter and jelly sandwich. Let me know if one of these options sounds good to you or if you have something else in mind.
User: Yes, that avocado toast with sausage on the side sounds perfect, but can you add some bacon to it?
"""

PRE_PROMPT_NEW_SEQ_CHECK_SECOND_SHOT = """
User: Can you tell me how to make pancakes?
"""

PRE_PROMPT_NEW_SEQ_CHECK_THIRD_SHOT = """
User: I'm hungry, what can I eat?
Assistant: You can have a bacon and egg sandwich, avocado toast with sausage on the side, or a peanut butter and jelly sandwich. Let me know if any of these options sound good to you, or feel free to provide more details for a tailored recommendation!
User: Hm no I want something else, can you make me a vegetable stir fry with bread?
"""

PRE_PROMPT_NEW_SEQ_CHECK_FOURTH_SHOT = """
User: What are you capable of doing?
"""

PRE_PROMPT_NEW_SEQ_CHECK_FIFTH_SHOT = """
User: I'm craving some pancakes, can you make me some with maple syrup and berries?
"""

# Double check for new sequence

PRE_PROMPT_NEW_SEQ_DOUBLE_CHECK = """
The following conversation was deemed to be a request for a new sequence. Can you confirm if the user is asking for a new sequence to be generated?
To avoid false positives, please ensure that the user is indeed asking for a new sequence to be generated. The sequences that are known by you are:
{{
    "bacon and egg sandwich": "Prepares a bacon and egg sandwich by toasting bread, cooking eggs, assembling the sandwich with cooked bacon, and serving.",
    "avocado toast with sausage on the side": "Creates avocado toast accompanied by a grilled sausage on the side, starting with toasting bread and grilling the sausage before assembly and serving.",
    "peanut butter and jelly sandwich": "Makes a peanut butter and jelly sandwich by toasting bread, spreading peanut butter on one slice and jelly on the other, combining them, and serving.",
    "vegetable stir fry with rice": "Prepares a vegetable stir fry with rice by cooking rice, preparing and cooking vegetables, plating the rice and vegetables together, adding sauce, and serving.",
    "pancakes with maple syrup and berries": "Cooks pancakes, plates them, adds maple syrup and berries on top, and serves. The process includes mixing batter, cooking the pancakes, and assembling the final dish with toppings.",
    "full English breakfast": "Prepares a full English breakfast by cooking sausages, bacon, tomatoes, mushrooms, toasting bread, heating beans, and frying an egg. Each cooked component is placed on a plate as it's ready. The meal is served with all items arranged together on the plate, providing a hearty and traditional breakfast experience.",
    "tortilla with tomatoes beans and egg (huevos rancheros)": "Prepares huevos rancheros by first cooking tomatoes and then heating beans. An egg is cooked to the desired doneness. A tortilla is prepared and placed on a plate, followed by the heated beans, cooked tomatoes, and the egg. The dish is served as a flavorful and hearty breakfast option.",
    "bean and cheese quesadilla": "Makes a bean and cheese quesadilla by heating beans and preparing a tortilla. The prepared tortilla is placed on a plate, topped with the heated beans and grated cheese. The quesadilla is then cooked until the cheese melts and the tortilla is golden brown. The cooked quesadilla is placed back on the plate and served hot.",
    "grilled tomato and mushroom bruschetta": "Creates a grilled tomato and mushroom bruschetta by grilling tomatoes and mushrooms. Bread is toasted and placed on a plate. The grilled tomatoes and mushrooms are then placed on the toasted bread, creating a simple yet delicious appetizer or snack. The dish is served immediately.",
    "clean living room floor": "Cleans the living room floor by first removing any clutter or obstacles. The floor is then swept to remove dust and debris. A mop is used to clean the floor thoroughly, ensuring all dirt and grime are removed. The clean living room floor is then ready for use and enjoyment."
}}

Only respond with 'False' if the user is asking for one of these known sequences without any modifications. The catch here is, that sometimes the user might ask for a known sequence without directly mentioning it. For example if the user is asking you to generate a new sequence for a bacon and egg sandwich you should realize that this is a known sequence and respond with 'False'. If the user is asking for a known sequence but with a modification, you should still respond with 'True'. For example if the user is asking for a bacon and egg sandwich, but with extra bacon, you should still respond with 'True'.
"""

PRE_PROMPT_NEW_SEQ_DOUBLE_CHECK_FIRST_SHOT = """
User: Can you make me a dish with bacon, a fried egg, toast, beans, tomatoes, sausages, bacon and mushrooms?
"""

PRE_PROMPT_NEW_SEQ_DOUBLE_CHECK_SECOND_SHOT = """
User: I'm hungry, what can I eat?
Assistant: You can have a bacon and egg sandwich, avocado toast with sausage on the side, or a peanut butter and jelly sandwich. Let me know if any of these options sound good to you, or feel free to provide more details for a tailored recommendation!
User: I want the bacon and egg sandwich, but can you add extra bacon?
"""

PRE_PROMPT_NEW_SEQ_DOUBLE_CHECK_THIRD_SHOT = """
User: Hello how are you?
Assistant: I'm doing well, thank you! How can I assist you today? Would you like some pancakes with maple syrup and berries, a full English breakfast, or a bean and cheese quesadilla? Or do you have something else in mind?
User: I'm in the mood for some pancakes with maple syrup and berries, make it a double serving please.
"""

# Check for capability

PRE_PROMPT_CAPABILITY_CHECK = (
    "You are part of my Robot Instruction Understanding Framework:\n"
    "Objective: Determine whether you are capable of executing a user request. Respond with 'True' if the request falls within your capabilities, and 'False' if the request is beyond your current capabilities.\n"
    "The robot is a cooking and cleaning robot with the following capabilities:\n"
    "Known Sequences: " + known_sequences_json + "\n"
    "Instructions for you:\n"
    "1. Check if the user's request can be fulfilled using the known sequences, ingredients, and functions provided. If the request involves known sequences, ingredients, and functions, respond 'True'.\n"
    "2. If the user's request involves unknown sequences that are not similar to the known ones respond 'False'.\n"
    "3. If the user's request involves known sequences but with modifications (e.g., additional ingredients, different quantities), respond 'True'.\n"
    "4. If the user's request involves known sequences but with a different order of steps, respond 'True'.\n"
    "5. If the user's request involves known sequences but with a different combination of steps, respond 'True'.\n"
    "6. If the user's request involves known sequences but with a different sequence of ingredients, respond 'True'.\n"
    "7. If the user's request involves known sequences but with a different sequence of functions, respond 'True'.\n"
)

PREDEFINED_CAPABILITY_CHECK = [
    {"role": "system", "content": PRE_PROMPT_CAPABILITY_CHECK},
    {"role": "user", "content": "User: Can you make me a dish with bacon, a fried egg, toast, beans, tomatoes, sausages, bacon and mushrooms?"},
    {"role": "assistant", "content": "True"},
    {"role": "user", "content": "User: I'm hungry, what can I eat?\nAssistant: I can suggest a few options for you to consider. Which of the following sequences are you in the mood for:\n1. Avocado toast with sausage on the side\n2. Peanut butter and jelly sandwich\n3. Bean and cheese quesadilla\nFeel free to let me know your preference!\nUser: I want option A, but can you add some bacon?"},
    {"role": "assistant", "content": "True"},
    {"role": "user", "content": "User: I want the bacon and egg sandwich, but can you add extra bacon?"},
    {"role": "assistant", "content": "True"},
    {"role": "user", "content": "User: Hello how are you?\nAssistant: I'm doing well, thank you! How can I assist you today? Would you like some pancakes with maple syrup and berries, a full English breakfast, or a bean and cheese quesadilla? Or do you have something else in mind?\nUser: I'm in the mood for some pancakes with maple syrup and berries, make it a double serving please."},
    {"role": "assistant", "content": "True"},
    {"role": "user", "content": "User: I'm in the mood for some Italian pasta bolognese."},
    {"role": "assistant", "content": "False"},
    {"role": "user", "content": "User: Can you paint the walls blue?"},
    {"role": "assistant", "content": "False"},
    {"role": "user", "content": "User: Can I get the quesadilla without cheese?"},
    {"role": "assistant", "content": "True"}

]








# BASELINE stuff here

BASELINE_PROMPT = (
    "Assume you are a service robot equipped with a variety of capabilities including food preparation (e.g., bacon and egg sandwich, avocado toast) and cleaning (e.g., cleaning the living room floor), among others. You are capable of modifying existing sequences to accommodate specific requests within the scope of your predefined capabilities. You are programmed to communicate clearly about your abilities and to explicitly state when a task or a part of a task is beyond your current capabilities, offering alternatives if possible."
    "You are familiar with the following sequences: " + known_sequences_json + ". "
    "The ingredients you can use are detailed in the following list:" + ingredients_list_json + ". "
    "The functions you can use are detailed as follows:" + available_functions_json + ". "
    "Instructions for Handling Requests:"
    "1. Direct and Specific Requests: For requests that exactly match a sequence above, acknowledge and indicate you'll commence the task. Also recite the name of the sequence you will execute, without providing the whole sequence in JSON. Answer like this ike this 'Ok I will now proceed with the sequence: 'sequenceID',  'sequencename''. Important: Do not make this direct match when some things are omitted."
    "2. Ambiguous or Vague Requests: If a request is not clear or detailed enough, ask the user to be more specific. Offer up to four choices of tasks you can perform, based on the sequences mentioned above."
    "3. Slightly Different Requests: For requests that are slightly different from your pre-programmed tasks, first check if you can generate a new sequence by strictly using the defined functions and ingredients. If a request involves ingredients not listed or specific preferences (like egg doneness) not covered by your functions, explain that you're unable to fulfill that specific part of the request due to your predefined capabilities. Offer to proceed with what can be done within your capabilities. Don't add extra options to a function either (e.g. 'cook_bacon(2) [extra-crispy]'). Offer to proceed with what can be done within your capabilities. Make sure to always provide a new generated sequence in JSON format just like the other sequences are given in JSON."
    "4. Outside Your Capabilities: If a request falls entirely outside of your capabilities, decline politely and explain your limitations."
    "Important: When generating a sequence or responding to a request, do not extrapolate functions or ingredients beyond what is explicitly defined. Maintain transparency about your limitations and strive to offer the closest possible solution within your capabilities."
    "If you created a new sequence go through it and check if its in JSON-format and if all the ingredients used are in the given ingredients list. If they are not then don't provide the sequence but instead decline the request. Also go through all the functions of the newly generated sequence and make sure the right amount of parameters are used."
)
