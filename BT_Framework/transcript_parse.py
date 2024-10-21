import pandas as pd
import re
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Alignment, Font
from openpyxl.utils import get_column_letter

def process_assistant_text(text):
    # Keywords to identify where the JSON sequence starts
    keywords = ["Here�s the new sequence in JSON format:", "JSON format"]
    for keyword in keywords:
        if keyword in text:
            # Split the content based on the keyword
            parts = text.split(keyword, 1)
            if len(parts) > 1:
                # Add the specific phrase before the JSON
                modified_text = parts[0].strip() + "\n[this part is not spoken by furhat]\n" + keyword + parts[1].strip()
                #print(modified_text)
                return modified_text
    return text

def parse_text(text):
    # Split the text into individual lines
    lines = text.strip().split('\n')

    # Variables to store parsed data
    data = []
    participant_id = None

    # Regular expressions to identify the parts of the text
    id_pattern = re.compile(r'Participant (\d+)')
    user_pattern = re.compile(r'^User:')
    assistant_pattern = re.compile(r'^Assistant:')
    system_keywords = [
        "Is it ambiguous?", "Does it map to the action in var_KnowNo?", 
        "Furhat is being used with Baseline", "var_KnowNo", 
        "Tree is initialized", "Run number", "This run took", "Total number of LLM calls"
    ]

    # Extract participant ID from the first line
    for line in lines:
        match = id_pattern.search(line)
        if match:
            participant_id = match.group(1)
            break

    if not participant_id:
        print("Participant ID not found.")
        return

    # Iterate through the lines to categorize and extract information
    current_speaker = None
    current_text = []
    
    for line in lines:
        if user_pattern.match(line):
            if current_speaker:
                if current_speaker == 'Assistant':
                    # Process and append the entire assistant output before adding it to the data
                    ass_output = "\n".join(current_text).strip()
                    ass_output = process_assistant_text(ass_output)
                    data.append((participant_id, current_speaker, ass_output))
                else:
                    data.append((participant_id, current_speaker, "\n".join(current_text).strip()))
            current_speaker = 'User'
            # Check if the split result has the expected format
            parts = line.split('User: ', 1)
            if len(parts) > 1:
                current_text = [parts[1].strip()]
            else:
                current_text = []
        elif assistant_pattern.match(line):
            if current_speaker:
                if current_speaker == 'Assistant':
                    # Process and append the entire assistant output before adding it to the data
                    ass_output = "\n".join(current_text).strip()
                    ass_output = process_assistant_text(ass_output)
                    data.append((participant_id, current_speaker, ass_output))
                else:
                    data.append((participant_id, current_speaker, "\n".join(current_text).strip()))
            current_speaker = 'Assistant'
            parts = line.split('Assistant: ', 1)
            if len(parts) > 1:
                current_text = [parts[1].strip()]
            else:
                current_text = []
        elif any(keyword in line for keyword in system_keywords) or line.startswith("Time:") or line.startswith("Version:") or line.startswith("Run:"):
            if current_speaker:
                if current_speaker == 'Assistant':
                    ass_output = "\n".join(current_text).strip()
                    ass_output = process_assistant_text(ass_output)
                    data.append((participant_id, current_speaker, ass_output))
                else:
                    data.append((participant_id, current_speaker, "\n".join(current_text).strip()))
            current_speaker = 'System'
            current_text = [line.strip()]
        else:
            current_text.append(line.strip())

    if current_speaker:
        if current_speaker == 'Assistant':
            ass_output = "\n".join(current_text).strip()
            ass_output = process_assistant_text(ass_output)
            data.append((participant_id, current_speaker, ass_output))
        else:
            data.append((participant_id, current_speaker, "\n".join(current_text).strip()))

    return data

