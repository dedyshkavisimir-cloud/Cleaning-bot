import telebot
from telebot import types
from datetime import datetime, timedelta
import json

TOKEN = "8695031161:AAFqAoGy2m14wnLOjuEywRG5FSKs77GiJRI"
ADMIN_ID = 146998462

import time

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
        "Welcome to Cleaning Pros Team 🧼",
        reply_markup=main_menu(m.chat.id)
    )


# ---------- PRICES ----------

@bot.message_handler(func=lambda m: m.text == "💰 Prices")
def prices_menu(m):

    bot.send_message(
    m.chat.id,
"""
💰 *CLEANING PRICES*

━━━━━━━━━━━━

🧹 *Regular cleaning*
• 1 bedroom — $120
• 2 bedrooms — $150
• 3 bedrooms — $180

━━━━━━━━━━━━

✨ *Deep cleaning*
• 1 bedroom — $180
• 2 bedrooms — $220
• 3 bedrooms — $260

━━━━━━━━━━━━

🚚 *Move out cleaning*
• 1 bedroom — $200
• 2 bedrooms — $250
• 3 bedrooms — $300
""",
parse_mode="Markdown"
)


# ---------- CONTACT ----------

@bot.message_handler(func=lambda m: m.text == "📞 Contact")
def contact(m):

    bot.send_message(
        m.chat.id,
"""
📞 Cleaning Pros Team

Phone:
253-202-0979

Email:
manager@excellentsolution.online
"""
    )


# ---------- BOOK CLEANING ----------

@bot.message_handler(func=lambda m: m.text == "🧹 Book cleaning")
def cleaning_type(m):

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for i in prices:
        kb.add(i)

    bot.send_message(
        m.chat.id,
        "🧹 Choose cleaning type",
        reply_markup=kb
    )


# ---------- BEDROOMS ----------

@bot.message_handler(func=lambda m: m.text in ["Regular cleaning","Deep cleaning","Move out cleaning"])
def bedrooms(m):

    user_data[m.chat.id] = {}
    user_data[m.chat.id]["cleaning"] = m.text

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("1 Bedroom","2 Bedrooms","3 Bedrooms")

    bot.send_message(
        m.chat.id,
        "How many bedrooms?",
        reply_markup=kb
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
        kb.add((today + timedelta(days=i)).strftime("%b %d"))

    kb.add("📆 Pick another date")

    bot.send_message(
        m.chat.id,
        f"💰 Estimated price: ${d['price']}\n\n📅 Choose cleaning date",
        reply_markup=kb
    )
    user_data[m.chat.id]["step"] = "date"


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "date")
def select_date(m):

    if m.chat.id not in user_data:
        return

    if m.text == "📆 Pick another date":
        return

    # сохраняем дату
    user_data[m.chat.id]["date"] = m.text

    bot.send_message(
        m.chat.id,
        f"📅 Date selected: {m.text}"
    )

    # клавиатура extras
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Inside oven")
    kb.add("Inside fridge")
    kb.add("Windows")
    kb.add("Done")

    bot.send_message(
        m.chat.id,
        "✨ Select extras (you can choose several).\nPress DONE when finished.",
        reply_markup=kb
    )

    user_data[m.chat.id]["extras"] = []
    user_data[m.chat.id]["step"] = "extras"

@bot.message_handler(func=lambda m: m.text == "📆 Pick another date")
def manual_date(m):

    bot.send_message(
        m.chat.id,
        "Enter date in format:\n\nMM/DD/YYYY\n\nExample: 06/25/2026"
    )

    user_data[m.chat.id]["step"] = "manual_date"

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "manual_date")
def save_manual_date(m):

    try:
        d = datetime.strptime(m.text, "%m/%d/%Y")

        user_data[m.chat.id]["date"] = m.text

        bot.send_message(m.chat.id, f"📅 Date selected: {m.text}")

        bot.send_message(m.chat.id, "Enter your name")

        user_data[m.chat.id]["step"] = "name"

        # дальше можно идти к адресу или следующему шагу

    except:
        bot.send_message(
            m.chat.id,
            "❌ Wrong format\n\nUse MM/DD/YYYY\nExample: 06/25/2026"
        )
        

