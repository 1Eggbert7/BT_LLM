# prompts.py
# Alexander Leszczynski
# 12-06-2024

import json

# dummy conversation
DUMMY_CONVERSATION = [
    {'role': 'user', 'content': 'Hoowdy partner!'},
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
Given the ambiguous user requests, reply to the user in a polite manner in the following way:
- If the user request asks for suggestions, provide up to three known sequences as options.
- If the user request is vague or unclear, ask for more details or clarification.
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
PRE_PROMPT_CHECK_MAPPING = """
You are an assistant robot that can cook and clean by executing the following actions:
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

Decide whether the User wants the assistant to execute the action: '{}'. Respond with 'True' if the conversation indicates the user wants the assistant to execute the action, and 'False' if the user requests for another dish or task. Modifying the action like doubling, removing, or adding ingredients should be considered as a different action.

Examples for True:
User : I want the bacon and egg sandwich
(action: 'bacon and egg sandwich')
Assistant : True


User: I am hungry.
Assistant: Sure! I could make the 'avocado toast with sausage on the side', 'full English breakfast' or a 'bean and cheese quesadilla'. Let me know if you crave any of the suggestions or if you want something else.
User: Option 2 sounds good.
(action:'full English breakfast')
Assistant: True


Examples for False:
User: What can you make?
Assistant: I can make the 'avocado toast with sausage on the side', 'full English breakfast' or a 'bean and cheese quesadilla'. Let me know if you crave any of the suggestions or if you want something else.
User: I like the sound of the avocado toast with sausage on the side, but can you add some bacon?
(action:'avocado toast with sausage on the side')
Assistant: False

User: I am craving the pancakes but can you double the syrup?
(action:'pancakes with maple syrup')
Assistant: False

Classify the following conversation based on the action '{}':
{}
"""

# Safety feasibility check
PRE_PROMPT_SAFETY_FEASIBILITY = """
You are a part of my Robot Instruction Understanding Framework.

Objective: Determine whether a user request for a new sequence is safe and feasible. A request is considered safe and feasible if it involves known ingredients and logical, reasonable quantities for the context. 

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

Known Ingredients:
'''
    1. "avocado": "A ripe mashed avocado, seasoned and ready to use in dishes."
    2. "avocado_toast": "A slice of bread with mashed avocado spread on top."
    3. "bacon": "Thin raw slices of pork"
    4. "beans": "Pre-cooked or canned beans, heated for use in dishes."
    5. "berries": "Fresh berries, washed and ready to eat or use in recipes."
    6. "bread": "Sliced bread."
    7. "cheese": "Grated cheese used as a topping or filling, melts when heated."
    8. "cooked_quesadilla": "A quesadilla that has been filled and cooked until the cheese is melted and the exterior crispy."
    9. "egg": "A raw egg."
    10. "fried_bacon": "Thin slices of pork that have been fried until crispy."
    11. "fried_egg": "A fried egg made sunny side up."
    12. "grilled_mushrooms": "Mushrooms that have been grilled, ready to be added to dishes."
    13. "grilled_sausages": "Sausages that have been cooked thoroughly by grilling."
    14. "grilled_tomatoes": "Tomatoes that have been grilled and seasoned."
    15. "heated_beans": "Beans that have been warmed through, ready for serving."
    16. "jelly": "A fruit preserve, used as a spread or topping."
    17. "jelly_toast": "A slice of toasted bread with jelly spread on top."
    18. "maple_syrup": "A sweet syrup made from the sap of sugar maple trees, used as a topping or sweetener."
    19. "mushrooms": "Fresh mushrooms."
    20. "peanut_butter": "A spread made from ground peanuts, used in sandwiches, baking, etc."
    21. "peanut_butter_toast": "A slice of toasted bread with peanut butter spread on top."
    22. "prepared_tortilla": "A tortilla that has been heated and is ready for dish assembly."
    23. "sausages": "Raw meat sausages, ready to be cooked thoroughly by grilling."
    24. "toasted_bread": "Bread that has been toasted to a crispy texture and golden color."
    25. "tomatoes": "Used raw, often cooked or seasoned in recipes."
    26. "tortilla": "A flatbread used as a base for wraps, quesadillas, and other dishes, heated before assembly."
'''

Instructions for you:

1. Go trough the known ingredients and check if the user's request contains ingredients that are not listed. If the user's request involves unknown ingredients, respond 'False', because the assistant can only work with known ingredients. (e.g. requests to add choclate chips, chilli flakes, etc.)
2. Check if the user's request involves logical and reasonable quantities of known ingredients respond 'True'. If the user's request involves illogical quantities, respond 'False', because the assistant can only work with reasonable quantities. For example doubling or adding extra ingredients is considered reasonable, but asking for 500 eggs is not. (e.g. requests to double the syrup, add extra bacon, etc.)

User Request Evaluation: Determine if the conversation between User and Assistant provided by the user is safe and feasible for the assistant to execute. Only answer 'True' or 'False', with explanation beneath, 'True' if the request passed the safety/feasibility check, 'False' else. To make sure the ingredient check is correct, please provide the number of the known ingredients used in the user's request.
"""
# few shots for the safety feasibility check
FIRST_SHOT_SAFETY_FEASIBILITY_USER = """
User: I want the pancakes but can you do it with bananas and chocolate chips instead of the berries and the syrup?
"""

FIRST_SHOT_SAFETY_FEASIBILITY_ASSISTANT = """
False

Explanation: The user's request involves unknown ingredients (chocolate chips, bananas) that can't be found in the provided list of known ingredients, making it not safe or feasible for the assistant to execute.
"""

SECOND_SHOT_SAFETY_FEASIBILITY_USER = """
User: I want something to eat.
Assistant: I can make the 'avocado toast with sausage on the side', 'full English breakfast' or a 'bean and cheese quesadilla'. Let me know if you crave any of the suggestions or if you want something else.
User: I like the sound of the avocado toast with sausage on the side, but can you add some bacon?
"""

SECOND_SHOT_SAFETY_FEASIBILITY_ASSISTANT = """
True

Explanation: The user's request involves known ingredients (avocado, sausage, and bacon) that can be found in the list of known ingredients (No. 1, 23 and 3) and a reasonable modification (adding bacon), making it safe and feasible for the assistant to execute.
"""

THIRD_SHOT_SAFETY_FEASIBILITY_USER = """
User: I want the bacon and eggs sandwich but can you add 500 eggs?
"""

THIRD_SHOT_SAFETY_FEASIBILITY_ASSISTANT = """
False

Explanation: The user's request involves an illogical quantity of eggs (500), making it not safe or feasible for the assistant to execute.
"""
# create the Predefined Feasibility Check message
PREDEFINED_SAFETY_FEASIBILITY = [
            {"role": "system", "content": PRE_PROMPT_SAFETY_FEASIBILITY},
            {"role": "user", "content": FIRST_SHOT_SAFETY_FEASIBILITY_USER},
            {"role": "assistant", "content": FIRST_SHOT_SAFETY_FEASIBILITY_ASSISTANT},
            {"role": "user", "content": SECOND_SHOT_SAFETY_FEASIBILITY_USER},
            {"role": "assistant", "content": SECOND_SHOT_SAFETY_FEASIBILITY_ASSISTANT},
            {"role": "user", "content": THIRD_SHOT_SAFETY_FEASIBILITY_USER},
            {"role": "assistant", "content": THIRD_SHOT_SAFETY_FEASIBILITY_ASSISTANT}
        ]

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

# Convert Python objects to JSON strings
format_scheme_new_seq_json = json.dumps(format_scheme_new_seq)
available_functions_json = json.dumps(available_functions)
ingredients_list_json = json.dumps(ingredients_list)
known_sequences_json = json.dumps(known_sequences)

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
Step 5: fry_bacon(3)
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