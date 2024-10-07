import telebot
import datetime
import time
import threading
import random
import logging

# Логирование действий
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = telebot.TeleBot('PLACE TOKEN HERE')

# Хранение напоминаний пользователей
user_reminders = {}

# Команда /start
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    bot.reply_to(message, """Привет! Я чат бот, который будет напоминать тебе пить водичку!
    С моей помощью ты можешь:
    /fact - узнать что-то новое о воде
    /my_reminders - просмотреть список напоминаний
    /set_reminder - добавить напоминание
    /remove_reminder - удалить напоминание""")

    # Если пользователь новый, инициализируем список с напоминаниями по умолчанию
    if chat_id not in user_reminders:
        user_reminders[chat_id] = ["09:00", "14:00", "18:00"]  # Стандартные напоминания
        reminder_thread = threading.Thread(target=send_reminders, args=(chat_id,))
        reminder_thread.start()

# Команда /fact
@bot.message_handler(commands=['fact'])
def fact_message(message):
    facts = [
        "*Вода на Земле может быть старше самой Солнечной системы*: Исследования показывают, что от 30% до 50% воды в наших океанах возможно присутствовала в межзвездном пространстве еще до формирования Солнечной системы около 4,6 миллиарда лет назад.",
        "*Горячая вода замерзает быстрее холодной*: Это явление известно как эффект Мпемба. Под определенными условиями горячая вода может замерзать быстрее, чем холодная, хотя ученые до сих пор полностью не разгадали механизм этого процесса.",
        "*Больше воды в атмосфере, чем во всех реках мира*: Объем водяного пара в атмосфере Земли в любой момент времени превышает объем воды во всех реках мира вместе взятых.",
        "*Человеческое тело состоит примерно на 60% из воды*: Каждый орган и ткань организма требует воды для правильного функционирования. Мозг и сердце состоят на 73% из воды, а легкие — примерно на 83%.",
        "*Замороженная вода (лед) менее плотная, чем жидкая вода*: Это единственная известная жидкость, которая в твердом состоянии имеет меньшую плотность, чем в жидком. Это объясняет, почему лед плавает на поверхности воды.",
        "*На планете больше пресной воды заморожено в ледниках*: Более 68% пресной воды на Земле находится в ледниках и ледяных покровах, особенно в Антарктиде и Гренландии.",
        "*Вода может существовать в трёх состояниях одновременно*: При определённых условиях температуры и давления, известных как тройная точка, вода может одновременно существовать в виде льда, воды и пара.",
        "*Вода не имеет калорий*: Вода является единственным напитком, который не содержит калорий, сахара или жира."
    ]
    random_fact = random.choice(facts)
    bot.reply_to(message, f'Лови факт о воде:\n{random_fact}', parse_mode="Markdown")

# Команда /set_reminder — установка напоминаний
@bot.message_handler(commands=['set_reminder'])
def set_reminder(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите время в формате HH:MM для установки напоминания")

    # Создаём временный обработчик для ожидания ввода времени
    bot.register_next_step_handler(message, get_time_input)

# Функция для получения времени от пользователя
def get_time_input(message):
    chat_id = message.chat.id
    time_input = message.text.strip()

    try:
        # Проверяем корректность введённого времени
        datetime.datetime.strptime(time_input, '%H:%M')

        # Добавляем напоминание пользователю
        if chat_id in user_reminders:
            user_reminders[chat_id].append(time_input)
        else:
            user_reminders[chat_id] = [time_input]

        bot.send_message(chat_id, f"Напоминание установлено на {time_input}")
    except ValueError:
        bot.send_message(chat_id, "Неверный формат времени. Введите снова в формате HH:MM")
        bot.register_next_step_handler(message, get_time_input)

# Команда /my_reminders — просмотр всех напоминаний
@bot.message_handler(commands=['my_reminders'])
def my_reminders(message):
    chat_id = message.chat.id
    reminders = user_reminders.get(chat_id, [])  # Получаем напоминания пользователя
    if reminders:
        reminders_str = "\n".join(reminders)
        bot.reply_to(message, f"Ваши напоминания:\n{reminders_str}")
    else:
        bot.reply_to(message, "У вас нет установленных напоминаний.")

# Команда /remove_reminder — удаление напоминаний
@bot.message_handler(commands=['remove_reminder'])
def remove_reminder(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите время напоминания, которое хотите удалить (формат HH:MM)")

    # Создаём временный обработчик для ожидания ввода времени на удаление
    bot.register_next_step_handler(message, delete_time_input)

# Функция для удаления напоминания
def delete_time_input(message):
    chat_id = message.chat.id
    time_input = message.text.strip()

    if chat_id in user_reminders and time_input in user_reminders[chat_id]:
        user_reminders[chat_id].remove(time_input)
        bot.send_message(chat_id, f"Напоминание на {time_input} удалено")
    else:
        bot.send_message(chat_id, "Такого напоминания нет.")
        bot.register_next_step_handler(message, delete_time_input)

# Функция для отправки напоминаний
def send_reminders(chat_id):
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        reminders = user_reminders.get(chat_id, [])

        if now in reminders:
            bot.send_message(chat_id, "Напоминание - выпей стакан воды!")

        time.sleep(60)  # Проверка каждые 60 секунд

# Запуск бота
bot.polling(none_stop=True)
