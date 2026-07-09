TOKEN = "ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН"
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os
import random
import json
from datetime import datetime, timedelta

TOKEN = "8739778187:AAHoaQ9_Aqtigf8Jyq68xM2mZKQ67Ax1CvE"
CARDS_FOLDER = "/sdcard/Download/memes"
DATA_FILE = "users_data.json"

COOLDOWN_HOURS = 12

keyboard = [["Тянуть карту"]]
reply_markup = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True
)


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


users_data = load_data()


def can_draw(user_id):
    if user_id not in users_data:
        return True

    if "last_draw" not in users_data[user_id]:
        return True

    last_time = datetime.fromisoformat(
        users_data[user_id]["last_draw"]
    )

    return datetime.now() >= last_time + timedelta(hours=COOLDOWN_HOURS)


def get_random_card():
    files = os.listdir(CARDS_FOLDER)

    images = [
        f for f in files
        if f.lower().endswith(
            (".jpg", ".jpeg", ".png", ".webp")
        )
    ]

    if not images:
        return None

    return os.path.join(
        CARDS_FOLDER,
        random.choice(images)
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет ✨\n"
        "Нажми кнопку «Тянуть карту» 🔮",
        reply_markup=reply_markup
    )


async def draw_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if not can_draw(user_id):
        await update.message.reply_text(
            "Карты говорят: приходи позже 🔮"
        )
        return

    card_path = get_random_card()

    if not card_path:
        await update.message.reply_text(
            "Карт не найдено 😢"
        )
        return

    with open(card_path, "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption="Твоя карта на сегодня 🔮"
        )

    users_data[user_id] = {
        "last_draw": datetime.now().isoformat()
    }

    save_data(users_data)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Тянуть карту":
        await draw_card(update, context)


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

print("Бот запущен")

app.run_polling()
