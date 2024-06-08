# utils.py
# Alexander Leszczynski
# 08-06-2024 

def format_conversation(conversation):
        """
        This function formats the conversation to be used in the LLM call.
        """
        # The format should be User: <user_input> Assistant: <assistant_response> User: <user_input> ...
        formatted_conversation = ""
        for i, message in enumerate(conversation):
            if i % 2 == 0:
                formatted_conversation += f"User: {message['content']}\n"
            else:
                formatted_conversation += f"Assistant: {message['content']}\n"
        return formatted_conversation

