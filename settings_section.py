import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

STATIC_SETTINGS_GUIDE_LINK = "https://docs.google.com/document/d/1jbLpnreexrBDGiHLfmGho1RgdU1iaxDQJFO2NAMYpG0/edit?tab=t.0#heading=h.396gwqj7im4s"

user_states = {}

# Показ меню настроек
async def show_settings(update, context):
    user_id = update.message.from_user.id
    user_states[user_id] = "waiting_for_config_file"

    buttons = [
        [InlineKeyboardButton("📄 Как создать конфигурационный файл?", url=STATIC_SETTINGS_GUIDE_LINK)],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="cancel")]
    ]

    await update.message.reply_text(
        "Пришлите файл конфигурации или воспользуйтесь инструкцией:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Обработка присланного файла
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_states.get(user_id) != "waiting_for_config_file":
        return

    document = update.message.document
    if not document:
        await update.message.reply_text("Пожалуйста, отправьте именно файл.")
        return

    # Сохраняем файл
    file = await context.bot.get_file(document.file_id)
    file_path = f"configs/{document.file_name}"
    await file.download_to_drive(file_path)

    # Проверка файла
    if validate_file(file_path):
        await update.message.reply_text(f"Файл {document.file_name} успешно получен и прошёл проверку ✅")
    else:
        os.remove(file_path)

        buttons = [
            [InlineKeyboardButton("📄 Как создать конфигурационный файл?", url=STATIC_SETTINGS_GUIDE_LINK)],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="cancel")]
        ]

        await update.message.reply_text(
            "Файл составлен неверно. Попробуйте еще раз:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

# Простейшая проверка файла (например, проверяем, что он .json и начинается с { )
def validate_file(file_path):
    if not file_path.endswith(".json"):
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content.startswith("{") and content.endswith("}"):
                return True
    except Exception:
        return False

    return False
