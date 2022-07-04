import telebot
import sqlite3
import json
import os
import re
from telebot import types
from random import randint
from dotenv import load_dotenv
from fuzzywuzzy import fuzz, process
from selenium import webdriver
from time import sleep
from random import randint
from datetime import date


load_dotenv()
bot_token = os.getenv('SECRET_KEY')
t_bot = telebot.TeleBot(bot_token)
driver = webdriver.Safari()


mas=[]
if os.path.exists('brain/robot_response.txt'):
    f=open('brain/robot_response.txt', 'r', encoding='UTF-8')
    for x in f:
        if(len(x.strip()) > 2):
            mas.append(x.strip().lower())
    f.close()


keyboard1 = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
btn_start = types.KeyboardButton(text='/create_user')
btn_poll = types.KeyboardButton(text='/poll')
btn_link = types.KeyboardButton(text='/link')
btn_close = types.KeyboardButton(text='/close')
btn_todo = types.KeyboardButton(text='/create_todo')
btn_show_tasks = types.KeyboardButton(text='/show_tasks')
btn_photo = types.KeyboardButton(text='/photo')
keyboard1.add(btn_start, btn_poll, btn_todo, btn_show_tasks, btn_link, btn_photo, btn_close)


def answer(text):
    try:
        if text.lower().strip().isdigit():
            return "What does this number mean?"
        text=text.lower().strip()
        if os.path.exists('brain/robot_response.txt'):
            a = 0
            n = 0
            nn = 0
            for q in mas:
                if('u: ' in q):
                    aa=(fuzz.token_sort_ratio(q.replace('u: ',''), text))
                    if(aa > a and aa!= a):
                        a = aa
                        nn = n
                n = n + 1
            s = mas[nn + 1]
            res = process.extract(text, mas, limit=2, scorer=fuzz.token_sort_ratio)
            for i in res:
                if i[1] < 20:
                    return "Negative. I don't get it"
            return s
        else:
            return False
    except:
        return False


def check_task_date():
    connect = sqlite3.connect('brain/brain_data.db')
    cursor = connect.cursor()
    today = date.today()
    date_today = "{}.{}.{}".format(today.day, today.month, today.year)

    check_date_query = f""" DELETE FROM user_todo WHERE date <> '{date_today}'; """
    cursor.execute(check_date_query)
    connect.commit()


@t_bot.message_handler(commands=['start'])
def start_working(message):
    connect = sqlite3.connect('brain/brain_data.db')
    cursor = connect.cursor()

    start_query = """ CREATE TABLE IF NOT EXISTS login_id(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_user_tg INTEGER,
        pol_answer TEXT,
        UNIQUE(id_user_tg)
    ); """

    cursor.execute(start_query)
    connect.commit()

    start_query_2 = """ CREATE TABLE IF NOT EXISTS user_todo(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        id_done INTEGER,
        user_id INTEGER, 
        date TEXT,
        FOREIGN KEY(user_id) REFERENCES login_id(id)
        ); """

    cursor.execute(start_query_2)
    connect.commit()

    stick_start = 'CAACAgIAAxkBAAPDYq8lRlC5sSuswv1gdJKe4be-7boAAisCAAM4oAoBRWsX17hroiQE'
    t_bot.send_sticker(message.chat.id, stick_start)
    t_bot.send_message(message.chat.id, f'Hello {message.chat.first_name}! Choose buttons below', reply_markup=keyboard1)


@t_bot.message_handler(commands=['create_user'])
def start(message):
    connect = sqlite3.connect('brain/brain_data.db')
    cursor = connect.cursor()

    people_id = message.chat.id
    check_query = f""" SELECT id_user_tg FROM login_id WHERE id_user_tg = {people_id}; """
    cursor.execute(check_query)
    connect.commit()
    data = cursor.fetchone()

    if data is None:
        user_id = [message.chat.id]
        write_query = """ INSERT OR IGNORE INTO login_id(id_user_tg) VALUES(?); """
        cursor.execute(write_query, (user_id))
        connect.commit()
        t_bot.send_message(message.chat.id,
                        f'No problemo. User {message.chat.first_name} {message.chat.last_name} was created!',
                        reply_markup=keyboard1)
    else:
        t_bot.send_message(message.chat.id, 
                        'This user is already exist!', 
                        reply_markup=keyboard1)
    
    t_bot.send_message(message.chat.id, 
                        'You can delete your user from the base /delete_user', reply_markup=keyboard1)


