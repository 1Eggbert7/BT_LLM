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
Paricipant 49
RunID A
Version: 1.3
Tue Sep 24 18:16:07 2024
Furhat is being used with Baseline
Assistant: Hello! I am Gregory, your home assistant. How can I help you today?
User: uh let's see there's a lot of dirt on the floor could you clean the living room 
Time: Tue Sep 24 18:16:23 2024
Assistant: Great choice! I will start the task for: clean living room floor.
Time: Tue Sep 24 18:16:24 2024
Run number: 1 ended at: Tue Sep 24 18:16:24 2024
This run took 1 turns
Total number of LLM calls: 1

Version: 1.3
Tue Sep 24 18:16:29 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: I am feeling feeling a bit hungry mind suggesting something healthy for me 
Time: Tue Sep 24 18:16:56 2024
Assistant: I can suggest a couple of healthy options for you:

1. **Avocado Toast with Sausage on the Side** - A nutritious and filling option that combines whole grains with healthy fats and protein.
2. **Vegetable Stir Fry with Rice** - A dish packed with vitamins and fiber, along with a serving of rice for energy.

Please let me know which option you prefer, or if you'd like more details about them!
Time: Tue Sep 24 18:16:58 2024
User: I think I'll go for the 1 with stir fried rice 
Time: Tue Sep 24 18:17:30 2024
Assistant: It seems like you're interested in having **Avocado Toast with Sausage on the Side** and **Vegetable Stir Fry with Rice**. I can prepare the avocado toast with the sausages, and separately, I can make the vegetable stir fry with rice. 

First, I will start with the avocado toast with sausages on the side. Then, I will prepare the vegetable stir fry with rice. Here�s a quick overview of the first sequence I�ll execute:

- **Avocado Toast with Sausage on the Side**

Great choice! I will start the task for: **avocado toast with sausage on the side**. 

Once that's done, I will proceed with the vegetable stir fry with rice. 

Here�s the sequence for the vegetable stir fry with rice in JSON format:

```json
{
  "task": "vegetable stir fry with rice",
  "ID": "4",
  "sequence": [
    {"step": "1", "action": "cook_rice(1)"},
    {"step": "2", "action": "fry_vegetables(1)"},
    {"step": "3", "action": "place_on_plate(cooked_rice, 1)"},
    {"step": "4", "action": "place_on_plate(fried_vegetables, 1)"},
    {"step": "5", "action": "serve()"}
  ]
}
```

Let me know if you'd like any changes or if you're ready for me to begin!
Time: Tue Sep 24 18:17:38 2024
Run number: 2 ended at: Tue Sep 24 18:17:38 2024
This run took 2 turns
Total number of LLM calls: 2

Version: 1.3
Tue Sep 24 18:18:28 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: let's see I am thinking of eating some avocado toast with sausage on the side but could you put the sausage on the toast instead 
Time: Tue Sep 24 18:18:56 2024
Assistant: I can certainly help you with preparing avocado toast and grilling sausages, but based on my current abilities, I cannot modify the existing recipe to place the sausages directly on the toast. Instead, I can prepare the avocado toast and serve the sausages on the side, as originally intended.

Let's go ahead with that plan. First, I will toast one slice of bread, grill two sausages, spread mashed avocado on the toasted bread, place the grilled sausages on the plate, and serve everything together.

Here�s the new sequence in JSON format: 
```json
{
  "task": "avocado toast with sausages on the side",
  "ID": "2",
  "sequence": [
    {"step": "1", "action": "toast_bread(1)"},
    {"step": "2", "action": "grill_sausages(2)"},
    {"step": "3", "action": "spread_on_bread(avocado)"},
    {"step": "4", "action": "place_on_plate(grilled_sausages, 1)"},
    {"step": "5", "action": "serve()"}
  ]
}
```
I�m starting the task for: avocado toast with sausage on the side.
Time: Tue Sep 24 18:19:00 2024
Run number: 3 ended at: Tue Sep 24 18:19:00 2024
This run took 3 turns
Total number of LLM calls: 1

