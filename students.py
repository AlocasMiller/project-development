from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, filters

NAME, DESCRIPTION, PHONE = range(3)

async def start_create_student(update, context):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Введите имя ученика:")
    return NAME

async def get_name(update, context):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Введите краткое описание ученика:")
    return DESCRIPTION

async def get_description(update, context):
    context.user_data['description'] = update.message.text

    contact_button = KeyboardButton("📱 Отправить номер телефона", request_contact=True)
    cancel_button = KeyboardButton("❌ Отменить")

    reply_markup = ReplyKeyboardMarkup([[contact_button], [cancel_button]], resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text("Пожалуйста, отправьте номер телефона ученика или нажмите ❌ Отменить:", reply_markup=reply_markup)
    return PHONE

async def get_phone(update, context):
    if update.message.contact:
        phone_number = update.message.contact.phone_number
        context.user_data['phone'] = phone_number

        name = context.user_data['name']
        description = context.user_data['description']

        # сбор json
        student = {
            "name": name,
            "description": description,
            "phone": phone_number,
        }

        await update.message.reply_text(
            f"Ученик создан:\n",
            f"Имя: {name}\n"
            f"Описание: {description}\n"
            f"Телефон: {phone_number}",
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text("Пожалуйста, используйте кнопку для отправки номера телефона или нажмите ❌ Отменить.")
        return PHONE

conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_create_student, pattern='^create_student$')],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
        PHONE: [MessageHandler(filters.CONTACT, get_phone)],
    },
    fallbacks=[],
)
