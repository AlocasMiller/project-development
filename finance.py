import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

user_states = {}

async def show_finance_menu(update, context):
    buttons = [
        [InlineKeyboardButton("💰 Задолженности", callback_data="finance_debts")],
        [InlineKeyboardButton("📊 Статистика", callback_data="finance_stats")],
        [InlineKeyboardButton("📈 Прогноз", callback_data="finance_forecast")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="cancel")]
    ]

    await update.message.reply_text(
        "Финансовая аналитика:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def load_debts():
    with open("debts.json", "r", encoding="utf-8") as file:
        return json.load(file)

async def show_debts(update, context):
    debts_data = load_debts()
    total_debt = debts_data["total_debt"]

    # Сообщение с общей суммой и кнопкой
    text = f"<b>Общая сумма задолженностей:</b> {total_debt} ₽"
    buttons = [[InlineKeyboardButton("🔔 Напомнить всем", callback_data="remind_all")]]
    markup = InlineKeyboardMarkup(buttons)

    await update.callback_query.message.edit_text(
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )

    # Отправка отдельного блока на каждого студента
    for student in debts_data["students"]:
        student_text = f"<b>{student['name']}, {student['days_overdue']} дн.</b>\n"
        for payment in student["payments"]:
            student_text += f"{payment['date']}: {payment['amount']} ₽\n"

        student_buttons = [[InlineKeyboardButton(f"🔔 Напомнить: {student['name']}", callback_data=f"remind_{student['name']}")]]
        student_markup = InlineKeyboardMarkup(student_buttons)

        await update.effective_chat.send_message(
            text=student_text,
            reply_markup=student_markup,
            parse_mode="HTML"
        )

# Выбор периода
async def ask_period(update, context, mode):
    user_id = update.callback_query.from_user.id
    user_states[user_id] = {"state": "choose_period", "mode": mode}

    buttons = [
        [InlineKeyboardButton("Месяц", callback_data="period_month")],
        [InlineKeyboardButton("Три месяца", callback_data="period_3months")],
        [InlineKeyboardButton("Полгода", callback_data="period_6months")],
        [InlineKeyboardButton("Год", callback_data="period_year")],
        [InlineKeyboardButton("За все время", callback_data="period_all")],
        [InlineKeyboardButton("Свой период", callback_data="period_custom")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="cancel")]
    ]

    await update.callback_query.message.edit_text(
        "Выберите период:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# Ввод начальной даты
async def ask_start_date(update, context):
    user_id = update.callback_query.from_user.id
    user_states[user_id]["state"] = "waiting_start_date"

    await update.callback_query.message.edit_text(
        "Введите дату начала периода в формате DD.MM.YYYY:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="cancel")]])
    )


# Ввод конечной даты
async def ask_end_date(update, context):
    user_id = update.message.from_user.id
    user_states[user_id]["state"] = "waiting_end_date"

    await update.message.reply_text(
        "Введите дату окончания периода в формате DD.MM.YYYY:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="cancel")]])
    )


# Обработка текстового ввода дат
async def handle_text(update, context):
    user_id = update.message.from_user.id
    state_data = user_states.get(user_id)

    if not state_data:
        return

    if state_data["state"] == "waiting_start_date":
        state_data["start_date"] = update.message.text.strip()
        await ask_end_date(update, context)

    elif state_data["state"] == "waiting_end_date":
        state_data["end_date"] = update.message.text.strip()
        mode = state_data["mode"]
        start = state_data["start_date"]
        end = state_data["end_date"]

        if mode == "stats":
            await show_statistics(update, context, start, end)
        else:
            await show_forecast(update, context, start, end)

        user_states.pop(user_id, None)


# Показ статистики
async def show_statistics(update, start, end):
    await update.callback_query.message.reply_text(
        f"<b>Статистика за период:</b> {start} - {end}\n"
        f"Доход: 12345 ₽\n"
        f"Проведено занятий: 50\n"
        f"Потрачено часов: 100\n"
        f"Количество учеников: 30\n"
        f"Отмененные занятия: 5\n"
        f"ключ: значение",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="cancel")]])
    )


# Показ прогноза
async def show_forecast(update, start, end):
    await update.callback_query.message.reply_text(
        f"<b>Прогноз на период:</b> {start} - {end}\n"
        f"Доход: 15000 ₽\n"
        f"Проведено занятий: 60\n"
        f"Потрачено часов: 120\n"
        f"Количество учеников: 35\n"
        f"Отмененные занятия: 3\n"
        f"ключ: значение",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="cancel")]])
    )
