# actions.py
# Alexander Leszczynski
# 30-08-2024

import py_trees
from openai import OpenAI
from prompts import PRE_PROMPT_AMBIGUOUS_ANSWER, PRE_PROMPT_KNOWN, FORMAT_SCHEME, FIRST_SHOT, SECOND_SHOT, THIRD_SHOT, PRE_PROMPT_KNOWNO, SECOND_SHOT_ASSISTANT_ANSWER, TEST_JSON_MC_RAW, PRE_PROMPT_MC_SCORES, AMBIGUOUS_SHOT, PREDEFINED_SAFETY_FEASIBILITY, PRE_PROMPT_NEW_SEQ, FIRST_SHOT_EXPLAIN_SEQ, FIRST_SHOT_EXPLAIN_SEQ_ANSWER, PRE_PROMPT_SAFETY_FEASIBILITY
from config import MAX_LLM_CALL, LLM, FURHAT, EXPLAIN
from utils import format_conversation, speak, record_speech
import state
import json
import random
import numpy as np
import time
import re

client = OpenAI()

class PrintAmbiguousAnswer(py_trees.behaviour.Behaviour):
    """
    This action prints an ambiguous answer to the user. Informing the user that the request is ambiguous and offering to help with more information.
    """

    def __init__(self, name, conversation):
        super(PrintAmbiguousAnswer, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if EXPLAIN:
            response = "Sorry ,but your request is ambiguous to me. I will need more information to help you. Could you please provide more details or clarify your request?"
            if FURHAT:
                speak(state.var_furhat, response)
            print("Assistant Explanation: ", response)
            state.var_transcript += "Assistant Explanation: " + response + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
        elif LLM:
            # Call the LLM to generate the response
            #print("the conversation before the LLM call: ", self.conversation)
            response = self.generate_ambiguous_response_with_llm(self.conversation)
            print("Assistant: ", response.replace('\\n', '\n').replace('\\\'', '\''))
            state.var_transcript += "Assistant: " + response.replace('\\n', '\n').replace('\\\'', '\'') + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            if FURHAT:
                speak(state.var_furhat, response)
            self.conversation.append({"role": "assistant", "content": response}) 
            #print("conversation with the LLM response: ", self.conversation)
        else:
            if FURHAT:
                speak(state.var_furhat, "Yo I'm sorry, I cannot help you at the moment. The Large Language Model is not available.")
            print("The LLM variable is set to False. Therefore, I cannot help you at the moment. The Large Language Model is not available.")
            state.var_transcript += "The LLM variable is set to False. Therefore, I cannot help you at the moment. The Large Language Model is not available.\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"

        formated_conversation = format_conversation(self.conversation)
        #print("The conversation log after the ambiguous answer: ", formated_conversation)
        return py_trees.common.Status.SUCCESS
    
    def generate_ambiguous_response_with_llm(self, conversation):
        """
        This function generates a response to an ambiguous user input using the Chatgpt-4o-mini model.
        """
        # This logic is to prevent the LLM from being called too many times
        if state.var_total_llm_calls >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            state.var_transcript += "Exceeded the maximum number of LLM calls.\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "I'm sorry, I cannot help you at the moment.The maximum number of LLM calls has been exceeded."
        state.var_total_llm_calls += 1
        #print("number of total llm calls was raised to: ", state.var_total_llm_calls)
        #print("the conversation before the LLM call: ", conversation)
        try:
            # Construct the final prompt by inserting the user input
            predefined_messages_ambiguous_answer = [
                    {"role": "system", "content": PRE_PROMPT_AMBIGUOUS_ANSWER}
                ]
            
            # this is where shots are added
            first_shot = {"role": "user", "content": "Assistant: Hello! I am Gregory, your home assistant. How can I help you today?\nUser: Hello there, I'm hungry. What can I eat?"}
            first_shot_answer = {"role": "assistant", "content": "There are multiple options in my list that might fit your order. I can help you with the hunger. Here are some suggestions to fight your hunger: \n1. A 'peanut butter and jelly sandwich' is a classic \n2. A 'bacon and egg sandwich' or \n 3. Some 'pancakes with maple syrup and berries'. \nWhich one would you like to have?"}

            second_shot = {"role": "user", "content": "Assistant: Hello! I am Gregory, your home assistant. How can I help you today?\nUser: I can you make me hachapuri"}
            second_shot_answer = {"role": "assistant", "content": "There are multiple options in my list that might fit your order. I understand you're looking for 'hachapuri'. Unfortunately, that isn't part of the recipes I know how to make. However, I can offer you some of my known actions like \n a 'bean and cheese quesadilla' or \n a 'grilled tomato and mushroom bruschetta' or \n a 'tortilla with tomatoes, beans, and egg (huevos rancheros)'. \nPlease let me know if any of these options interest you, or if you have any other preferences or requests."}
            
            third_shot = {"role": "user", "content": "Assistant: Hello! I am Gregory, your home assistant. How can I help you today?\nUser: um I'm not sure what to eat\nAssistant: Hello! If you're not sure what to eat, here are a few options you can consider:\n1. Pancakes with maple syrup and berries\n2. Full English breakfast\n3. Vegetable stir fry with rice\nLet me know if any of these options sound good to you, or if you need more suggestions!\nUser: what do you recommend"} 
            third_shot_answer = {"role": "assistant", "content": "There are multiple options in my list that might fit your order. If you want a hearty breakfast, I recommend the 'full English breakfast'. It's a classic English breakfast with eggs, bacon, sausage, beans, mushrooms and toast. Would you like that?"}

            fourth_shot = {"role": "user", "content": "Assistant: Hello! I am Gregory, your home assistant. How can I help you today?\nUser: um can i get the bacon and accent please"}
            fourth_shot_answer = {"role": "assistant", "content": "There are multiple options in my list that might fit your order. Did i understand it right that you're looking for a 'bacon and egg sandwich'. I can prepare that for you. Or would you like something else?"}

            formatted_conversation = format_conversation(conversation)

            predefined_messages_ambiguous_answer = predefined_messages_ambiguous_answer + [first_shot, first_shot_answer, second_shot, second_shot_answer, third_shot, third_shot_answer, fourth_shot, fourth_shot_answer]

            # Append the formatted conversation to the predefined messages
            predefined_messages_ambiguous_answer.append(
                {
                    "role": "user",
                    "content": formatted_conversation
                }
            )
            messages = predefined_messages_ambiguous_answer
            #print("prepromt Messages for answering: ", messages)

            # Make the API call
            completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    # response_format={ "type": "json_object" },
                    messages=messages
                    )
            
            # Extract and return the response content
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error in LLM call: {e}")
            state.var_transcript += "Error in LLM call: " + str(e) + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "False"
        