@t_bot.message_handler(commands=['delete_user'])
def delete(message):
    connect = sqlite3.connect('brain/brain_data.db')
    cursor = connect.cursor()
    people_id = message.from_user.id

    check_query = f""" SELECT login_id.id 
    FROM login_id
    WHERE login_id.id_user_tg = {people_id};
    """
    cursor.execute(check_query)
    connect.commit()
    numb = cursor.fetchone()

    if numb is not None:
        delete_query_todo = f""" DELETE FROM user_todo
        WHERE user_todo.user_id = {numb[0]};
        """
        cursor.execute(delete_query_todo)
        connect.commit()

    delete_query = f""" DELETE FROM login_id
    WHERE login_id.id_user_tg = {people_id};
    """
    cursor.execute(delete_query)
    connect.commit()

    t_bot.send_message(message.chat.id, 
                    f'Hasta la vista, baby! User {message.chat.first_name} {message.chat.last_name} was terminated from the base',
                    reply_markup=keyboard1)


@t_bot.message_handler(commands=['task_done'])
def task_is_done(message):
    connect3 = sqlite3.connect('brain/brain_data.db')
    cursor3 = connect3.cursor()
    id_user_teleg = message.from_user.id

    check_query = f""" SELECT id_user_tg FROM login_id WHERE id_user_tg = {id_user_teleg}; """
    cursor3.execute(check_query)
    connect3.commit()
    data = cursor3.fetchone()

    if data is None:
         t_bot.send_message(message.chat.id, 'Negative. First of all you have to be registered')
    else:
        msg_done_task = t_bot.send_message(message.chat.id, 'What task do you want to finish?')
        t_bot.register_next_step_handler(msg_done_task, done_task)


@t_bot.message_handler(commands=['poll'])
def start_poll(message):
    connect5 = sqlite3.connect('brain/brain_data.db')
    cursor5 = connect5.cursor()
    people_id = message.from_user.id

    check_query = f""" SELECT id_user_tg FROM login_id WHERE id_user_tg = {people_id}; """
    cursor5.execute(check_query)
    connect5.commit()
    data = cursor5.fetchone()

    if data is None:
        t_bot.send_message(message.chat.id, 'Negative. First of all you have to be registered')
    else:
        t_bot.send_poll(message.chat.id,
                        question='There is no fate but what we make for ourselves.',
                        options=['Agree', 'Disagree', 'Maybe'],
                        allows_multiple_answers=False,
                        is_anonymous = False,
                        )


@t_bot.message_handler(commands=['link'])
def link(message):
    search_msg = t_bot.send_message(message.chat.id, 'Enter what do you want to find on YouTube?')
    t_bot.register_next_step_handler(search_msg, count_search)


@t_bot.message_handler(commands=['close', 'open'])
def close_kb(message):
    if message.text == '/close':
        keyboard_close = types.ReplyKeyboardRemove()
        t_bot.send_message(message.chat.id, 'Done', reply_markup=keyboard_close)
        t_bot.send_message(message.chat.id, 'You can open the keyboard by command /open', reply_markup=keyboard_close)
    elif message.text == '/open':
        t_bot.send_message(message.chat.id, 'Done', reply_markup=keyboard1)


