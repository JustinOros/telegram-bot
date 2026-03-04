# 🤖 telegram-bot

A lightweight AI-powered Telegram bot that responds like a real texting friend.

It uses OpenAI to generate short, casual responses while mirroring the user’s exact texting style, including capitalization, punctuation, shorthand, and energy.

---

## ✨ Features

* 🧠 Powered by OpenAI (`gpt-4o`)
* 💬 Mirrors user texting style automatically
* ⏱ Simulated “read” delay
* ⌨️ Realistic typing indicator timing
* 🧾 Conversation memory (last 20 messages per chat)
* 🎭 Customizable personality via `personality.txt`
* 📄 Automatic `.env` setup on first run
* 📝 Logging to `telegram-bot.log`

---

## 📦 Requirements

* Python 3.9+
* OpenAI API Key
* Telegram Bot Token

---

## 🔧 Installation

### 1️⃣ Clone the repo

```bash
git clone https://github.com/JustinOros/telegram-bot.git
cd telegram-bot
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the bot

```bash
python telegram-bot.py
```

On first run, it will prompt you for:

* OpenAI API Key
* Telegram Bot Token

It will then create a `.env` file automatically.

---

## 🔐 Environment Variables

The bot uses a `.env` file:

```
OPENAI_API_KEY=your_openai_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

⚠️ Important:
Make sure `.env` is included in `.gitignore` so you never upload your API keys.

---

## 🎭 Personality Customization

The bot loads its personality from:

```
personality.txt
```

If it doesn’t exist, a default one is created automatically.

You can edit this file to change the bot’s tone, for example:

* More sarcastic
* More professional
* More flirty
* Super minimal replies
* Long-form explanations

---

## 🧠 Style Mirroring System

The bot automatically:

* Matches capitalization
* Matches punctuation usage
* Matches grammar looseness
* Uses the same shorthand (u, rn, idk, lmk, etc.)
* Matches message length & energy

It does this dynamically per message.

---

## 📁 Project Structure

```
telegram-bot.py
personality.txt
.env
telegram-bot.log
```

---

## ⚙️ Configuration Constants

Inside `telegram-bot.py`:

* `MAX_HISTORY = 20` → Conversation memory length
* `WORDS_PER_MINUTE = 30` → Typing simulation speed
* `READ_DELAY_MIN/MAX` → Simulated reading delay
* `TYPING_ACTION_INTERVAL` → Telegram typing refresh rate

---

## 🛑 Stopping the Bot

Press:

```
Ctrl + C
```

---

## 💻 Prevent macOS from Sleeping

If you're running the bot on macOS and want to prevent your computer from going to sleep, use:

```bash
caffeinate -i python telegram-bot.py
```

This keeps the system awake while the bot is running.

---

## 🧾 Logs

All logs are written to:

```
telegram-bot.log
```

Console output is also enabled.

---

## 🚨 Troubleshooting

### Missing dependencies

Run:

```bash
pip install -r requirements.txt
```

### Network errors

* Check internet connection
* Ensure Telegram is not blocked
* Verify your bot token is correct

---

## 🛡 Security Notes

* Never commit your `.env` file
* If keys are exposed, immediately rotate them
* Use a private repo if testing

---

## 📄 License

MIT (or add your preferred license)

---

Built for fun, realism, and that “this might actually be a human” vibe 😎

---