class WaitForUserInput(py_trees.behaviour.Behaviour):
    """
    This action waits for new user input from the keyboard.
    """

    def __init__(self, name, process_user_input_func, conversation):
        super(WaitForUserInput, self).__init__(name)
        self.process_user_input_func = process_user_input_func
        self.conversation = conversation

    def update(self):
        if FURHAT: 
            new_user_input = record_speech(state.var_furhat)
        else:
            new_user_input = input("User: ")
        self.conversation.append({"role": "user", "content": new_user_input})
        state.var_transcript += "User: " + new_user_input + "\n"
        state.var_transcript += "Time: " + time.strftime("%c") + "\n"
        formatted_conversation = format_conversation(self.conversation)
        #print("The conversation log after the user input: ", formatted_conversation)

        if new_user_input != "esc":
            self.process_user_input_func(new_user_input)  # Re-trigger the behavior tree with the new input, don't retrigger when esc is pressed
        #else:
            #if FURHAT:
            #    speak(state.var_furhat, "Alright, that's it for this task.")
        return py_trees.common.Status.SUCCESS

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
    
class KnowNoMapping(py_trees.behaviour.Behaviour):
    """
    This action leverages a modified version of the KnowNo-framework to fill the var_KnowNo list with possible actions that could map to the user input.
    """

    def __init__(self, name, conversation):
        super(KnowNoMapping, self).__init__(name)
        self.conversation = conversation

    def update(self):

        #create_messages_KnowNo(conversation)
        # make sure var_known_no is empty
        if LLM:
            state.var_KnowNo = []

            result = self.create_mc_KnowNo(self.conversation)
            #print("Result: ", result)
            the_options, the_options_list , the_add_mc_prefix = self.process_mc_raw(result, add_mc='something else')
            #print("the options: ", the_options)
            #print("the add mc prefix: ", the_add_mc_prefix)
            logprobs = self.get_logprobs(the_options, self.conversation)
            #print('\n====== Raw log probabilities for each option ======')
            #for option, logprob in logprobs.items():
            #    print(f'Option: {option} \t log prob: {logprob}')

            # next we fill the state of var_KnowNo with the options that are above a certain threshold
            self.fill_var_KnowNo(logprobs, the_options_list)
            print("var_KnowNo: ", state.var_KnowNo)
            state.var_transcript += "var_KnowNo: " + str(state.var_KnowNo) + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
        else:
            state.var_KnowNo = ['Magical robot soup']
            print("The LLM variable is set to False. Therefore, I cannot help you at the moment. The Large Language Model is not available.")
            state.var_transcript += "The LLM variable is set to False. Therefore, I cannot help you at the moment. The Large Language Model is not available.\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"

        KnowNo_bool = self.KnowNo_legit(state.var_KnowNo)
        if not KnowNo_bool:
            self.correct_knowno()

        #print("The var_KnowNo list after the correction: ", state.var_KnowNo)
        return py_trees.common.Status.SUCCESS
    
    def correct_knowno(self):
        """
        This function corrects the var_KnowNo list if it contains actions that are not part of the known sequences. Unknown actions are deleted from the list.
        """
        with open('sequences.json', 'r') as f:
            known_sequences = json.load(f)
        known_sequences_json = json.dumps(known_sequences)

        print("The var_KnowNo list before the correction: ", state.var_KnowNo)
        print("it contains a number of : ", len(state.var_KnowNo), " actions.")

        # Create a filtered list that keeps only known actions or 'something else'
        state.var_KnowNo = [action for action in state.var_KnowNo if action in known_sequences_json or action == "something else"]

        # make sure something else is not 2 times in the list 
        # first see if it contains something else
        if state.var_KnowNo.count("something else") > 1:
            state.var_KnowNo = [action for action in state.var_KnowNo if action != "something else"]
            state.var_KnowNo.append("something else")

        # make sure its not empty and at least add 'something else' if it is
        if len(state.var_KnowNo) == 0:
            state.var_KnowNo.append("something else")

        
    
    def KnowNo_legit(self, var_KnowNo):
        """
        Checks if the KnowNo list is legitimate, by checking if each element is part of the known sequence list or says "something else".
        """
        with open('sequences.json', 'r') as f:
            known_sequences = json.load(f)
        known_sequences_json = json.dumps(known_sequences)

        for action in var_KnowNo:
            if action not in known_sequences_json:
                if action != "something else":
                    print("The action: ", action, " is not part of the known sequences.")
                    return False
       

        return True
    
    
    def fill_var_KnowNo(self, logprobs, the_options_list):
        """
        This function fills the var_KnowNo list with the options that are above a certain threshold.
        """
        qhat = 0.900
        top_tokens = list(logprobs.keys())
        top_logprobs = [logprob if logprob is not None else -1e10 for logprob in logprobs.values()]  # Replace None with a large negative number to avoid errors

        mc_smx_all = self.temperature_scaling(top_logprobs, temperature=5)
        
        # include all options with score >= 1-qhat
        prediction_set = [
            token for token_ind, token in enumerate(top_tokens)
            if mc_smx_all[token_ind] >= 1 - qhat
        ]

        # print
        #print('Softmax scores:', mc_smx_all)
        #print('Prediction set of the KnowNo operation:', prediction_set)

        case = {
                'A': 1,
                'B': 2,
                'C': 3,
                'D': 4,
                'E': 5
            }
        
        for token in prediction_set:
            state.var_KnowNo.append(the_options_list[case[token] - 1])
        #print("var_KnowNo: ", state.var_KnowNo)

    def temperature_scaling(self, logits, temperature):
        """
        This function applies temperature scaling to the logits.
        """
        #print('Temperature scaling with T =', temperature)
        #print('Original logits:', logits)
        logits = np.array(logits)
        logits /= temperature

        # apply softmax
        logits -= logits.max()
        logits = logits - np.log(np.sum(np.exp(logits)))
        smx = np.exp(logits)
        #print('Scaled logits:', smx)
        return smx

    def create_mc_KnowNo(self, conversation):
        """
        This function creates the multi-choice messages for the KnowNo-framework.
        """
        # This logic is to prevent the LLM from being called too many times
        if state.var_total_llm_calls >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            state.var_transcript += "Exceeded the maximum number of LLM calls.\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "I'm sorry, I cannot help you at the moment. The maximum number of LLM calls has been exceeded."
        
        state.var_total_llm_calls += 1

        predefined_messages_KnowNo = [
            {"role": "system", "content": PRE_PROMPT_KNOWNO.format(FORMAT_SCHEME)},
            {"role": "user", "content": "I want the bacon and egg sandwich."},
            {"role": "assistant", "content": FIRST_SHOT},
            {"role": "user", "content": "Hey, I'm hungry, what can I eat?"},
            {"role": "assistant", "content": SECOND_SHOT_ASSISTANT_ANSWER},
            {"role": "user", "content": "I'll have option 2."},
            {"role": "assistant", "content": SECOND_SHOT}
        ]

        messages = predefined_messages_KnowNo + conversation  # Start with the predefined context.

        try:
            # Make the API call
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            
            # Extract the result
            result = completion.choices[0].message.content.strip()

            # Try to detect and extract the JSON part using regex
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            
            if json_match:
                # Extract the JSON part
                json_str = json_match.group(0)
                try:
                    # Parse the JSON part
                    json_result = json.loads(json_str)
                    return json_result
                except json.JSONDecodeError:
                    # Handle failed JSON parsing even after extraction
                    print("Failed to parse extracted JSON. Received result:", json_str)
                    state.var_transcript += "Error: Failed to parse extracted JSON.\n"
                    state.var_transcript += "Time: " + time.strftime("%c") + "\n"
                    return {"choices": [{"action": "something else"}]}  # Fallback content

            else:
                # If no JSON found in the response
                print("No JSON found in the response. Received result:", result)
                state.var_transcript += "Error: No JSON found in the response.\n"
                state.var_transcript += "Time: " + time.strftime("%c") + "\n"
                return {"choices": [{"action": "something else"}]}  # Fallback content
        
            
        except Exception as e:
            print(f"Error in LLM call: {e}")
            state.var_transcript += "Error in LLM call: " + str(e) + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "Failed LLM call"

    
    def get_logprobs(self, options, conversation):
        """
        This function gets the logprobs for the multi-choice options.
        """
        if state.var_total_llm_calls >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            state.var_transcript += "Exceeded the maximum number of LLM calls.\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "I'm sorry, I cannot help you at the moment.The maximum number of LLM calls has been exceeded."
        state.var_total_llm_calls += 1

        predefined_messages_mc_scores = [
                    {"role": "system", "content": PRE_PROMPT_MC_SCORES}
                ]
        
        # idea: add more shots to the conversation
        first_shot = {"role": "user", "content": "The options are: A) grilled tomato and mushroom bruschetta\nB) an option not listed here\nC) bacon and egg sandwich\nD) full English breakfast\nE) vegetable stir fry with rice. Now select the letter that fits best to the following conversation: \nUser: can I have a grilled tomato and mushroom to set up please\nAssistant: It seems like you're requesting a 'grilled tomato and mushroom bruschetta.' I can prepare that for you. Would you like anything else with it?\nUser: no\n"}
        first_shot_answer = {"role": "assistant", "content": "A"}

        second_shot = {"role": "user", "content": "The options are: A) an option not listed here\nB) full English breakfast\nC) bean and cheese quesadilla\nD) pancakes with maple syrup and berries\nE) grilled tomato and mushroom bruschetta. Now select the letter that fits best to the following conversation: \nUser: I can you make me hachapuri\nAssistant: I apologize for any confusion, but could you please provide more details or clarify your request for hachapuri? Are you looking for a specific type of hachapuri or any particular ingredients or preferences? Once I have more information, I can assist you better.?\nUser: I have more information I can assist you better hachapuri aari\nAssistant: Thank you for clarifying! Unfortunately, the recipe for 'hachapuri aari' is not within my known recipes. However, I can offer you some other options:\n 1. 'Bean and Cheese Quesadilla': Makes a bean and cheese quesadilla by heating beans and preparing a tortilla. The quesadilla is served hot and ready to enjoy.\n2. 'Grilled Tomato and Mushroom Bruschetta': Creates a grilled tomato and mushroom bruschetta by grilling tomatoes and mushrooms on toasted bread, making a simple yet delicious appetizer.\n3. 'Tortilla with Tomatoes, Beans, and Egg (Huevos Rancheros)': Prepares huevos rancheros with a tortilla, beans, tomatoes, and eggs in a flavorful breakfast dish.\nPlease let me know if any of these options interest you, or if you have any other preferences or requests.\nUser: the first 1\n"}
        second_shot_answer = {"role": "assistant", "content": "C"}

        convo_to_add = {"role": "user", "content": "The options are: " + options + ". Now select the letter that fits best to the following conversation: \n" + format_conversation(conversation)}
        #print("formatted conversation: ", convo_to_add)
        
        messages = predefined_messages_mc_scores + [first_shot, first_shot_answer, second_shot, second_shot_answer, convo_to_add]
        

        try:
            # Make the API call
            completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    logprobs=True,
                    top_logprobs=20,
                    max_tokens=1,
                    logit_bias={
                        32: 100.0,   #  A (without space at front)
                        33: 100.0,   #  B (without space at front)
                        34: 100.0,   #  C (without space at front)
                        35: 100.0,   #  D (without space at front)
                        36: 100.0,   #  E (without space at front)
                        362: 100.0,  #  A (with space at front)
                        426: 100.0,  #  B (with space at front)
                        356: 100.0,  #  C (with space at front)
                        423: 100.0,  #  D (with space at front)
                        469: 100.0   #  E (with space at front)
                    }
                    )
            
            option_logprobs = {'A': None, 'B': None, 'C': None, 'D': None, 'E': None}
            choice = completion.choices[0]

            # Access the content, which contains the logprobs details for each token
            content_logprobs = choice.logprobs.content

            # Iterate through each token's logprob in content_logprobs
            for token_logprob in content_logprobs:
                # For each token, iterate through its top_logprobs to find probabilities of interest
                for top_logprob in token_logprob.top_logprobs:
                    # Check if the current top_logprob token is one of our options (A, B, C, D, or E)
                    #print(top_logprob)
                    if top_logprob.token in option_logprobs:
                        # If this is the first time we see a logprob for this token or if this logprob is higher, update it                        
                        if option_logprobs[top_logprob.token] is None or top_logprob.logprob > option_logprobs[top_logprob.token]:
                            option_logprobs[top_logprob.token] = top_logprob.logprob

            # Convert option_logprobs to a list of log probabilities in the same order as top_tokens for consistency
            top_tokens = ['A', 'B', 'C', 'D', 'E']  # Define the order of tokens explicitly
            top_logprobs = [option_logprobs[token] if token in option_logprobs else float('-inf') for token in top_tokens]  # Use '-inf' for missing options

            #print('\n====== Raw log probabilities for each option ======')
            #for option, logprob in option_logprobs.items():
            #    print(f'Option: {option} \t log prob: {logprob}')
            #print("options are: ", options)

            # Extract and return the response content
            return option_logprobs
        except Exception as e:
            print(f"Error in LLM call: {e}")
            state.var_transcript += "Error in LLM call: " + str(e) + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "Failed LLM call"

    def process_mc_raw(self, mc_raw, add_mc='something else'):
        """
        This function processes the raw output from the LLM for the multi-choice options.
        """
        mc_processed_all = []

        # mc_raw is now expected to be a dictionary (already parsed JSON), so we don't need to parse it again.
        mc_gen_raw_json = mc_raw

        # Now mc_gen_raw_json is a dictionary, we access its 'choices' key
        if "choices" not in mc_gen_raw_json:
            raise Exception("Missing 'choices' key in mc_raw.")

        for choice in mc_gen_raw_json["choices"]:
            # Combine the option and action into a single string
            option_action = f"{choice['action']}"
            # Append the combined string to the list
            mc_processed_all.append(option_action)

        # Remove duplicates
        mc_processed_all = list(set(mc_processed_all))

        # Ensure there are at least 4 options, fill with 'do nothing' if needed
        while len(mc_processed_all) < 4:
            mc_processed_all.append('do nothing')

        # Prepare prefixes
        prefix_all = ['A) ', 'B) ', 'C) ', 'D) ']
        if add_mc is not None:
            mc_processed_all.append(add_mc)
            prefix_all.append('E) ')
        
        # Shuffle the options randomly
        random.shuffle(mc_processed_all)

        # Ensure 'something else' is the last option
        if add_mc in mc_processed_all:
            mc_processed_all.remove(add_mc)
        mc_processed_all.append(add_mc)

        # Create the final prompt
        mc_prompt = ''
        for mc_ind, (prefix, mc) in enumerate(zip(prefix_all, mc_processed_all)):
            mc_prompt += prefix + mc
            if mc_ind < len(mc_processed_all) - 1:
                mc_prompt += '\n'

        # Add prefix for 'something else'
        add_mc_prefix = prefix_all[mc_processed_all.index(add_mc)][0]

        return mc_prompt, mc_processed_all, add_mc_prefix