Version: 1.3
Tue Sep 24 18:19:33 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User:  I think it's time for the kid to take a nap mind putting him to sleep 
Time: Tue Sep 24 18:19:57 2024
Assistant: I'm unable to assist with putting a child to sleep, as my capabilities are focused on food preparation and cleaning tasks. However, I can help with preparing a meal or cleaning a specific area if you'd like. Let me know how I can assist you!
Time: Tue Sep 24 18:19:58 2024
User: skip
Time: Tue Sep 24 18:20:26 2024
Run number: 4 ended at: Tue Sep 24 18:20:26 2024
This run took 4 turns
Total number of LLM calls: 2

Version: 1.3
Tue Sep 24 18:20:27 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User:      let's see I want hey it's like you know bread and you put stuff in in the bread and other stuff 
Time: Tue Sep 24 18:21:24 2024
Assistant: It seems like you're looking for something that involves making a sandwich, but your request is a bit unclear. Here are three options based on what I can prepare:

1. Bacon and Egg Sandwich
2. Peanut Butter and Jelly Sandwich
3. Grilled Tomato and Mushroom Bruschetta

Could you please specify which one you would like me to make?
Time: Tue Sep 24 18:21:26 2024
User: I think what was the first 1 
Time: Tue Sep 24 18:21:55 2024
Assistant: Great choice! I will start the task for: bacon and egg sandwich.
Time: Tue Sep 24 18:21:55 2024
Run number: 5 ended at: Tue Sep 24 18:21:55 2024
This run took 5 turns
Total number of LLM calls: 2

Version: 1.3
Tue Sep 24 18:27:05 2024
Tree is initialized and furhat is used

Assistant: Hello! I am Gregory, your home assistant. How can I help you today?
User: pancakes
Is it ambiguous? True
Time: Tue Sep 24 18:27:05 2024
Assistant: There are multiple options in my list that might fit your order. It sounds like you would like pancakes. I can prepare 'pancakes with maple syrup and berries' for you. Would you like that? If you have any specific requests regarding ingredients or quantities, please let me know!
Time: Tue Sep 24 18:27:07 2024
User: yes I would like that 
Time: Tue Sep 24 18:27:28 2024
Is it ambiguous? False
Time: Tue Sep 24 18:27:29 2024
Is it known? True
Time: Tue Sep 24 18:27:29 2024
var_KnowNo: ['pancakes with maple syrup and berries']
Time: Tue Sep 24 18:27:32 2024
Does it map to the action in var_KnowNo? True
Time: Tue Sep 24 18:27:33 2024
Assistant: Great choice! I will get the task for pancakes with maple syrup and berries started.
Time: Tue Sep 24 18:27:33 2024
Run number: 1 ended at: Tue Sep 24 18:27:33 2024
This run took 5 turns
Total number of LLM calls: 7

Run: 2
Tue Sep 24 18:27:54 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: well it's been a tough week so how about you make me something sweet 
Is it ambiguous? True
Time: Tue Sep 24 18:27:55 2024
Assistant: There are multiple options in my list that might fit your order. Since you're looking for something sweet, I recommend the 'pancakes with maple syrup and berries'. They're a delicious treat! Would you like me to prepare that for you?
Time: Tue Sep 24 18:27:56 2024
User: sure yeah 
Time: Tue Sep 24 18:28:11 2024
Is it ambiguous? False
Time: Tue Sep 24 18:28:12 2024
Is it known? True
Time: Tue Sep 24 18:28:13 2024
var_KnowNo: ['pancakes with maple syrup and berries']
Time: Tue Sep 24 18:28:15 2024
Does it map to the action in var_KnowNo? True
Time: Tue Sep 24 18:28:15 2024
Assistant: Great choice! I will get the task for pancakes with maple syrup and berries started.
Time: Tue Sep 24 18:28:15 2024
Run number: 2 ended at: Tue Sep 24 18:28:15 2024
This run took 5 turns
Total number of LLM calls: 7

