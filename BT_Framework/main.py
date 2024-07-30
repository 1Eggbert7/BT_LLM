# main.py
# Alexander Leszczynski
# 30-07-2024 

import py_trees
from actions import WaitForUserInput, PrintAmbiguousAnswer, KnowNoMapping, ExecuteAction, RunSafetyCheck, DeclineRequest, GenerateNewSequence, ExplainSequence, ReportFailureBackToUser, ExecuteNewSequence, AskUserForNewRequest, AskUserToSpecifyWithKnowNo, SetVarKnownTrue, FallbackAnswer
from conditions import CheckForAmbiguity, CheckForNewSeq, CheckVarKnownCondition, CheckForKnown, CheckVarKnowNo, CheckMapping, CheckVarInf, CheckNewSeq, CheckUserOkWithNewSeq, CheckForNewSeq2, CheckVarKnownFalse
from config import LLM, FURHAT_IP_ADDRESS, FURHAT_VOICE_NAME, FURHAT, VERSION, BASELINE
from baseline import run_baseline
import state
from prompts import DUMMY_CONVERSATION, BASELINE_PROMPT
from utils import format_conversation, initialize_furhat, record_speech, save_transcript
#import cProfile
import keyboard
import time
from openai import OpenAI

#py_trees.logging.level = py_trees.logging.Level.DEBUG

user_input =  "Good day sir" #format_conversation(DUMMY_CONVERSATION)# Contains the user input
conversation = []  # Contains the conversation history between the user and the system