class ExecuteAction(py_trees.behaviour.Behaviour):
    """
    This action executes the action that maps to the user input, by acknowledging the user input and providing the response.
    """

    def __init__(self, name, conversation):
        super(ExecuteAction, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if EXPLAIN:
            response = "I understood your request and will now execute the action."
        else:
            response = self.execute_action(self.conversation)
        
        if FURHAT:
            #state.var_furhat.gesture(name="Nod") # Furhat nods to acknowledge the user input
            speak(state.var_furhat, response)
        self.conversation.append({"role": "assistant", "content": response})
        print("Assistant: ", response)
        state.var_transcript += "Assistant: " + response + "\n"
        state.var_transcript += "Time: " + time.strftime("%c") + "\n"
        formatted_conversation = format_conversation(self.conversation)
        #print("The conversation log after the action execution: ", formatted_conversation)

        return py_trees.common.Status.SUCCESS

    def execute_action(self, conversation):
        """
        This function executes the action by acknowledging the user input and providing the response.
        """
        #choices =  ['bacon and egg sandwich', 'avocado toast with sausage on the side', 'peanut butter and jelly sandwich', 'vegetable stir fry with rice', 'pancakes with maple syrup and berries', 'full English breakfast', 'tortilla with tomatoes beans and egg (huevos rancheros)', 'bean and cheese quesadilla', 'grilled tomato and mushroom bruschetta', 'clean living room floor']
        #random_choice = random.choice(choices)
        response = "Great choice! I will get the task for {} started.".format(state.var_KnowNo[0])
        return response

class ExecuteNewSequence(py_trees.behaviour.Behaviour):
    """
    This action executes the new sequence that was generated.
    """

    def __init__(self, name, conversation):
        super(ExecuteNewSequence, self).__init__(name)
        self.conversation = conversation
    
    def update(self):
        if EXPLAIN:
            response = "You confirmed the newly generated sequence. I will now proceed to execute it."
        else:
            response = self.execute_new_sequence()
        self.conversation.append({"role": "assistant", "content": response})

        if FURHAT:
            speak(state.var_furhat, response)
        print("Assistant: ", response)
        state.var_transcript += "Assistant: " + response + "\n"
        state.var_transcript += "Time: " + time.strftime("%c") + "\n"

        formatted_conversation = format_conversation(self.conversation)
        #print("The conversation log after the new sequence execution: ", formatted_conversation)

        return py_trees.common.Status.SUCCESS

    def execute_new_sequence(self):
        """
        This function executes the new sequence that was generated.
        """
        response = "Great then I will now proceed to make the: {}".format(state.var_generated_sequence_name)
        return response

class RunSafetyCheck(py_trees.behaviour.Behaviour):
    """
    This action runs a safety check to ensure that the user request for a new Sequenence is feasible and safe.
    """

    def __init__(self, name, conversation):
        super(RunSafetyCheck, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if LLM:
            response = self.run_safety_check(self.conversation)
            print("Did it pass the safety check?: ", response)
            state.var_transcript += "Did it pass the safety check?: " + response + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
        else:
            print("Safety Check 1")
            state.var_transcript += "Safety Check 1.\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            response = 'False'  # Default to 'False' if LLM is not used

        if 'true' in response.strip()[:10].lower():
            state.var_inf = False
            return py_trees.common.Status.SUCCESS
        else:
            state.var_inf = True

            # Extract the part after "Explanation:"
            if 'Explanation:' in response:
                explanation = response.split('Explanation:')[1].strip()
                state.var_decline_explanation = explanation
            return py_trees.common.Status.SUCCESS


    def run_safety_check(self, conversation):
        """
        This function runs a safety check to ensure that the action to be executed is safe, with Chatgpt-4o-mini.
        """
        # This logic is to prevent the LLM from being called too many times
        if state.var_total_llm_calls >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            state.var_transcript += "Exceeded the maximum number of LLM calls.\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "I'm sorry, I cannot help you at the moment.The maximum number of LLM calls has been exceeded."
        state.var_total_llm_calls += 1
        formatted_conversation = format_conversation(conversation)
        #print("formatted conversation: ", formatted_conversation)

        try:
            predefined_messages_sfty_check = [
                    {"role": "system", "content": PRE_PROMPT_SAFETY_FEASIBILITY}
                ]
            
            # this is where shots are added
            first_shot = {"role": "user", "content": "User: I want the pancakes but can you do it with bananas and chocolate chips instead of the berries and the syrup?"}
            first_shot_answer = {"role": "assistant", "content": "False\nExplanation: The request involves unknown ingredients (chocolate chips, bananas) that can't be found in the provided list of known ingredients, making it not feasible for the me to execute."}

            second_shot = {"role": "user", "content": "User: I want something to eat.\n Assistant: I can make the 'avocado toast with sausage on the side', 'full English breakfast' or a 'bean and cheese quesadilla'. Let me know if you crave any of the suggestions or if you want something else.\nUser: I like the sound of the avocado toast with sausage on the side, but can you add some bacon?"}
            second_shot_answer = {"role": "assistant", "content": "True\nExplanation: The request involves known ingredients (avocado, sausage, and bacon) that can be found in the list of known ingredients (No. 1, 23 and 3) and a reasonable modification (adding bacon), making it feasible for me to execute."}
            
            third_shot = {"role": "user", "content": "User: I want the bacon and eggs sandwich but can you add 500 eggs?"} 
            third_shot_answer = {"role": "assistant", "content": "False\nExplanation: The request involves an unreasonable quantity of eggs (500), making it not feasible for me to execute."}

            fourth_shot = {"role": "user", "content": "User: can i get the bacon and egg sandwich but can you add five times the ammount of bacon?"}
            fourth_shot_answer = {"role": "assistant", "content": "True\nExplanation: The request involves known ingredients (bacon, eggs and bread) that can be found in the list of known ingredients (No. 3, 10 and 6) and a reasonable modification (adding five times the ammount of bacon), making it feasible for me to execute."}
            
            fifth_shot = {"role": "user", "content": "Assistant: Hello! I am Gregory, your home assistant. How can I help you today?\nUser: I would like to have the sandwich as described in the menu.\nAssistant: I'm sorry, your request was classified to be ambiguous, can you say which of the following options is correct?\nOption 1: bacon and egg sandwich\nOption 2: an option not listed here\nOr do you want me to do something else?\nUser: its an option not listed\nAssistant: I'm sorry, but I can't prepare a sandwich that isn't on the list. However, I can help you with other cooking tasks or suggestions! What would you like to request instead?\nUser: well a sandwich with avocado"}
            fifth_shot_answer = {"role": "assistant", "content": "True\nExplanation: The request involves known ingredients (avocado) that can be found in the list of known ingredients (No. 1), making it feasible for me to execute."}

            sixth_shot = {"role": "user", "content": "Assistant: Hello! I am Gregory, your home assistant. How can I help you today?\nUser: Can I get plain rice?"}
            sixth_shot_answer = {"role": "assistant", "content": "True\nExplanation: The request involves known ingredients (rice) that can be found in the list of known ingredients (No. 2), making it feasible for me to execute."}

            seventh_shot = {"role": "user", "content": "Assistant: Hello! I am Gregory, your home assistant. How can I help you today?\nUser:uh could you prepare a bruschetta with green tomato but no mushrooms\nAssistant: Your request seems to be outside of my capabilities. Please provide a new different request.\nUser: can I get a brushetta with green tomatoes\nAssistant: There are multiple options in my list that might fit your order. While I can't prepare a bruschetta specifically with green tomatoes or customize it beyond the known recipes, I can make a 'grilled tomato and mushroom bruschetta'. It involves grilling tomatoes and mushrooms and serving them on toasted bread. Would you like me to prepare that instead?\nUser: I would like to prepare that dish but with no mushrooms"}
            seventh_shot_answer = {"role": "assistant", "content": "True\nExplanation: The request involves known ingredients (tomatoes) that can be found in the list of known ingredients (No. 28), making it feasible for me to execute."}

            formatted_conversation = format_conversation(conversation)

            predefined_messages_sfty_check = predefined_messages_sfty_check + [first_shot, first_shot_answer, second_shot, second_shot_answer, third_shot, third_shot_answer, fourth_shot, fourth_shot_answer, fifth_shot, fifth_shot_answer, sixth_shot, sixth_shot_answer, seventh_shot, seventh_shot_answer]

            # Append the formatted conversation to the predefined messages
            predefined_messages_sfty_check.append(
                {
                    "role": "user",
                    "content": formatted_conversation
                }
            )

            messages = predefined_messages_sfty_check
            #print("prepromt Messages for answering: ", messages)

            # Make the API call
            completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    # response_format={ "type": "json_object" },
                    messages=messages
                    )
            
            # Extract and return the response content
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error in LLM call: {e}")
            state.var_transcript += "Error in LLM call: " + str(e) + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "Failed LLM call"
        
class DeclineRequest(py_trees.behaviour.Behaviour):
    """
    This action declines the user request if the safety check fails.
    """

    def __init__(self, name, conversation):
        super(DeclineRequest, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if EXPLAIN:
            response = "I'm sorry, I cannot execute the action you requested. Because it was declared unsafe or infeasible by me."
        else:
            response = "I'm sorry, but i can't fulfill your request it is unsafe or unfeasible to me. The reason is: {}".format(state.var_decline_explanation)
    
        if FURHAT:
            speak(state.var_furhat, response)
        print("Assistant: ", response)
        state.var_transcript += "Assistant: " + response + "\n"
        state.var_transcript += "Time: " + time.strftime("%c") + "\n"
        
        # append the response to the conversation
        self.conversation.append({"role": "assistant", "content": response})

        formatted_conversation = format_conversation(self.conversation)
        #print("The conversation log after declining the request: ", formatted_conversation)      

        return py_trees.common.Status.SUCCESS

# needs testing
class GenerateNewSequence(py_trees.behaviour.Behaviour):
    """
    This action generates a new sequence given the action is safe and feasible.
    """

    def __init__(self, name, conversation):
        super(GenerateNewSequence, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if LLM:
            response = self.generate_new_sequence(self.conversation)
            print("The generated sequence is: ", response)
            state.var_transcript += "The generated sequence is: " + response + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            state.var_generated_sequence = response
        else:
            print("Generate New Sequence 1")
            state.var_transcript += "Generate New Sequence 1.\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            response = 'False'
        return py_trees.common.Status.SUCCESS

    def generate_new_sequence(self, conversation):
        """
        This function generates a new sequence given the action is safe and feasible.
        """
        # This logic is to prevent the LLM from being called too many times
        if state.var_total_llm_calls >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            state.var_transcript += "Exceeded the maximum number of LLM calls.\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "I'm sorry, I cannot help you at the moment.The maximum number of LLM calls has been exceeded."
        state.var_total_llm_calls += 1
        #print("number of total llm calls was raised to: ", state.var_total_llm_calls)
        try:
            # Construct the final prompt by inserting the user input
            predefined_messages_new_sequence = [
                    {"role": "system", "content": PRE_PROMPT_NEW_SEQ}
                ]

            formated_conversation = format_conversation(conversation)
            predefined_messages_new_sequence.append(
                {
                    "role": "user",
                    "content": f"Given this conversation, can you generate a new sequence for me?\n{formated_conversation}"
                }
            )
            messages = predefined_messages_new_sequence  # Start with the predefined context.
            #print("prepromt Messages for generating new sequence: ", messages)

            # Make the API call
            completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    response_format={ "type": "json_object" },
                    messages=messages
                    )
            
            # Extract and return the response content
            response_content = completion.choices[0].message.content
            
            # Parse the JSON response and save it to the variable
            state.var_generated_sequence = json.loads(response_content)
            #print("Generated sequence in the var: ", state.var_generated_sequence)

            # Extract and return the response content
            return response_content
        except Exception as e:
            print(f"Error in LLM call: {e}")
            state.var_transcript += "Error in LLM call: " + str(e) + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "Failed LLM call"

# needs testing
class ExplainSequence(py_trees.behaviour.Behaviour):
    """
    This action explains the generated sequence to the user.
    """

    def __init__(self, name, conversation):
        super(ExplainSequence, self).__init__(name)
        self.conversation = conversation

    def update(self):
        #print("The sequence to explain is the generated sequence: ", state.var_generated_sequence)
        if LLM:
            response, sequence_name = self.explain_sequence(self.conversation)
            print("Assistant: ", response)
            state.var_transcript += "Assistant: " + response + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            state.var_generated_sequence_name = sequence_name  # Save the sequence name
            print("var_generated_sequence_name is: ", state.var_generated_sequence_name)
            state.var_transcript += "var_generated_sequence_name is: " + state.var_generated_sequence_name + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            if FURHAT:
                speak(state.var_furhat, response)
        else:
            print("The sequence to explain is the generated sequence: ", state.var_generated_sequence)
            state.var_transcript += "The sequence to explain is the generated sequence.\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            print("The sequence is a very great sequence. \nIt is a very good sequence.")
            state.var_transcript += "The sequence is a very great sequence. \nIt is a very good sequence.\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            response = 'False'
        return py_trees.common.Status.SUCCESS
    
    def explain_sequence(self, conversation):
        """
        This function explains the generated sequence to the user with the Chatgpt-4o-mini model.
        """
        # This logic is to prevent the LLM from being called too many times
        if state.var_total_llm_calls >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            state.var_transcript += "Exceeded the maximum number of LLM calls.\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "I'm sorry, I cannot help you at the moment.The maximum number of LLM calls has been exceeded."
        state.var_total_llm_calls += 1
        #print("number of total llm calls was raised to: ", state.var_total_llm_calls)
        try:
            # Construct the final prompt by inserting the user input
            predefined_messages_explain_sequence = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that explains the steps a robot will take to fulfill a user's request. "
                        "The explanation should be clear and concise, focusing on the actions without adding unnecessary details. "
                        "At the start of the explanation, mention that you will perform a new set of steps to fulfill the user's request. "
                        "At the end of the explanation, ask the user if the steps sound good to them and name the sequence with var_generated_sequence_name. "
                        "Do not provide any extra information or detail about how the actions are performed beyond what is specified."
                    )
                }
            ]
            
            first_shot = {"role": "user", "content": FIRST_SHOT_EXPLAIN_SEQ}
            first_shot_answer = {"role": "assistant", "content": FIRST_SHOT_EXPLAIN_SEQ_ANSWER}
            predefined_messages_explain_sequence.append(first_shot)
            predefined_messages_explain_sequence.append(first_shot_answer)

            #print("got here and the sequence is: ", state.var_generated_sequence)
            #print("The type of the sequence is: ", type(state.var_generated_sequence))

            # Parse the sequence JSON if it's not already parsed
            if isinstance(state.var_generated_sequence, str):
                try:
                    state.var_generated_sequence = json.loads(state.var_generated_sequence)
                    #print("Parsed sequence: ", state.var_generated_sequence)
                except json.JSONDecodeError as e:
                    print("Error parsing JSON: ", e)
                    state.var_transcript += "Error parsing JSON: " + str(e) + "\n"
                    state.var_transcript += "Time: " + time.strftime("%c") + "\n"
                    return "Failed to parse sequence JSON", None


            #print("can i access it: ", state.var_generated_sequence['sequence'])
            # Convert the sequence to a string format
            sequence_str = "\n".join([f"Step {item['step']}: {item['action']}" for item in state.var_generated_sequence['sequence']])
            #print("The sequence string: ", sequence_str)
            # Format the conversation
            formated_conversation = format_conversation(conversation)
            #print("the formatted conversation: ", formated_conversation)
            # Append the formatted conversation and sequence to the predefined messages
            predefined_messages_explain_sequence.append(
                {
                    "role": "user",
                    "content": f"Yes, now given the following conversation and the generated sequence, can you explain the sequence to me?\n{formated_conversation}\nThe sequence is:\n{sequence_str}"
                }
            )

            messages = predefined_messages_explain_sequence  # Start with the predefined context.
            #print("prepromt Messages for explaining the sequence: ", messages)
            
            # Print debug information before the API call
            #print("Pre-prompt messages for explaining the sequence: ", messages)

            # Make the API call
            completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                    )
            
            # Extract and return the response content
            full_response = completion.choices[0].message.content
            #print("Full response from the model: ", full_response)

            # Extract the sequence name from the response
            sequence_name = "None"
            if "var_generated_sequence_name" in full_response:
                start_index = full_response.index("var_generated_sequence_name: '") + len("var_generated_sequence_name: '")
                end_index = full_response.index("'", start_index)
                sequence_name = full_response[start_index:end_index]
                full_response = full_response.replace(f"var_generated_sequence_name: '{sequence_name}'", "").strip()

            return full_response, sequence_name
        except Exception as e:
            print(f"Error in LLM call: {e}")
            state.var_transcript += "Error in LLM call: " + str(e) + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "Failed LLM call", None
        
