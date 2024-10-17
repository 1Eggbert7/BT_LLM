import re
from datetime import datetime
import json

def check_json(sequence_str, functions_file='functions.json', ingredients_file='ingredients.json'):
    """
    This function checks if the provided sequence (as a string) is valid JSON and conforms to the format
    and function requirements defined in the original CheckNewSeq class.
    """

    def load_json(filepath):
        """This function loads a JSON file."""
        with open(filepath, 'r') as file:
            return json.load(file)

    def check_sequence_format(sequence):
        """This function checks the format of the sequence."""
        found_errors = []
        if not sequence or not isinstance(sequence, dict):
            return False, "The sequence is empty or not properly formatted."

        for step in sequence.get("sequence", []):
            if "step" not in step:
                found_errors.append("Each step must contain 'step' and 'action' fields. 'step' is missing.")
            if "action" not in step:
                found_errors.append("Each step must contain 'step' and 'action' fields. 'action' is missing.")
            if not isinstance(step.get("step", ""), str):
                found_errors.append("Step number must be a string.")
            if not isinstance(step.get("action", ""), str):
                found_errors.append("Action must be a string.")

        if found_errors:
            return False, "The sequence contains errors: " + ", ".join(found_errors)
        return True, "Sequence format is valid."

    def check_functions_exist(sequence, functions, ingredients):
        """This function checks if the functions in the sequence exist in the functions list and if the parameters are correct."""
        found_errors = []
        for step in sequence.get("sequence", []):
            action = step.get("action", "")
            func_name = action.split("(")[0]

            # Extract parameters from action
            params = action[action.find("(") + 1 : action.find(")")].split(",")
            params = [p.strip() for p in params if p.strip()]

            function_found = False
            for full_func_name in functions.get("functions", {}).keys():
                if full_func_name.startswith(func_name + "("):
                    function_found = True
                    func_signature = full_func_name
                    expected_params = func_signature[func_signature.find("(") + 1 : func_signature.find(")")].split(",")
                    expected_params = [p.strip() for p in expected_params if p.strip()]

                    # Check parameter count and types
                    if len(params) != len(expected_params):
                        found_errors.append(f"Function '{func_signature}' expects {len(expected_params)} parameters, but {len(params)} were provided.")
                    else:
                        for i, expected_param in enumerate(expected_params):
                            if expected_param == "number" and not params[i].isnumeric():
                                found_errors.append(f"Function '{func_signature}' expects parameter {i} to be a number, but '{params[i]}' was provided.")
                            elif expected_param == "item" and params[i] not in ingredients.get("ingredients", []):
                                found_errors.append(f"Function '{func_signature}' expects parameter {i} to be an item, but '{params[i]}' was provided.")
                            elif expected_param == "sandwich_item" and params[i] not in ["avocado_toast", "jelly_toast", "peanut_butter_toast", "toasted_bread"]:
                                found_errors.append(f"Function '{func_signature}' expects parameter {i} to be a sandwich item, but '{params[i]}' was provided.")
                    break

            if not function_found:
                found_errors.append(f"Function '{func_name}' does not exist in the functions list.")

        if found_errors:
            return False, "Errors found in the sequence: " + ", ".join(found_errors)
        return True, "All functions exist and parameters are valid."

    # 1. Check if the string is valid JSON
    try:
        sequence = json.loads(sequence_str)
    except json.JSONDecodeError as e:
        return False, f"Error decoding JSON: {e}"

    # 2. Check the format of the sequence
    format_check, format_message = check_sequence_format(sequence)
    if not format_check:
        return False, format_message

    # 3. Check the functions and parameters
    functions = load_json(functions_file)
    ingredients = load_json(ingredients_file)
    functions_check, functions_message = check_functions_exist(sequence, functions, ingredients)
    if not functions_check:
        return False, functions_message

    # If everything passed, return success
    return True, "The sequence is valid."