# ---------- FLOW HANDLER ----------

@bot.message_handler(func=lambda m: m.chat.id in user_data and user_data[m.chat.id].get("step") in ["extras","name","phone","address"])
def flow(m):

    d = user_data[m.chat.id]
    step = d.get("step")

    if not m.text:
        return

    if step == "extras":

        if m.text.lower() == "done":
            bot.send_message(m.chat.id, "👤 Enter your name")
            d["step"] = "name"
            return

        d["extras"].append(m.text)

        bot.send_message(
            m.chat.id,
            f"✅ {m.text} added\nSelect more or press DONE."
        )
        return


    if step == "name":

        d["name"] = m.text

        bot.send_message(m.chat.id, "📞 Enter your phone number")

        d["step"] = "phone"
        return


    if step == "phone":

        d["phone"] = m.text

        bot.send_message(m.chat.id, "📍 Enter your address")

        d["step"] = "address"
        return


    if step == "address":

        d["address"] = m.text

        bookings = load_bookings()
        bookings.append(d)
        save_bookings(bookings)

        bot.send_message(
            ADMIN_ID,
f"""
🆕 NEW CLEANING REQUEST

👤 Client: {d['name']}
📞 Phone: {d['phone']}

🧹 Service: {d['cleaning']}
🛏 Bedrooms: {d['bedrooms']}
📅 Date: {d['date']}

✨ Extras: {", ".join(d['extras']) if d['extras'] else "None"}

📍 Address:
{d['address']}

💰 Price: ${d['price']}
"""
        )

        bot.send_message(
            m.chat.id,
            "✅ Booking confirmed! We will contact you shortly.",
            reply_markup=main_menu(m.chat.id)
        )

        del user_data[m.chat.id]
        

# ---------- ADMIN PANEL ----------

@bot.message_handler(func=lambda m: "Admin panel" in m.text)
def admin(m):

    if m.chat.id != ADMIN_ID:
        return

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📅 Today bookings")
    kb.add("📅 Tomorrow bookings")
    kb.add("💰 Income")

    bot.send_message(m.chat.id, "Admin panel", reply_markup=kb)


@bot.message_handler(func=lambda m: m.text == "📅 Today bookings")
def today(m):

    if m.chat.id != ADMIN_ID:
        return

    data = load_bookings()
    today = datetime.now().strftime("%b %d")

    result = ""

    for b in data:
        if b["date"] == today:
            result += f"""
🧹 {b['cleaning']}
🏠 {b['bedrooms']} bedrooms
📅 {b['date']}
💰 ${b['price']}
📍 {b['address']}
👤 {b['name']}
📞 {b['phone']}

────────────
"""

    if result == "":
        result = "No bookings today"

    bot.send_message(m.chat.id, result)


@bot.message_handler(func=lambda m: m.text == "📅 Tomorrow bookings")
def tomorrow(m):

    if m.chat.id != ADMIN_ID:
        return

    data = load_bookings()
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%b %d")

    result = ""

    for b in data:
        if b["date"] == tomorrow:
            result += f"""
🧹 {b['cleaning']}
🏠 {b['bedrooms']} bedrooms
📅 {b['date']}
💰 ${b['price']}
📍 {b['address']}
👤 {b['name']}
📞 {b['phone']}

────────────
"""

    if result == "":
        result = "No bookings for tomorrow"

    bot.send_message(m.chat.id, result)


# ---------- INCOME ----------

# ---------- INCOME ----------

@bot.message_handler(func=lambda m: m.text == "💰 Income")
def income(m):

    bookings = load_bookings()

    total = sum(i["price"] for i in bookings)

    bot.send_message(
        m.chat.id,
        f"💰 Total income: ${total}"
    )

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)

