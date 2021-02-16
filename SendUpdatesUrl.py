import urllib.request
import config
import sqlite3 as sq


def select_users():
    with sq.connect("quiz.db") as config:
        cur = config.cursor()
        select_all_category_name = "SELECT user_id FROM users"
        cur.execute(select_all_category_name)
        users_ids_dirt = cur.fetchall()
        users_ids = []
        cur.close()
        for i in range(len(users_ids_dirt)):
            users_ids.append(users_ids_dirt[i][0])
        print("users_ids", users_ids)
        return users_ids


chat_ids = select_users()
print("users_ids после селекта", chat_ids)
# chat_ids = [199610041, 273077469, 308729527, 884721281, 142867079]
text = """test na live, sorry"""
text = text.replace(" ", "%20")
text = text.replace("\n", "%0A")

for i in chat_ids:
    urllib.request.urlopen(f"https://api.telegram.org/bot{config.Token}/sendMessage?chat_id={i}&text={text}")
