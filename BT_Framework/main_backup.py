import py_trees
from openai import OpenAI
client = OpenAI()

# DEBUG stuff
LLM = True # True when LLMs are being used

# Global variables
user_input = "I'm hungry what can you do for me?"  # Contains the user input
conversation = []  # Contains the conversation history between the user and the system

var_known = False  # Indicates whether the user input requests the execution of a known sequence
var_one = False  # Indicates whether KnowNo mapping maps to only one sequence
var_inf = False  # Indicates whether a sequence is infeasible to be generated, due to safety protocols
var_seq_ok = False  # Indicates whether a generated sequence passed the automated tests

MAX_LLM_CALL = 2  # Maximum number of calls to the LLM

# Prompts for the framework

# Pre-prompt for checking ambiguity
pre_prompt_ambiguous = """
Please classify user input as either 'True' if it's ambiguous or 'False' if it's not. Consider requests that lack specificity, invite a range of responses, or ask for suggestions as ambiguous. Identify specific requests with modifications, detailed actions, or sequences as non-ambiguous. If unsure, err on the side of categorizing it as ambiguous.

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

pre_prompt_ambiguous_answer =  """
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
Given the ambiguous user requests reply to the user in a polite manner in the following way:
- ask the user to specify his request
- based on the known sequences provide up to 3 suggestions that might fit the user request.
"""


# Behavior tree Actions

class PrintAmbiguousAnswer(py_trees.behaviour.Behaviour):
    
    var_llm_calls_ambiguity_answer = 0  # Number of calls to the LLM

    def __init__(self, name, conversation):
        super(PrintAmbiguousAnswer, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if LLM:
            # Call the LLM to generate the response
            #print("the conversation before the LLM call: ", self.conversation)
            response = self.generate_ambiguous_response_with_llm(self.conversation)
            print(response.replace('\\n', '\n').replace('\\\'', '\''))
            self.conversation.append({"role": "assistant", "content": response}) 
            #print("conversation with the LLM response: ", self.conversation)
        else:
            print("Ambiguous Answer 1")
        return py_trees.common.Status.SUCCESS
    
    def generate_ambiguous_response_with_llm(self, conversation):
        """
        This function generates a response to an ambiguous user input using the Chatgpt 3.5 turbo model.
        """
        # This logic is to prevent the LLM from being called too many times
        if PrintAmbiguousAnswer.var_llm_calls_ambiguity_answer >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            return "I'm sorry, I cannot help you at the moment.The maximum number of LLM calls has been exceeded."
        PrintAmbiguousAnswer.var_llm_calls_ambiguity_answer += 1
        #print("var_llm_calls_ambiguity_answer: ", PrintAmbiguousAnswer.var_llm_calls_ambiguity_answer)

        try:
            # Construct the final prompt by inserting the user input
            predefined_messages_ambiguous_answer = [
                    {"role": "system", "content": pre_prompt_ambiguous_answer},
                ]
            messages = predefined_messages_ambiguous_answer + self.conversation  # Start with the predefined context.
            #print("prepromt Messages for answering: ", messages)

            # Make the API call
            completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    # response_format={ "type": "json_object" },
                    messages=messages
                    )
            
            # Extract and return the response content
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error in LLM call: {e}")
            return "False"
        
class WaitForUserInput(py_trees.behaviour.Behaviour):
    """
    This action waits for new user input from the keyboard.
    """

    def __init__(self, name):
        super(WaitForUserInput, self).__init__(name)

    def update(self):
        new_user_input = input("Please specify your request based on the suggestions: ")
        process_user_input(new_user_input)  # Re-trigger the behavior tree with the new input
        return py_trees.common.Status.SUCCESS

    
# Behavior tree Conditions

class CheckForAmbiguity(py_trees.behaviour.Behaviour):
    """
    This is the condition to check if the user input is ambiguous.
    """
    var_llm_calls_ambiguity = 0  # Number of calls to the LLM
    # Condition to check if the user input is ambiguous
    def __init__(self, name, conversation):
        super(CheckForAmbiguity, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if LLM:
            # Call the LLM to check for ambiguity
            #print("the conversation before the LLM call: ", self.conversation)
            response = self.check_ambiguity_with_llm(self.conversation)
            print("Is it Ambiguous?: ", response)
            if response == "True":
                return py_trees.common.Status.SUCCESS
        elif 'ambig' in self.conversation[-1]['content']:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

    def check_ambiguity_with_llm(self, conversation):
        """
        This function checks if the user input is ambiguous using the Chatgpt 3.5 turbo model.
        """
        # This logic is to prevent the LLM from being called too many times
        if CheckForAmbiguity.var_llm_calls_ambiguity >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            return "False"
        CheckForAmbiguity.var_llm_calls_ambiguity += 1
        #print("var_llm_calls_ambiguity: ", CheckForAmbiguity.var_llm_calls_ambiguity)   

        try:
            # Construct the final prompt by inserting the user input
            predefined_messages_ambiguous = [
                    {"role": "system", "content": pre_prompt_ambiguous},
                ]

            messages = predefined_messages_ambiguous + conversation  # Start with the predefined context.
            #print("Check this convo for ambiguity: ", messages)

            # Make the API call
            completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    # response_format={ "type": "json_object" },
                    messages=messages
                    )
            
            # Extract and return the response content
            print("the response from the LLM call: ", completion.choices[0].message)
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error in LLM call: {e}")
            return "False"

class PrintExit1(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super(PrintExit1, self).__init__(name)

    def update(self):
        print("Eggbert1")
        return py_trees.common.Status.SUCCESS

class PrintExit2(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super(PrintExit2, self).__init__(name)

    def update(self):
        print("Eggbert2")
        return py_trees.common.Status.SUCCESS
    
class PrintExit3(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super(PrintExit3, self).__init__(name)

    def update(self):
        print("Eggbert3")
        return py_trees.common.Status.SUCCESS

class CheckForNewSeq(py_trees.behaviour.Behaviour):
    counter = 0  # Class attribute to count the total calls across instances

    def __init__(self, name, conversation):
        super(CheckForNewSeq, self).__init__(name)
        self.conversation = conversation

    def update(self):
        # later i will have an api call to openai here that checks if the input_string requests a new sequence
        CheckForNewSeq.counter += 1  # Increment the counter each time the behavior is called
        if 'New Seq' in self.conversation[-1]['content']:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE



# Behavior tree

def build_tree(conversation):
    root = py_trees.composites.Selector(name="Root Selector", memory=False)
    
    # First sequence: Check for ambiguity and then print "Answer for Ambiguity"
    sequence_1 = py_trees.composites.Sequence(name="Sequence 1", memory=False)
    check_ambiguity = CheckForAmbiguity(name="Check for Ambiguity", conversation=conversation)
    print_answer_for_ambiguity = PrintAmbiguousAnswer(name="Print 'Answer for Ambiguity'", conversation=conversation)
    wait_for_user_input = WaitForUserInput(name="Wait for User Input")
    sequence_1.add_children([check_ambiguity, print_answer_for_ambiguity, wait_for_user_input])
    
    # Second sequence: Check for new sequence and then print "Eggbert2"
    sequence_2 = py_trees.composites.Sequence(name="Sequence 2", memory=False)
    check_new_seq = CheckForNewSeq(name="Check for New Seq", conversation=conversation)
    print_exit2 = PrintExit2(name="Print 'Eggbert2'")
    sequence_2.add_children([check_new_seq, print_exit2])
    
    # Fallback action: Print "Eggbert3" if both sequences fail
    print_exit3 = PrintExit3(name="Print 'Eggbert3'")
    
    root.add_children([sequence_1, sequence_2, print_exit3])
    
    return root


# Function to update the conversation and re-trigger the behavior tree
def process_user_input(user_input):
    global conversation
    # Add the user input to the conversation history
    conversation.append({"role": "user", "content": user_input})

    #print("the tree will be ticked with the conversation: ", conversation)
    
    # Build and create the tree
    tree = build_tree(conversation)
    behaviour_tree = py_trees.trees.BehaviourTree(root=tree)
    
    # Tick the tree (i.e., run the behavior)
    behaviour_tree.tick()

# Initial user input processing
process_user_input(user_input)