class ReportFailureBackToUser(py_trees.behaviour.Behaviour):
    """
    This action reports the failure back to the user. It is triggered when the automated check of the newly generated sequence fails.
    """

    def __init__(self, name, conversation):
        super(ReportFailureBackToUser, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if EXPLAIN:
            response = "I’m sorry, but I ran into an issue while trying to create what you requested."
        if LLM:
            #response = self.report_failure_back_to_user()
            response = "I’m sorry, but I ran into an issue while trying to create the steps to accomodate your request. Would you like to try again, or do you have any other requests I can help with?"
        else:
            response = "The sequence failed the automated check."
        self.conversation.append({"role": "assistant", "content": response})
        if FURHAT:
            speak(state.var_furhat, response)
        print("Assistant: ", response)
        state.var_transcript += "Assistant: " + response + "\n"
        state.var_transcript += "Time: " + time.strftime("%c") + "\n"

        formatted_conversation = format_conversation(self.conversation)
        #print("The conversation log after reporting the failure back to the user: ", formatted_conversation)

        return py_trees.common.Status.SUCCESS

    def report_failure_back_to_user(self):
        """
        This function reports the failure back to the user with the ChatGPT-4o-mini model.
        """
        # This logic is to prevent the LLM from being called too many times
        if state.var_total_llm_calls >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            state.var_transcript += "Exceeded the maximum number of LLM calls.\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "I'm sorry, I cannot help you at the moment.The maximum number of LLM calls has been exceeded."
        state.var_total_llm_calls += 1
        #print("number of total llm calls was raised to: ", state.var_total_llm_calls)
        try:
            # Construct the final prompt by inserting the user input
            error_messages = "\n".join(state.var_found_errors_in_sequence)

            predefined_messages_report_failure = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that reports back to the user when the automated check of the newly generated sequence fails. "
                        "The report should be clear and concise, explaining the reason for the failure without adding unnecessary details. "
                        "At the end of the report, ask the user if they would like to try generating a new set of steps to fullfill their request or if they have any other questions. "
                        "Do not provide any extra information or detail about how the actions are performed beyond what is specified."
                        "To report the failure you have access to the error messages: '" + error_messages + "' Make sure to explain the error messages to the user in a way that is easy to understand."
                    )
                }
            ]

            messages = predefined_messages_report_failure  # Start with the predefined context.
            #print("prepromt Messages for reporting failure in the sequence: ", messages)
            #state.var_transcript += "prepromt Messages for reporting failure in the sequence: " + str(messages) + "\n"

            # Make the API call
            completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                    )
            
            # Extract and return the response content
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error in LLM call: {e}")
            state.var_transcript += "Error in LLM call: " + str(e) + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"