@t_bot.message_handler(commands=['create_todo'])
def start_todo(message):
    connect5 = sqlite3.connect('brain/brain_data.db')
    cursor5 = connect5.cursor()
    people_id = message.from_user.id

    check_query = f""" SELECT id_user_tg FROM login_id WHERE id_user_tg = {people_id}; """
    cursor5.execute(check_query)
    connect5.commit()
    data = cursor5.fetchone()
    if data is None:
        t_bot.send_message(message.chat.id, 'Negative. First of all you have to be registered')
    else:
        todo_msg = t_bot.send_message(message.chat.id, 'Enter what do you want to write?')
        t_bot.register_next_step_handler(todo_msg, create_task)


@t_bot.message_handler(commands=['show_tasks'])
def show_all_tasks(message):
    connect3 = sqlite3.connect('brain/brain_data.db')
    cursor3 = connect3.cursor()
    id_user_teleg = message.from_user.id
    check_task_date()

    check_query = f""" SELECT id_user_tg FROM login_id WHERE id_user_tg = {id_user_teleg}; """
    cursor3.execute(check_query)
    connect3.commit()
    data = cursor3.fetchone()

    if data is None:
         t_bot.send_message(message.chat.id, 'Negative. First of all you have to be registered')
    else:
        selection_tasks = f""" SELECT user_todo.id, task, id_done
        FROM user_todo
        INNER JOIN login_id
        ON login_id.id = user_todo.user_id
        WHERE {id_user_teleg} = id_user_tg;
        """
        cursor3.execute(selection_tasks)
        data = cursor3.fetchone()

        if data is None:
            t_bot.send_message(message.chat.id, "You created no one")
        else:
            selection_tasks = f""" SELECT user_todo.id, task, id_done, date
            FROM user_todo
            INNER JOIN login_id
            ON login_id.id = user_todo.user_id
            WHERE {id_user_teleg} = id_user_tg;
            """
            cursor3.execute(selection_tasks)

            all_tasks = ""
            for i in cursor3.fetchall():
                if i[2] == 0:
                    sign = '<em><b> Active </b></em>'
                else:
                    sign = '<em><s><b> Done </b></s></em>'

                task_message = 'Task: ' + i[1] +' - ' + sign +' |today: '+ i[3] + '\n'
                all_tasks += task_message
            t_bot.send_message(message.chat.id, f"{all_tasks}", parse_mode='html')
            t_bot.send_message(message.chat.id, "You can finish some task by /task_done")


@t_bot.message_handler(commands=["photo"])
def photo_func(message):
    try:
        number = randint(1, 4)
        link = "content/photo{}.jpg".format(number)
        picture = open(link, "rb")
        t_bot.send_photo(message.chat.id, photo= picture, reply_markup= keyboard1)
        picture.close()
    except Exception as error_here:
        print(repr(error_here))


@t_bot.message_handler(content_types=["sticker"])
def send_sticker(message):
    number = randint(1, 8)

    with open('content/stickers.json', 'r', encoding='utf-8') as f:
        text = json.load(f)

        for i in text['stickers']:
            stick_robot = i.get(str(number), False)
            if stick_robot is False:
                pass
            else:
                t_bot.send_sticker(message.chat.id, stick_robot)


@t_bot.message_handler(regexp="[\":;=+@_#$%^&*()<>/\|}{~:§±-]")
def handle_message(message):
	t_bot.reply_to(message, "Wrong.")


@t_bot.message_handler(content_types=['text'])
def text(message):
    clear_msg = re.sub(r'[^a-z]', '', message.text.lower())

    if clear_msg in ['hello', 'hi']:
        t_bot.reply_to(message, f"Hello {message.chat.first_name}. I'm back")
    elif answer(message.text):
        msg=answer(message.text)
        t_bot.send_message(message.chat.id, msg)
    else:
        t_bot.reply_to(message, "Don't do that.")

def count_search(message):
    necessary_thing = message.text
    count_links = t_bot.send_message(message.chat.id, 'Enter how many links?')
    t_bot.register_next_step_handler(count_links, searching, necessary_thing)

