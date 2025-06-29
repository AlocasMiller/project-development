from datetime import datetime

from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from today import count_today_students, load_students
from study_plans import show_study_plans, add_study_plan_prompt, handle_text, user_states
from settings_section import show_settings, handle_document, user_states
from finance import show_finance_menu, ask_period, handle_text as finance_handle_text, user_states as finance_states, \
    show_debts, show_statistics

students = load_students()

async def show_schedule_buttons(update, context, period="today"):
    query = update.callback_query
    await query.answer()
    await query.message.delete()

    today = datetime.now()
    filtered_students = []

    for student in students:
        lesson_date = datetime.strptime(f"{student['date']}.{datetime.now().year}", "%d.%m.%Y")

        if period == "today" and lesson_date.date() == today.date():
            filtered_students.append(student)
        elif period == "3days" and 0 <= (lesson_date.date() - today.date()).days <= 3:
            filtered_students.append(student)
        elif period == "week" and 0 <= (lesson_date.date() - today.date()).days <= 7:
            filtered_students.append(student)

    if not filtered_students:
        await query.message.chat.send_message("Ученики за выбранный период не найдены.")
        return

    buttons = [
        [InlineKeyboardButton(student['name'] + " " + student['date'] + " " + student['time'], callback_data=f"student_{students.index(student)}")]
        for student in filtered_students
    ]
    buttons.append([InlineKeyboardButton("🔙 Отмена", callback_data="cancel")])

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text="Выберите ученика:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    data = query.data
    print(f"НАЖАТА КНОПКА: {data}")

    if data == "view_schedule":
        buttons = [
            [InlineKeyboardButton("📅 Сегодня", callback_data="period_today")],
            [InlineKeyboardButton("📆 Следующие 3 дня", callback_data="period_3days")],
            [InlineKeyboardButton("🗓 Следующая неделя", callback_data="period_week")],
            [InlineKeyboardButton("🔙 Отмена", callback_data="cancel")]
        ]
        markup = InlineKeyboardMarkup(buttons)

        await query.message.delete()

        await query.message.chat.send_message("Выберите период для просмотра расписания:", reply_markup=markup)

    elif data == "share_schedule":
        share_link = "https://example.com/schedule"  # Здесь может быть динамическая ссылка

        buttons = [
            [InlineKeyboardButton("🔙 Отмена", callback_data="cancel")]
        ]

        markup = InlineKeyboardMarkup(buttons)
        await query.message.delete()
        await query.message.chat.send_message(
            f"Скопируй ссылку и вставь в своё приложение календаря:\n{share_link}",
            reply_markup=markup
        )

    elif data == "period_today":
        await show_schedule_buttons(update, context, period="today")

    elif data == "period_3days":
        await show_schedule_buttons(update, context, period="3days")

    elif data == "period_week":
        await show_schedule_buttons(update, context, period="week")


    elif data.startswith("student_"):
        index = int(data.split("_")[1])
        student = students[index]
        name = student['name']
        date = student['date']
        time = student['time']
        payment = student['payment']
        description = student['description'] if student['description'] else "Нет"
        status = "✅ Оплачено" if student['status_payment'] else "❌ Не оплачено"

        text = (
            f"<b>👨‍🎓 {name}</b>\n"
            f"📅 Дата: {date}\n"
            f"⏰ Время: {time}\n"
            f"💸 Стоимость: {payment} руб.\n"
            f"📝 Заметка: {description}\n"
            f"💳 Статус: {status}"
        )

        buttons = [
            [InlineKeyboardButton("📄 Теория", url=student['materials_link'])],
            [InlineKeyboardButton("📚 Домашняя работа", url=student['homework_link'])],
            [InlineKeyboardButton("🔄 Перенести", callback_data=f"reschedule_{index}")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_lesson_{index}")],
            [InlineKeyboardButton("✏️ Изменить", callback_data=f"edit_{index}")],
            [InlineKeyboardButton("🔙 Отмена", callback_data="cancel")]
        ]

        await query.answer()
        await query.message.delete()
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="HTML"
        )


    elif data == "cancel":
        await query.answer()
        if user_id in user_states:
            user_states.pop(user_id)
        # Удаляем меню с кнопками отмены
        await query.message.delete()

        # Удаляем все сообщения расписания, если они есть
        chat_id = query.message.chat.id
        msg_ids = context.user_data.get('schedule_messages', [])
        for message_id in msg_ids:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            except:
                pass  # Сообщение могло быть уже удалено

        # Очищаем список сообщений после удаления
        context.user_data['schedule_messages'] = []

        # Отправляем главное меню
        await query.message.chat.send_message("Выберите действие:", reply_markup=main_markup)

    elif data.startswith("call_"):
        student_num = data.split("_")[1]
        await query.edit_message_text(f"Напоминание: звонок студенту #{student_num} за 15 минут до занятия.", reply_markup=None)

    elif data.startswith("reschedule_"):
        student_num = data.split("_")[1]
        await query.edit_message_text(f"Функция переноса для студента #{student_num} будет добавлена позже.", reply_markup=None)

    elif data == "no_materials":
        await query.edit_message_text("Для этого ученика материалы не доступны.", reply_markup=None)

    elif data == "add_study_plan":
        await add_study_plan_prompt(update, context)

    elif query.data == "finance_debts":
        await show_debts(update, context)

    elif query.data == "remind_all":
        await query.message.reply_text("Всем отправлены напоминания о задолженностях.")

    elif query.data.startswith("remind_"):
        name = query.data.replace("remind_", "")
        await query.message.reply_text(f"Отправлено напоминание для {name}.")

    elif data == "finance_stats":
        await ask_period(update, context, mode="stats")

    elif data == "finance_forecast":
        await ask_period(update, context, mode="forecast")

    elif data in ["period_month", "period_3months", "period_halfyear", "period_year", "period_alltime"]:
        mode = context.user_data.get("finance_mode")  # Сохраняем заранее выбранный режим (stats или forecast)
        await show_statistics(update,"12.12.12", "12.12.12")
    elif data == "period_custom":
        await ask_period(update, context)

