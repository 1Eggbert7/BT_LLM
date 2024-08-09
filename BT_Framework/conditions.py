# conditions.py
# Alexander Leszczynski
# 07-08-2024

import py_trees
from openai import OpenAI
from prompts import PRE_PROMPT_AMBIGUOUS, PRE_PROMPT_KNOWN, PRE_PROMPT_KNOWN_2, PRE_PROMPT_AMBIGUOUS2, PRE_PROMPT_CHECK_MAPPING, PRE_PROMPT_NEW_SEQ_CHECK, PRE_PROMPT_NEW_SEQ_CHECK_FIRST_SHOT, PRE_PROMPT_NEW_SEQ_CHECK_SECOND_SHOT, PRE_PROMPT_NEW_SEQ_CHECK_THIRD_SHOT, PRE_PROMPT_NEW_SEQ_DOUBLE_CHECK, PRE_PROMPT_NEW_SEQ_DOUBLE_CHECK_FIRST_SHOT, PRE_PROMPT_NEW_SEQ_DOUBLE_CHECK_SECOND_SHOT, PRE_PROMPT_NEW_SEQ_DOUBLE_CHECK_THIRD_SHOT, PRE_PROMPT_NEW_SEQ_CHECK_FOURTH_SHOT, PRE_PROMPT_NEW_SEQ_CHECK_FIFTH_SHOT, PREDEFINED_CAPABILITY_CHECK
from config import MAX_LLM_CALL, LLM, FURHAT
import state
import json
from furhat_remote_api import FurhatRemoteAPI
from transformers import pipeline
from utils import record_speech, format_conversation

client = OpenAI()

