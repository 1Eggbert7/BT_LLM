# main.py
# Alexander Leszczynski
# 08-06-2024 

import py_trees
from actions import WaitForUserInput, PrintAmbiguousAnswer, PrintExit1, PrintExit2, PrintExit3, KnowNoMapping, ExecuteAction, RunSafetyCheck, DeclineRequest, GenerateNewSequence, ExplainSequence
from conditions import CheckForAmbiguity, CheckForNewSeq, CheckVarKnownCondition, CheckForKnown, CheckVarKnowNo, CheckMapping, CheckVarInf, CheckNewSeq
from config import LLM
import state
from prompts import DUMMY_CONVERSATION
from utils import format_conversation

#py_trees.logging.level = py_trees.logging.Level.DEBUG

user_input =  format_conversation(DUMMY_CONVERSATION)# Contains the user input
conversation = []  # Contains the conversation history between the user and the system

def build_tree(conversation, process_user_input):
    root = py_trees.composites.Selector(name="Full BT Root Selector", memory=False)
    
    # Sequence 1: Check for ambiguity, print answer for ambiguity, wait for user input. This sequence has 3 sub sequences
    sequence_1 = py_trees.composites.Sequence(name="Sequence 1", memory=False)
    check_ambiguity = CheckForAmbiguity(name="Check for Ambiguity", conversation=conversation)
    print_answer_for_ambiguity = PrintAmbiguousAnswer(name="Print 'Answer for Ambiguity'", conversation=conversation)
    wait_for_user_input = WaitForUserInput(name="Wait for User Input", process_user_input_func=process_user_input)
    sequence_1.add_children([check_ambiguity, print_answer_for_ambiguity, wait_for_user_input]) # Level 1
    
    # Sequence 2: Check for Known sequence and generate new sequence if needed. This sequence has 5 sub selectors and 6 sub sequences
    sequence_2 = py_trees.composites.Sequence(name="Sequence 2", memory=False)
    
    
    print_exit2 = PrintExit2(name="Print 'Eggbert2'")
    
    # Sequences and Selectors for Sequence 2
    sub_selector_2_1 = py_trees.composites.Selector(name="Sub Selector 2.1", memory=False) # this selector is a child of sequence_2
    sub_selector_2_2 = py_trees.composites.Selector(name="Sub Selector 2.2", memory=False) # this selector is a child of sequence_2
    sub_sequence_2_2_1 = py_trees.composites.Sequence(name="Sub Sequence 2.2.1", memory=False) # this sequence is a child of sub_selector_2_2
    sub_sequence_2_2_2 = py_trees.composites.Sequence(name="Sub Sequence 2.2.2", memory=False) # this sequence is a child of sub_selector_2_2
    sub_selector_2_2_2_1 = py_trees.composites.Selector(name="Sub Selector 2.2.2.1", memory=False) # this selector is a child of sub_sequence_2_2_2
    sub_sequence_2_2_2_1_1 = py_trees.composites.Sequence(name="Sub Sequence 2.2.2.1.1", memory=False) # this sequence is a child of sub_selector_2_2_2_1
    sub_sequence_2_2_2_1_2 = py_trees.composites.Sequence(name="Sub Sequence 2.2.2.1.2", memory=False) # this sequence is a child of sub_selector_2_2_2_1
    sub_selector_2_2_2_1_2_1 = py_trees.composites.Selector(name="Sub Selector 2.2.2.1.2.1", memory=False) # this selector is a child of sub_sequence_2_2_2_1_2
    sub_sequence_2_2_2_1_2_1_1 = py_trees.composites.Sequence(name="Sub Sequence 2.2.2.1.2.1.1", memory=False) # this sequence is a child of sub_selector_2_2_2_1_2_1

    # Sub selector 2.1
    check_var_known = CheckVarKnownCondition(name="Check for var_known")
    check_known = CheckForKnown(name= "Check for known", conversation=conversation)
    sub_selector_2_1.add_children([check_var_known, check_known])                                       # Level 2 

    # Sub sequence 2.2.1
    check_var_knowNo = CheckVarKnowNo(name="Check if var_KnowNo == 1")
    check_legitness_of_mapping = CheckMapping(name="Check Mapping", conversation=conversation)
    execute_action = ExecuteAction(name="Execute known Action", conversation=conversation)
    sub_sequence_2_2_1.add_children([check_var_knowNo, check_legitness_of_mapping, execute_action])     # Level 3    

    # Sub sequence 2.2.2.1.1
    check_var_inf = CheckVarInf(name="Check for var_inf")
    decline_request = DeclineRequest(name="Decline Request")
    sub_sequence_2_2_2_1_1.add_children([check_var_inf, decline_request])                               # Level 5

    # Sub sequence 2.2.2.1.2.1.1
    check_new_seq = CheckNewSeq(name="Check New Sequence")
    explain_sequence = ExplainSequence(name="Explain Sequence", conversation=conversation)
    sub_sequence_2_2_2_1_2_1_1.add_children([check_new_seq, explain_sequence])                          # Level 7

    # Sub selector 2.2.2.1.2.1
    sub_selector_2_2_2_1_2_1.add_children([sub_sequence_2_2_2_1_2_1_1])                                 # Level 6

    # Sub sequence 2.2.2.1.2
    generate_new_sequence = GenerateNewSequence(name="Generate New Sequence", conversation=conversation)
    sub_sequence_2_2_2_1_2.add_children([generate_new_sequence, sub_selector_2_2_2_1_2_1])              # Level 5

    # Sub selector 2.2.2.1
    sub_selector_2_2_2_1.add_children([sub_sequence_2_2_2_1_1, sub_sequence_2_2_2_1_2])                 # Level 4                                    

    # Sub sequence 2.2.2
    check_var_knowNo_2 = CheckVarKnowNo(name="Check if var_KnowNo == 1 again")
    run_safety_check = RunSafetyCheck(name="Run Safety Check", conversation=conversation)
    print_exit1 = PrintExit1(name="Print 'Eggbert1'") # placeholder for now
    sub_sequence_2_2_2.add_children([check_var_knowNo_2, run_safety_check, sub_selector_2_2_2_1])       # Level 3

    # Sub selector 2.2
    sub_selector_2_2.add_children([sub_sequence_2_2_1, sub_sequence_2_2_2])                             # Level 2
    
    # Sequence 2
    know_no_mapping = KnowNoMapping(name="KnowNo Mapping", conversation=conversation)
    sequence_2.add_children([sub_selector_2_1, know_no_mapping, sub_selector_2_2])                      # Level 1
    
    # Fallback action: Print "Eggbert3" if both sequences fail
    print_exit3 = PrintExit3(name="Print 'Eggbert3'") # will not be executed atm
    
    root.add_children([sequence_1, sequence_2, print_exit3]) # Level 0
    
    return root

