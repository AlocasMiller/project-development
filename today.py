from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
import json

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

def calculate_total_payment(file_path='students.json'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            students = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

    total = 0
    for student in students:
        price = student.get('payment', 0)
        if isinstance(price, (int, float)):
            total += price
    return total

def create_student_messages_with_buttons():
    students = load_students()
    if not students:
        return [("Сегодня занятий нет.", None)]

    messages_with_markup = []

    for i, student in enumerate(students, 1):
        time_str = student.get('time', '00:00')
        name = student.get('name', 'Без имени')
        subject = student.get('subject', 'Неизвестный предмет')
        materials_link = student.get('materials_link', None)

        text = f"{i}. {time_str} — {name} ({subject})"

        try:
            lesson_time = datetime.strptime(time_str, "%H:%M")
            call_time = (lesson_time - timedelta(minutes=15)).strftime("%H:%M")
        except ValueError:
            call_time = "??:??"

        # Формируем кнопки в 2 ряда по 2 кнопки
        row1 = []
        if materials_link:
            row1.append(InlineKeyboardButton(text="📝 Материалы", url=materials_link))
        else:
            row1.append(InlineKeyboardButton(text="📝 Материалы", callback_data="no_materials"))

        row1.append(InlineKeyboardButton(text=f"📞 Звонок в {call_time}", callback_data=f"call_{i}"))

        row2 = [
            InlineKeyboardButton(text="⏱️ Перенести", callback_data=f"reschedule_{i}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
        ]

        markup = InlineKeyboardMarkup([row1, row2])

        messages_with_markup.append((text, markup))

    return messages_with_markup

