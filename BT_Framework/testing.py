def quick_check_user_answer(user_answer):
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

print(quick_check_user_answer("that sounds good. Do that."))