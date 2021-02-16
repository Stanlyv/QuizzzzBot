import telebot
from telebot import types
import config
import sqlite3 as sq
import random
from datetime import datetime

bot = telebot.TeleBot(config.Token)


# начало
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """Ну здарова, отец.
Тут ты сможешь отвечать на каверзные вопросы, участвовать в викторинах и многое другое. Планируется расширение вопросной базы по разным темам. Не теряйся :)""")
    bot.send_message(message.chat.id, "Если готов к вопросикам, то пиши /question")
    checkadd(message)


#   наличие юзера в БД и записываем его, если его там нет
def checkadd(message):
    with sq.connect("quiz.db") as config:
        username, first_name, last_name = message.chat.username, message.chat.first_name,message.chat.last_name
        username = "'{}'".format(username) if username is not None else "Null"
        first_name = "'{}'".format(first_name) if first_name is not None else "Null"
        last_name = "'{}'".format(last_name) if last_name is not None else "Null"
        print(username, first_name, last_name)
        cur = config.cursor()
        select_query = f"SELECT COUNT(id) FROM users WHERE user_id = {message.chat.id}"
        insert_query = f"INSERT INTO users (user_id, username, fisrt_name, last_name) VALUES ({message.chat.id},{username},{first_name},{last_name}) "
        cur.execute(select_query)
        res = cur.fetchall()
        if res[0][0] == 0:
            cur.execute(insert_query)
            print("добавили пользователя",message.chat.id, "в базу")
        else:
            print("пользователь",message.chat.id, "был в базе")
        cur.close()


# @bot.message_handler(func=lambda message: True)
random_num = 0
random_question_id = 0
all_category_name = []
category_data = ""


# выбираем категорию
@bot.message_handler(commands=['question'])
def choose_category(message):
    checkadd(message)
    with sq.connect("quiz.db") as config:
        cur = config.cursor()
        markup_inline = types.InlineKeyboardMarkup()
        select_all_category_name = "SELECT category_name FROM category"
        cur.execute(select_all_category_name)
        global all_category_name
        all_category_name = cur.fetchall()
        print("all_category_name: ", all_category_name)
        cur.close()
        for i in range(len(all_category_name)):
            item = types.InlineKeyboardButton(text=all_category_name[i][0], callback_data=f"category_{all_category_name[i][0]}")
            markup_inline.add(item)
        bot.send_message(message.chat.id, "Выберите категорию", reply_markup=markup_inline)
        # bot.register_next_step_handler(msg, answer_category)


# определяем, выбрал ли юзер категорию
@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def answer_category(call):
    call.data = call.data[9:]
    print("дошел до answer_category")
    print("call.data: ", call.data)
    print("call.message.text", call.message.text)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=(f"Вы выбрали {call.data}"), reply_markup=False)
    for i in range(len(all_category_name)):
        if call.data == all_category_name[i][0]:
            print("Сижу в цикле.all_category_name[i][0]: ", all_category_name[i][0])
            print("Сижу в цикле. call.data:", call.data)
            print("Сижу в цикле. call.message:", call.message)
            ask(call.message, all_category_name[i][0])
            return
    # следующие две строки не обязательны, ибо функция выполняет лишь действия с кнопок (хотя без кнопок выполняют, дичь)
    bot.send_message(call.message.chat.id, "Вы не выбрали категорию")
    choose_category(call.message)


# задаем вопрос
def ask(message, category_name):
    global category_data
    category_data = category_name
    print("дошел до ask")
    print("категория: ", category_data)
    print("message.chat.id:", message.chat.id)
    with sq.connect("quiz.db") as config:
        cur = config.cursor()

        # получаем список всех вопросов
        select_all_question_ids = f'''SELECT questions.id FROM questions
         INNER JOIN category ON questions.category_id = category.id
         WHERE category_name = "{category_data}"'''
        cur.execute(select_all_question_ids)
        all_question_ids = cur.fetchall()
        print("all_question_ids:", all_question_ids)

        # получаем список отвеченых вопросов текущего юзера
        select_done_question_ids = f"""SELECT question_id FROM answers WHERE user_id = {message.chat.id}"""
        cur.execute(select_done_question_ids)
        done_question_ids = cur.fetchall()
        print("done_question_ids:", done_question_ids)

        # вычитаем данные одного списка из другого
        not_done_question_ids_dirt = list(set(all_question_ids) - set(done_question_ids))
        not_done_question_ids = []
        for i in range(len(not_done_question_ids_dirt)):
            not_done_question_ids.append(not_done_question_ids_dirt[i][0])
        print("not_done_question_ids:", not_done_question_ids)
        print("len(not_done_question_ids):", len(not_done_question_ids))
        if len(not_done_question_ids) == 0:
            bot.send_message(message.chat.id,
                             "Ты ответил на все возможные вопросы в данной категории. Могу предложить обнулить твои результаты /reset. Либо жди новых вопросов и нажимай /question.")
            return

        # выбираем случайный номер вопроса
        global random_num
        random_num = random.randint(1, len(not_done_question_ids))
        global random_question_id
        random_question_id = not_done_question_ids[random_num - 1]
        select_new_question_id = f"""SELECT question FROM questions WHERE id = {random_question_id}"""
        cur.execute(select_new_question_id)
        question = cur.fetchall()
        bot.send_message(message.chat.id, question)

        cur.close()


