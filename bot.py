import telebot
from telebot import types

TOKEN = "8718208942:AAFyH8qxm9_9Zb-NAalEf-g0WaQ8kn_9-N0"
CLOSED_GROUP_ID = -1003955950402

bot = telebot.TeleBot(TOKEN)

# Храним ID последнего сообщения бота для каждого пользователя (чтобы потом удалить)
last_bot_message = {}

# ==================== БАЗА ЗНАНИЙ ====================
knowledge = {
    "нет карты памяти": "Если подсвечивается желтым — это не ошибка, а рекомендация. Просто вставь карту памяти и пройдёт.",
    "ошибка автопроверки esc 4": "Если мотор при подключении АКБ прокручивается, то осматривай его детальнее — не попало ли в него что-то. Если ничего нет — на замену мотора или отправляй в ремонт.",
    "ошибка автопроверки esc 3": "Если мотор при подключении АКБ прокручивается, то осматривай его детальнее — не попало ли в него что-то. Если ничего нет — на замену мотора или отправляй в ремонт.",
    "ошибка автопроверки esc 2": "Если мотор при подключении АКБ прокручивается, то осматривай его детальнее — не попало ли в него что-то. Если ничего нет — на замену мотора или отправляй в ремонт.",
    "ошибка автопроверки esc 1": "Если мотор при подключении АКБ прокручивается, то осматривай его детальнее — не попало ли в него что-то. Если ничего нет — на замену мотора или отправляй в ремонт.",
}

# ==================== КНОПКИ ====================
def get_start_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Погнали разбираться", callback_data="start_dialog")
    markup.add(btn)
    return markup

def get_end_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Я понял, пошёл работать", callback_data="end_dialog")
    markup.add(btn)
    return markup

# ==================== ОБРАБОТЧИКИ ====================
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type != 'private':
        return  # Бот отвечает только в личном чате с ним
    bot.send_message(
        message.chat.id,
        "Привет , братец! Я бот помощник.",
        reply_markup=get_start_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == "start_dialog")
def start_dialog(call):
    if call.message.chat.type != 'private':
        return
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="*Я помогаю в решении частых проблем в работе.*\n"
             "*Важно вводить в точности как на пульте.*\n"
             "В случае проблем пиши @Remzaa",
        parse_mode="Markdown"
    )
    msg = bot.send_message(
        call.message.chat.id,
        "Ниже пиши свою проблему:",
        reply_markup=get_end_keyboard()
    )
    last_bot_message[call.from_user.id] = msg.message_id

@bot.callback_query_handler(func=lambda call: call.data == "end_dialog")
def end_dialog(call):
    if call.message.chat.type != 'private':
        return
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    # Удаляем сообщение с кнопкой "Я понял, пошёл работать"
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass

    # Удаляем предыдущее сообщение бота (с ответом)
    if user_id in last_bot_message:
        try:
            bot.delete_message(chat_id, last_bot_message[user_id])
        except:
            pass
        last_bot_message.pop(user_id, None)

    # Показываем новое приветствие
    bot.send_message(
        chat_id,
        "Диалог завершён. Если что-то ещё понадобится — нажми /start",
        reply_markup=get_start_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.chat.type != 'private':
        return  # Бот реагирует ТОЛЬКО в личном чате с ботом, а не в закрытой группе!

    user_id = message.from_user.id
    text = message.text.lower().strip()

    # Проверка подписки
    try:
        member = bot.get_chat_member(CLOSED_GROUP_ID, user_id)
        if member.status not in ['member', 'administrator', 'creator']:
            bot.reply_to(message, "Чтобы задавать вопросы, нужно быть участником закрытой группы @ZonaDJI.")
            return
    except:
        bot.reply_to(message, "Ошибка проверки подписки.")
        return

    if text in knowledge:
        msg = bot.reply_to(message, knowledge[text], reply_markup=get_end_keyboard())
        last_bot_message[user_id] = msg.message_id
    else:
        msg = bot.reply_to(message, "Извини, я пока не знаю ответ на этот вопрос. Для скорейшего обучения напиши моему хозяину @Remzaa.", reply_markup=get_end_keyboard())
        last_bot_message[user_id] = msg.message_id

print("Бот запущен...")
bot.polling()
