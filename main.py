import telebot
import config
import sqlite3 as sq
import random

# Подключение к БД
# with sq.connect("config.py") as config:
#     cur = config.cursor()
# Выполнение SQL запроса в БД
#     query = """
# #
# #     """
#     cur.execute(query)

bot = telebot.TeleBot(config.Token)

#проверяем наличие юзера в БД и записываем его, если его там нет
def checkadd(chat_id):
    with sq.connect("quiz.db") as config:
        cur = config.cursor()

        select_query = f"""SELECT COUNT(id) FROM users
        WHERE user_id = {chat_id}
        """

        insert_query = f"""INSERT INTO users (user_id)
        VALUES ({chat_id})"""

        cur.execute(select_query)
        res = cur.fetchall()
        if res[0][0] == 0:
            cur.execute(insert_query)
        else:
            print("не ноль, братан")
        cur.close()

#начало
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """Ну здарова, отец.
Тут ты сможешь отвечать на каверзные вопросы, участвовать в викторинах и многое другое. Планируется расширение вопросной базы по разным темам. Не теряйся :)""")
    bot.send_message(message.chat.id, "Если готов к вопросикам, то пиши /question")
    checkadd(message.chat.id)


# @bot.message_handler(func=lambda message: True)
random_num = 0
random_question_id = 0


@bot.message_handler(commands=['question'])
#задаем вопрос
def ask(message):

    with sq.connect("quiz.db") as config:
        cur = config.cursor()
#получаем список всех вопросов
        select_all_question_ids = f"""SELECT id FROM questions"""
        cur.execute(select_all_question_ids)
        all_question_ids = cur.fetchall()
        print("all_question_ids:", all_question_ids)
#получаем список отвеченых вопросов текущего юзера
        select_done_question_ids = f"""SELECT question_id FROM answers WHERE user_id = {message.chat.id}"""
        cur.execute(select_done_question_ids)
        done_question_ids = cur.fetchall()
        print("done_question_ids:", done_question_ids)
#вычитаем данные одного списка из другого
        not_done_question_ids_dirt = list(set(all_question_ids) - set(done_question_ids))
        not_done_question_ids =[]
        for i in range(len(not_done_question_ids_dirt)):
            not_done_question_ids.append(not_done_question_ids_dirt[i][0])
        print("not_done_question_ids:", not_done_question_ids)
        print("len(not_done_question_ids):", len(not_done_question_ids))
        if len(not_done_question_ids) == 0:
            bot.send_message(message.chat.id, "Ты ответил на все возможные вопросы.Могу предложить обнулить твои результаты /reset. Либо жди новых вопросов и нажимай /question.")
            return
# выбираем случайный номер вопроса
        global random_num
        random_num = random.randint(1, len(not_done_question_ids))
        global random_question_id
        random_question_id = not_done_question_ids[random_num-1]
        select_new_question_id = f"""SELECT question FROM questions WHERE id = {random_question_id}"""
        cur.execute(select_new_question_id)
        question = cur.fetchall()
        bot.send_message(message.chat.id, question)

        cur.close()

#удаляем инфу пройденых вопросах юзера
@bot.message_handler(commands=['reset'])
def reset_stat(message):
    with sq.connect("quiz.db") as config:
        cur = config.cursor()
        remove_stats = f"""DELETE FROM answers WHERE user_id = {message.chat.id}"""
        cur.execute(remove_stats)

        bot.send_message(message.chat.id, "Ну вот, ты удалил все свои достижения. Чтобы начать отвечать на вопросы, нажимай /question")

        cur.close()
@bot.message_handler(func=lambda message: True)
#получаем и обрабатываем ответ
def answer(message):
    global random_num
    if random_num > 0:
        #вытаскиваем ответ с БД
        with sq.connect("quiz.db") as config:
            cur = config.cursor()

            select_query = f"""SELECT answer FROM questions WHERE id = {random_question_id}"""
            cur.execute(select_query)
            answer = cur.fetchall()
            flag = True
            while flag:
                if message.text.lower() == answer[0][0].lower():

                    #вставили пометку в бд, что игрок ответил на данный вопрос
                    insert_query = f"INSERT INTO answers (user_id, question_id) VALUES ({message.chat.id}, {random_question_id})"
                    cur.execute(insert_query)

                    bot.send_message(message.chat.id, "Молодец, следующий вопрос:")
                    flag = False
                    random_num = 0
                else:
                    bot.send_message(message.chat.id, "Не верно. Глянь, правильно ли ты написал ответ. Если не справляешься, можешь выбрать новый вопрос. /question")
                    return
            cur.close()
        random_num = 0
        ask(message)
    else:
        bot.send_message(message.chat.id, "Ты еще не получил вопрос, дружочек. Тыкай /question.")
        return

bot.polling(none_stop=True)