Run: 3
Tue Sep 24 18:28:44 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User:  so would you mind making me an avocado toast with sausages but can you put the sausages on the toast 
Is it ambiguous? False
Time: Tue Sep 24 18:28:45 2024
Is it known? False
Time: Tue Sep 24 18:28:46 2024
Is it within the capabilities of the robot? True
Time: Tue Sep 24 18:28:46 2024
Is a new sequence requested?: True
Time: Tue Sep 24 18:28:47 2024
Is a new sequence actually requested? True
Time: Tue Sep 24 18:28:47 2024
Did it pass the safety check?: True
Explanation: The request involves known ingredients (avocado and sausages) that can be found in the list of known ingredients (No. 1 and 23) and is a reasonable modification (putting sausages on the toast), making it feasible for me to execute.
Time: Tue Sep 24 18:28:49 2024
The generated sequence is: {"sequence": [{"step": "1", "action": "toast_bread(1)"}, {"step": "2", "action": "grill_sausages(2)"}, {"step": "3", "action": "spread_on_bread(avocado)"}, {"step": "4", "action": "place_on_sandwich(grilled_sausages, 2)"}, {"step": "5", "action": "serve()"}]}
Time: Tue Sep 24 18:28:52 2024
Assistant: Sure, to fulfill your request I will follow these steps. First, I'll toast one slice of bread. 
Next, I'll grill two sausages. 
After that, I'll spread avocado on the toasted bread. 
Then, I'll place the grilled sausages on top of the avocado toast. 
Finally, I'll serve the avocado toast with sausages on it. 
Does this process sound good to you?
Time: Tue Sep 24 18:28:53 2024
var_generated_sequence_name is: avocado toast with sausages
Time: Tue Sep 24 18:28:53 2024
User:yeah 
Time: Tue Sep 24 18:29:19 2024
Assistant: Great then I will now proceed to make the: avocado toast with sausages
Time: Tue Sep 24 18:29:20 2024
Run number: 3 ended at: Tue Sep 24 18:29:20 2024
This run took 4 turns
Total number of LLM calls: 8

Run: 4
Tue Sep 24 18:29:42 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: um I think is full of unwashed dishes could you put them in the washing machine 
Is it ambiguous? True
Time: Tue Sep 24 18:29:43 2024
Assistant: I'm sorry, but putting dishes in the washing machine is outside the scope of my capabilities. However, I can assist you in cleaning the living room floor if that's something you'd like. Would you like me to help with that instead?
Time: Tue Sep 24 18:29:45 2024
User: no it's quite clean 
Time: Tue Sep 24 18:30:01 2024
Is it ambiguous? True
Time: Tue Sep 24 18:30:02 2024
Assistant: There are multiple options in my list that might fit your order. Since I can't help with washing dishes, how about I suggest something else? I could prepare you a meal like a 'bacon and egg sandwich', 'vegetable stir fry with rice', or 'grilled tomato and mushroom bruschetta'. Would any of those options work for you?
Time: Tue Sep 24 18:30:03 2024
User: skip
Time: Tue Sep 24 18:30:35 2024
Run number: 4 ended at: Tue Sep 24 18:30:35 2024
This run took 6 turns
Total number of LLM calls: 4

Run: 5
Tue Sep 24 18:31:21 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: mine helped me like clear out some things 
Is it ambiguous? True
Time: Tue Sep 24 18:31:21 2024
Assistant: It seems like you're asking for help with cleaning. Could you please clarify if you'd like me to clean a specific area, such as the living room floor, or assist you in organizing items? Let me know how I can assist you further!
Time: Tue Sep 24 18:31:22 2024
User:  yeah that's the it's where we sit around and watch the 
Time: Tue Sep 24 18:31:47 2024
Is it ambiguous? True
Time: Tue Sep 24 18:31:48 2024
Assistant: It seems like you're referring to cleaning the living room area. I can help with that! Would you like me to clean the living room floor for you?
Time: Tue Sep 24 18:31:49 2024
User: yes
Time: Tue Sep 24 18:32:04 2024
Is it ambiguous? False
Time: Tue Sep 24 18:32:05 2024
Is it known? True
Time: Tue Sep 24 18:32:06 2024
var_KnowNo: ['clean living room floor']
Time: Tue Sep 24 18:32:08 2024
Does it map to the action in var_KnowNo? True
Time: Tue Sep 24 18:32:09 2024
Assistant: Great choice! I will get the task for clean living room floor started.
Time: Tue Sep 24 18:32:09 2024
Run number: 5 ended at: Tue Sep 24 18:32:09 2024
This run took 7 turns
Total number of LLM calls: 9
"""

# Run the analysis
analyze_transcript(example_transcript)