class CheckForAmbiguity(py_trees.behaviour.Behaviour):
    """
    This is the condition to check if the user input is ambiguous.
    """
    # Condition to check if the user input is ambiguous
    def __init__(self, name, conversation):
        super(CheckForAmbiguity, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if LLM:
            # Call the LLM to check for ambiguity
            response = self.check_ambiguity_with_llm(self.conversation)
            print("Is it ambiguous? ", response)
            state.var_transcript += "Is it ambiguous? " + response + "\n"
            if response == "True": # for more flexible acceptance, one could also check if the response contains "True" within the first 15 characters
                return py_trees.common.Status.SUCCESS
        elif 'ambig' in self.conversation[-1]['content'].lower():
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

    def check_ambiguity_with_llm(self, conversation):
        """
        This function checks if the user input is ambiguous using the Chatgpt 3.5 turbo model.
        """
        # This logic is to prevent the LLM from being called too many times
        if state.var_total_llm_calls >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            state.var_transcript += "Exceeded the maximum number of LLM calls.\n"
            return "False"
        state.var_total_llm_calls += 1
        #print("number of total llm calls was raised to: ", state.var_total_llm_calls)
        
        # for debugging purposes
        formatted_conversation = format_conversation(conversation)
        #print("Formatted conversation: ", formatted_conversation)

        try:
            # Construct the final prompt by inserting the user input#
            if len(conversation) == 1:
                predefined_messages_ambiguous = [
                        {"role": "system", "content": PRE_PROMPT_AMBIGUOUS},
                    ]
            else:
                predefined_messages_ambiguous = [
                        {"role": "system", "content": PRE_PROMPT_AMBIGUOUS2},
                    ]
            messages = predefined_messages_ambiguous + conversation  # Start with the predefined context.
            #print("Messages: ", messages)

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
            state.var_transcript += f"Error in LLM call: {e}\n"
            return "False"
        
class CheckForNewSeq(py_trees.behaviour.Behaviour):
    """
    This condition checks if the user wants a new sequence.
    """

    def __init__(self, name, conversation):
        super(CheckForNewSeq, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if LLM:
            # Call the LLM to check if the user wants a new sequence
            response = self.check_new_sequence_with_llm(self.conversation)
            print("Is a new sequence requested?: ", response)
            state.var_transcript += "Is a new sequence requested?: " + response + "\n"
            if response == "True":
                return py_trees.common.Status.SUCCESS
        elif 'new sequence' in self.conversation[-1]['content']:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

    def check_new_sequence_with_llm(self, conversation):
        """
        This function checks if the user wants a new sequence using the Chatgpt 3.5 turbo model.
        """
        # This logic is to prevent the LLM from being called too many times
        if state.var_total_llm_calls >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            state.var_transcript += "Exceeded the maximum number of LLM calls.\n"
            return "False"
        state.var_total_llm_calls += 1
        #print("number of total llm calls was raised to: ", state.var_total_llm_calls)

        try:
            # Construct the final prompt by inserting the user input
            predefined_messages_new_sequence = [
                    {"role": "system", "content": PRE_PROMPT_NEW_SEQ_CHECK}
                ]
           
            first_shot = {"role": "user", "content": PRE_PROMPT_NEW_SEQ_CHECK_FIRST_SHOT}
            predefined_messages_new_sequence.append(first_shot) 
            first_shot_answer = {"role": "system", "content": "True"}
            predefined_messages_new_sequence.append(first_shot_answer)

            second_shot = {"role": "user", "content": PRE_PROMPT_NEW_SEQ_CHECK_SECOND_SHOT}
            predefined_messages_new_sequence.append(second_shot)
            second_shot_answer = {"role": "system", "content": "False"}
            predefined_messages_new_sequence.append(second_shot_answer)

            third_shot = {"role": "user", "content": PRE_PROMPT_NEW_SEQ_CHECK_THIRD_SHOT}
            predefined_messages_new_sequence.append(third_shot)
            third_shot_answer = {"role": "system", "content": "True"}        
            predefined_messages_new_sequence.append(third_shot_answer)

            fourth_shot = {"role": "user", "content": PRE_PROMPT_NEW_SEQ_CHECK_FOURTH_SHOT}
            predefined_messages_new_sequence.append(fourth_shot)
            fourth_shot_answer = {"role": "system", "content": "False"}        
            predefined_messages_new_sequence.append(fourth_shot_answer)

            fifth_shot = {"role": "user", "content": PRE_PROMPT_NEW_SEQ_CHECK_FIFTH_SHOT}
            predefined_messages_new_sequence.append(fifth_shot)
            fifth_shot_answer = {"role": "system", "content": "True"}
            predefined_messages_new_sequence.append(fifth_shot_answer)

            
            formatted_conversation = format_conversation(conversation)      
            convo_to_add = {"role": "user", "content": formatted_conversation}
            predefined_messages_new_sequence.append(convo_to_add)  
            messages = predefined_messages_new_sequence
            #print("Messages for New Sequence: ", messages)


            #print("Messages: ", messages)

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
            state.var_transcript += f"Error in LLM call: {e}\n"
            return "False"

class CheckForNewSeq2(py_trees.behaviour.Behaviour):
    """
    This condition checks if the user actually wants a new sequence, given that the system classified the user input to be requesting a new sequence.
    """

    def __init__(self, name, conversation):
        super(CheckForNewSeq2, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if LLM:
            # Call the LLM to check if the user wants a new sequence
            response = self.check_new_sequence_with_llm(self.conversation)
            print("Is a new sequence actually requested? ", response)
            state.var_transcript += "Is a new sequence actually requested?" + response + "\n"
            if response == "True":
                return py_trees.common.Status.SUCCESS
        elif 'new sequence' in self.conversation[-1]['content']:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

    def check_new_sequence_with_llm(self, conversation):
        """
        This function checks if the user wants a new sequence using the Chatgpt 3.5 turbo model.
        """
        # This logic is to prevent the LLM from being called too many times
        if state.var_total_llm_calls >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            state.var_transcript += "Exceeded the maximum number of LLM calls.\n"
            return "False"
        state.var_total_llm_calls += 1
        #print("number of total llm calls was raised to: ", state.var_total_llm_calls)

        try:
            # Construct the final prompt by inserting the user input
            predefined_messages_new_sequence = [
                    {"role": "system", "content": PRE_PROMPT_NEW_SEQ_DOUBLE_CHECK}
                ]
           
            first_shot = {"role": "user", "content": PRE_PROMPT_NEW_SEQ_DOUBLE_CHECK_FIRST_SHOT}
            predefined_messages_new_sequence.append(first_shot)
            first_shot_answer = {"role": "system", "content": "False"}
            predefined_messages_new_sequence.append(first_shot_answer)

            second_shot = {"role": "user", "content": PRE_PROMPT_NEW_SEQ_DOUBLE_CHECK_SECOND_SHOT}
            predefined_messages_new_sequence.append(second_shot)
            second_shot_answer = {"role": "system", "content": "True"}
            predefined_messages_new_sequence.append(second_shot_answer)

            third_shot = {"role": "user", "content": PRE_PROMPT_NEW_SEQ_DOUBLE_CHECK_THIRD_SHOT}
            predefined_messages_new_sequence.append(third_shot)
            third_shot_answer = {"role": "system", "content": "True"}
            predefined_messages_new_sequence.append(third_shot_answer)
                        
            formatted_conversation = format_conversation(conversation)
            convo_to_add = {"role": "user", "content": formatted_conversation}
            predefined_messages_new_sequence.append(convo_to_add)
            messages = predefined_messages_new_sequence
            #print("Messages for New Sequence: ", messages)

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
            state.var_transcript += f"Error in LLM call: {e}\n"
            return "False"
        
class CheckVarKnownCondition(py_trees.behaviour.Behaviour):
    """
    This condition checks if var_known is True.
    """

    def __init__(self, name):
        super(CheckVarKnownCondition, self).__init__(name)

    def update(self):
        if state.var_known:
            #print("var_known is True")
            return py_trees.common.Status.SUCCESS
        #print("var_known is False")
        return py_trees.common.Status.FAILURE

class CheckVarKnownFalse(py_trees.behaviour.Behaviour):
    """
    This condition checks if var_known is False.
    """

    def __init__(self, name):
        super(CheckVarKnownFalse, self).__init__(name)

    def update(self):
        if not state.var_known:
            #print("var_known is False")
            return py_trees.common.Status.SUCCESS
        #print("var_known is True")
        return py_trees.common.Status.FAILURE


# replied: "Great choice! I'll prepare some delicious pancakes with maple syrup and berries for you. Just sit back and enjoy!" instead of 'True'
"""
User:  Hey I'm hungry.
Is it Ambiguous?:  True
Assistant:  Hello! I can definitely help with that. What specific dish would you like me to prepare for you?
User: I don't know, do you have any suggestions?
Is it Ambiguous?:  True
Assistant:  Of course! Here are a few options for you to choose from:
1. Full English breakfast
2. Avocado toast with sausage on the side
3. Pancakes with maple syrup and berries

Please let me know if any of these options appeal to you, or if you have any other preferences!
User: Number 3 sounds yummy, I want that
Is it Ambiguous?:  False
Is it Known?:  Great choice! I'll prepare some delicious pancakes with maple syrup and berries for you. Just sit back and enjoy!
Eggbert3
"""
class CheckForKnown(py_trees.behaviour.Behaviour):
    """
    This condition checks if the user input is known.
    """

    def __init__(self, name, conversation):
        super(CheckForKnown, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if LLM:
            # Call the LLM to check if the user input is known
            response = self.check_known_with_llm(self.conversation)
            print("Is it known? ", response)
            state.var_transcript += "Is it known? " + response + "\n"
            if response == "True": # for more flexible acceptance, one could also check if the response contains "True" within the first 15 characters
                return py_trees.common.Status.SUCCESS
        
        elif 'known' in self.conversation[-1]['content'].lower():
            print("Is it known?: True")
            state.var_transcript += "Is it known? True\n"
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE
    
    def check_known_with_llm(self, conversation):
        """
        This function checks if the user input is known using the Chatgpt 3.5 turbo model.
        """
        # This logic is to prevent the LLM from being called too many times
        if state.var_total_llm_calls >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            state.var_transcript += "Exceeded the maximum number of LLM calls.\n"
            return "False"
        state.var_total_llm_calls += 1
        #print("number of total llm calls was raised to: ", state.var_total_llm_calls)

        try:
            # Construct the final prompt by inserting the user input
            if len(conversation) == 1:
                predefined_messages_known = [
                    {"role": "system", "content": PRE_PROMPT_KNOWN},
                ]
                # idea is to add shots here
                first_shot = {"role": "user", "content": "User: Make me a bacon and egg sandwich."}
                first_shot_answer = {"role": "assistant", "content": "True"}

                second_shot = {"role": "user", "content":"User: Can you suggest something to eat?"}
                second_shot_answer = {"role": "assistant", "content": "False"}

                third_shot = {"role": "user", "content":"User: Prepare a vegetable stir fry with rice."}
                third_shot_answer = {"role": "assistant", "content": "True"}

                fourth_shot = {"role": "user", "content":"User: What can you do?"}
                fourth_shot_answer = {"role": "assistant", "content": "False"}

                fifth_shot = {"role": "user", "content":"User: I heard the grilled tomato and mushroom bruschetta is good. I'll have that."}
                fifth_shot_answer = {"role": "assistant", "content": "True"}

                sixth_shot = {"role": "user", "content":"User: Please make me a chicken salad without tomatoes."}
                sixth_shot_answer = {"role": "assistant", "content": "False"}

                seventh_shot = {"role": "user", "content":"User: I'd like a peanut butter and jelly sandwich, but can you add bananas?"}
                seventh_shot_answer = {"role": "assistant", "content": "False"}

                eighth_shot = {"role": "user", "content":"User: I'm craving a grilled cheese sandwich."}
                eighth_shot_answer = {"role": "assistant", "content": "False"}

                nineth_shot = {"role": "user", "content":"User: Allegedly, the PB&J sandwich is good. I'll have that."}
                nineth_shot_answer = {"role": "assistant", "content": "True"}

                tenth_shot = {"role": "user", "content":"User: I think some pancakes would do me good."}
                tenth_shot_answer = {"role": "assistant", "content": "True"}

                # now add the shots to the predefined messages
                predefined_messages_known = predefined_messages_known + [first_shot, first_shot_answer, second_shot, second_shot_answer, third_shot, third_shot_answer, fourth_shot, fourth_shot_answer, fifth_shot, fifth_shot_answer, sixth_shot, sixth_shot_answer, seventh_shot, seventh_shot_answer, eighth_shot, eighth_shot_answer, nineth_shot, nineth_shot_answer, tenth_shot, tenth_shot_answer]


            else:
                predefined_messages_known = [
                        {"role": "system", "content": PRE_PROMPT_KNOWN_2},
                    ]
                
                first_shot = {"role": "user", "content": "User: I'm hungry, what can I eat?\nAssistant: You can have a bacon and egg sandwich, avocado toast with sausage on the side, or a peanut butter and jelly sandwich.\nUser: I want option A."}
                first_shot_answer = {"role": "assistant", "content": "True"}

                second_shot = {"role": "user", "content":"User: I don't know um I'm Italian and I would like something from my home uh country can you make me something\nAssistant: I'd be happy to help you with a dish from your home country! 🇮🇹 Could you please provide more details or preferences for the Italian dish you would like? It could be a specific name or ingredients you enjoy.\nUser: anything you can do thats italian is fine\nAssistant: I'm sorry, but creating specific Italian dishes is outside the known sequences I can perform. However, I can suggest making a grilled tomato and mushroom bruschetta, which is a simple and delicious Italian appetizer. Would you like me to proceed with that suggestion, or is there anything else you'd prefer within the known sequences I can execute?\nUser: yeah that then"}
                second_shot_answer = {"role": "assistant", "content": "True"}

                third_shot = {"role": "user", "content":"User: um I'm not sure what to eat\nAssistant: Hello! If you're not sure what to eat, here are a few options you can consider: \n1. Pancakes with maple syrup and berries\n2. Full English breakfast\n3. Vegetable stir fry with rice\nLet me know if any of these options sound good to you, or if you need more suggestions!\nUser: what do you recommend\nAssistant: I can suggest a few options for you to consider. Which of the following sequences are you in the mood for:\n1. Avocado toast with sausage on the side\n2. Peanut butter and jelly sandwich\n3. Bean and cheese quesadilla\nFeel free to let me know your preference or if you have any dietary restrictions!\nUser: uh yeah I would like the the cheese quesadilla but without cheese"}
                third_shot_answer = {"role": "assistant", "content": "False"}
                
                fourth_shot = {"role": "user", "content":"User: can I have a grilled tomato and mushroom to set up please\nAssistant: It seems like you're requesting a 'grilled tomato and mushroom bruschetta.' I can prepare that for you. Would you like anything else with it?\nUser: no"}
                fourth_shot_answer = {"role": "assistant", "content": "True"}

                fifth_shot = {"role": "user", "content":"User: I can you make me hachapuri\nAssistant: I apologize for any confusion, but could you please provide more details or clarify your request for hachapuri? Are you looking for a specific type of hachapuri or any particular ingredients or preferences? Once I have more information, I can assist you better.\nUser: I have more information I can assist you better hachapuri aari\nAssistant: Thank you for clarifying! Unfortunately, the sequence for 'hachapuri aari' is not within my known sequences. However, I can offer you some other options:\n1. 'Bean and Cheese Quesadilla': Makes a bean and cheese quesadilla by heating beans and preparing a tortilla. The quesadilla is served hot and ready to enjoy.\n2. 'Grilled Tomato and Mushroom Bruschetta': Creates a grilled tomato and mushroom bruschetta by grilling tomatoes and mushrooms on toasted bread, making a simple yet delicious appetizer.\n3. 'Tortilla with Tomatoes, Beans, and Egg (Huevos Rancheros)': Prepares huevos rancheros with a tortilla, beans, tomatoes, and eggs in a flavorful breakfast dish.\nPlease let me know if any of these options interest you, or if you have any other preferences or requests.\nUser: the first 1"}
                fifth_shot_answer = {"role": "assistant", "content": "True"}

                #now add the shots to the predefined messages
                predefined_messages_known = predefined_messages_known + [first_shot, first_shot_answer, second_shot, second_shot_answer, third_shot, third_shot_answer, fourth_shot, fourth_shot_answer, fifth_shot, fifth_shot_answer]
                
            convo_to_add = {"role": "user", "content": format_conversation(conversation)}
            messages = predefined_messages_known + [convo_to_add]
            #print("Messages for Known: ", messages)
            #print("The conversation before the LLM call: ", conversation)

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
            state.var_transcript += f"Error in LLM call: {e}\n"
            return "False"
        
class CheckVarKnowNo(py_trees.behaviour.Behaviour):
    """
    This condition checks if var_KnowNo only contains one action. If this is false then it contains more than one action. 0 is not possible.
    """

    def __init__(self, name):
        super(CheckVarKnowNo, self).__init__(name)

    def update(self):
        if len(state.var_KnowNo) == 1:
            #print("var_KnowNo has only one action", state.var_KnowNo)
            return py_trees.common.Status.SUCCESS
        #print("var_KnowNo has more than one action", state.var_KnowNo)
        return py_trees.common.Status.FAILURE

class CheckMapping(py_trees.behaviour.Behaviour):
    """
    This condition checks if the user input maps to the action in var_KnowNo.
    """

    def __init__(self, name, conversation):
        super(CheckMapping, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if LLM:
            # Call the LLM to check if the user input maps to the action in var_KnowNo
            response = self.check_mapping_with_llm(self.conversation)
            print("Does it map to the action in var_KnowNo? ", response)
            state.var_transcript += "Does it map to the action in var_KnowNo? " + response + "\n"
            if response == "True":
                return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

    def check_mapping_with_llm(self, conversation):
        """
        This function checks if the user input actually maps to the action in var_KnowNo using the Chatgpt 3.5 turbo model.
        """
        # This logic is to prevent the LLM from being called too many times
        if state.var_total_llm_calls >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            state.var_transcript += "Exceeded the maximum number of LLM calls.\n"
            return "False"
        state.var_total_llm_calls += 1
        #print("number of total llm calls was raised to: ", state.var_total_llm_calls)

        try:
            # Construct the final prompt by inserting the user input
            formatted_conversation = format_conversation(conversation)
            predefined_messages = [
                    {"role": "system", "content": PRE_PROMPT_CHECK_MAPPING},
                    {"role": "user", "content": "Does the following action" + 'bacon and egg sandwich' + "map to the user input: \n" + "I want the bacon and egg sandwich"},
                    {"role": "assistant", "content": "True"},
                    {"role": "user", "content": "Does the following action" + 'full english breakfast' + "map to the user input: \n" + "User: I am hungry.\n" + "Assistant: Sure! I could make the 'avocado toast with sausage on the side', 'full English breakfast' or a 'bean and cheese quesadilla'. Let me know if you crave any of the suggestions or if you want something else.\n" + "User: Option 2 sounds good.\n"},
                    {"role": "assistant", "content": "True"},
                    {"role": "user", "content": "Does the following action" + 'avocado toast with sausage on the side' + "map to the user input: \n" + "User: What can you make?\n" + "Assistant: I can make the 'avocado toast with sausage on the side', 'full English breakfast' or a 'bean and cheese quesadilla'. Let me know if you crave any of the suggestions or if you want something else.\n" + "User: I like the sound of the avocado toast with sausage on the side, but can you add some bacon?\n"},
                    {"role": "assistant", "content": "False"},
                    {"role": "user", "content": "Does the following action" + 'pancakes with maple syrup and berries' + "map to the user input: \n" + "User: I am craving the pancakes but can you double the syrup?\n"},
                    {"role": "assistant", "content": "False"},
                    {"role": "user", "content": "Does the following action" + state.var_KnowNo[0] + "map to the user input: \n" + formatted_conversation},
                ]
            messages = predefined_messages # Start with the predefined context.
            #print("varKnowNo: ", state.var_KnowNo[0])
            #print("formatted_conversation: ", formatted_conversation)
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
            state.var_transcript += f"Error in LLM call: {e}\n"
            return "False"
        
class CheckVarInf(py_trees.behaviour.Behaviour):
    """
    This condition checks if var_inf is True.
    """

    def __init__(self, name):
        super(CheckVarInf, self).__init__(name)

    def update(self):
        if state.var_inf:
            #print("var_inf is True")
            return py_trees.common.Status.SUCCESS
        #print("var_inf is False")
        return py_trees.common.Status.FAILURE

class CheckNewSeq(py_trees.behaviour.Behaviour):
    """
    This action checks the new sequence generated by the LLM. The sequence is in the var_generated_sequence variable.
    """

    def __init__(self, name):
        super(CheckNewSeq, self).__init__(name)

    def update(self):
        #self.logger.debug("%s [CheckNewSeq::update()]" % self.name) # this is a debugtool to see the name of the action

        sequence = state.var_generated_sequence
        if not sequence:
            self.logger.error("The generated sequence is empty.")
            return py_trees.common.Status.FAILURE
        
        
        #print("Sequence before checking the format: ", sequence)
        #print("The type of the sequence: ", type(sequence))
        
        # Convert string to dict if needed
        if isinstance(sequence, str):
            try:
                sequence = json.loads(sequence)
            except json.JSONDecodeError as e:
                self.logger.error(f"Error decoding JSON: {e}")
                return py_trees.common.Status.FAILURE
            
        #print("Sequence after checking the format: ", sequence)


        format_check, format_message = self.check_sequence_format(sequence)
        if not format_check:
            self.logger.error(format_message)
            return py_trees.common.Status.FAILURE
        else:
            self.logger.debug(format_message)
        
        functions = self.load_json('functions.json')
        ingredients = self.load_json('ingredients.json')
        functions_check, functions_message = self.check_functions_exist(sequence, functions, ingredients)
        if not functions_check:
            functions_message = "The sequence contains errors. Please check the following:\n" + "\n".join(state.var_found_errors_in_sequence)
            self.logger.error(functions_message)
            return py_trees.common.Status.FAILURE
        print("Sequence is valid.")
        return py_trees.common.Status.SUCCESS

    def load_json(self, filepath):
        """
        This function loads a JSON file.
        """
        with open(filepath, 'r') as file:
            return json.load(file)

    # can be improved
    def check_sequence_format(self, sequence):
        """
        This function checks the format of the sequence generated by the LLM.
        """
        if not sequence or not isinstance(sequence, dict):
            return False, "The sequence is empty or not properly formatted."
        
        for step in sequence["sequence"]:
            
            if "step" not in step:
                state.var_found_errors_in_sequence.append("Each step must contain 'step' and 'action' fields. 'step' is missing.")
            if "action" not in step:
                state.var_found_errors_in_sequence.append("Each step must contain 'step' and 'action' fields. 'action' is missing.")
            if state.var_found_errors_in_sequence:
                return False, "The sequence contains errors. Please check the following:\n" + "\n".join(state.var_found_errors_in_sequence)
            if not isinstance(step["step"], str):
                state.var_found_errors_in_sequence.append("Step number must be a string.")
            if not isinstance(step["action"], str):
                state.var_found_errors_in_sequence.append("Action must be a string.")
            if state.var_found_errors_in_sequence:
                return False, "The sequence contains errors. Please check the following:\n" + "\n".join(state.var_found_errors_in_sequence)                
        
        return True, "Sequence format is valid."

    def check_functions_exist(self, sequence, functions, ingredients):
        """
        This function checks if the functions in the sequence exist in the functions list. It also checks if the parameters are of the correct type and exist in the ingredients list.
        """
        # Iterate through the sequence steps
        for step in sequence["sequence"]:
            action = step["action"]
            func_name = action.split("(")[0]
            #print("func_name: ", func_name)
            
            # Extract parameters from action
            params = action[action.find("(") + 1 : action.find(")")].split(",")
            params = [p.strip() for p in params if p.strip()]

            function_found = False
            for full_func_name in functions["functions"].keys():
                # Check if the function name matches the start of the full function name (including parameter signature) in one of the functions
                if full_func_name.startswith(func_name + "("):
                    #print("found the function that matches the action", full_func_name, func_name)
                    function_found = True
                    func_signature = full_func_name
                    expected_params = func_signature[func_signature.find("(") + 1 : func_signature.find(")")].split(",")
                    expected_params = [p.strip() for p in expected_params if p.strip()]
                    i = 0 
                    #print("params and expected_params: ", params, expected_params)
                    if len(params) != len(expected_params):
                        error_message = f"Function '{func_signature}' expects {len(expected_params)} parameters, but {len(params), params} were provided."
                        state.var_found_errors_in_sequence.append(error_message)
                    elif len(params) == 0:
                        self.logger.debug(f"Function '{func_signature}' has no parameters.")
                    else:
                        for expected_param in expected_params:
                            # for each parameter, check if the type of the parameter matches the expected type
                            match expected_param:
                                case "number":
                                    if not params[i].isnumeric():
                                        #print(f"param {i, params[i]} is not a number") # return error
                                        error_message = f"Function '{func_signature}' expects parameter {i} to be a number, but '{params[i]}' was provided."
                                        state.var_found_errors_in_sequence.append(error_message) 
                                    else: 
                                        self.logger.debug(f"param {i, params[i]} is a number")     
                                case "item":
                                    if params[i] not in ingredients["ingredients"]:
                                        #print(f"param {i, params[i]} is not an item of ingredients") # return error
                                        error_message = f"Function '{func_signature}' expects parameter {i} to be an item, but '{params[i]}' was provided."
                                        state.var_found_errors_in_sequence.append(error_message)
                                    else:
                                        self.logger.debug(f"param {i, params[i]} is an item of ingredients")
                                case "sandwich_item":
                                    if params[i] not in ["avocado_toast", "jelly_toast", "peanut_butter_toast", "toasted_bread"]:
                                        #print(f"param {i, params[i]} is not an item of sandwich_items")
                                        error_message = f"Function '{func_signature}' expects parameter {i} to be a bread item, but '{params[i]}' was provided."
                                        state.var_found_errors_in_sequence.append(error_message)
                                    else:
                                        self.logger.debug(f"param {i, params[i]} is an item of sandwich_items")
                                case "toasted_bread":
                                    if params[i] not in ["toasted_bread"]:
                                        #print(f"param {i, params[i]} is not an item of toasted_bread")
                                        error_message = f"Function '{func_signature}' expects parameter {i} to be toasted bread, but '{params[i]}' was provided."
                                        state.var_found_errors_in_sequence.append(error_message)
                                    else:
                                        self.logger.debug(f"param {i, params[i]} is a toasted_bread")
                                case _:
                                    #print(f"Function '{func_signature}' has an unexpected parameter signature.")
                                    error_message = f"Function '{func_signature}' has an unexpected parameter signature."
                                    state.var_found_errors_in_sequence.append(error_message)
                            i += 1

                        break
            
            if not function_found:
                #print(f"Function '{func_name}' does not exist in the functions list.")
                error_message = f"Function '{func_name}' does not exist in the functions list."
                state.var_found_errors_in_sequence.append(error_message)
            
        if state.var_found_errors_in_sequence:
                return False, "Errors were found in the sequence."
        return True, "All functions exist in the functions list."

class CheckUserOkWithNewSeq(py_trees.behaviour.Behaviour):
    """
    This condition checks if the user is okay with the new sequence generated by the LLM.
    """

    def __init__(self, name, conversation):
        super(CheckUserOkWithNewSeq, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if FURHAT:
            recorded_text = record_speech(state.var_furhat)
            print("Total listened: ", recorded_text)
            state.var_transcript += "Total listened:" + recorded_text + "\n"
            self.conversation.append({"role": "user", "content": recorded_text})
        else:
            user_input = input("User: ")
            self.conversation.append({"role": "user", "content": user_input})
        sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        user_answer = self.conversation[-1]['content']

        # if the user answer is less than 15 characters, we manually check if the answer contains 'yes' or 'no' and such
        if len(user_answer) < 15:
            quick_check = self.quick_check_user_answer(user_answer)
            if quick_check == "affirmative":
                self.logger.info("User is okay with the new sequence. (quick check)")
                return py_trees.common.Status.SUCCESS
            elif quick_check == "negative":
                self.logger.info("User is not okay with the new sequence.")
                return py_trees.common.Status.FAILURE
            else:
                self.logger.info("User answer needs further checking.")

        #print("using sentiment analysis on: ", user_answer)
        result = sentiment_analyzer(user_answer)
        #print(result)
        if result[0]['label'] == 'POSITIVE':
            self.logger.info("User is okay with the new sequence.")
            return py_trees.common.Status.SUCCESS
        self.logger.info("User is not okay with the new sequence.")
        return py_trees.common.Status.FAILURE

    def quick_check_user_answer(self, user_answer):
        """
        This function quickly checks the user answer if it is less than 15 characters.
        """
        # Define lists for quick checks
        affirmatives = ["yes", "yeah", "ok", "sure", "yup", "jup", "jap", "ye", "of course", "naturally", "good"]
        affirmative_buts = ["but", "however", "no", "and", "not"]
        negatives = ["no", "wrong", "false", "not"]
        
        
        for affirmative in affirmatives:
            if affirmative in user_answer.lower():
                # Check if it also contains an affirmative but
                for affirmative_but in affirmative_buts:
                    if affirmative_but in user_answer.lower():
                        return "needs further checking"
                return "affirmative"
        
        # Check for negatives
        for negative in negatives:
            if negative in user_answer.lower():
                return "negative"
    
        return "needs further checking"  # Default if it does not match any quick check

class CheckCapability(py_trees.behaviour.Behaviour):
    """
    This condition checks if the robot is capable of performing the requested action.
    """

    def __init__(self, name, conversation):
        super(CheckCapability, self).__init__(name)
        self.conversation = conversation

    def update(self):
        if LLM:
            # Call the LLM to check if the user input is known
            response = self.check_capability_with_llm(self.conversation)
            print("Is it within the capabilities of the robot? ", response)
            if response == "True":
                state.var_capable = True
            else:
                state.var_capable = False
            state.var_transcript += "Is it within the capabilities of the robot? " + response + "\n"
            if response == "True": # for more flexible acceptance, one could also check if the response contains "True" within the first 15 characters
                return py_trees.common.Status.SUCCESS
        
        elif 'capable' in self.conversation[-1]['content'].lower():
            print("Is it within the capabilities of the robot? True")
            state.var_transcript += "Is it within the capabilities of the robot? True\n"
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE
    
    def check_capability_with_llm(self, conversation):
        """
        This function checks if the robot is capable of executing the users request using the Chatgpt 3.5 turbo model.
        """
        # This logic is to prevent the LLM from being called too many times
        if state.var_total_llm_calls >= MAX_LLM_CALL:
            print("Exceeded the maximum number of LLM calls.")
            state.var_transcript += "Exceeded the maximum number of LLM calls.\n"
            return "False"
        state.var_total_llm_calls += 1
        #print("number of total llm calls was raised to: ", state.var_total_llm_calls)

        try:
            predefined_messages_capability = PREDEFINED_CAPABILITY_CHECK
            formatted_conversation = format_conversation(conversation)
            #print("formatted_conversation: ", formatted_conversation)
            convo_to_add = {"role": "user", "content": formatted_conversation}
            predefined_messages_capability.append(convo_to_add)

            #print("The conversation before the LLM call: ", conversation)
            #print("Messages for Known: ", messages)

            # Make the API call
            completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    # response_format={ "type": "json_object" },
                    messages=predefined_messages_capability
                    )
            
            # Extract and return the response content
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error in LLM call: {e}")
            state.var_transcript += f"Error in LLM call: {e}\n"
            return "False"
 



