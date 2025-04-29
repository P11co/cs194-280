# gram.py
import asyncio
import datetime
import logging
import sys
from os import getenv
from collections import defaultdict
import json
import re
import os 
import time


print("CWD is:", os.getcwd())

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatAction
from aiogram.filters import CommandStart
from aiogram.types import Message, ReactionTypeEmoji

from google import genai

# --- CrewAI Imports ---
from crewai import Agent, Task, Crew, Process
from mindmates.crew import Mindmates

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

TOKEN = getenv("BOT_TOKEN")
GEMINI_API_KEY = getenv("GEMINI_API_KEY")

# Initialize Gemini Client
if not GEMINI_API_KEY:
    logging.error("GEMINI_API_KEY not found.")
    sys.exit("Gemini API Key is required.")
else:
    try:
        # This client will used by the filter function
        client = genai.Client(api_key=GEMINI_API_KEY)
        logging.info("Gemini configured successfully (for filter or direct calls).")
    except Exception as e:
        logging.error(f"Failed to configure Gemini: {e}")
        sys.exit("Exiting due to Gemini configuration error.")

dp = Dispatcher()

chat_id = None # global chat_id, used for bot check-in

# --- Simple In-Memory Chat History ---
# Warning: Use a database for persistence.
chat_histories = defaultdict(list)
MAX_HISTORY_LEN = 10 # Keep last 10 turns (User + Bot)


has_checked_in = False # record whether check-in's already performed so we don't ask the question over and over again
last_user_response_time = 0 # record the time that we've last heard from user

def add_to_history(chat_id, role, content):
    """Adds a message to the chat history for a user."""
    chat_histories[chat_id].append({"role": role, "content": content})
    # Keep history length manageable
    if len(chat_histories[chat_id]) > MAX_HISTORY_LEN * 2:
        chat_histories[chat_id] = chat_histories[chat_id][-(MAX_HISTORY_LEN * 2):]

def get_formatted_history(chat_id):
    """Formats history for the LLM prompt."""
    history = chat_histories.get(chat_id, [])
    # Simple formatting example:
    return "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

# --- Filter Function ---
async def filter_lifestyle_experts_async(chat_history: str, user_input: str, expert_list: list) -> list:
    """
    Returns a list of relevant expert TOPICS (e.g., ["work/study", "exercise"]).
    """
    logging.info("Filtering relevant experts...")
    relevant_topics = []
    full_text = chat_history + "\nUser: " + user_input
    if "study" in full_text.lower() or "work" in full_text.lower():
        relevant_topics.append("work/study")
    if "exercise" in full_text.lower() or "tired" in full_text.lower() or "gym" in full_text.lower():
         relevant_topics.append("exercise")
    if "relationship" in full_text.lower() or "friend" in full_text.lower() or "partner" in full_text.lower():
         relevant_topics.append("relationships")
    if "hobby" in full_text.lower() or "fun" in full_text.lower() or "bored" in full_text.lower():
        relevant_topics.append("hobby")
    if "food" in full_text.lower() or "eat" in full_text.lower() or "diet" in full_text.lower() or "nutrition" in full_text.lower():
        relevant_topics.append("food")

    logging.info(f"Filter result: {relevant_topics}")
    return relevant_topics

# --- Mindmates Crew Factory Instance ---
# We create an instance of the class that defines agents
mindmates_definitions = Mindmates()

# --- Telegram Handlers ---
# Modification 1: insert check-in logic
# assume that the agent will step in and ask check-in questions when we haven't heard from user for some time (5 minutes)
# ------------------------------
async def notifier(bot: Bot):
    await asyncio.sleep(10) # give the bot some time to fully start up (when first run)
    global has_checked_in
    global chat_id
    global last_user_response_time
    while True:
        if not has_checked_in and time.time() - last_user_response_time >= 300:
            from mindmates.utils.workflow_utils import perform_checkin
            check_in_response = perform_checkin()
            if check_in_response != "None":
                await bot.send_message(chat_id, check_in_response)
                add_to_history(chat_id, "Bot", check_in_response)
            has_checked_in = True
        await asyncio.sleep(60)
# ------------------------------

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """ Handler for the /start command """
    global chat_id
    response = f"Hello, {html.bold(message.from_user.full_name)}! I'm here to listen. Tell me what's on your mind."
    chat_id = message.chat.id
    chat_histories[chat_id] = [] # Clear history on /start
    await message.answer(response)
    add_to_history(chat_id, "Bot", response)