# удаляем инфу пройденых вопросах юзера
@bot.message_handler(commands=['reset'])
def reset_question(message):
    checkadd(message)
    btns = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btns.add(types.KeyboardButton("Да"),types.KeyboardButton("Нет"))
    msg = bot.send_message(message.chat.id, "Ты уверен что хочешь удалить все свои ответы?", reply_markup=btns)
    bot.register_next_step_handler(msg, reset_stat)

def reset_stat(message):
    if message.text.lower() == "да":
        with sq.connect("quiz.db") as config:
            cur = config.cursor()
            remove_stats = f"""DELETE FROM answers WHERE user_id = {message.chat.id}"""
            cur.execute(remove_stats)

            bot.send_message(message.chat.id,
                             "Ну вот, ты удалил все свои достижения. Чтобы начать отвечать на вопросы, нажимай /question", reply_markup=types.ReplyKeyboardRemove())
            cur.close()
    elif message.text.lower() == "нет":
        bot.send_message(message.chat.id, "Нет, так нет. Выбирай вопросики :) /question")
        return
    else:
        reset_question(message)
        return

# блок с фидбеком к разработчику в два этапа: вызов функции -> взятие и передача сообщения
@bot.message_handler(commands=['feedback'])
def send_feedback(message):
    checkadd(message)
    print("message.chat.id: ", message.chat.id)
    msg = bot.send_message(message.chat.id, "Введите ваше сообщение разработчику. (Пока поддерживается лишь текст)")
    bot.register_next_step_handler(msg, feedback)


def feedback(message):
    feedback_text = f"""Username: {message.chat.username}
Name: {message.chat.first_name} 
Last name: {message.chat.last_name}
Date: {datetime.utcfromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')} 
↓↓↓↓↓↓↓"""
    # отсылаю в группу с ботами и мной
    bot.send_message(-581149603, feedback_text)
    bot.forward_message(-581149603, message.chat.id, message.id)
    bot.send_message(message.chat.id, "Ваше сообщение доставлено!")


@bot.message_handler(func=lambda message: True)
# получаем и обрабатываем ответ
def answer(message):
    checkadd(message)
    print("дошел до answer")
    print("category_data:", category_data)
    global random_num
    if random_num > 0:
        # вытаскиваем ответ с БД
        with sq.connect("quiz.db") as config:
            cur = config.cursor()
            select_category_id = f'SELECT id FROM category WHERE category_name = "{category_data}"'
            cur.execute(select_category_id)
            category_id = cur.fetchall()
            print("category_id: ", category_id)
            select_query = f"""SELECT answer FROM questions WHERE id = {random_question_id}"""
            cur.execute(select_query)
            answer = cur.fetchall()
            flag = True
            while flag:
                if message.text.lower() == answer[0][0].lower():

                    # вставили пометку в бд, что игрок ответил на данный вопрос
                    insert_query = f"INSERT INTO answers (user_id, question_id, question_type) VALUES ({message.chat.id}, {random_question_id}, {category_id[0][0]}) "
                    cur.execute(insert_query)

                    bot.send_message(message.chat.id, "Молодец, следующий вопрос:")
                    flag = False
                    random_num = 0
                else:
                    bot.send_message(message.chat.id,
                                     "Не верно. Глянь, правильно ли ты написал ответ. Если не справляешься, можешь выбрать новый вопрос. /question")
                    return
            cur.close()
        random_num = 0
        ask(message, category_data)
        return
    else:
        bot.send_message(message.chat.id, "Ты еще не получил вопрос, дружочек. Тыкай /question.")
        return


bot.polling(none_stop=True)