def build_test_tree():
    # just for testing conditions and actions directly
    root = py_trees.composites.Sequence(name="Test Tree", memory=False)

    check_sequence = CheckNewSeq(name="Check New Sequence")
    explain_sequence = ExplainSequence(name="Explain Sequence", conversation=conversation)

    root.add_children([check_sequence, explain_sequence])

    return root

def test_conditions_and_actions(user_input):
    global conversation
    conversation = DUMMY_CONVERSATION
    state.var_KnowNo = ['pancakes with maple syrup and berries']
    state.var_generated_sequence = state.var_generated_sequence_test

    tree = build_test_tree()
    
    behaviour_tree = py_trees.trees.BehaviourTree(root=tree)
    behaviour_tree.tick()
    # Render the behavior tree
    py_trees.display.render_dot_tree(behaviour_tree.root)

def process_user_input(user_input):
    global conversation
    conversation.append({"role": "user", "content": user_input})

    tree = build_tree(conversation, process_user_input)
    behaviour_tree = py_trees.trees.BehaviourTree(root=tree)
    behaviour_tree.tick()

    # Render the behavior tree
    py_trees.display.render_dot_tree(behaviour_tree.root)

# Initial user input processing
print("User: ", user_input)

# Full BT is called with the user input
process_user_input(user_input)

# Test conditions and actions directly

#test_conditions_and_actions(user_input)

#test_conditions_and_actions(user_input)
print(state.var_total_llm_calls)