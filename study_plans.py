import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

STATIC_GUIDE_LINK = "https://docs.google.com/document/d/1jbLpnreexrBDGiHLfmGho1RgdU1iaxDQJFO2NAMYpG0/edit?tab=t.0#heading=h.396gwqj7im4s"

user_states = {}

# Загрузка учебных планов из файла
def load_study_plans():
    with open("study_plans.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Отправка меню с учебными планами
async def show_study_plans(update, context):
    plans = load_study_plans()

    buttons = []

    for idx, plan in enumerate(plans):
        buttons.append([InlineKeyboardButton(f"План {idx + 1}", url=plan["link"])])

    buttons.append([InlineKeyboardButton("➕ Добавить", callback_data="add_study_plan")])
    buttons.append([InlineKeyboardButton("🔙 Отмена", callback_data="cancel")])

    await update.message.reply_text(
        "Учебные планы:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def add_study_plan_prompt(update, context):
    user_id = update.callback_query.from_user.id
    user_states[user_id] = "waiting_for_study_plan_link"

    buttons = [
        [InlineKeyboardButton("📄 Как создать учебный план?", url=STATIC_GUIDE_LINK)],
        [InlineKeyboardButton("🔙 Отмена", callback_data="cancel")]
    ]

    await update.callback_query.message.delete()
    await update.callback_query.message.chat.send_message(
        "Отправьте ссылку на учебный план в приложении Google Sheets:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_text(update, context):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_states.get(user_id) == "waiting_for_study_plan_link":
        # Обработка ссылки
        if validate_link(text):
            save_study_plan(text)
            user_states.pop(user_id)
            buttons = [
                [InlineKeyboardButton("🏠 В главное меню", callback_data="cancel")]
            ]
            await update.message.reply_text(
                "Учебный план успешно добавлен!",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            buttons = [
                [InlineKeyboardButton("📄 Как создать учебный план?", url=STATIC_GUIDE_LINK)],
                [InlineKeyboardButton("🔙 Отмена", callback_data="cancel")]
            ]
            await update.message.reply_text(
                "Учебный план составлен неверно. Попробуйте еще раз:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

def validate_link(link):
    return link.startswith("https://docs.google.com/spreadsheets/")

def save_study_plan(link):
    with open("study_plans.json", "r", encoding="utf-8") as file:
        plans = json.load(file)

    plans.append({"link": link})

    with open("study_plans.json", "w", encoding="utf-8") as file:
        json.dump(plans, file, ensure_ascii=False, indent=2)