from datetime import datetime
from mindmates.crew import Mindmates
import json
import re

CALENDAR_PATH="./src/memory_pool/calendar.json"

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

# def strip_json_fences(s: str) -> str:
#     """
#     Remove any leading/trailing ```json…``` fences or stray backticks.
#     """
#     # This will grab the contents between ```json and the closing ```
#     m = re.search(r"```json\s*([\s\S]*?)```", s)
#     if m:
#         return m.group(1).strip()
#     # fallback: just remove any stray backticks
#     return s.strip().strip("`")

# def read_and_clean_output(raw: str) -> str:
#     cleaned = strip_json_fences(raw)
#     # optional: validate before writing
#     json.loads(cleaned)  
#     return cleaned

def perform_memory_update(chat_history):
    ''' Given the current chat history, perform update on memory pool (calender & diary log)'''
    print("Performing memory update ...")
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    calendar = read_calendar(CALENDAR_PATH)
    chat_inputs = {
        'current_time': current_time,
        'chat_history': chat_history,
        'calendar': calendar
    }
    output = Mindmates().memory_update_Crew().kickoff(inputs=chat_inputs)
    
    from src.mindmates.utils.models import CalendarEvent
    import logging
    
    # try Pydantic output first
    if output and output.pydantic and isinstance(output.pydantic, CalendarEvent):
        output_data = output.pydantic.model_dump() # Convert Pydantic model to di
        logging.info("Successfully used output.pydantic")
    elif output and output.json_dict and isinstance(output.json_dict, dict):
        output_data = output.json_dict
        logging.info("Successfully used output.pydantic")
    else:
        output_data = "Calendar Agent failed to receive a valid JSON type file"
        logging.warning("CalendarAgent failed to generate JSON type output.pydantic content")
        
    # clean it
    # clean_json = read_and_clean_output(output.raw)
    # overwrite the calendar.json file with pure JSON
    with open(CALENDAR_PATH, "w", encoding="utf-8") as f:
        f.write(output_data)