def write_to_excel(data, filename='Transkript of Conversation/transcript_parsed.xlsx'):
    # Create a DataFrame and write to Excel
    df = pd.DataFrame(data, columns=['ID', 'Who', 'What'])

    # Write the DataFrame to an Excel file
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Transcript')

        # Access the workbook and worksheet to apply formatting
        workbook = writer.book
        worksheet = writer.sheets['Transcript']

        # Apply conditional formatting and merged cells
        fill_user = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # Light green
        fill_assistant = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")  # Light blue
        fill_system = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")  # Light orange

        # Merge cells for the ID column
        worksheet.merge_cells(start_row=2, start_column=1, end_row=len(df) + 1, end_column=1)
        cell = worksheet.cell(row=2, column=1)
        cell.alignment = Alignment(horizontal='center', vertical='top')

        # Merge repeated "Who" column values
        start_row = 2
        for row in range(3, len(df) + 2):
            previous_value = worksheet.cell(row=start_row, column=2).value
            current_value = worksheet.cell(row=row, column=2).value

            if current_value != previous_value:
                if row - 1 > start_row:
                    # Merge cells for the repeated value
                    worksheet.merge_cells(start_row=start_row, start_column=2, end_row=row - 1, end_column=2)
                    merged_cell = worksheet.cell(row=start_row, column=2)
                    merged_cell.value = f"{previous_value}:"  # Add ":" to the merged cell value
                    merged_cell.alignment = Alignment(vertical='top')
                start_row = row

        # For the last repeated segment
        if len(df) + 1 > start_row:
            worksheet.merge_cells(start_row=start_row, start_column=2, end_row=len(df) + 1, end_column=2)
            merged_cell = worksheet.cell(row=start_row, column=2)
            merged_cell.alignment = Alignment(vertical='top')

        # Apply formatting based on the "Who" column
        for row in range(2, len(df) + 2):
            who_value = worksheet.cell(row=row, column=2).value
            who_cell = worksheet.cell(row=row, column=2)
            what_cell = worksheet.cell(row=row, column=3)

            # Convert the cell row and column to a coordinate string (e.g., "B2")
            cell_coord = f"B{row}"
            merged = False

            # Check if the cell is part of any merged range
            for merged_range in worksheet.merged_cells.ranges:
                if cell_coord in merged_range:
                    merged = True
                    break

            # Add ":" to the 'Who' values only if not merged
            if not merged:
                who_cell.value = f"{who_value}:"

            # Apply conditional formatting based on the value of 'Who'
            if who_value == 'User' or who_value == 'User:':
                who_cell.fill = fill_user
            elif who_value == 'Assistant' or who_value == 'Assistant:':
                who_cell.fill = fill_assistant
            elif who_value == 'System' or who_value == 'System:':
                who_cell.fill = fill_system

            # Wrap text in the 'What' column
            what_cell.alignment = Alignment(wrap_text=True, vertical='top')  # Align the 'What' column values at the top

            # Align the text in the 'Who' column at the top
            who_cell.alignment = Alignment(vertical='top')

        # Auto-size the columns
        for col in range(1, 4):
            max_length = 0
            col_letter = get_column_letter(col)
            for cell in worksheet[col_letter]:
                try:
                    max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            worksheet.column_dimensions[col_letter].width = max_length + 5