class AskUserForNewRequest(py_trees.behaviour.Behaviour):
    """
    This action asks the user for a new request after the failure of the automated check of the newly generated sequence.
    """

    def __init__(self, name, conversation):
        super(AskUserForNewRequest, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if EXPLAIN:
            response = "I understand that you say that the newly generated sequence does not meet your expectations."
        else:
            response = "I'm sorry I couldn't create what you requested. Could you state your request again, but in a clearer way? Or do you have any other requests I can help with?"
        self.conversation.append({"role": "assistant", "content": response})

        if FURHAT:
            speak(state.var_furhat, response)
        print("Assistant: ", response)
        state.var_transcript += "Assistant: " + response + "\n"
        state.var_transcript += "Time: " + time.strftime("%c") + "\n"

        formatted_conversation = format_conversation(self.conversation)
        #print("The conversation log after asking the user for a new request: ", formatted_conversation)

        return py_trees.common.Status.SUCCESS

class AskUserToSpecifyWithKnowNo(py_trees.behaviour.Behaviour):
    """
    This action asks the user to specify their request based on the options provided in the KnowNo variable.
    """

    def __init__(self, name, conversation):
        super(AskUserToSpecifyWithKnowNo, self).__init__(name)
        self.conversation = conversation

    def update(self):
        sth_else_in = False
        if EXPLAIN:
            response = "I matched your request to multiple possible actions. I need you to make a clearer request."
        else:
            response = "I'm sorry, I found more than one option to fit your request, can you say which of the following options is correct? "
            for i, option in enumerate(state.var_KnowNo):
                response += f"\nOption {i + 1}: {option}"
                if option == "something else":
                    sth_else_in = True
                    
            if sth_else_in:
                response += "\nLet me know which option suits you best."
            else:
                response += "\nOr do you want me to do something else?"
        # if only sth else is in the list then the response should be different
        if len(state.var_KnowNo) == 1 and state.var_KnowNo[0] == "something else":
            response = "I'm sorry, but I couldn't fully understand your request. Can you provide more information or specify your request in a different way?"
        self.conversation.append({"role": "assistant", "content": response})

        if FURHAT:
            speak(state.var_furhat, response)
        print("Assistant: ", response)
        state.var_transcript += "Assistant: " + response + "\n"
        state.var_transcript += "Time: " + time.strftime("%c") + "\n"

        formatted_conversation = format_conversation(self.conversation)
        #print("The conversation log after asking the user to specify their request with KnowNo: ", formatted_conversation)

        state.var_known = False
        state.var_one = False
        state.var_inf = False
        state.var_seq_ok = False
        state.var_KnowNo = []  # List of actions that could map to the user input
        return py_trees.common.Status.SUCCESS

class SetVarKnownTrue(py_trees.behaviour.Behaviour):
    """
    This action sets the var_known variable to True.
    """

    def __init__(self, name, process_user_input_func, conversation):
        super(SetVarKnownTrue, self).__init__(name)
        self.process_user_input_func = process_user_input_func
        self.conversation = conversation

    def update(self):
        if EXPLAIN:
            response = "I thought your request requires me to generate a new sequence, but after double checking I think your request matches an action I know."
        else:
            #response = "Hold on dear user, I think I know what you want. Let me execute the action for you."
            response = "I initially thought your request would require me to create a new set of actions, but after double checking, I believe your request matches something I already know how to do." # explaining
        self.conversation.append({"role": "assistant", "content": response})
        
        if FURHAT:
            speak(state.var_furhat, response)
        print("Assistant: ", response)
        state.var_transcript += "Assistant: " + response + "\n"
        state.var_transcript += "Time: " + time.strftime("%c") + "\n"
        state.var_known = True
        
        formatted_conversation = format_conversation(self.conversation)
        #print("The conversation log after setting the var_known variable to True: ", formatted_conversation)
        self.process_user_input_func(response)  # Re-trigger the behavior tree with the new input
        return py_trees.common.Status.SUCCESS

class FallbackAnswer(py_trees.behaviour.Behaviour):
    """
    This action provides a fallback answer when the user input is not understood.
    """

    def __init__(self, name, conversation):
        super(FallbackAnswer, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if EXPLAIN:
            response = "Your request couldn't be matched to any known actions. I need you to make a clearer request."
        elif LLM:
            response = self.generate_fallback_answer(self.conversation)
        else:
            response = "I'm sorry, but i couldn't classify your request. Is there anything I can do for you? I could give you suggestions if you want me to."
        self.conversation.append({"role": "assistant", "content": response})

        if FURHAT:
            speak(state.var_furhat, response)
        print("Assistant: ", response)
        state.var_transcript += "Assistant: " + response + "\n"
        state.var_transcript += "Time: " + time.strftime("%c") + "\n"

        formatted_conversation = format_conversation(self.conversation)
        #print("The conversation at Fallback step is: ", formatted_conversation)

        return py_trees.common.Status.SUCCESS
    
    def generate_fallback_answer(self, conversation):
        """
        This function generates a fallback answer when the user input is not understood.
        """
        # This logic is to prevent the LLM from being called too many times
        if state.var_total_llm_calls >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            state.var_transcript += "Exceeded the maximum number of LLM calls.\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "I'm sorry, I cannot help you at the moment.The maximum number of LLM calls has been exceeded."
        state.var_total_llm_calls += 1
        #print("number of total llm calls was raised to: ", state.var_total_llm_calls)
        try:
            # Construct the final prompt by inserting the user input
            if state.var_capable:
                predefined_messages_fallback = [
                        {"role": "system", "content": "You are a helpful robot assistant that can execute cooking tasks as well as one cleaning task. Your job is to find out what the user wants from you and ask him for more information if necessary."}
                    ]
            else:
                predefined_messages_fallback = [
                        {"role": "system", "content": "You are a helpful robot assistant that can execute cooking tasks as well as one cleaning task. You are not able to execute the task the user requested as it is outside of your capabilities. Your job is to decline the request and ask the user for a new different request. Firstly state that the task is outside of your capabilities with 'Your request seems to be outside of my capabilities.' and ask the user for a new different request. Do not suggest to the user that you can assist them with their request or provide any other information."}
                    ]
                
                first_shot = {"role": "user", "content": "User: I want the pancakes but can you do it with bananas and chocolate chips instead of the berries and the syrup?"}
                first_shot_answer = {"role": "assistant", "content": "Your request seems to be outside of my capabilities. I can't execute the task you requested, please provide a different request."}

                second_shot = {"role": "user", "content": "User: I want something to eat.\n Assistant: I can make the 'avocado toast with sausage on the side', 'full English breakfast' or a 'bean and cheese quesadilla'. Let me know if you crave any of the suggestions or if you want something else.\nUser: I like the sound of the avocado toast with sausage on the side, but can you add 500 eggs?"}
                second_shot_answer = {"role": "assistant", "content": "Your request seems to be outside of my capabilities. I can't execute the task you requested, please provide a different request, maybe with a reasonable amount of eggs."}

            formatted_conversation = format_conversation(conversation)

            predefined_messages_fallback.append({"role": "user", "content": formatted_conversation})
            messages = predefined_messages_fallback
            #print("prepromt Messages for the fallback answer: ", messages)

            # Make the API call
            completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    # response_format={ "type": "json_object" },
                    messages=messages
                    )
            
            # Extract and return the response content
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error in LLM call: {e}")
            state.var_transcript += "Error in LLM call: " + str(e) + "\n"
            state.var_transcript += "Time: " + time.strftime("%c") + "\n"
            return "Failed LLM call"



