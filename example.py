import logging
import datetime
import sqlite3
import schedule
import time

import telebot
from telebot import types
import telebot_calendar
from telebot_calendar import CallbackData
from datetime import timedelta
from multiprocessing import Process
from telebot.types import ReplyKeyboardRemove, CallbackQuery
import threading

now = datetime.datetime.today()+timedelta(days=1)


API_TOKEN = "1389166758:AAFdOums7OxBt7fXvfnViAckG78XjM1yNxc"
#logger = telebot.logger
#telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(API_TOKEN)

# Creates a unique calendar
calendar_1 = CallbackData("calendar_1", "action", "year", "month", "day")

def addtoquestions(id,text):
    
    conn = sqlite3.connect('baza.db')
    c = conn.cursor()
    c.execute("SELECT chatid FROM clienty WHERE chatid='{id}'")
    if c.fetchone() is None:
       queryvar = "INSERT INTO clienty VALUES(?,?)"
       c.execute(queryvar, (id,text,))
       conn.commit()
    else:
       bot.send_message(id,"Вы уже выбрали дату")
       dataop=now.strftime('%d.%m.%Y')
       bot.send_message(id,dataop)

def sendl():
    threading.Timer(10.0, sendl).start()
    dataop=now.strftime('%d.%m.%Y')
    
    conn = sqlite3.connect('baza.db')
    c = conn.cursor()
    c.execute("SELECT chatid FROM clienty WHERE vremya=?",(dataop,))
    chatidbd = c.fetchall()
    for chatid in chatidbd:
        try:
             bot.send_message(chatid[0],"Завтра прием у Ферузы!")
        except:
            bot.send_message(chatid[0],"упс")
    c.execute("DELETE FROM clienty WHERE vremya=?",(dataop,))
    conn.commit()   
 

                     
@bot.message_handler(commands=["start"])
def check_other_messages(message):
    now = datetime.datetime.now()  # Get the current date
    bot.send_message(
        message.chat.id,
        "Выберите дату",
        reply_markup=telebot_calendar.create_calendar(
            name=calendar_1.prefix,
            year=now.year,
            month=now.month,  # Specify the NAME of your calendar
        ),
    )
    

@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
def callback_inline(call: CallbackQuery):
    """
    Обработка inline callback запросов
    :param call:
    :return:
    """

    # At this point, we are sure that this calendar is ours. So we cut the line by the separator of our calendar
    name, action, year, month, day = call.data.split(calendar_1.sep)
    # Processing the calendar. Get either the date or None if the buttons are of a different type
    date = telebot_calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
    if action == "DAY":
        bot.send_message(
            chat_id=call.from_user.id,
            text=f"Вы выбрали {date.strftime('%d.%m.%Y')}",
            reply_markup=ReplyKeyboardRemove(),
        )
        addtoquestions(call.message.chat.id,date.strftime('%d.%m.%Y'))
        print(f"{calendar_1}: Day: {date.strftime('%d.%m.%Y')}")
    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Отмена",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_1}: Cancellation")


sendl()

bot.polling(none_stop=True)
