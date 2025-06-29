import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def count_today_students(file_path='students.json'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            students = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

    return len(students)

def load_students(file_path='students.json'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            students = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    return students

def load_student_for_list():
    with open("student_list.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Отправка списка учеников
async def show_students(update, context):
    students = load_student_for_list()

    buttons = [[InlineKeyboardButton("➕ Добавить", callback_data="add_student")]]

    # Список учеников
    for idx, student in enumerate(students):
        buttons.append([InlineKeyboardButton(student["name"], callback_data=f"students_list_{idx}")])

    # Кнопка "Назад"
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_groups_menu")])

    await update.callback_query.message.edit_text(
        "Список учеников:\nНажмите на ученика чтобы посмотреть или изменить информацию о нем",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_students_callback(update, context, callback_data):
    students = load_student_for_list()

    if callback_data.startswith("students_list_"):
        idx = int(callback_data.split("_")[-1])
        student = students[idx]

        text = (
            f"👤 ФИО: {student['name']}\n"
            f"📱 Телефон: {student.get('phone', 'Не указано')}\n"
            f"👨‍👩‍👧 Родитель: {student.get('parent', 'Не указано')}"
        )

        buttons = [
            [InlineKeyboardButton("🔄 Обновить", callback_data=f"students_update_{idx}"),
             InlineKeyboardButton("🗑️ Удалить", callback_data=f"students_delete_{idx}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="students_back_to_list")]
        ]

        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    elif callback_data == "students_back_to_list":
        await show_students(update, context)

    elif callback_data.startswith("students_delete_"):
        idx = int(callback_data.split("_")[-1])
        deleted_student = students.pop(idx)

        save_students(students)

        await update.callback_query.message.edit_text(
            f"✅ Ученик {deleted_student['name']} удалён.",
        )
        await show_students(update, context)

    elif callback_data.startswith("students_update_"):
        await update.callback_query.message.edit_text(
            "Отправьте новое ФИО ученика:"
        )

def save_students(students):
    with open("students.json", "w", encoding="utf-8") as file:
        json.dump(students, file, ensure_ascii=False, indent=2)