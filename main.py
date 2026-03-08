import telebot
from telebot import types
from datetime import datetime, timedelta
import json

TOKEN = "8695031161:AAFqAoGy2m14wnLOjuEywRG5FSKs77GiJRI"
ADMIN_ID = 146998462

bot = telebot.TeleBot(TOKEN)

user_data = {}

prices = {
    "Regular cleaning": {"1":120,"2":150,"3":180},
    "Deep cleaning": {"1":180,"2":220,"3":260},
    "Move out cleaning": {"1":200,"2":250,"3":300}
}

def load_bookings():
    try:
        with open("bookings.json") as f:
            return json.load(f)
    except:
        return []

def save_bookings(data):
    with open("bookings.json","w") as f:
        json.dump(data,f,indent=2)

def main_menu(user):

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("Book cleaning")

    if user == ADMIN_ID:
        kb.add("Admin panel")

    return kb

@bot.message_handler(commands=["start"])
def start(m):

    bot.send_message(
        m.chat.id,
        "Welcome to Cleaning Pros Team 🧼",
        reply_markup=main_menu(m.chat.id)
    )

@bot.message_handler(func=lambda m: m.text == "Book cleaning")
def cleaning_type(m):

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for i in prices:
        kb.add(i)

    bot.send_message(m.chat.id,"Choose cleaning type",reply_markup=kb)

@bot.message_handler(func=lambda m: m.text in prices)
def bedrooms(m):

    user_data[m.chat.id] = {"cleaning":m.text}

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("1","2","3")

    bot.send_message(m.chat.id,"Bedrooms?",reply_markup=kb)

@bot.message_handler(func=lambda m: m.text in ["1","2","3"])
def choose_date(m):

    d = user_data[m.chat.id]

    d["bedrooms"] = m.text
    d["price"] = prices[d["cleaning"]][m.text]

    today = datetime.now()

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for i in range(1,4):
        kb.add((today + timedelta(days=i)).strftime("%b %d"))

    bot.send_message(m.chat.id,"Choose date",reply_markup=kb)

@bot.message_handler(func=lambda m: m.chat.id in user_data and "date" not in user_data[m.chat.id])
def extras(m):

    user_data[m.chat.id]["date"] = m.text

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Inside fridge","Inside oven","No extras")

    bot.send_message(m.chat.id,"Extras?",reply_markup=kb)

@bot.message_handler(func=lambda m: m.text in ["Inside fridge","Inside oven","No extras"])
def address(m):

    user_data[m.chat.id]["extras"] = m.text

    bot.send_message(m.chat.id,"Send address")

@bot.message_handler(func=lambda m: m.chat.id in user_data and "address" not in user_data[m.chat.id])
def phone(m):

    user_data[m.chat.id]["address"] = m.text

    bot.send_message(m.chat.id,"Send phone number")

@bot.message_handler(func=lambda m: m.chat.id in user_data and "phone" not in user_data[m.chat.id])
def finish(m):

    d = user_data[m.chat.id]

    d["phone"] = m.text
    d["name"] = m.from_user.first_name
    d["chat_id"] = m.chat.id

    bookings = load_bookings()
    bookings.append(d)
    save_bookings(bookings)

    bot.send_message(
        m.chat.id,
        "✅ Thank you! Your request has been sent.",
        reply_markup=main_menu(m.chat.id)
    )

    bot.send_message(
        ADMIN_ID,
f"""
NEW CLEANING REQUEST

Cleaning: {d['cleaning']}
Bedrooms: {d['bedrooms']}
Price: ${d['price']}

Date: {d['date']}
Extras: {d['extras']}

Address: {d['address']}
Phone: {d['phone']}

Client: {d['name']}
"""
)

    del user_data[m.chat.id]

@bot.message_handler(func=lambda m: m.text == "Admin panel")
def admin(m):

    if m.chat.id != ADMIN_ID:
        return

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Today bookings","Income")

    bot.send_message(m.chat.id,"Admin panel",reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "Today bookings")
def today(m):

    bookings = load_bookings()

    today = datetime.now().strftime("%b %d")

    text = "TODAY BOOKINGS\n\n"

    for i in bookings:
        if i["date"] == today:
            text += f"{i['name']} ${i['price']}\n"

    bot.send_message(m.chat.id,text)

@bot.message_handler(func=lambda m: m.text == "Income")
def income(m):

    bookings = load_bookings()

    total = sum(i["price"] for i in bookings)

    bot.send_message(m.chat.id,f"Total income: ${total}")

bot.infinity_polling()
