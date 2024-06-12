# state.py
# Alexander Leszczynski
# 12-06-2024

var_known = False
var_one = False
var_inf = False
var_seq_ok = False
var_KnowNo = [] # List of actions that could map to the user input
var_total_llm_calls = 0 # Total number of calls to the LLM
var_inf = False
var_decline_explanation = "The request was ok"
var_generated_sequence = None
var_found_errors_in_sequence = []
var_generated_sequence_ok = False
var_generated_sequence_name = ""
var_furhat = None

# example sequence
var_generated_sequence_test = {"sequence": [
        {"step": "1", "action": "toast_bread(2)"},
        {"step": "2", "action": "fry_eggs(1)"},
        {"step": "3", "action": "initiate_sandwich(toasted_bread)"},
        {"step": "4", "action": "place_on_sandwich(fried_egg, 1)"},
        {"step": "5", "action": "fry_bacon(2)"},
        {"step": "6", "action": "place_on_sandwich(fried_bacon, 2)"},
        {"step": "7", "action": "place_on_sandwich(toasted_bread, 1)"},
        {"step": "8", "action": "grill_sausages(2)"},
        {"step": "9", "action": "place_on_plate(grilled_sausages, 1)"},
        {"step": "10", "action": "serve()"}
      ]}