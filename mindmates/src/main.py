#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from mindmates.crew import Mindmates
from mindmates.utils.llm_utils import filter_lifestyle_experts

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

CALENDAR_PATH="./knowledge/calendar.txt"

def get_user_input():
    print("(Enter \"End\" to quit the chat) User: ", end="")
    user_input = input()
    return user_input

def read_calendar(calendar_path):
    with open(calendar_path, "r", encoding="utf-8") as f:
        text = f.read()
    return text

def run():
    """
    Run the crew.
    """
    chat_history = ""
    
    try:
        print("Performing check-in ...")
        # perform check in
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        calendar = read_calendar(CALENDAR_PATH)
        check_in_inputs = {
            'current_time': current_time,
            'chat_history': chat_history,
            'calendar': calendar
        }
        output = Mindmates().checkInCrew().kickoff(inputs=check_in_inputs)

        if output.raw == 'None': # the check-in agent finds it no need to raise questions about past events
            # the user might want to chat with the bot
            user_input = get_user_input()
            while user_input != "End":
                chat_history += "User: " + user_input + '\n'

                now = datetime.now()
                current_time = now.strftime("%Y-%m-%d %H:%M:%S")
                calendar = read_calendar(CALENDAR_PATH)
                chat_inputs = {
                    'current_time': current_time,
                    'chat_history': chat_history,
                    'calendar': calendar
                }

                output = Mindmates().chatCrew().kickoff(inputs=chat_inputs).tasks_output[0] # get the chat output
                print("BOT:", output.raw)
                chat_history += "Assisstant: " + output.raw + '\n'

                user_input = get_user_input()
        else:
            # check-in agent raises a check-in question
            print("BOT:", output.raw)
            chat_history += "Assisstant: " + output.raw + '\n'

            # the user responds to the question and starts chatting with the companion chatbot agent
            user_input = get_user_input()
            while user_input != "End":
                chat_history += "User: " + user_input + '\n'

                now = datetime.now()
                current_time = now.strftime("%Y-%m-%d %H:%M:%S")
                calendar = read_calendar(CALENDAR_PATH)
                chat_inputs = {
                    'current_time': current_time,
                    'chat_history': chat_history,
                    'calendar': calendar
                }

                output = Mindmates().chatCrew().kickoff(inputs=chat_inputs).tasks_output[0] # get the chat output
                print("BOT:", output.raw)
                chat_history += "Assisstant: " + output.raw + '\n'

                user_input = get_user_input()


    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        Mindmates().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Mindmates().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    try:
        Mindmates().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
