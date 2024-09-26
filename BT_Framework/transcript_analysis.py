import re
from datetime import datetime

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

    # Output the result
    print(f"The Baseline took a total of {total_turns_baseline} turns.")
    print(f"The BT took a total of {total_turns_bt} turns.")
    print(f"Total time spent with Baseline: {total_time_baseline:.2f} minutes")
    print(f"Total time spent with BT: {total_time_bt:.2f} minutes")

# Example input (using the sample provided)
example_transcript = """
Participant 05
RunID A
Version: 1.3
Tue Sep 17 13:13:51 2024
Furhat is being used with Baseline
Assistant: Hello! I am Gregory, your home assistant. How can I help you today?
User: hi Gregory can you please make me a grilled tomato mushroom bruschetta 
Time: Tue Sep 17 13:14:04 2024
Assistant: Great choice! I will start the task for: grilled tomato and mushroom bruschetta.
Time: Tue Sep 17 13:14:05 2024
Run number: 1 ended at: Tue Sep 17 13:14:05 2024
This run took 1 turns
Total number of LLM calls: 1

Version: 1.3
Tue Sep 17 13:14:10 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hi can you please suggest something sweet Savory or healthy from the list 
Time: Tue Sep 17 13:14:27 2024
Assistant: It sounds like you're looking for something tasty! Here are three options from my list that cover sweet, savory, or healthy:

1. **Pancakes with Maple Syrup and Berries** - A sweet option that's perfect for breakfast or a snack.
2. **Avocado Toast with Sausage on the Side** - A savory choice that includes healthy fats from the avocado and protein from the sausage.
3. **Vegetable Stir Fry with Rice** - A healthy and savory dish loaded with vegetables.

Please let me know which one you�d like to proceed with!
Time: Tue Sep 17 13:14:29 2024
User: the vegetable stir fry with the rice sounds really nice that'd be good 
Time: Tue Sep 17 13:15:06 2024
Assistant: Great choice! I will start the task for: **vegetable stir fry with rice**.
Time: Tue Sep 17 13:15:07 2024
Run number: 2 ended at: Tue Sep 17 13:15:07 2024
This run took 2 turns
Total number of LLM calls: 2

Version: 1.3
Tue Sep 17 13:15:13 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hi regarding the vegetable stir fry with the rice instead of rice can you make it with noodles 
Time: Tue Sep 17 13:15:30 2024
Assistant: Unfortunately, my current capabilities do not include modifying recipes to substitute rice with noodles, as noodles are not part of the predefined ingredients or tasks I can perform. However, I can still prepare a vegetable stir fry with rice according to the original sequence.

Would you like me to proceed with the vegetable stir fry with rice? Let me know!
Time: Tue Sep 17 13:15:31 2024
User: yes that'd be good please 
Time: Tue Sep 17 13:15:55 2024
Assistant: Great choice! I will start the task for: vegetable stir fry with rice.
Time: Tue Sep 17 13:15:56 2024
Run number: 3 ended at: Tue Sep 17 13:15:56 2024
This run took 3 turns
Total number of LLM calls: 2

Version: 1.3
Tue Sep 17 13:16:02 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: can you please um wash your dishes 
Time: Tue Sep 17 13:16:15 2024
Assistant: I apologize, but washing dishes is currently outside of my capabilities. I can assist with food preparation and cleaning tasks such as vacuuming and mopping floors. If there's a specific task related to food or cleaning that I can help you with, please let me know!
Time: Tue Sep 17 13:16:16 2024
Assistant: I am sorry. I did not get that. Can you please repeat?
User: Gregory can you please meet me something nice for breakfast that sweet and healthy 
Time: Tue Sep 17 13:16:56 2024
Assistant: It seems your request is a bit vague regarding the specifics. However, I can prepare options such as pancakes with maple syrup and berries or avocado toast, both of which can be sweet and healthy. 

Which one would you prefer?
Time: Tue Sep 17 13:16:57 2024
Assistant: I am sorry. I did not get that. Can you please repeat?
User: some avocado toast 
Time: Tue Sep 17 13:17:24 2024
Assistant: Great choice! I will start the task for: avocado toast with sausage on the side.
Time: Tue Sep 17 13:17:24 2024
Run number: 4 ended at: Tue Sep 17 13:17:24 2024
This run took 4 turns
Total number of LLM calls: 3

Run number: 5 ended at: Tue Sep 17 13:17:29 2024
This run took 5 turns
Total number of LLM calls: 0

Version: 1.3
Tue Sep 17 13:22:45 2024
Tree is initialized and furhat is used

Assistant: Hello! I am Gregory, your home assistant. How can I help you today?
User: hi Gregory can you please make me a full English breakfast 
Is it ambiguous? False
Time: Tue Sep 17 13:22:46 2024
Is it known? True
Time: Tue Sep 17 13:22:46 2024
var_KnowNo: ['full English breakfast']
Time: Tue Sep 17 13:22:48 2024
Does it map to the action in var_KnowNo? True
Time: Tue Sep 17 13:22:49 2024
Assistant: Great choice! I will get the task for full English breakfast started.
Time: Tue Sep 17 13:22:49 2024
Run number: 1 ended at: Tue Sep 17 13:22:49 2024
This run took 3 turns
Total number of LLM calls: 5

Run: 2
Tue Sep 17 13:23:06 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: why can you please suggest something healthy from the list 
Is it ambiguous? True
Time: Tue Sep 17 13:23:06 2024
Assistant: There are multiple options in my list that might fit your order. Here are a few healthy options you can consider: 
1. 'Vegetable stir fry with rice' 
2. 'Avocado toast with sausage on the side'
3. 'Tortilla with tomatoes, beans, and egg (huevos rancheros)' 

Let me know if any of these sound good to you!
Time: Tue Sep 17 13:23:08 2024
User: hi the 2 3 the tortilla sounds very nice can you please make it for me 
Time: Tue Sep 17 13:23:36 2024
Is it ambiguous? False
Time: Tue Sep 17 13:23:36 2024
Is it known? True
Time: Tue Sep 17 13:23:37 2024
var_KnowNo: ['tortilla with tomatoes beans and egg (huevos rancheros)']
Time: Tue Sep 17 13:23:39 2024
Does it map to the action in var_KnowNo? True
Time: Tue Sep 17 13:23:39 2024
Assistant: Great choice! I will get the task for tortilla with tomatoes beans and egg (huevos rancheros) started.
Time: Tue Sep 17 13:23:39 2024
Run number: 2 ended at: Tue Sep 17 13:23:39 2024
This run took 5 turns
Total number of LLM calls: 7

Run: 3
Tue Sep 17 13:24:05 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hi Gregory can you please make me a peanut butter and jelly sandwich without the jelly 
Is it ambiguous? False
Time: Tue Sep 17 13:24:05 2024
Is it known? False
Time: Tue Sep 17 13:24:06 2024
Is it within the capabilities of the robot? True
Time: Tue Sep 17 13:24:06 2024
Is a new sequence requested?: True
Time: Tue Sep 17 13:24:07 2024
Is a new sequence actually requested? True
Time: Tue Sep 17 13:24:07 2024
Did it pass the safety check?: True
Explanation: The request involves known ingredients (peanut butter and bread) that can be found in the list of known ingredients (No. 10 and 28), making it feasible for me to execute.
Time: Tue Sep 17 13:24:08 2024
The generated sequence is: {"sequence": [{"step": "1", "action": "toast_bread(2)"}, {"step": "2", "action": "spread_on_bread(peanut_butter)"}, {"step": "3", "action": "combine_breads(peanut_butter_toast, toasted_bread)"}, {"step": "4", "action": "serve()"}]}
Time: Tue Sep 17 13:24:10 2024
Assistant: Sure, I'll perform a new set of steps to fulfill your request for a peanut butter and jelly sandwich without the jelly. 

First, I will toast two slices of bread. 
Next, I'll spread peanut butter on one of the toasted slices. 
After that, I'll combine the two slices of bread together. 
Finally, I will serve the sandwich. 

Does this sequence sound good to you?
Time: Tue Sep 17 13:24:11 2024
var_generated_sequence_name is: peanut butter sandwich without jelly
Time: Tue Sep 17 13:24:11 2024
User:yes it does thank you 
Time: Tue Sep 17 13:24:37 2024
Assistant: Great then I will now proceed to make the: peanut butter sandwich without jelly
Time: Tue Sep 17 13:24:38 2024
Run number: 3 ended at: Tue Sep 17 13:24:38 2024
This run took 4 turns
Total number of LLM calls: 8

Run: 4
Tue Sep 17 13:24:54 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: Gregory can you please make me an iced latte 
Is it ambiguous? False
Time: Tue Sep 17 13:24:55 2024
Is it known? False
Time: Tue Sep 17 13:24:55 2024
Is it within the capabilities of the robot? False
Time: Tue Sep 17 13:24:56 2024
Assistant: Your request seems to be outside of my capabilities. Please let me know a new different request.
Time: Tue Sep 17 13:24:57 2024
Assistant: I am sorry. I did not get that. Can you please repeat?
User: hi Gregory can you please make me some spaghetti 
Time: Tue Sep 17 13:25:28 2024
Is it ambiguous? True
Time: Tue Sep 17 13:25:29 2024
Assistant: I'm sorry, but making spaghetti is outside the scope of my capabilities. However, I can offer you options like a 'bacon and egg sandwich', 'vegetable stir fry with rice', or 'bean and cheese quesadilla'. Please let me know if any of these options interest you, or if you have another request!
Time: Tue Sep 17 13:25:31 2024
User: can you please make me a bean and cheese cases deal 
Time: Tue Sep 17 13:25:52 2024
Is it ambiguous? False
Time: Tue Sep 17 13:25:53 2024
Is it known? True
Time: Tue Sep 17 13:25:53 2024
var_KnowNo: ['bean and cheese quesadilla']
Time: Tue Sep 17 13:25:55 2024
Does it map to the action in var_KnowNo? True
Time: Tue Sep 17 13:25:56 2024
Assistant: Great choice! I will get the task for bean and cheese quesadilla started.
Time: Tue Sep 17 13:25:56 2024
Run number: 4 ended at: Tue Sep 17 13:25:56 2024
This run took 7 turns
Total number of LLM calls: 11

Run: 5
Tue Sep 17 13:26:16 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hi can you please make me something Italian 
Is it ambiguous? True
Time: Tue Sep 17 13:26:17 2024
Assistant: There are multiple options in my list that might fit your order. I'm sorry, but Italian dishes are outside the scope of my known sequences. However, I can suggest something similar that you might enjoy, like a 'grilled tomato and mushroom bruschetta', which has some Italian flavors. Would you like that?
Time: Tue Sep 17 13:26:18 2024
User: yes please that sounds good 
Time: Tue Sep 17 13:26:40 2024
Is it ambiguous? False
Time: Tue Sep 17 13:26:40 2024
Is it known? True
Time: Tue Sep 17 13:26:41 2024
var_KnowNo: ['grilled tomato and mushroom bruschetta']
Time: Tue Sep 17 13:26:43 2024
Does it map to the action in var_KnowNo? True
Time: Tue Sep 17 13:26:43 2024
Assistant: Great choice! I will get the task for grilled tomato and mushroom bruschetta started.
Time: Tue Sep 17 13:26:43 2024
Run number: 5 ended at: Tue Sep 17 13:26:43 2024
This run took 5 turns
Total number of LLM calls: 7
"""

# Run the analysis
analyze_transcript(example_transcript)
