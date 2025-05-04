from datetime import datetime
from mindmates.crew import Mindmates
import json
import re

CALENDAR_PATH="./data/calendar.json"

def perform_checkin():
    ''' Perform checkin based on current user calender '''
    print("Performing check-in ...")
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    calendar = read_calendar(CALENDAR_PATH)
    check_in_inputs = {
        'current_time': current_time,
        'calendar': calendar
    }
    output = Mindmates().checkin_crew().kickoff(inputs=check_in_inputs)
    return output.raw

def read_calendar(calendar_path):
    # load the JSON array
    with open(calendar_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # rebuild the original text format
    lines = []
    for entry in data:
        time     = entry.get("time", "")
        schedule = entry.get("schedule", "")
        feedback = entry.get("feedback", "")
        lines.append(f"Time: {time}\tSchedule: {schedule}\tFeedback: {feedback}")
    
    if len(lines) == 0:
        return "[Empty]"
    
    return "\n".join(lines)

def perform_memory_update(chat_history):
    ''' Given the current chat history, perform update on Calendar'''
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    calendar = read_calendar(CALENDAR_PATH)
    chat_inputs = {
        'current_time': current_time,
        'chat_history': chat_history,
        'calendar': calendar
    }
    output = Mindmates().memory_update_Crew().kickoff(inputs=chat_inputs)
    print("Performing memory update:\n", output)
    
    from src.mindmates.utils.models import CalendarEvent
    import logging
    
    # # try Pydantic output first
    # if output and output.pydantic and isinstance(output.pydantic, CalendarEvent):
    #     output_data = output.pydantic
    #     logging.info("Successfully used Calendar file output.pydantic")
    # elif output and output.json_dict and isinstance(output.json_dict, dict):
    #     output_data = output.json_dict
    #     logging.info("Successfully used Calendar file output.pydantic")
    # else:
    #     logging.warning("Calendar_agent: failed to output a valid JSON type file")
    #     logging.warning(output.pydantic)

    # # overwrite the calendar.json file with pure JSON
    # print("----------------------------------------------------->Writing to:", CALENDAR_PATH)
    # with open(CALENDAR_PATH, "w", encoding="utf-8") as f:
    #     json.dump(output.pydantic.model_dump(), f, ensure_ascii=False, indent=2)
    
    # In workflow_utils.py
    if output and output.raw:
        cleaned_output = clean_json_output(output.raw)
        try:
            output_data = json.loads(cleaned_output)
            # overwrite the calendar.json file with pure JSON
            print("----------------------------------------------------->Writing to:", CALENDAR_PATH)
            with open(CALENDAR_PATH, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            logging.warning("Failed to parse JSON even after cleaning")

def clean_json_output(raw_output):
    if raw_output.startswith("```json"):
        # Remove the first 7 characters
        clean_json = raw_output[7:-3].strip()
        return clean_json
    return raw_output  # Return original if pattern doesn't match
