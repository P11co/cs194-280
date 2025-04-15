import asyncio
import logging
import sys
from os import getenv

from dotenv import load_dotenv
load_dotenv()

from aiogram import Bot, Dispatcher, html, F # F is for Filters
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatAction # Import ChatAction
from aiogram.filters import CommandStart # Removed Command, not used here
from aiogram.types import Message # Removed CallbackQuery, not used here
# Removed InlineKeyboardBuilder, not used here

from google import genai

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

TOKEN = getenv("BOT_TOKEN")
GEMINI_API_KEY = getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logging.error("GEMINI_API_KEY not found in environment variables.")
    sys.exit("Gemini API Key is required.")
else:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        logging.info("Gemini configured successfully.")
    except Exception as e:
        logging.error(f"Failed to configure Gemini: {e}")
        sys.exit("Exiting due to Gemini configuration error.")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

# --- Gemini Interaction Function ---

# Function to call the Gemini API (Synchronous/Blocking)
def get_llm_response_sync(prompt: str) -> str:
    """
    Sends the prompt to the Gemini API and returns the text response.
    This is a BLOCKING function.
    """
    logging.info(f"Sending prompt to Gemini: '{prompt[:50]}...'") # Log prompt start
    try:
        model = 'gemini-1.5-flash-8b'

        # Generate content
        # The contents parameter needs to be a list with the prompt
        response = client.models.generate_content(model=model, contents=[prompt])
        logging.info(f"Received response from Gemini")
        
        # Extract the text from the response
        # The text is in the first candidate's content parts
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            # Extract the text from the first part
            result_text = response.candidates[0].content.parts[0].text
            logging.info(f"Extracted text: {result_text[:50]}...")
            return result_text
        else:
            # Handle empty response
            logging.warning("Gemini returned an empty response")
            return "Sorry, I received an empty response from the AI."

    except Exception as e:
        logging.error(f"Error during Gemini API call: {e}")
        # Propagate the error or return a user-friendly message
        return f"Sorry, an error occurred while contacting the AI: {e}"

# --- Aiogram Handlers ---

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Handler for the /start command
    """
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! Send me a message, and I'll try to respond using Gemini.")

# Removed the echo_handler entirely

@dp.message(F.text) # Trigger on any text message
async def handle_llm_request(message: Message, bot: Bot): # Added bot parameter
    """
    Handles incoming text messages, sends them to Gemini, and replies.
    """
    user_input = message.text
    if not user_input: # Ignore empty messages if any
        return

    # Indicate the bot is thinking using chat action "TYPING"
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    try:
        # Run the blocking Gemini call in a separate thread
        # Pass the user's text directly as the prompt
        llm_result = await asyncio.to_thread(get_llm_response_sync, user_input)

        # Send the result back
        await message.answer(llm_result)

    except Exception as e:
        # Catch potential errors from asyncio.to_thread or message sending
        logging.error(f"Error in handle_llm_request: {e}")
        await message.answer("Sorry, I encountered an internal error while processing your request.")

# --- Main Execution ---

async def main() -> None:
    # Initialize Bot instance with default bot properties
    # Use ParseMode.HTML to allow HTML formatting in messages
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    logging.info("Starting bot polling...")
    # Start polling for updates
    # Pass the bot instance to the dispatcher implicitly through start_polling
    # Handlers can now access the bot instance if needed (like for send_chat_action)
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    # Make sure environment variables are loaded before running main
    if not TOKEN:
        sys.exit("BOT_TOKEN not found in environment variables. Exiting.")
    # Gemini Key check happens earlier during configuration

    asyncio.run(main())