def analyze_transcript(transcript: str):
    # Initialize counters and variables
    total_turns_baseline = 0
    total_turns_bt = 0
    start_time_baseline = None
    end_time_baseline = None
    start_time_bt = None
    end_time_bt = None
    current_mode = None
    prev_line = ''
    prev_speaker = None
    last_timestamp = None
    
    # Split the transcript into lines
    lines = transcript.splitlines()
    
    # Regular expression patterns
    run_end_pattern = re.compile(r"Run number: (\d+) ended at: (.+)")
    run_start_pattern = re.compile(r"Run[: ](\d+)")
    mode_pattern_baseline = re.compile(r"Furhat is being used with Baseline")
    mode_pattern_bt = re.compile(r"Tree is initialized and furhat is used")
    timestamp_pattern = re.compile(r'^\w{3} \w{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4}$')
    assistant_line_pattern = re.compile(r'^Assistant:')
    user_line_pattern = re.compile(r'^User:')
    apology_line = 'Assistant: I am sorry. I did not get that. Can you please repeat?'
    
    # Loop through each line
    for line in lines:
        line = line.strip()
        
        # Check for timestamp
        if timestamp_pattern.match(line):
            last_timestamp = datetime.strptime(line, "%a %b %d %H:%M:%S %Y")
        
        # Check for mode change to Baseline
        if mode_pattern_baseline.search(line):
            # Set end time for previous mode
            if current_mode == "BT" and end_time_bt is None:
                end_time_bt = last_timestamp
            current_mode = "Baseline"
            if start_time_baseline is None:
                start_time_baseline = last_timestamp
        # Check for mode change to BT
        elif mode_pattern_bt.search(line):
            # Set end time for previous mode
            if current_mode == "Baseline" and end_time_baseline is None:
                end_time_baseline = last_timestamp
            current_mode = "BT"
            if start_time_bt is None:
                start_time_bt = last_timestamp

        # Check for run end (update end times)
        run_end_match = run_end_pattern.search(line)
        if run_end_match and current_mode:
            end_time_str = run_end_match.group(2).strip()
            end_time = datetime.strptime(end_time_str, "%a %b %d %H:%M:%S %Y")
            if current_mode == "Baseline":
                end_time_baseline = end_time
            elif current_mode == "BT":
                end_time_bt = end_time

        # Check for speaker lines
        if assistant_line_pattern.match(line):
            current_speaker = "Assistant"
            # Special case: Do not count the turn if the Assistant repeats "I am sorry..."
            if prev_speaker == "Assistant" and line == apology_line:
                pass  # Do not count this turn
            else:
                if current_mode == "Baseline":
                    total_turns_baseline += 1
                elif current_mode == "BT":
                    total_turns_bt += 1
            # Update previous speaker
            prev_speaker = current_speaker
        elif user_line_pattern.match(line):
            current_speaker = "User"
            if current_mode == "Baseline":
                total_turns_baseline += 1
            elif current_mode == "BT":
                total_turns_bt += 1
            # Update previous speaker
            prev_speaker = current_speaker
        else:
            # Do not update prev_speaker if line is not a speaker line
            current_speaker = None

    # After processing all lines, set end time for the last mode if not already set
    if current_mode == "Baseline" and end_time_baseline is None:
        end_time_baseline = last_timestamp
    elif current_mode == "BT" and end_time_bt is None:
        end_time_bt = last_timestamp

    # Calculate total time spent in minutes
    total_time_baseline = (end_time_baseline - start_time_baseline).total_seconds() / 60 if start_time_baseline and end_time_baseline else 0
    total_time_bt = (end_time_bt - start_time_bt).total_seconds() / 60 if start_time_bt and end_time_bt else 0

    # Convert baseline time
    baseline_minutes, baseline_seconds = minutes_to_minutes_seconds(total_time_baseline)
    bt_minutes, bt_seconds = minutes_to_minutes_seconds(total_time_bt)

    # Output the result with zero-padded seconds
    print(f"Baseline TTR: {total_turns_baseline}")
    print(f"BT TTR: {total_turns_bt}")
    print(f"Total Baseline: {baseline_minutes}:{baseline_seconds:02d} minutes")
    print(f"Total BT: {bt_minutes}:{bt_seconds:02d} minutes")



# Function to convert minutes to minutes and seconds
def minutes_to_minutes_seconds(total_minutes):
    minutes = int(total_minutes)
    seconds = int((total_minutes - minutes) * 60)
    return minutes, seconds


