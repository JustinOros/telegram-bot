import os
import sys
import asyncio
import logging
import random
from pathlib import Path
from dotenv import load_dotenv
from telegram.error import NetworkError

ENV_FILE = Path(".env")
PERSONALITY_FILE = Path("personality.txt")
LOG_FILE = Path("telegram-bot.log")
WORDS_PER_MINUTE = 30
CHARS_PER_SECOND = (WORDS_PER_MINUTE * 5) / 60
MAX_HISTORY = 20
READ_DELAY_MIN = 1
READ_DELAY_MAX = 10
TYPING_ACTION_INTERVAL = 4

logging.basicConfig(level=logging.WARNING)
for noisy in ("httpx", "httpcore", "telegram", "apscheduler"):
    logging.getLogger(noisy).setLevel(logging.ERROR)

logger = logging.getLogger("telegramGPT")
logger.setLevel(logging.INFO)
logger.propagate = False

_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_file_handler = logging.FileHandler(LOG_FILE)
_file_handler.setFormatter(_formatter)
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_formatter)
logger.addHandler(_file_handler)
logger.addHandler(_console_handler)

def create_env_file():
    print("\n🚀 Welcome to Telegram-bot! First-time setup...\n")
    openai_key = input("Enter your OpenAI API Key: ").strip()
    telegram_token = input("Enter your Telegram Bot Token: ").strip()

    with open(ENV_FILE, "w") as f:
        f.write(f"OPENAI_API_KEY={openai_key}\n")
        f.write(f"TELEGRAM_BOT_TOKEN={telegram_token}\n")

    logger.info("Created .env file with user credentials")
    print("\n✅ .env file created and saved!\n")

def load_personality():
    if PERSONALITY_FILE.exists():
        return PERSONALITY_FILE.read_text().strip()
    default = (
        "You are a chill, helpful friend responding via text message. "
        "Keep ALL responses very short — 1 to 3 sentences max. "
        "No long explanations unless explicitly asked. "
        "Be casual, friendly, and to the point. "
        "Write like you're texting a friend, not writing an essay."
    )
    PERSONALITY_FILE.write_text(default)
    logger.info("personality.txt not found — created with default personality")
    return default

def typing_delay(text):
    return max(1.0, len(text) / CHARS_PER_SECOND)

def main():
    if not ENV_FILE.exists():
        create_env_file()

    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not all([openai_api_key, telegram_token]):
        logger.error("Missing values in .env — delete it and re-run to set up again.")
        sys.exit(1)

    try:
        from openai import OpenAI
        from telegram import Update
        from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        print("Run: pip install openai python-telegram-bot python-dotenv")
        sys.exit(1)

    openai_client = OpenAI(api_key=openai_api_key)
    personality = load_personality()
    conversation_histories = {}

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name
        user_text = update.message.text

        if chat_id not in conversation_histories:
            conversation_histories[chat_id] = []

        history = conversation_histories[chat_id]
        history.append({"role": "user", "content": user_text})

        logger.info(f"[{username}] {user_text}")

        trimmed_history = history[-MAX_HISTORY:]

        mimic_instruction = (
            f"\n\nThe person just sent you this message: {repr(user_text)}\n"
            "You must mirror their exact texting style in your reply. Follow these rules strictly:\n"
            "- Capitalization: If their message starts with a capital letter, start yours with one too. If they use all lowercase, you use all lowercase.\n"
            "- Punctuation: If they use no punctuation, use none. If they use periods, commas, question marks, use them the same way.\n"
            "- Grammar: If they write in proper grammatical sentences, you do too. If they write loosely or skip words, match that.\n"
            "- Shorthand: If they use shorthand like 'u' for 'you', 'r' for 'are', 'ur' for 'your', 'tbh', 'ngl', 'imo', 'idk', 'lmk', 'rn', 'omg', 'wtf', etc — use the same shorthand naturally in your reply.\n"
            "- Length: Match the approximate length and energy of their message.\n"
            "Do not explain or comment on their style. Just mirror it naturally."
        )

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": personality + mimic_instruction}] + trimmed_history
        )

        reply = response.choices[0].message.content.strip()
        history.append({"role": "assistant", "content": reply})

        logger.info(f"[GPT -> {username}] {reply}")

        read_delay = random.uniform(READ_DELAY_MIN, READ_DELAY_MAX)
        await asyncio.sleep(read_delay)

        typing_duration = typing_delay(reply)
        elapsed = 0
        while elapsed < typing_duration:
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            chunk = min(TYPING_ACTION_INTERVAL, typing_duration - elapsed)
            await asyncio.sleep(chunk)
            elapsed += chunk

        await update.message.reply_text(reply)

    async def error_handler(update, context):
        err = context.error
        if isinstance(err, NetworkError):
            if "Bad Gateway" in str(err) or "nodename nor servname" in str(err):
                logger.error(f"❌ Network error: {err}")
            else:
                logger.error(f"❌ Network error: {err}")
        else:
            logger.error(f"❌ Unexpected error: {err}")

    app = ApplicationBuilder().token(telegram_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Telegram-bot started")
    print("✅ Telegram-bot is running! Open Telegram and message your bot. (Ctrl+C to stop)\n")
    try:
        app.run_polling()
    except NetworkError:
        logger.error("❌ Could not connect to api.telegram.org — check your internet connection and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