main_keyboard = [
    ['📅 Расписание'],
    ['👨‍🎓 Ученики и группы'],
    ['💸 Финансы'],
    ['📊 Учебные планы'],
    ['⚙️ Настройка']
]
main_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = count_today_students()
    text = f"Привет! Сегодня учеников: {count}\nВыберите действие:"
    await update.message.reply_text(text, reply_markup=main_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_states.get(user_id) == "waiting_for_study_plan_link":
        await handle_text(update, context)
        return

    if finance_states.get(user_id):
        await finance_handle_text(update, context)
        return

    if text == '📅 Расписание':
        buttons = [
            [InlineKeyboardButton("👀 Посмотреть", callback_data="view_schedule")],
            [InlineKeyboardButton("📤 Поделиться", callback_data="share_schedule")]
        ]
        markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Что ты хочешь сделать?", reply_markup=markup)
    elif text == "📊 Учебные планы":
        await show_study_plans(update, context)
    elif text == "⚙️ Настройка":
        await show_settings(update, context)
    elif text == "💸 Финансы":
        await show_finance_menu(update, context)
    elif text in ['👨‍🎓 Ученики и группы']:
        await update.message.reply_text(f"Вы нажали: {text}\n(Здесь будет логика для этого раздела)", reply_markup=main_markup)
    else:
        await update.message.reply_text("Я не понял, выберите действие:", reply_markup=main_markup)

if __name__ == '__main__':
    app = ApplicationBuilder().token('7511367039:AAEHApD7LOeuCq2-_Cb8jBXuZeYlIKBIe1I').build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("Бот запущен")
    app.run_polling()
