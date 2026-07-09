from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os
import random
import json
from datetime import datetime, timedelta

TOKEN = os.getenv("TELEGRAM_TOKEN")

CARDS_FOLDER = "memes"
DATA_FILE = "users_data.json"

COOLDOWN_HOURS = 12

keyboard = [["Тянуть карту"]]
reply_markup = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True
)


def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 🎴\nНажми кнопку, чтобы получить карту.",
        reply_markup=reply_markup
    )


async def get_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    users = load_users()

    now = datetime.now()

    if user_id in users:
        last_time = datetime.fromisoformat(users[user_id])
        if now - last_time < timedelta(hours=COOLDOWN_HOURS):
            await update.message.reply_text(
                "⏳ Ты уже тянул карту. Попробуй позже."
            )
            return

    if not os.path.exists(CARDS_FOLDER):
        await update.message.reply_text(
            "Папка с картами пока пустая."
        )
        return

    cards = [
        file for file in os.listdir(CARDS_FOLDER)
        if file.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if not cards:
        await update.message.reply_text(
            "Карт пока нет."
        )
        return

    card = random.choice(cards)

    users[user_id] = now.isoformat()
    save_users(users)

    with open(os.path.join(CARDS_FOLDER, card), "rb") as photo:
        await update.message.reply_photo(photo=photo)


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Тянуть карту":
        await get_card(update, context)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