def build_tree(conversation, process_user_input):
    root = py_trees.composites.Selector(name="Full BT Root Selector", memory=False)
    
    # Sequence 1: Check for ambiguity, print answer for ambiguity, wait for user input. This sequence has 3 sub sequences
    sequence_1 = py_trees.composites.Sequence(name="Sequence 1", memory=False)
    check_var_known_false = CheckVarKnownFalse(name="Check for var_known == False")
    check_ambiguity = CheckForAmbiguity(name="Check for Ambiguity", conversation=conversation)
    print_answer_for_ambiguity = PrintAmbiguousAnswer(name="Print 'Answer for Ambiguity'", conversation=conversation)
    wait_for_user_input = WaitForUserInput(name="Wait for User Input", process_user_input_func=process_user_input, conversation=conversation)
    sequence_1.add_children([check_var_known_false, check_ambiguity, print_answer_for_ambiguity, wait_for_user_input])  # Level 1
    
    # Sequence 2: Check for Known sequence and generate new sequence if needed. This sequence has 5 sub selectors and 6 sub sequences
    sequence_2 = py_trees.composites.Sequence(name="Sequence 2", memory=False)

    # Sequences and Selectors for Sequence 2
    sub_selector_2_1 = py_trees.composites.Selector(name="Sub Selector 2.1", memory=False) # this selector is a child of sequence_2
    sub_selector_2_2 = py_trees.composites.Selector(name="Sub Selector 2.2", memory=False) # this selector is a child of sequence_2
    sub_sequence_2_2_1 = py_trees.composites.Sequence(name="Sub Sequence 2.2.1", memory=False) # this sequence is a child of sub_selector_2_2
    sub_sequence_2_2_2 = py_trees.composites.Sequence(name="Sub Sequence 2.2.2", memory=False) # this sequence is a child of sub_selector_2_2
    sub_sequence_2_2_3 = py_trees.composites.Sequence(name="Sub Sequence 2.2.3", memory=False) # this sequence is a child of sub_selector_2_2
    sub_selector_2_2_2_1 = py_trees.composites.Selector(name="Sub Selector 2.2.2.1", memory=False) # this selector is a child of sub_sequence_2_2_2
    sub_sequence_2_2_2_1_1 = py_trees.composites.Sequence(name="Sub Sequence 2.2.2.1.1", memory=False) # this sequence is a child of sub_selector_2_2_2_1
    sub_sequence_2_2_2_1_2 = py_trees.composites.Sequence(name="Sub Sequence 2.2.2.1.2", memory=False) # this sequence is a child of sub_selector_2_2_2_1
    sub_selector_2_2_2_1_2_1 = py_trees.composites.Selector(name="Sub Selector 2.2.2.1.2.1", memory=False) # this selector is a child of sub_sequence_2_2_2_1_2
    sub_sequence_2_2_2_1_2_1_1 = py_trees.composites.Sequence(name="Sub Sequence 2.2.2.1.2.1.1", memory=False) # this sequence is a child of sub_selector_2_2_2_1_2_1
    sub_sequence_2_2_2_1_2_1_2 = py_trees.composites.Sequence(name="Sub Sequence 2.2.2.1.2.1.2", memory=False) # this sequence is a child of sub_selector_2_2_2_1_2_1
    sub_selector_2_2_2_1_2_1_1_1 = py_trees.composites.Selector(name="Sub Selector 2.2.2.1.2.1.1.1", memory=False) # this selector is a child of sub_sequence_2_2_2_1_2_1_1
    sub_sequence_2_2_2_1_2_1_1_1_1 = py_trees.composites.Sequence(name="Sub Sequence 2.2.2.1.2.1.1.1.1", memory=False) # this sequence is a child of sub_selector_2_2_2_1_2_1_1_1
    sub_sequence_2_2_2_1_2_1_1_1_2 = py_trees.composites.Sequence(name="Sub Sequence 2.2.2.1.2.1.1.1.2", memory=False) # this sequence is a child of sub_selector_2_2_2_1_2_1_1_1

    # Sub selector 2.1
    check_var_known = CheckVarKnownCondition(name="Check for var_known")
    check_known = CheckForKnown(name= "Check for known", conversation=conversation)
    sub_selector_2_1.add_children([check_var_known, check_known])                                               # Level 2 

    # Sub sequence 2.2.1
    check_var_knowNo = CheckVarKnowNo(name="Check if var_KnowNo == 1")
    check_legitness_of_mapping = CheckMapping(name="Check Mapping", conversation=conversation)
    execute_action = ExecuteAction(name="Execute known Action", conversation=conversation)
    sub_sequence_2_2_1.add_children([check_var_knowNo, check_legitness_of_mapping, execute_action])             # Level 3    

    # Sub sequence 2.2.2.1.1
    check_var_inf = CheckVarInf(name="Check for var_inf")
    decline_request = DeclineRequest(name="Decline Request", conversation=conversation)
    wait_for_user_input_2 = WaitForUserInput(name="Wait for User Input", process_user_input_func=process_user_input, conversation=conversation)
    sub_sequence_2_2_2_1_1.add_children([check_var_inf, decline_request, wait_for_user_input_2])                # Level 5

    # Sub sequence 2.2.2.1.2.1.1.1.1
    check_if_user_ok_with_new_seq = CheckUserOkWithNewSeq(name="Check if user is ok with new sequence", conversation=conversation)
    execute_new_sequence = ExecuteNewSequence(name="Execute New Sequence", conversation=conversation)
    sub_sequence_2_2_2_1_2_1_1_1_1.add_children([check_if_user_ok_with_new_seq, execute_new_sequence])          # Level 9

    # Sub sequence 2.2.2.1.2.1.1.1.2
    ask_user_for_new_request = AskUserForNewRequest(name="Ask User for New Request", conversation=conversation)
    wait_for_user_input_3 = WaitForUserInput(name="Wait for User Input", process_user_input_func=process_user_input, conversation=conversation)
    sub_sequence_2_2_2_1_2_1_1_1_2.add_children([ask_user_for_new_request, wait_for_user_input_3])              # Level 9

    # Sub selector 2.2.2.1.2.1.1.1
    sub_selector_2_2_2_1_2_1_1_1.add_children([sub_sequence_2_2_2_1_2_1_1_1_1, sub_sequence_2_2_2_1_2_1_1_1_2]) # Level 8

    # Sub sequence 2.2.2.1.2.1.1
    check_new_seq = CheckNewSeq(name="Check New Sequence")
    explain_sequence = ExplainSequence(name="Explain Sequence", conversation=conversation)
    sub_sequence_2_2_2_1_2_1_1.add_children([check_new_seq, explain_sequence, sub_selector_2_2_2_1_2_1_1_1])    # Level 7

    # Sub sequence 2.2.2.1.2.1.2
    report_failure = ReportFailureBackToUser(name="Report Failure Back to User", conversation=conversation)
    wait_for_user_input_4 = WaitForUserInput(name="Wait for User Input", process_user_input_func=process_user_input, conversation=conversation)
    sub_sequence_2_2_2_1_2_1_2.add_children([report_failure, wait_for_user_input_4])                            # Level 7

    # Sub selector 2.2.2.1.2.1
    sub_selector_2_2_2_1_2_1.add_children([sub_sequence_2_2_2_1_2_1_1, sub_sequence_2_2_2_1_2_1_2])             # Level 6

    # Sub sequence 2.2.2.1.2
    generate_new_sequence = GenerateNewSequence(name="Generate New Sequence", conversation=conversation)
    sub_sequence_2_2_2_1_2.add_children([generate_new_sequence, sub_selector_2_2_2_1_2_1])                      # Level 5

    # Sub selector 2.2.2.1
    sub_selector_2_2_2_1.add_children([sub_sequence_2_2_2_1_1, sub_sequence_2_2_2_1_2])                         # Level 4                                    

    # Sub sequence 2.2.2
    check_var_knowNo_2 = CheckVarKnowNo(name="Check if var_KnowNo == 1 again")
    run_safety_check = RunSafetyCheck(name="Run Safety Check", conversation=conversation)
    sub_sequence_2_2_2.add_children([check_var_knowNo_2, run_safety_check, sub_selector_2_2_2_1])               # Level 3

    # Sub sequence 2.2.3
    ask_user_to_specify_with_know_no = AskUserToSpecifyWithKnowNo(name="Ask User to Specify with KnowNo", conversation=conversation)
    wait_for_user_input_5 = WaitForUserInput(name="Wait for User Input", process_user_input_func=process_user_input, conversation=conversation)
    sub_sequence_2_2_3.add_children([ask_user_to_specify_with_know_no, wait_for_user_input_5])                  # Level 3

    # Sub selector 2.2
    sub_selector_2_2.add_children([sub_sequence_2_2_1, sub_sequence_2_2_2, sub_sequence_2_2_3])                 # Level 2
    
    # Sequence 2
    know_no_mapping = KnowNoMapping(name="KnowNo Mapping", conversation=conversation)
    sequence_2.add_children([sub_selector_2_1, know_no_mapping, sub_selector_2_2])                              # Level 1
    
    # Sequence 3: 
    sequence_3 = py_trees.composites.Sequence(name="Sequence 3", memory=False)

    # Sub sequences and selectors for Sequence 3
    sub_selector_3_1 = py_trees.composites.Selector(name="Sub Selector 3.1", memory=False) # this selector is a child of sequence_3
    sub_sequence_3_1_1 = py_trees.composites.Sequence(name="Sub Sequence 3.1.1", memory=False) # this sequence is a child of sub_selector_3_1
    sub_selector_3_1_1_1 = py_trees.composites.Selector(name="Sub Selector 3.1.1.1", memory=False) # this selector is a child of sub_sequence_3_1_1
    sub_sequence_3_1_1_1_1 = py_trees.composites.Sequence(name="Sub Sequence 3.1.1.1.1", memory=False) # this sequence is a child of sub_selector_3_1_1_1
    sub_sequence_3_1_1_1_2 = py_trees.composites.Sequence(name="Sub Sequence 3.1.1.1.2", memory=False) # this sequence is a child of sub_selector_3_1_1_1
    sub_selector_3_1_1_1_2_1 = py_trees.composites.Selector(name="Sub Selector 3.1.1.1.2.1", memory=False) # this selector is a child of sub_sequence_3_1_1_1_2
    sub_sequence_3_1_1_1_2_1_1 = py_trees.composites.Sequence(name="Sub Sequence 3.1.1.1.2.1.1", memory=False) # this sequence is a child of sub_selector_3_1_1_1_2_1
    sub_sequence_3_1_1_1_2_1_2 = py_trees.composites.Sequence(name="Sub Sequence 3.1.1.1.2.1.2", memory=False) # this sequence is a child of sub_selector_3_1_1_1_2_1
    sub_selector_3_1_1_1_2_1_1_1 = py_trees.composites.Selector(name="Sub Selector 3.1.1.1.2.1.1.1", memory=False) # this selector is a child of sub_sequence_3_1_1_1_2_1_1
    sub_sequence_3_1_1_1_2_1_1_1_1 = py_trees.composites.Sequence(name="Sub Sequence 3.1.1.1.2.1.1.1.1", memory=False) # this sequence is a child of sub_selector_3_1_1_1_2_1_1_1
    sub_sequence_3_1_1_1_2_1_1_1_2 = py_trees.composites.Sequence(name="Sub Sequence 3.1.1.1.2.1.1.1.2", memory=False) # this sequence is a child of sub_selector_3_1_1_1_2_1_1_1

    # Sub sequence 3.1.1.1.2.1.1.1.1
    check_if_user_ok_with_new_seq_2 = CheckUserOkWithNewSeq(name="Check if user is ok with new sequence", conversation=conversation)
    execute_new_sequence_2 = ExecuteNewSequence(name="Execute New Sequence", conversation=conversation)
    sub_sequence_3_1_1_1_2_1_1_1_1.add_children([check_if_user_ok_with_new_seq_2, execute_new_sequence_2])      # Level 9
    
    # Sub sequence 3.1.1.1.2.1.1.1.2
    ask_user_for_new_request_2 = AskUserForNewRequest(name="Ask User for New Request", conversation=conversation)
    wait_for_user_input_8 = WaitForUserInput(name="Wait for User Input", process_user_input_func=process_user_input, conversation=conversation)
    sub_sequence_3_1_1_1_2_1_1_1_2.add_children([ask_user_for_new_request_2, wait_for_user_input_8])            # Level 9
    
    # Sub selector 3.1.1.1.2.1.1.1
    sub_selector_3_1_1_1_2_1_1_1.add_children([sub_sequence_3_1_1_1_2_1_1_1_1, sub_sequence_3_1_1_1_2_1_1_1_2]) # Level 8    

    # Sub Sequence 3.1.1.1.2.1.1
    check_new_seq_2 = CheckNewSeq(name="Check New Sequence")
    explain_sequence_2 = ExplainSequence(name="Explain Sequence", conversation=conversation)
    sub_sequence_3_1_1_1_2_1_1.add_children([check_new_seq_2, explain_sequence_2, sub_selector_3_1_1_1_2_1_1_1]) # Level 7

    # Sub sequence 3.1.1.1.2.1.2
    report_failure_2 = ReportFailureBackToUser(name="Report Failure Back to User", conversation=conversation)
    wait_for_user_input_7 = WaitForUserInput(name="Wait for User Input", process_user_input_func=process_user_input, conversation=conversation)
    sub_sequence_3_1_1_1_2_1_2.add_children([report_failure_2, wait_for_user_input_7])                          # Level 7

    # Sub Selector 3.1.1.1.2.1
    sub_selector_3_1_1_1_2_1.add_children([sub_sequence_3_1_1_1_2_1_1, sub_sequence_3_1_1_1_2_1_2])             # Level 6

    # Sub Sequence 3.1.1.1.2
    generate_new_sequence_2 = GenerateNewSequence(name="Generate New Sequence", conversation=conversation)
    sub_sequence_3_1_1_1_2.add_children([generate_new_sequence_2, sub_selector_3_1_1_1_2_1])                    # Level 5
    
    # Sub Sequence 3.1.1.1.1
    check_var_inf_2 = CheckVarInf(name="Check for var_inf")
    decline_request_2 = DeclineRequest(name="Decline Request", conversation=conversation)
    wait_for_user_input_6 = WaitForUserInput(name="Wait for User Input", process_user_input_func=process_user_input, conversation=conversation)
    sub_sequence_3_1_1_1_1.add_children([check_var_inf_2, decline_request_2, wait_for_user_input_6])            # Level 5

    # Sub Selector 3.1.1.1
    sub_selector_3_1_1_1.add_children([sub_sequence_3_1_1_1_1, sub_sequence_3_1_1_1_2])                         # Level 4
    
    # Sub Sequence 3.1.1
    check_for_new_seq_2 = CheckForNewSeq2(name="Does it actually need a new Seq?", conversation=conversation)
    run_safety_check_2 = RunSafetyCheck(name="Run Safety Check", conversation=conversation)
    sub_sequence_3_1_1.add_children([check_for_new_seq_2, run_safety_check_2, sub_selector_3_1_1_1])            # Level 3

    # Sub Selector 3.1
    set_var_known_true = SetVarKnownTrue(name="Set var_known to True", process_user_input_func=process_user_input, conversation=conversation)
    sub_selector_3_1.add_children([sub_sequence_3_1_1, set_var_known_true])                                     # Level 2

    # Sequence 3
    check_for_new_seq = CheckForNewSeq(name="Check for New Sequence", conversation=conversation)
    sequence_3.add_children([check_for_new_seq, sub_selector_3_1])                                              # Level 1

    # Sequence 4: Fallback action
    sequence_4 = py_trees.composites.Sequence(name="Sequence 4", memory=False)

    # Fallback action: Say youre confused and ask the user if he wants you to do something
    fallback_answer = FallbackAnswer(name="Answer that user instruction is unclear", conversation=conversation)
    wait_for_user_input_9 = WaitForUserInput(name="Wait for User Input", process_user_input_func=process_user_input, conversation=conversation)
    sequence_4.add_children([fallback_answer, wait_for_user_input_9])                                           # Level 1

    root.add_children([sequence_1, sequence_2, sequence_3, sequence_4])                                         # Level 0
    return root

