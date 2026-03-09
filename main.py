import telebot
from telebot import types
from datetime import datetime, timedelta
import json
import time

TOKEN = "8695031161:AAFqAoGy2m14wnLOjuEywRG5FSKs77GiJRI"
ADMIN_ID = 146998462

bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()
time.sleep(1)

user_data = {}

prices = {
    "Regular cleaning": {"1":120,"2":150,"3":180},
    "Deep cleaning": {"1":180,"2":220,"3":260},
    "Move out cleaning": {"1":200,"2":250,"3":300}
}

# ---------- STORAGE ----------

def load_bookings():
    try:
        with open("bookings.json") as f:
            return json.load(f)
    except:
        return []

def save_bookings(data):
    with open("bookings.json","w") as f:
        json.dump(data,f,indent=2)

# ---------- MENU ----------

def main_menu(user):

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("🧹 Book cleaning")
    kb.add("💰 Prices","📞 Contact")

    if user == ADMIN_ID:
        kb.add("⚙ Admin panel")

    return kb

# ---------- START ----------

@bot.message_handler(commands=["start"])
def start(m):

    bot.send_message(
        m.chat.id,
"""
🧼 *Cleaning Pros Team*

Professional house cleaning service
""",
        reply_markup=main_menu(m.chat.id),
        parse_mode="Markdown"
    )

# ---------- PRICES ----------

@bot.message_handler(func=lambda m: m.text == "💰 Prices")
def prices_menu(m):

    bot.send_message(
m.chat.id,
"""
💰 *CLEANING PRICES*

━━━━━━━━━━━━

🧹 Regular cleaning  
1 bedroom — $120  
2 bedrooms — $150  
3 bedrooms — $180  

━━━━━━━━━━━━

✨ Deep cleaning  
1 bedroom — $180  
2 bedrooms — $220  
3 bedrooms — $260  

━━━━━━━━━━━━

🚚 Move out cleaning  
1 bedroom — $200  
2 bedrooms — $250  
3 bedrooms — $300  
""",
parse_mode="Markdown"
)

# ---------- CONTACT ----------

@bot.message_handler(func=lambda m: m.text == "📞 Contact")
def contact(m):

    bot.send_message(
m.chat.id,
"""
📞 *Cleaning Pros Team*

Phone  
253-202-0979

Email  
manager@excellentsolution.online
""",
parse_mode="Markdown"
)

# ---------- BOOK CLEANING ----------

