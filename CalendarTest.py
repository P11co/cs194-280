import autogen
import os
from dotenv import load_dotenv
import datetime
import time
import threading
import json

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("API Key not found in .env file!")
    exit()


# Configure your LLM (e.g., Gemini)
config_list_gemini = [
    {
        "model": "gemini-2.0-flash",
        "api_key": api_key,
        "api_type": "google"
    }
]

llm_config_gemini = {"config_list": config_list_gemini, "seed": 42}

planner_agent = autogen.AssistantAgent(
    name="Planner",
    llm_config=llm_config_gemini,
    system_message="You are a helpful planner. You carefully read the user's messages to identify any mentioned events and their associated times or desired follow-up times. "
    "When you identify an event and a specific time for a reminder or follow-up, store the event description and the exact datetime object for the alert. "
    "You will then inform the user that you have noted the event and the alert time. "
    "When given specific instructions to follow a format, you will follow that format without generating any other output tokens."
)

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "coding", "use_docker": False},
)

events_to_alert = []
planner_processing = False

def process_user_input(message):
    user_proxy.send(message, planner_agent)
    planner_response(planner_agent, [{"role": "user", "content": message}], user_proxy)

def planner_response(recipient, messages, sender):
    global planner_processing
    planner_processing = True
    print("DEBUG: planner_response function called.")
    last_message = messages[-1].get("content", "")
    print(f"{sender.name} says: {last_message}")

    # Try to get structured information from the LLM about events and times
    response = recipient.generate_reply(messages=[{
        "role": "user",
        
        "content": f"{last_message}\n\nIdentify any events mentioned and their associated times or follow-up times."
        "After you have identified all events, generate a JSON object containing all events in the following format: "
        "event_name: 'soccer practice' description: 'user is going to practice soccer, presumably with friends'"
        "wakeup_time: '2025-04-13 06:30:00'"
    }])

    try:
        print("RESPONSE CONTENT")
        print(response['content'])
        print("END RESPONSE CONTENT")
        structured_info = json.loads(response)
        if "events" in structured_info:
            for event_data in structured_info["events"]:
                description = event_data.get("description")
                alert_time_str = event_data.get("alert_time")
                if description and alert_time_str:
                    try:
                        alert_time_obj = datetime.datetime.fromisoformat(alert_time_str)
                        events_to_alert.append({"event": description, "alert_time": alert_time_obj})
                        print(f"Okay, I've noted to remind you about '{description}' at {alert_time_obj.strftime('%I:%M%p')}.")
                    except ValueError:
                        print("Sorry, I couldn't understand the time format provided by the LLM.")
        else:
            print("no events")
        recipient.reply(messages=messages, sender=sender)
    except json.JSONDecodeError:
        print("Planner received non-JSON response for event extraction.")
        recipient.reply(messages=messages, sender=sender)

    planner_processing = False

planner_agent.register_reply(autogen.Agent, planner_response)

def check_for_soonest_event():
    while True:
        time.sleep(30)  # Check for the soonest event every 30 seconds
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))) # Assuming Berkeley time
        alerts_to_trigger = [event for event in list(events_to_alert) if event["alert_time"] <= now] # TODO: use a heap sorted by alert time instead
        for alert in alerts_to_trigger:
            print(f"\n⏰ ALERT! It's {now.strftime('%I:%M%p')}. How was your {alert['event']}?\n")
            planner_agent.send(f"User has just finished {alert['event']}, ask them about how it went.", planner_agent)
            events_to_alert.remove(alert) # Remove triggered alert

# Start the background task to check for the soonest event
soonest_event_thread = threading.Thread(target=check_for_soonest_event, daemon=True)
soonest_event_thread.start()

# Initial user interaction
process_user_input("Hello Planner, I have dinner with my mom around 4pm and I'd like you to ask me about it shortly after. Also, soccer practice is at six. Additionally, wake me up in one minute")
print("loop started")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")