@dp.message(F.text)
async def handle_crewai_request(message: Message, bot: Bot):
    """ Handles incoming text, filters experts, runs dynamic CrewAI crew, and replies. """
    global has_checked_in
    user_input = message.text
    chat_id = message.chat.id
    message_id = message.message_id # <-- Get the ID of the user's message

    if not user_input:
        return
    
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(1) # <-- ADD FOR TESTING ONLY - forces typing status for 1s

    # 1. Add user message to history
    formatted_history = get_formatted_history(chat_id)
    add_to_history(chat_id, "User", user_input)

    try:
        # 2. Filter Relevant Experts
        expert_agent_keys_map = { # Map readable topic name to agent method name in crew.py
            "work/study": "workstudy_agent",
            "relationships": "relationship_agent",
            "hobby": "hobby_agent",
            "exercise": "exercise_agent",
            "food": "food_agent",
        }
        all_expert_topics = list(expert_agent_keys_map.keys())
        relevant_topics = await filter_lifestyle_experts_async(formatted_history, user_input, all_expert_topics)

        # 3. Get Agent Instances
        # Always include the main therapy agent
        therapy_agent_instance = mindmates_definitions.therapy_agent() # Call the method
        if not therapy_agent_instance:
             raise ValueError("Could not instantiate therapy_agent")

        relevant_expert_agents = []
        for topic in relevant_topics:
            agent_key = expert_agent_keys_map.get(topic)
            if agent_key:
                agent_instance = mindmates_definitions.get_agent_by_name(agent_key)
                if agent_instance:
                    relevant_expert_agents.append(agent_instance)
                else:
                    logging.warning(f"Could not find or instantiate agent for topic: {topic} (key: {agent_key})")

        # 4. Create Tasks Dynamically
        expert_tasks = []
        for agent_instance in relevant_expert_agents:
            task = Task(
                description=f"User Message Context:\n'''\n{formatted_history}\nUser: {user_input}\n'''\n\nBased *only* on the user message context above, analyze it strictly from your domain perspective ({agent_instance.role}). Focus *only* on aspects relevant to your expertise. If nothing is relevant, state that clearly.",
                expected_output=f"A concise analysis (max 2-3 bullet points) containing only the most critical insights from your specific domain ({agent_instance.role}). If nothing relevant, output 'No specific insights from my domain.'",
                agent=agent_instance,
                # Add async_execution=True if tasks can run in parallel
                # async_execution=True
            )
            expert_tasks.append(task)

        # RAG Context Retrieval
        from mindmates.utils.embedding_utils import load_vectordb, fetch_rag_context
        
        input_query = f"Find me information relevant to {user_input}"
        VECTOR_DB = load_vectordb()
        rag_context = fetch_rag_context(input_query, VECTOR_DB, top_n=3)
        print("RAG Context dump:", rag_context)
            
        from mindmates.utils.models import TherapyOutput

        synthesis_task = Task(
            description=f"""User Message Context:\n'''\n{formatted_history}\nUser: {user_input}\n'''\n\n
                        Review the user message context and the analyses from expert agents (if any).
                        1. Synthesize perspectives into a supportive therapeutic text response for the user. Use emojis when appropriate. Try to mirror the way the user talks, so incorporate modern internet slang if the user uses it actively.
                        2. Suggest ONE suitable **standard Unicode emoji** reaction from this specific, commonly allowed list: 👍, ❤️, 🔥, 🎉, 🤔, 🙏. 
                        
                        Here is what each of these emojis means:
                        👍 Thumbs Up – agreement, approval or simple “got it”
                        ❤️ Red Heart – warmth, affection, gratitude or strong support
                        🔥 Fire – something “awesome,” impressive or “on fire”
                        🎉 Party Popper – celebration, congratulations or festive cheer
                        🤔 Thinking Face – pondering, curiosity, mild doubt or asking for clarification
                        🙏 Folded Hands – thanks, please, hope or sincere support
                        If no standard emoji feels appropriate, suggest "None".
                        
                        Return ONLY the JSON object matching the expected schema, nothing else.
                        
                        Here are some relevant QNA pairs other patients have asked and how practitioners responded to them. Refer to them only if the context is relevant.
                        {rag_context}
                        """,
            expected_output="A JSON object conforming to the TherapyOutput schema.", # Schema has final_response (str) and suggested_reaction (Optional[str])
            agent=therapy_agent_instance,
            context=expert_tasks,
            output_pydantic=TherapyOutput # Use the Pydantic model for structure
        )

        # 5. Assemble the Dynamic Crew FOR THIS REQUEST
        all_involved_agents = [therapy_agent_instance] + relevant_expert_agents
        all_tasks = expert_tasks + [synthesis_task] # Experts run first, then synthesis

        dynamic_crew = Crew(
            agents=all_involved_agents,
            tasks=all_tasks,
            process=Process.sequential, # Ensures experts run before synthesis due to context dependency
            memory=True, # Enable memory for this run (helps context passing via RAG)
            verbose=True # Set to 1 or 2 for debugging, 0 for production
        )

        # 6. Kickoff the Dynamic Crew
        logging.info(f"Kicking off dynamic CrewAI for chat {chat_id} with {len(relevant_expert_agents)} relevant experts.")
        # Inputs might not be needed if description has all context, but can be passed if tasks use {variables}
        crew_inputs = {
             'user_input': user_input, # Example if tasks use {user_input}
             'chat_history': formatted_history # Example if tasks use {chat_history}
        }
        crew_result = await dynamic_crew.kickoff_async(inputs=crew_inputs) # Use async
        logging.info(f"CrewAI kickoff_async completed for chat {chat_id}.")

        # 7. Process and Send Result
        final_response_text = "Sorry, I couldn't formulate a response right now."
        reaction_to_set = None
        output_data = None # Variable to hold the successfully parsed dictionary

        # --- Try CrewAI's parsing first (assuming you used output_pydantic=TherapyOutput) ---
        if crew_result and crew_result.pydantic and isinstance(crew_result.pydantic, TherapyOutput):
            output_data = crew_result.pydantic.model_dump() # Convert Pydantic model to dict
            logging.info("Successfully used crew_result.pydantic")
        elif crew_result and crew_result.json_dict and isinstance(crew_result.json_dict, dict):
            output_data = crew_result.json_dict
            logging.info("Successfully used crew_result.json_dict")

        # --- If CrewAI parsing failed, try manual parsing of raw output ---
        if output_data is None and crew_result and crew_result.raw:
            raw_output = crew_result.raw
            logging.warning("CrewAI parsing failed. Attempting manual parse of raw output.")
            logging.debug(f"Raw Output for manual parse:\n{raw_output}")

            # Attempt to extract JSON string (handles `````` and potentially other issues)
            json_match = re.search(r"``````", raw_output, re.DOTALL | re.IGNORECASE)
            json_string = None
            if json_match:
                json_string = json_match.group(1) # Extract content within markdown
            else: # Fallback: find braces
                start_index = raw_output.find('{')
                end_index = raw_output.rfind('}')
                if start_index != -1 and end_index != -1 and start_index < end_index:
                    json_string = raw_output[start_index:end_index+1]

            # Try parsing the extracted string
            if json_string:
                try:
                    output_data = json.loads(json_string) # Use loads() on the string
                    if not isinstance(output_data, dict):
                        logging.warning("Manual JSON parse result was not a dictionary.")
                        output_data = None
                    else:
                        logging.info("Manual JSON parse successful.")
                except json.JSONDecodeError as json_err:
                    logging.warning(f"Manual JSONDecodeError: {json_err}. Falling back to raw output.")
                    final_response_text = raw_output # Use raw output if manual parse fails
                    output_data = None
            else:
                final_response_text = raw_output
                logging.warning("No parsable JSON structure found manually. Using raw output.")

        # --- Extract data if parsing was successful ---
        if output_data and isinstance(output_data, dict):
            final_response_text = output_data.get('final_response', final_response_text)
            reaction_to_set = output_data.get('suggested_reaction')
            # ... (emoji validation and setting reaction_to_set) ...
        elif not crew_result or not crew_result.raw:
            logging.error("Crew execution failed or returned empty result.")
        # If output_data is None, final_response_text might already be raw_output
            
        # --- Set Reaction (if suggested) ---
        print("EMOJI TO RESPOND BEFORE IF LOOP:", reaction_to_set)
        if reaction_to_set:
            print("EMOJI TO RESPOND:", reaction_to_set)
            try:
                await bot.set_message_reaction(
                    chat_id=chat_id,
                    message_id=message_id, # User's message ID
                    reaction=[ReactionTypeEmoji(emoji=reaction_to_set)]
                )
                logging.info(f"Reacted with '{reaction_to_set}' to message {message_id}")
            except Exception as reaction_error:
                logging.warning(f"Could not set suggested reaction '{reaction_to_set}': {reaction_error}")
                
        # --- End Set Reaction ---

        # 8. Add bot response to history
        add_to_history(chat_id, "Bot", final_response_text)
        await message.answer(final_response_text)
        
        # Modification 2: insert context summary and calendar update logic
        # right after each round of conversation
        # ------------------------------
        # update the time recording when the user last sent a message
        # (so that when the channel is idle for some time, we can perform check-in)
        global last_user_response_time
        last_user_response_time = time.time()
        # calendar update
        from mindmates.utils.workflow_utils import perform_memory_update
        current_history = get_formatted_history(chat_id)
        perform_memory_update(current_history)
        has_checked_in = False
        # ------------------------------

    except Exception as e:
        print(GEMINI_API_KEY)
        print(load_dotenv(find_dotenv()), find_dotenv())
        logging.error(f"Error during CrewAI execution or Telegram response for chat {chat_id}: {e}", exc_info=True)
        await message.answer("Sorry, I encountered an internal error while processing your request with the AI crew.")


# --- Main Execution ---
async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    asyncio.create_task(notifier(bot))
    logging.info("Starting bot polling...")
    await dp.start_polling(bot, skip_updates=True) # skip_updates=False might be better during dev


if __name__ == "__main__":
    if not TOKEN:
        sys.exit("BOT_TOKEN not found. Exiting.")
    asyncio.run(main())