@bot.message_handler(func=lambda m: m.text == "🧹 Book cleaning")
def cleaning_type(m):

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for i in prices:
        kb.add(i)

    bot.send_message(
        m.chat.id,
        "🧹 *Choose cleaning type*",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ---------- BEDROOMS ----------

@bot.message_handler(func=lambda m: m.text in prices)
def bedrooms(m):

    user_data[m.chat.id] = {}
    user_data[m.chat.id]["cleaning"] = m.text

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("1 Bedroom","2 Bedrooms","3 Bedrooms")

    bot.send_message(
        m.chat.id,
        "🏠 *How many bedrooms?*",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ---------- DATE ----------

@bot.message_handler(func=lambda m: m.text in ["1 Bedroom","2 Bedrooms","3 Bedrooms"])
def choose_date(m):

    d = user_data[m.chat.id]

    bedrooms = m.text.split()[0]

    d["bedrooms"] = bedrooms
    d["price"] = prices[d["cleaning"]][bedrooms]

    today = datetime.now()

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for i in range(1,4):
        kb.add((today + timedelta(days=i)).strftime("%m-%d-%Y"))

    kb.add("📅 Enter another date")

    bot.send_message(
        m.chat.id,
f"""
💰 *Estimated price:* ${d['price']}

━━━━━━━━━━━━

📅 *Choose cleaning date*
""",
        reply_markup=kb,
        parse_mode="Markdown"
    )

    d["step"] = "date"



# ---------- FLOW ----------

@bot.message_handler(content_types=["text"])
def flow(m):

    if m.chat.id not in user_data:
        return

    d = user_data[m.chat.id]

    if "step" not in d:
        return

    step = d["step"]

    # ----- DATE -----
    if step == "date":

        if m.text == "📅 Enter another date":

            bot.send_message(
                m.chat.id,
                "Enter date in format MM-DD-YYYY\nExample: 06-25-2026"
            )

            d["step"] = "manual_date"
            return

        # пользователь выбрал одну из кнопок даты
        d["date"] = m.text

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("Inside oven", "Inside fridge", "Windows")
        kb.add("Done")

        bot.send_message(
            m.chat.id,
            "✨ Select extra services (optional)",
            reply_markup=kb
        )

        d["extras"] = []
        d["step"] = "extras"
        return


    # ----- MANUAL DATE -----
    if step == "manual_date":

        try:
            datetime.strptime(m.text, "%m-%d-%Y")

            d["date"] = m.text

            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add("Inside oven", "Inside fridge", "Windows")
            kb.add("Done")

            bot.send_message(
                m.chat.id,
                "✨ Select extra services",
                reply_markup=kb
            )

            d["extras"] = []
            d["step"] = "extras"

        except:
            bot.send_message(
                m.chat.id,
                "❌ Wrong format\nUse MM-DD-YYYY"
            )

        return


    # ----- EXTRAS -----
    if step == "extras":

        if m.text == "Done":

            bot.send_message(
                m.chat.id,
                "👤 Enter your name"
            )

            d["step"] = "name"
            return

        d["extras"].append(m.text)

        bot.send_message(
            m.chat.id,
            f"✅ {m.text} added"
        )
        return


    # ----- NAME -----
    if step == "name":

        d["name"] = m.text

        bot.send_message(
            m.chat.id,
            "📞 Enter your phone"
        )

        d["step"] = "phone"
        return


    # ----- PHONE -----
    if step == "phone":

        d["phone"] = m.text

        bot.send_message(
            m.chat.id,
            "📍 Enter your address"
        )

        d["step"] = "address"
        return


    # ----- ADDRESS -----
    if step == "address":

        d["address"] = m.text

        bookings = load_bookings()

        order_id = len(bookings) + 1
        d["order_id"] = order_id

        bookings.append(d)
        save_bookings(bookings)

        extras = ", ".join(d["extras"]) if d["extras"] else "None"

        bot.send_message(
            ADMIN_ID,
            f"""
🧹 NEW CLEANING REQUEST

Order #{order_id}

Client: {d['name']}
Phone: {d['phone']}

Service: {d['cleaning']}
Bedrooms: {d['bedrooms']}
Date: {d['date']}

Extras: {extras}

Address:
{d['address']}

Price: ${d['price']}
"""
        )

        bot.send_message(
            m.chat.id,
            "✅ Booking confirmed!\nOur manager will contact you shortly.",
            reply_markup=main_menu(m.chat.id)
        )

        del user_data[m.chat.id]

# ---------- ADMIN PANEL ----------

@bot.message_handler(func=lambda m: m.text == "⚙ Admin panel" and m.chat.id == ADMIN_ID)
def admin_panel(m):

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📅 Today bookings")
    kb.add("📅 Tomorrow bookings")
    kb.add("💰 Income")

    bot.send_message(m.chat.id,"⚙ Admin panel",reply_markup=kb)

# ---------- TODAY ----------

@bot.message_handler(func=lambda m: m.text == "📅 Today bookings" and m.chat.id == ADMIN_ID)
def today_bookings(m):

    bookings = load_bookings()

    today = datetime.now().strftime("%m-%d-%Y")

    result = ""

    for b in bookings:

        if b["date"] == today:

            result += f"{b['name']} | {b['cleaning']} | ${b['price']}\n"

    if result == "":
        result = "No bookings today"

    bot.send_message(m.chat.id,result)

# ---------- TOMORROW ----------

@bot.message_handler(func=lambda m: m.text == "📅 Tomorrow bookings" and m.chat.id == ADMIN_ID)
def tomorrow_bookings(m):

    bookings = load_bookings()

    tomorrow = (datetime.now()+timedelta(days=1)).strftime("%m-%d-%Y")

    result = ""

    for b in bookings:

        if b["date"] == tomorrow:

            result += f"{b['name']} | {b['cleaning']} | ${b['price']}\n"

    if result == "":
        result = "No bookings tomorrow"

    bot.send_message(m.chat.id,result)

# ---------- INCOME ----------

@bot.message_handler(func=lambda m: m.text == "💰 Income" and m.chat.id == ADMIN_ID)
def income(m):

    bookings = load_bookings()

    total = sum(i["price"] for i in bookings)

    bot.send_message(
        m.chat.id,
        f"💰 Total income: ${total}"
    )

bot.infinity_polling(skip_pending=True)