# Example input (using the sample provided)
example_transcript = """
Paricipant 26
RunID B
Version: 1.3
Fri Sep 20 14:52:07 2024
Tree is initialized and furhat is used

Assistant: Hello! I am Gregory, your home assistant. How can I help you today?
User: perform a task for me bacon and egg sandwich
Is it ambiguous? False
Time: Fri Sep 20 14:52:07 2024
Is it known? True
Time: Fri Sep 20 14:52:08 2024
var_KnowNo: ['bacon and egg sandwich']
Time: Fri Sep 20 14:52:11 2024
Does it map to the action in var_KnowNo? True
Time: Fri Sep 20 14:52:12 2024
Assistant: Great choice! I will get the task for bacon and egg sandwich started.
Time: Fri Sep 20 14:52:12 2024
Run number: 1 ended at: Fri Sep 20 14:52:12 2024
This run took 3 turns
Total number of LLM calls: 5

Run: 2
Fri Sep 20 14:52:31 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hello I want to suggest me something healthy to eat 
Is it ambiguous? True
Time: Fri Sep 20 14:52:35 2024
Assistant: There are multiple options in my list that might fit your order. For a healthy option, I recommend:
1. Avocado toast with sausage on the side
2. Vegetable stir fry with rice
3. A bean and cheese quesadilla (as it's a good source of protein).

Let me know if any of these options sound good to you!
Time: Fri Sep 20 14:52:37 2024
User: opotion 1
Time: Fri Sep 20 14:53:08 2024
Is it ambiguous? False
Time: Fri Sep 20 14:53:09 2024
Is it known? True
Time: Fri Sep 20 14:53:09 2024
var_KnowNo: ['avocado toast with sausage on the side']
Time: Fri Sep 20 14:53:13 2024
Does it map to the action in var_KnowNo? True
Time: Fri Sep 20 14:53:13 2024
Assistant: Great choice! I will get the task for avocado toast with sausage on the side started.
Time: Fri Sep 20 14:53:13 2024
Run number: 2 ended at: Fri Sep 20 14:53:13 2024
This run took 5 turns
Total number of LLM calls: 7

Run: 3
Fri Sep 20 14:53:35 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hello pancakes but with chocolate 
Is it ambiguous? True
Time: Fri Sep 20 14:53:35 2024
Assistant: There are multiple options in my list that might fit your order. I understand you're looking for pancakes, which I can make for you. However, I don't specifically have a recipe for pancakes with chocolate. I can prepare regular 'pancakes with maple syrup and berries' for you instead. Would you like me to proceed with that?
Time: Fri Sep 20 14:53:37 2024
User: do I have other options 
Time: Fri Sep 20 14:54:00 2024
Is it ambiguous? True
Time: Fri Sep 20 14:54:00 2024
Assistant: There are multiple options in my list that might fit your order. Here are some other options you might consider instead of pancakes:
1. A 'full English breakfast'
2. A 'vegetable stir fry with rice'
3. A 'bacon and egg sandwich'

Let me know if any of these options sound good to you, or if you'd like to combine pancakes with another dish!
Time: Fri Sep 20 14:54:02 2024
User: can I customize the sandwich 
Time: Fri Sep 20 14:54:28 2024
Is it ambiguous? True
Time: Fri Sep 20 14:54:29 2024
Assistant: There are multiple options in my list that might fit your order. I can certainly help with customizing the 'bacon and egg sandwich'. Please let me know what specific changes or additions you would like to make to the sandwich, and I'll prepare it accordingly!
Time: Fri Sep 20 14:54:31 2024
User: can you add tomatoes and cucumber 
Time: Fri Sep 20 14:54:51 2024
Is it ambiguous? False
Time: Fri Sep 20 14:54:53 2024
Is it known? False
Time: Fri Sep 20 14:54:53 2024
Is it within the capabilities of the robot? True
Time: Fri Sep 20 14:54:54 2024
Is a new sequence requested?: True
Time: Fri Sep 20 14:54:55 2024
Is a new sequence actually requested? True
Time: Fri Sep 20 14:54:55 2024
Did it pass the safety check?: False
Explanation: The request involves an unknown ingredient (cucumber) that can't be found in the provided list of known ingredients, making it not feasible for me to execute.
Time: Fri Sep 20 14:54:57 2024
Assistant: I'm sorry, but i can't fulfill your request it is unsafe or unfeasible to me. The reason is: The request involves an unknown ingredient (cucumber) that can't be found in the provided list of known ingredients, making it not feasible for me to execute.
Time: Fri Sep 20 14:54:57 2024
User: then just add the tomato
Time: Fri Sep 20 14:55:24 2024
Is it ambiguous? False
Time: Fri Sep 20 14:55:26 2024
Is it known? False
Time: Fri Sep 20 14:55:26 2024
Is it within the capabilities of the robot? True
Time: Fri Sep 20 14:55:27 2024
Is a new sequence requested?: True
Time: Fri Sep 20 14:55:27 2024
Is a new sequence actually requested? True
Time: Fri Sep 20 14:55:28 2024
Did it pass the safety check?: True
Explanation: The request involves known ingredients (bacon, egg, bread, and tomatoes) that can be found in the list of known ingredients (No. 3 and 28), making it feasible for me to execute.
Time: Fri Sep 20 14:55:29 2024
The generated sequence is: {"sequence": [{"step": "1", "action": "toast_bread(2)"}, {"step": "2", "action": "fry_eggs(1)"}, {"step": "3", "action": "initiate_sandwich(toasted_bread)"}, {"step": "4", "action": "place_on_sandwich(fried_egg, 1)"}, {"step": "5", "action": "cook_bacon(2)"}, {"step": "6", "action": "place_on_sandwich(fried_bacon, 2)"}, {"step": "7", "action": "place_on_sandwich(grilled_tomatoes, 1)"}, {"step": "8", "action": "place_on_sandwich(toasted_bread, 1)"}, {"step": "9", "action": "serve()"}]}
Time: Fri Sep 20 14:55:33 2024
Assistant: Sure! To fulfill your request for the customized bacon and egg sandwich, I will take the following steps:

First, I will toast two slices of bread. 
Then, I will fry one egg. 
Next, I will initiate the sandwich by using the toasted bread. 
After that, I'll place the fried egg on the sandwich. 
Following this, I'll cook two pieces of bacon and place them on the sandwich. 
Next, I'll add grilled tomatoes to the sandwich. 
Finally, I'll place the other slice of toasted bread on top and serve the sandwich.

Does this sequence sound good to you?
Time: Fri Sep 20 14:55:35 2024
var_generated_sequence_name is: customized bacon and egg sandwich with tomato
Time: Fri Sep 20 14:55:35 2024
User:yes thank you 
Time: Fri Sep 20 14:56:12 2024
Assistant: Great then I will now proceed to make the: customized bacon and egg sandwich with tomato
Time: Fri Sep 20 14:56:14 2024
Run number: 3 ended at: Fri Sep 20 14:56:14 2024
This run took 12 turns
Total number of LLM calls: 20

Run: 4
Fri Sep 20 14:56:30 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hello I want to make a coffee for me 
Is it ambiguous? True
Time: Fri Sep 20 14:56:31 2024
Assistant: I appreciate your request, but unfortunately, making coffee is outside the scope of my capabilities. However, I can prepare a delicious 'bacon and egg sandwich' or perhaps some 'pancakes with maple syrup and berries' if you're interested. Let me know what you'd like!
Time: Fri Sep 20 14:56:33 2024
User: no I want something to drink do you have any option for 
Time: Fri Sep 20 14:56:56 2024
Is it ambiguous? True
Time: Fri Sep 20 14:56:57 2024
Assistant: I appreciate your request, but unfortunately, making drinks is outside the scope of my capabilities. However, I can offer you some tasty food options, such as a 'peanut butter and jelly sandwich', a 'vegetable stir fry with rice', or a 'grilled tomato and mushroom bruschetta'. Let me know if you would like any of these or if you have something else in mind!
Time: Fri Sep 20 14:56:59 2024
User: skip
Time: Fri Sep 20 14:57:23 2024
Run number: 4 ended at: Fri Sep 20 14:57:23 2024
This run took 6 turns
Total number of LLM calls: 4

Run: 5
Fri Sep 20 14:57:48 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hello I want to prepare for me a breakfast sausages tomatoes and any other ingredient that you can suggest 
Is it ambiguous? True
Time: Fri Sep 20 14:57:49 2024
Assistant: There are multiple options in my list that might fit your order. Based on your request for sausages and tomatoes for breakfast, I recommend the 'full English breakfast'. It includes sausages, tomatoes, bacon, beans, mushrooms, toast, and fried eggs. Would you like me to prepare that for you?
Time: Fri Sep 20 14:57:50 2024
User: yes please I would appreciate that 
Time: Fri Sep 20 14:58:13 2024
Is it ambiguous? False
Time: Fri Sep 20 14:58:14 2024
Is it known? True
Time: Fri Sep 20 14:58:15 2024
var_KnowNo: ['full English breakfast']
Time: Fri Sep 20 14:58:18 2024
Does it map to the action in var_KnowNo? True
Time: Fri Sep 20 14:58:18 2024
Assistant: Great choice! I will get the task for full English breakfast started.
Time: Fri Sep 20 14:58:18 2024
Run number: 5 ended at: Fri Sep 20 14:58:18 2024
This run took 5 turns
Total number of LLM calls: 7

Version: 1.3
Fri Sep 20 15:05:47 2024
Furhat is being used with Baseline
Assistant: Hello! I am Gregory, your home assistant. How can I help you today?
User: hello uh I want to make for me pancakes with syrup and and berries 
Time: Fri Sep 20 15:06:01 2024
Assistant: Great choice! I will start the task for: pancakes with maple syrup and berries.
Time: Fri Sep 20 15:06:02 2024
Run number: 1 ended at: Fri Sep 20 15:06:02 2024
This run took 1 turns
Total number of LLM calls: 1

Version: 1.3
Fri Sep 20 15:06:07 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hello I want the suggestion for something sweet to eat 
Time: Fri Sep 20 15:06:23 2024
Assistant: It seems you�re looking for something sweet to eat! Here are three sweet options I can prepare for you:

1. Pancakes with maple syrup and berries
2. Peanut butter and jelly sandwich
3. Avocado toast (though this is more of a savory option, it can be sweetened with honey if desired)

Please let me know if any of these options sound good to you, or if you'd like me to suggest something else!
Time: Fri Sep 20 15:06:25 2024
User: let's go with peanut butter and jelly sandwich 
Time: Fri Sep 20 15:06:55 2024
Assistant: Great choice! I will start the task for: peanut butter and jelly sandwich.
Time: Fri Sep 20 15:06:56 2024
Run number: 2 ended at: Fri Sep 20 15:06:56 2024
This run took 2 turns
Total number of LLM calls: 2

Version: 1.3
Fri Sep 20 15:07:02 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hello uh I want and been and cheese but um some modifications  
Time: Fri Sep 20 15:07:31 2024
Assistant: It seems like you'd like to make modifications to the bean and cheese quesadilla, but I need more specific details about your request. Could you please clarify what changes you'd like to make? 

Here are a few options you could choose from:
1. Would you like to add any extra ingredients to the quesadilla?
2. Do you want the tortilla heated differently or the beans prepared in a specific way?
3. Would you like a different cooking method or additional toppings?

Let me know how you'd like to proceed!
Time: Fri Sep 20 15:07:33 2024
User: what different cooking method do you have 
Time: Fri Sep 20 15:08:08 2024
Assistant: My cooking methods are generally predefined for specific tasks. For the bean and cheese quesadilla, I can cook it using the following methods:

1. **Cook quesadilla**: This involves placing the filled tortilla on a hot surface until the exterior is crispy and the cheese inside melts.

Here�s the sequence for the bean and cheese quesadilla as per the standard method:

1. Heat the beans.
2. Prepare the tortilla.
3. Place the heated beans on the tortilla.
4. Add cheese.
5. Cook the quesadilla.
6. Serve.

If you have specific modifications in mind, like choosing a different ingredient or cooking it with a different style (e.g., frying instead of grilling), please let me know! Otherwise, I can proceed with the standard cooking method for the quesadilla.
Time: Fri Sep 20 15:08:11 2024
User: yes fry it
Time: Fri Sep 20 15:09:13 2024
Assistant: Frying the quesadilla instead of cooking it on a hot surface isn't part of my predefined capabilities, as I can only cook it in the manner specified. However, I can go ahead with the traditional cooking method for the bean and cheese quesadilla.

Here�s the standard sequence I will follow:

1. Heat the beans.
2. Prepare the tortilla.
3. Place the heated beans on the tortilla.
4. Add cheese.
5. Cook the quesadilla (as per the regular method used).
6. Serve.

If that works for you, let me know, and I'll start the task!
Time: Fri Sep 20 15:09:16 2024
User:  vegan cheese over the regular cheese 
Time: Fri Sep 20 15:10:04 2024
Assistant: I currently do not have vegan cheese listed in my ingredients, so I can't fulfill that specific part of your request. However, I can proceed with the standard bean and cheese quesadilla using regular cheese.

Here�s the sequence I will follow for the bean and cheese quesadilla:

1. Heat the beans.
2. Prepare the tortilla.
3. Place the heated beans on the tortilla.
4. Add cheese.
5. Cook the quesadilla.
6. Serve.

Let me know if you'd like me to start this task or if you have any other specific requests!
Time: Fri Sep 20 15:10:06 2024
User: let's go on with this 1 
Time: Fri Sep 20 15:10:46 2024
Assistant: Great choice! I will start the task for: bean and cheese quesadilla.
Time: Fri Sep 20 15:10:47 2024
Run number: 3 ended at: Fri Sep 20 15:10:47 2024
This run took 3 turns
Total number of LLM calls: 5

Version: 1.3
Fri Sep 20 15:10:53 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hello uh I want to sing a song for me 
Time: Fri Sep 20 15:11:07 2024
Assistant: I'm here to assist with tasks related to food preparation and cleaning, but singing isn�t within my capabilities. If there's something else I can help you with, such as preparing a meal or cleaning a space, just let me know!
Time: Fri Sep 20 15:11:08 2024
User: skip
Time: Fri Sep 20 15:11:25 2024
Run number: 4 ended at: Fri Sep 20 15:11:25 2024
This run took 4 turns
Total number of LLM calls: 2

Version: 1.3
Fri Sep 20 15:11:27 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
Assistant: I am sorry. I did not get that. Can you please repeat?
User: yes I won the toss with avocado  
Time: Fri Sep 20 15:12:30 2024
Assistant: It seems that your request is a bit unclear. Could you please provide more specific details about what you would like to do with avocado? 

Here are some options I can prepare that involve avocado:
1. Avocado toast with sausage on the side
2. Bacon and egg sandwich (if you'd like to modify it with avocado, I can prepare a new sequence)
3. Ask me to prepare something else using avocado

Please clarify your preference!
Time: Fri Sep 20 15:12:32 2024
User: the first 1 please 
Time: Fri Sep 20 15:13:03 2024
Assistant: Great choice! I will start the task for: avocado toast with sausage on the side.
Time: Fri Sep 20 15:13:03 2024
Run number: 5 ended at: Fri Sep 20 15:13:03 2024
This run took 5 turns
Total number of LLM calls: 2

Notes:

  Times: 14:42 - 15:30

  Overall:
    - STT bad because of bad pronounciation

  Base:
    - Lied on sweet suggestions and suggested avocado toast with honey again...

End of Paricipant 26 experiment 
"""

# Run the analysis
analyze_transcript(example_transcript)



json_string = """
{"sequence": [
{"step": "1", "action": "toast_bread(2)"}, 
{"step": "2", "action": "fry_eggs(1)"}, 
{"step": "3", "action": "initiate_sandwich(toasted_bread)"}, 
{"step": "4", "action": "place_on_sandwich(fried_egg, 1)"}, 
{"step": "5", "action": "cook_bacon(2)"}, 
{"step": "6", "action": "place_on_sandwich(fried_bacon, 2)"}, 
{"step": "7", "action": "place_on_sandwich(grilled_tomatoes, 1)"}, 
{"step": "8", "action": "place_on_sandwich(toasted_bread, 1)"}, 
{"step": "9", "action": "serve()"}]}
"""

result, message = check_json(json_string)
print(message)