def searching(message, necessary_thing):
    t_bot.send_message(message.chat.id, 'Start searching')

    video_href = 'https://www.youtube.com/results?search_query='+ necessary_thing
    driver.get(video_href)
    sleep(2)
    videos_link = driver.find_elements_by_id("video-title")
    range_number = int(message.text)

    for i in range(range_number):
        user_links = videos_link[i].get_attribute('href')
        if user_links is None:
            pass
        t_bot.send_message(message.chat.id, str(user_links))


def create_task(message):
    connect2 = sqlite3.connect('brain/brain_data.db')
    cursor2 = connect2.cursor()

    id_user_teleg = message.from_user.id

    check_query_seems_like = f""" SELECT user_todo.task
    FROM user_todo
    INNER JOIN login_id
    ON login_id.id = user_todo.user_id
    WHERE {id_user_teleg} = id_user_tg;
    """

    cursor2.execute(check_query_seems_like)
    connect2.commit()

    flag = False
    for i in cursor2.fetchall():
        if message.text == i[0]:
            flag = True
            t_bot.reply_to(message, "You have alredy this task.")

    if flag is False:
        user_id_here = message.from_user.id
        check_query = f""" SELECT id, id_user_tg FROM login_id WHERE id_user_tg = {user_id_here}; """
        cursor2.execute(check_query)
        connect2.commit()

        user_id_there = cursor2.fetchone()
        msg_task_user = message.text
        today = date.today()
        current_time = "{}.{}.{}".format(today.day, today.month, today.year)

        try:
            query1 = """ INSERT INTO user_todo (task, id_done, user_id, date) VALUES(?,?,?,?); """
            cursor2.execute(query1, [msg_task_user, 0, user_id_there[0], current_time])
            connect2.commit()
        except:
            t_bot.send_message(message.chat.id, "You have to be registred!")

        t_bot.send_message(message.chat.id, "Your task was created! Check them /show_tasks")


def done_task(message):
    connect4 = sqlite3.connect('brain/brain_data.db')
    cursor4 = connect4.cursor()
    msg_txt = message.text
    id_user_teleg = message.from_user.id

    check_query = f""" SELECT user_todo.task
    FROM user_todo
    INNER JOIN login_id
    ON login_id.id = user_todo.user_id
    WHERE {id_user_teleg} = id_user_tg
    AND user_todo.task = '{msg_txt}'
    ;
    """
    cursor4.execute(check_query)
    connect4.commit()
    data = cursor4.fetchone()

    if data is None:
        t_bot.send_message(message.chat.id, "There are no such tasks")
    else:
        done_task_query = f""" UPDATE user_todo
        SET id_done = 1
        WHERE user_todo.task = '{msg_txt}'
        AND EXISTS(
            SELECT id_user_tg 
            FROM login_id 
            WHERE {id_user_teleg} = id_user_tg
            AND user_todo.user_id = login_id.id
            );
        """

        cursor4.execute(done_task_query)
        connect4.commit()
        t_bot.send_message(message.chat.id, "Your task was finished! Check them /show_tasks")
    

@t_bot.message_handler(content_types=['photo'])
def photo_id_func(the_message):
    t_bot.reply_to(the_message, "Got it. \n Here is my")
    photo_func(the_message)


@t_bot.poll_answer_handler()
def handle_poll_answer(pollAnswer):
    connect = sqlite3.connect('brain/brain_data.db')
    cursor = connect.cursor()

    id_user = pollAnswer.user.id
    number = pollAnswer.option_ids[0]

    with open('content/stickers.json', 'r', encoding='utf-8') as f:
        text = json.load(f)  
        for i in text['answers']:
            answer_robot = i.get(str(number), False)
            if answer_robot is False:
                pass
            else:
                write_poll_query = f""" UPDATE login_id
                                        SET pol_answer = (?)
                                        WHERE id_user_tg = {id_user}; """
                cursor.execute(write_poll_query, [answer_robot])
                connect.commit()


if __name__ == "__main__":
    t_bot.polling(none_stop=True)

# \":;',.=+@_!#$%^&*()<>?/\|}{~:§±-