# Example usage
text = """
Participant 43
RunID C
Version: 1.3
Tue Sep 24 10:05:15 2024
Furhat is being used with Baseline
Assistant: Hello! I am Gregory, your home assistant. How can I help you today?
Assistant: I am sorry. I did not get that. Can you please repeat?
User: can you please help me prepare uh bean and cheese kadia 
Time: Tue Sep 24 10:05:41 2024
Assistant: It looks like you might be requesting a "bean and cheese quesadilla," but I'm not familiar with "bean and cheese kadia." 

If you meant "bean and cheese quesadilla," I can assist you with that! I will prepare a quesadilla using heated beans and cheese with a tortilla. 

First, I will heat the beans, prepare the tortilla, and then assemble and cook the quesadilla.

Here�s the new sequence in JSON format: 
```json
{
  "task": "bean and cheese quesadilla",
  "ID": "8",
  "sequence": [
    {"step": "1", "action": "heat_beans(1)"},
    {"step": "2", "action": "prepare_tortilla(1)"},
    {"step": "3", "action": "place_on_plate(prepared_tortilla, 1)"},
    {"step": "4", "action": "place_on_plate(heated_beans, 1)"},
    {"step": "5", "action": "place_on_plate(cheese, 1)"},
    {"step": "6", "action": "cook_quesadilla()"},
    {"step": "7", "action": "place_on_plate(cooked_quesadilla, 1)"},
    {"step": "8", "action": "serve()"}
  ]
}
```
Great choice! I will start the task for: bean and cheese quesadilla.
Time: Tue Sep 24 10:05:47 2024
Run number: 1 ended at: Tue Sep 24 10:05:47 2024
This run took 1 turns
Total number of LLM calls: 1

Version: 1.3
Tue Sep 24 10:06:10 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User:  uh can you suggest something sweet Savory or healthy from the list 
Time: Tue Sep 24 10:06:30 2024
Assistant: It seems your request is a bit vague. Could you please clarify what you mean by "something sweet, savory or healthy"? Here are a few options from the list that might fit those categories:

1. **Sweet**: Pancakes with maple syrup and berries.
2. **Savory**: Bacon and egg sandwich.
3. **Healthy**: Avocado toast with sausage on the side.

Let me know if any of these options interest you, or if you have something else in mind!
Time: Tue Sep 24 10:06:32 2024
User: uh can you prepare uh avocado toast for me 
Time: Tue Sep 24 10:07:03 2024
Assistant: Great choice! I will start the task for: avocado toast with sausage on the side.
Time: Tue Sep 24 10:07:04 2024
Run number: 2 ended at: Tue Sep 24 10:07:04 2024
This run took 2 turns
Total number of LLM calls: 2

Version: 1.3
Tue Sep 24 10:07:10 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User:   can you prepare peanut butter and jelly sandwich but with grilled Tomatoes added 
Time: Tue Sep 24 10:07:38 2024
Assistant: First, I will prepare a peanut butter and jelly sandwich and then add grilled tomatoes as an extra ingredient. I will toast the bread, spread peanut butter and jelly, and then place the grilled tomatoes on the sandwich. 

Here�s the new sequence in JSON format: 
```json
{
  "task": "peanut butter and jelly sandwich with grilled tomatoes",
  "ID": "3a",
  "sequence": [
    {"step": "1", "action": "toast_bread(2)"},
    {"step": "2", "action": "spread_on_bread(peanut_butter)"},
    {"step": "3", "action": "spread_on_bread(jelly)"},
    {"step": "4", "action": "grill_tomatoes(1)"},
    {"step": "5", "action": "combine_breads(jelly_toast, peanut_butter_toast)"},
    {"step": "6", "action": "place_on_sandwich(grilled_tomatoes, 1)"},
    {"step": "7", "action": "serve()"}
  ]
}
```
Time: Tue Sep 24 10:07:41 2024
Run number: 3 ended at: Tue Sep 24 10:07:41 2024
This run took 3 turns
Total number of LLM calls: 1

Version: 1.3
Tue Sep 24 10:07:56 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User:  can you help me uh clean the floor 
Time: Tue Sep 24 10:08:14 2024
Assistant: It seems that your request is a bit vague. However, I can assist with cleaning the living room floor. Here�s how I can help:

1. Clean living room floor 

Please confirm if you would like me to proceed with cleaning the living room floor!
Time: Tue Sep 24 10:08:15 2024
User: yes
Time: Tue Sep 24 10:08:43 2024
Assistant: Great choice! I will start the task for: clean living room floor.
Time: Tue Sep 24 10:08:44 2024
Run number: 4 ended at: Tue Sep 24 10:08:44 2024
This run took 4 turns
Total number of LLM calls: 2

Version: 1.3
Tue Sep 24 10:08:48 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hey uh can I get a a Mexican dish with tortilla and cheese 
Time: Tue Sep 24 10:09:07 2024
Assistant: It seems like you're looking for a Mexican dish that includes tortilla and cheese. I can prepare a "bean and cheese quesadilla" for you, which involves heating beans, preparing a tortilla, and cooking it with cheese.

First, I will heat the beans, prepare the tortilla, add the beans and cheese, then cook the quesadilla until it's crispy. 

Great choice! I will start the task for: bean and cheese quesadilla.
Time: Tue Sep 24 10:09:11 2024
Run number: 5 ended at: Tue Sep 24 10:09:11 2024
This run took 5 turns
Total number of LLM calls: 1

Version: 1.3
Tue Sep 24 10:14:58 2024
Tree is initialized and furhat is used

Assistant: Hello! I am Gregory, your home assistant. How can I help you today?
User: uh can you help me prepare a pancakes with maple syrup and berries 
Is it ambiguous? False
Time: Tue Sep 24 10:14:58 2024
Is it known? True
Time: Tue Sep 24 10:14:59 2024
var_KnowNo: ['pancakes with maple syrup and berries']
Time: Tue Sep 24 10:15:01 2024
Does it map to the action in var_KnowNo? True
Time: Tue Sep 24 10:15:02 2024
Assistant: Great choice! I will get the task for pancakes with maple syrup and berries started.
Time: Tue Sep 24 10:15:02 2024
Run number: 1 ended at: Tue Sep 24 10:15:02 2024
This run took 3 turns
Total number of LLM calls: 5

Run: 2
Tue Sep 24 10:15:21 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: uh can you suggest something sweet from the list 
Is it ambiguous? True
Time: Tue Sep 24 10:15:21 2024
Assistant: There are multiple options in my list that might fit your order. For something sweet, I recommend 'pancakes with maple syrup and berries'. It's a delightful dish that's perfect for satisfying a sweet craving. Would you like to have that?
Time: Tue Sep 24 10:15:22 2024
User: yes 
Time: Tue Sep 24 10:15:39 2024
Is it ambiguous? False
Time: Tue Sep 24 10:15:39 2024
Is it known? True
Time: Tue Sep 24 10:15:40 2024
var_KnowNo: ['pancakes with maple syrup and berries']
Time: Tue Sep 24 10:15:42 2024
Does it map to the action in var_KnowNo? True
Time: Tue Sep 24 10:15:43 2024
Assistant: Great choice! I will get the task for pancakes with maple syrup and berries started.
Time: Tue Sep 24 10:15:43 2024
Run number: 2 ended at: Tue Sep 24 10:15:43 2024
This run took 5 turns
Total number of LLM calls: 7

Run: 3
Tue Sep 24 10:16:07 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User:  uh can you help me prepare bacon and accent which with peanut butter 
Is it ambiguous? True
Time: Tue Sep 24 10:16:08 2024
Assistant: There are multiple options in my list that might fit your order. It seems like you would like a 'bacon and egg sandwich' but mentioned 'accent', which might be a miscommunication. Additionally, you mentioned peanut butter. 

Could you please clarify if you would like to combine the bacon and egg sandwich with peanut butter, or if you prefer a peanut butter and jelly sandwich instead? Let me know how you would like to proceed!
Time: Tue Sep 24 10:16:09 2024
User: yes I would like to combine get better 
Time: Tue Sep 24 10:16:38 2024
Is it ambiguous? True
Time: Tue Sep 24 10:16:40 2024
Assistant: There are multiple options in my list that might fit your order. To confirm, you would like to combine a 'bacon and egg sandwich' with peanut butter? I can prepare that for you. Please hang tight while I get started!
Time: Tue Sep 24 10:16:41 2024
User: yes generate that sequence for me
Time: Tue Sep 24 10:17:10 2024
Is it ambiguous? False
Time: Tue Sep 24 10:17:11 2024
Is it known? False
Time: Tue Sep 24 10:17:12 2024
Is it within the capabilities of the robot? True
Time: Tue Sep 24 10:17:13 2024
Is a new sequence requested?: True
Time: Tue Sep 24 10:17:13 2024
Is a new sequence actually requested? True
Time: Tue Sep 24 10:17:14 2024
Did it pass the safety check?: True
Explanation: The request involves known ingredients (bacon, egg, and peanut butter) that can be found in the list of known ingredients (No. 3, 10, and 22), making it feasible for me to execute.
Time: Tue Sep 24 10:17:15 2024
The generated sequence is: {"sequence": [{"step": "1", "action": "toast_bread(2)"}, {"step": "2", "action": "fry_eggs(1)"}, {"step": "3", "action": "initiate_sandwich(toasted_bread)"}, {"step": "4", "action": "place_on_sandwich(fried_egg, 1)"}, {"step": "5", "action": "cook_bacon(2)"}, {"step": "6", "action": "place_on_sandwich(fried_bacon, 2)"}, {"step": "7", "action": "spread_on_bread(peanut_butter)"}, {"step": "8", "action": "place_on_sandwich(toasted_bread, 1)"}, {"step": "9", "action": "serve()"}]}
Time: Tue Sep 24 10:17:17 2024
Assistant: Sure, I will perform a new set of steps to fulfill your request for a bacon and egg sandwich with peanut butter. 

First, I will toast two pieces of bread. 
Next, I'll fry one egg. 
Then, I will initiate the sandwich with the toasted bread. 
After placing the fried egg on the sandwich, I'll cook two pieces of bacon. 
Once the bacon is ready, I will add it to the sandwich. 
Following that, I will spread peanut butter on the bread. 
Finally, I'll place the other piece of toasted bread on top and serve the sandwich. 

Does this sequence sound good to you?
Time: Tue Sep 24 10:17:18 2024
var_generated_sequence_name is: bacon and egg sandwich with peanut butter
Time: Tue Sep 24 10:17:18 2024
User:yes 
Time: Tue Sep 24 10:17:54 2024
Assistant: Great then I will now proceed to make the: bacon and egg sandwich with peanut butter
Time: Tue Sep 24 10:17:56 2024
Run number: 3 ended at: Tue Sep 24 10:17:56 2024
This run took 8 turns
Total number of LLM calls: 12

Run: 4
Tue Sep 24 10:18:13 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: can you help me with washing my laundry 
Is it ambiguous? True
Time: Tue Sep 24 10:18:13 2024
Assistant: I apologize, but washing laundry is outside the scope of my capabilities. However, I can help you with cleaning tasks, such as 'cleaning the living room floor' if that would be helpful. Just let me know!
Time: Tue Sep 24 10:18:14 2024
User:  or can you help me with painting the walls 
Time: Tue Sep 24 10:18:40 2024
Is it ambiguous? True
Time: Tue Sep 24 10:18:42 2024
Assistant: I apologize, but painting walls is also outside the scope of my capabilities. However, I can assist you with cleaning tasks, such as 'cleaning the living room floor'. If that would be helpful, please let me know!
Time: Tue Sep 24 10:18:42 2024
User: skip
Time: Tue Sep 24 10:19:03 2024
Run number: 4 ended at: Tue Sep 24 10:19:03 2024
This run took 6 turns
Total number of LLM calls: 4

Run: 5
Tue Sep 24 10:19:33 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User:   hi can you suggest something healthy uh from the list uh with sausages 
Is it ambiguous? True
Time: Tue Sep 24 10:19:34 2024
Assistant: There are multiple options in my list that might fit your order. Based on your request for something healthy with sausages, I suggest:
1. 'Avocado toast with sausage on the side'
2. 'Full English breakfast' (which includes sausages among other items)

Would you like to go with one of these options?
Time: Tue Sep 24 10:19:35 2024
User: yes I would like to go with the first 1 
Time: Tue Sep 24 10:19:57 2024
Is it ambiguous? False
Time: Tue Sep 24 10:19:59 2024
Is it known? True
Time: Tue Sep 24 10:19:59 2024
var_KnowNo: ['avocado toast with sausage on the side']
Time: Tue Sep 24 10:20:02 2024
Does it map to the action in var_KnowNo? True
Time: Tue Sep 24 10:20:02 2024
Assistant: Great choice! I will get the task for avocado toast with sausage on the side started.
Time: Tue Sep 24 10:20:02 2024
Run number: 5 ended at: Tue Sep 24 10:20:02 2024
This run took 5 turns
Total number of LLM calls: 7

Notes:
  Times: 9:55 - 10:30

  Base: 
    - bad STT at T1
    - interesting T3 request that worked

  BT:
    - T3 had a long break because mic didn't pic up and i had to type in, but request worked and was interesting too.

End of Participant 43 experiment







Participant 44
RunID D
Version: 1.3
Tue Sep 24 12:23:16 2024
Tree is initialized and furhat is used

Assistant: Hello! I am Gregory, your home assistant. How can I help you today?
User: hi Gary can I uh to clean the living room floor 
Is it ambiguous? True
Time: Tue Sep 24 12:23:17 2024
Assistant: There are multiple options in my list that might fit your order. Yes, I can help you with that! I will clean the living room floor by removing any clutter, sweeping, and mopping it thoroughly. Please give me a moment to get started.
Time: Tue Sep 24 12:23:18 2024
User: skip
Time: Tue Sep 24 12:23:32 2024
Run number: 1 ended at: Tue Sep 24 12:23:32 2024
This run took 4 turns
Total number of LLM calls: 2

Run: 2
Tue Sep 24 12:23:48 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hey uh can I get something uh sweet Savory or healthy from the list 
Is it ambiguous? True
Time: Tue Sep 24 12:23:48 2024
Assistant: There are multiple options in my list that might fit your order. For something sweet, you might enjoy 'pancakes with maple syrup and berries'. For something savory, a 'bacon and egg sandwich' would be great. If you're looking for something healthy, I recommend 'vegetable stir fry with rice'. Which one would you like?
Time: Tue Sep 24 12:23:49 2024
Assistant: I am sorry. I did not get that. Can you please repeat?
User: I will get the vegetable 1 with the rice 
Time: Tue Sep 24 12:24:28 2024
Is it ambiguous? False
Time: Tue Sep 24 12:24:29 2024
Is it known? True
Time: Tue Sep 24 12:24:30 2024
var_KnowNo: ['vegetable stir fry with rice']
Time: Tue Sep 24 12:24:32 2024
Does it map to the action in var_KnowNo? True
Time: Tue Sep 24 12:24:32 2024
Assistant: Great choice! I will get the task for vegetable stir fry with rice started.
Time: Tue Sep 24 12:24:32 2024
Run number: 2 ended at: Tue Sep 24 12:24:33 2024
This run took 5 turns
Total number of LLM calls: 7

Run: 3
Tue Sep 24 12:25:00 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: um so uh can I add some extra uh vegetables like mushrooms or tomatoes in those stir fry 
Is it ambiguous? True
Time: Tue Sep 24 12:25:01 2024
Assistant: There are multiple options in my list that might fit your order. Yes, I can certainly add extra vegetables like mushrooms or tomatoes to the 'vegetable stir fry with rice'. Would you like to specify any particular quantity or should I proceed with a standard portion?
Time: Tue Sep 24 12:25:02 2024
User: uh maybe just um whatever you want 
Time: Tue Sep 24 12:25:26 2024
Is it ambiguous? True
Time: Tue Sep 24 12:25:27 2024
Assistant: I will prepare the 'vegetable stir fry with rice' with a standard portion of extra mushrooms and tomatoes. I'll start the process now. Please hold on for a moment!
Time: Tue Sep 24 12:25:28 2024
User: skip
Time: Tue Sep 24 12:25:44 2024
Run number: 3 ended at: Tue Sep 24 12:25:44 2024
This run took 6 turns
Total number of LLM calls: 4

Run: 4
Tue Sep 24 12:25:55 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hey can you walk my dog 
Is it ambiguous? True
Time: Tue Sep 24 12:25:55 2024
Assistant: I apologize, but walking your dog is outside the scope of my capabilities. However, I can help with cooking or cleaning. If you're in need of a meal, I can suggest making something like a 'bacon and egg sandwich' or a 'vegetable stir fry with rice'. Let me know how I can assist you!
Time: Tue Sep 24 12:25:56 2024
User: yeah uh maybe uh try to cook something easy and quick 
Time: Tue Sep 24 12:26:23 2024
Is it ambiguous? True
Time: Tue Sep 24 12:26:24 2024
Assistant: There are multiple options in my list that might fit your order. If you're looking for something easy and quick to prepare, I recommend:
1. A 'peanut butter and jelly sandwich' 
2. A 'grilled tomato and mushroom bruschetta' 
3. 'Avocado toast with sausage on the side'. 

Let me know which one you prefer, or if you have another idea in mind!
Time: Tue Sep 24 12:26:25 2024
User: which 1 has lower calories 
Time: Tue Sep 24 12:26:51 2024
Is it ambiguous? True
Time: Tue Sep 24 12:26:52 2024
Assistant: There are multiple options in my list that might fit your order. Generally, a 'grilled tomato and mushroom bruschetta' is likely to have lower calories compared to the other options. Would you like me to prepare that for you?
Time: Tue Sep 24 12:26:53 2024
User: yeah sure that take that 1 
Time: Tue Sep 24 12:27:09 2024
Is it ambiguous? False
Time: Tue Sep 24 12:27:10 2024
Is it known? True
Time: Tue Sep 24 12:27:11 2024
var_KnowNo: ['grilled tomato and mushroom bruschetta']
Time: Tue Sep 24 12:27:12 2024
Does it map to the action in var_KnowNo? True
Time: Tue Sep 24 12:27:13 2024
Assistant: Great choice! I will get the task for grilled tomato and mushroom bruschetta started.
Time: Tue Sep 24 12:27:13 2024
Run number: 4 ended at: Tue Sep 24 12:27:13 2024
This run took 9 turns
Total number of LLM calls: 11

Run: 5
Tue Sep 24 12:27:39 2024
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hey uh can I uh ask you to do something um that's a wrap there are some Vegetables and protein in it 
Is it ambiguous? True
Time: Tue Sep 24 12:27:40 2024
Assistant: There are multiple options in my list that might fit your order. It sounds like you're looking for something with vegetables and protein. I can prepare a 'vegetable stir fry with rice' for you. Would that work, or is there something specific you had in mind?
Time: Tue Sep 24 12:27:41 2024
User: something uh made from flowers like it's a wrap or yeah something Spanish or 
Time: Tue Sep 24 12:28:06 2024
Is it ambiguous? True
Time: Tue Sep 24 12:28:07 2024
Assistant: There are multiple options in my list that might fit your order. It seems like you're looking for a Spanish dish that resembles a wrap. Unfortunately, I don't have any options that specifically fit that description. However, I can prepare a 'bean and cheese quesadilla', which is a delicious option that involves tortillas and can be a good alternative. Would you like that?
Time: Tue Sep 24 12:28:08 2024
User: uh not really I want something actually uh uh with tomatoes in it 
Time: Tue Sep 24 12:28:40 2024
Is it ambiguous? True
Time: Tue Sep 24 12:28:41 2024
Assistant: There are multiple options in my list that might fit your order. Based on your request for something with tomatoes, I can prepare the 'tortilla with tomatoes, beans, and egg (huevos rancheros)'. Would that work for you?
Time: Tue Sep 24 12:28:42 2024
User: yeah that 1 uh it's the correct 1 and 1 
Time: Tue Sep 24 12:29:01 2024
Is it ambiguous? True
Time: Tue Sep 24 12:29:02 2024
Assistant: I understand you'd like the 'tortilla with tomatoes, beans, and egg (huevos rancheros)' and you're asking for one portion of it. I will prepare that for you. Give me a moment!
Time: Tue Sep 24 12:29:02 2024
User: skip
Time: Tue Sep 24 12:29:12 2024
Run number: 5 ended at: Tue Sep 24 12:29:12 2024
This run took 10 turns
Total number of LLM calls: 8

Version: 1.3
Tue Sep 24 12:35:07 2024
Furhat is being used with Baseline
Assistant: Hello! I am Gregory, your home assistant. How can I help you today?
User: hey Gregory um saying you English breakfast 
Time: Tue Sep 24 12:35:21 2024
Assistant: Great choice! I will start the task for: full English breakfast.
Time: Tue Sep 24 12:35:22 2024
Run number: 1 ended at: Tue Sep 24 12:35:22 2024
This run took 1 turns
Total number of LLM calls: 1

Version: 1.3
Tue Sep 24 12:35:27 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hey I want something uh sweet Savory or healthy from the list can you suggest something for me 
Time: Tue Sep 24 12:35:43 2024
Assistant: It seems like your request is a bit vague. However, I can suggest a few options from the list that match your categories of sweet, savory, or healthy:

1. **Pancakes with Maple Syrup and Berries** (sweet)
2. **Vegetable Stir Fry with Rice** (healthy)
3. **Avocado Toast with Sausage on the Side** (savory and healthy)

Please let me know which one you'd like, or if you have something else in mind!
Time: Tue Sep 24 12:35:45 2024
User: I would take the avocado toast with sausage on the side 
Time: Tue Sep 24 12:36:17 2024
Assistant: Great choice! I will start the task for: avocado toast with sausage on the side.
Time: Tue Sep 24 12:36:18 2024
Run number: 2 ended at: Tue Sep 24 12:36:18 2024
This run took 2 turns
Total number of LLM calls: 2

Version: 1.3
Tue Sep 24 12:36:23 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hey uh can I ask add some extra pumpkin on the avocado toast with sausage on the side 
Time: Tue Sep 24 12:36:40 2024
Assistant: I'm sorry, but I can't accommodate the request for extra pumpkin, as it is not listed among the ingredients I can use. However, I can proceed with the original task of making avocado toast with sausage on the side.

Great choice! I will start the task for: avocado toast with sausage on the side.
Time: Tue Sep 24 12:36:41 2024
Run number: 3 ended at: Tue Sep 24 12:36:41 2024
This run took 3 turns
Total number of LLM calls: 1

Version: 1.3
Tue Sep 24 12:36:59 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hey uh wants you to help me switch the light bulb in my living room 
Time: Tue Sep 24 12:37:19 2024
Assistant: I'm sorry, but changing light bulbs is beyond my current capabilities. I specialize in food preparation and cleaning tasks. If there's anything else I can assist you with, like cleaning your living room floor, please let me know!
Time: Tue Sep 24 12:37:21 2024
User: or maybe uh to clean the living room floor 
Time: Tue Sep 24 12:37:45 2024
Assistant: Great choice! I will start the task for: clean living room floor.
Time: Tue Sep 24 12:37:46 2024
Run number: 4 ended at: Tue Sep 24 12:37:46 2024
This run took 4 turns
Total number of LLM calls: 2

Version: 1.3
Tue Sep 24 12:37:52 2024
Furhat is being used with Baseline
Assistant: That's it for this task. Let's go onto the next one... Hello. How can I help you today?
User: hey uh for something with spread  
Time: Tue Sep 24 12:38:14 2024
Assistant: It seems like your request is a bit vague. Could you please clarify what type of dish you are looking for that includes a spread? 

Here are a few options I can help you with:

1. **Peanut Butter and Jelly Sandwich** - Includes spreads of peanut butter and jelly.
2. **Avocado Toast with Sausage on the Side** - Features avocado spread on toasted bread.

Let me know which one you would like, or if you have something else in mind!
Time: Tue Sep 24 12:38:15 2024
User: I will have the second 1 
Time: Tue Sep 24 12:38:45 2024
Assistant: Great choice! I will start the task for: avocado toast with sausage on the side.
Time: Tue Sep 24 12:38:46 2024
Run number: 5 ended at: Tue Sep 24 12:38:46 2024
This run took 5 turns
Total number of LLM calls: 2

Notes:
  Times: 12:14 - 13:09

  Overall:
    - STT bad at times because of uhms and breaks mid sentence

  BT:
    - a lot of fails where ambiuguous answer promised to execute a sequence... T1, T3 and T5 (don't know what happened there)

  Base:
    - denied to add pumpkin to avocado toast and without asking just executed avocado toast with sausage on the side sequence...

End of Participant 44 experiment
""" 
parsed_data = parse_text(text)
write_to_excel(parsed_data)