def build_test_tree():
    # just for testing conditions and actions directly
    root = py_trees.composites.Sequence(name="Test Tree\n?", memory=False)

    generate_new_seq = GenerateNewSequence(name="Generate New Sequence", conversation=conversation)
    check_new_seq = CheckNewSeq(name="Check New Sequence")

    root.add_children([generate_new_seq, check_new_seq])

    return root

def test_conditions_and_actions(user_input):
    global conversation
    conversation = DUMMY_CONVERSATION
    state.var_KnowNo = ['pancakes with maple syrup and berries', 'western breakfast sandwich with bacon and sausages']
    state.var_generated_sequence = state.Generated_sequence_in_the_var
    state.var_generated_sequence_name = "western breakfast sandwich with bacon and sausages"
    
    if FURHAT:
        state.var_furhat = initialize_furhat(FURHAT_IP_ADDRESS, FURHAT_VOICE_NAME)

    tree = build_test_tree()
    
    behaviour_tree = py_trees.trees.BehaviourTree(root=tree)
    
    #cProfile.runctx('behaviour_tree.tick()', globals(), locals())  # Profile the tick function
    behaviour_tree.tick()
    # Render the behavior tree
    #py_trees.display.render_dot_tree(behaviour_tree.root)

def process_user_input(user_input):
    global conversation, behaviour_tree  

    if FURHAT and state.var_furhat is None:
        state.var_furhat = initialize_furhat(FURHAT_IP_ADDRESS, FURHAT_VOICE_NAME)
        state.var_furhat.say(text = "Hello! I am Gregory. How can I help you today?")
        recorded_speech = record_speech(state.var_furhat)
        conversation.append({"role": "user", "content": recorded_speech})
        tree = build_tree(conversation, process_user_input)
        behaviour_tree = py_trees.trees.BehaviourTree(root=tree)
        print("Tree is initialized and furhat is used")
        state.var_transcript = "Version: " + VERSION + "\n" + time.strftime("%c") + "\nUser: " + recorded_speech + "\n" + "Tree is initialized and furhat is used" + "\n"
    elif state.var_furhat is None:
        state.var_furhat = "furhat not used in this run"
        tree = build_tree(conversation, process_user_input)
        behaviour_tree = py_trees.trees.BehaviourTree(root=tree)
        conversation.append({"role": "user", "content": user_input})
        print("user input: ", user_input)
        print("Tree is initialized but furhat is not")
        
        state.var_transcript = "Version: " + VERSION + "\n" + time.strftime("%c") + "\nUser: " + user_input + "\n" + "Tree is initialized but furhat is not" + "\n"
        
    behaviour_tree.tick()

    if len(conversation) < 2:
        py_trees.display.render_dot_tree(behaviour_tree.root)

# Full BT is called with the user input
if BASELINE:
    run_baseline()
else:
    process_user_input(user_input)

# Test conditions and actions directly   

#test_conditions_and_actions(user_input)
#print("conversation: ", conversation)

print(state.var_total_llm_calls)
if FURHAT:
    save_transcript(state.var_transcript)
    time.sleep(5)
    state.var_furhat.set_led(red =50 , green = 0 , blue = 0) # to indicate that the conversation is over
    state.var_furhat.say(text = "That's all for now. Thank you for the talk!")
    time.sleep(5)
    state.var_furhat.set_led(red = 0, green = 0, blue = 0) # Turn off the LED to avoid overheating
    state.var_furhat.attend(user="NONE") # Stop attending the user

