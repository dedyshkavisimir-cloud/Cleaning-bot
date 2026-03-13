import telebot
from telebot import types
from datetime import datetime, timedelta
import json
import time
import os
from flask import Flask, request

# ---------- STYLE ----------

def style(title, text):
    return f"""
🧼 *Cleaning Pros Team*
━━━━━━━━━━━━ 

*{title}*

{text}
"""

TOKEN = "8695031161:AAFqAoGy2m14wnLOjuEywRG5FSKs77GiJRI"
ADMIN_ID = 146998462

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

WEBHOOK_URL = "https://cleaning-bot-production-6581.up.railway.app/webhook"



user_data = {}

prices = {
    "Regular cleaning": {"1":120,"2":150,"3":180},
    "Deep cleaning": {"1":180,"2":220,"3":260},
    "Move out cleaning": {"1":200,"2":250,"3":300}
}

extras_prices = {
    "Inside oven": 25,
    "Inside fridge": 40,
    "Windows": 40
}

power_prices = {
    "Driveway": "180–240",
    "House exterior": "200–400",
    "Deck / Patio": "120–250",
    "Fence": "150–300",
    "Roof": "250–500"
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

    kb.add("⚡ Quick estimate")
    kb.add("🧹 Book house cleaning")
    kb.add("🌬 Dryer vent cleaning")
    kb.add("💧 Power washing")
    
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

    Professional cleaning services

    👇 Tap *Menu* below to choose a service
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
• 1 bedroom — $120  
• 2 bedrooms — $150  
• 3 bedrooms — $180  

━━━━━━━━━━━━

✨ Deep cleaning  
• 1 bedroom — $180  
• 2 bedrooms — $220  
• 3 bedrooms — $260  

━━━━━━━━━━━━

🚚 Move out cleaning  
• 1 bedroom — $200  
• 2 bedrooms — $250  
• 3 bedrooms — $300

━━━━━━━━━━━━

🌪 *Dryer Vent Cleaning*  
Estimated price: **$89-229**

Final price depends on:
• vent length  
• roof or wall access  
• heavy lint / bird nest

━━━━━━━━━━━━

💧 *Power Washing*

• Driveway — **$180-240**  
• House exterior — **$200-400**  
• Deck / Patio — **$120-250**  
• Fence — **$150-300**  
• Roof — **$250-500**

Final price depends on:
• surface size  
• moss removal  
• surface type
""",
        parse_mode="Markdown"
    )

# ---------- QUICK ESTIMATE ----------

@bot.message_handler(func=lambda m: m.text == "⚡ Quick estimate")
def quick_estimate(m):

    user_data[m.chat.id] = {"step": "quick_estimate"}

    bot.send_message(
        m.chat.id,
        style(
            "⚡ Quick estimate",
            """
    Send a short description of the job.

    Example:
    Driveway power washing in Bellevue.

    📸 You can attach photos for a more accurate estimate.
    """
        ),
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


# ---------- DRYER VENT ----------

@bot.message_handler(func=lambda m: m.text == "🌬 Dryer vent cleaning")
def dryer_vent(m):

    user_data[m.chat.id] = {}
    d = user_data[m.chat.id]

    d["step"] = "vent_date"

    bot.send_message(
        m.chat.id,
        style(
            "🌬 Dryer Vent Cleaning",
            """

    💰 *Estimated price:* $89 – $229

    Final price depends on:

    • vent length  
    • roof access  
    • heavy lint buildup  
    • bird nest removal  

    Most jobs take *30–45 minutes*

    ━━━━━━━━━━━━

    📅 Enter preferred service date

    Example:
    06-25-2026
    """
        ),
    parse_mode="Markdown"
    )


# ---------- POWER WASHING ----------

@bot.message_handler(func=lambda m: m.text == "💧 Power washing")
def power_washing(m):
    
    if m.chat.id not in user_data:
        user_data[m.chat.id] = {}
        
    d = user_data[m.chat.id]

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("Driveway")
    kb.add("House exterior")
    kb.add("Deck / Patio")
    kb.add("Fence")
    kb.add("Roof")

    bot.send_message(
        m.chat.id,
        style(
            "💧 Power Washing",
            "Select the surface you need cleaned."
        ),
    
        reply_markup=kb,
        parse_mode="Markdown"
    )

    d["step"] = "power_surface"


# ---------- BOOK CLEANING ----------

@bot.message_handler(func=lambda m: m.text == "🧹 Book house cleaning")
def cleaning_type(m):

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for i in prices:
        kb.add(i)

    bot.send_message(
        m.chat.id,
        style(
            "🧹 House Cleaning",
            "Choose cleaning type."
        ),
        reply_markup=kb,
        parse_mode="Markdown"
    )
    
     
# ---------- BEDROOMS ----------

@bot.message_handler(func=lambda m: m.text in prices)
def bedrooms(m):

    user_data[m.chat.id] = {}
    user_data[m.chat.id]["cleaning"] = m.text

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("1 Bedroom")
    kb.add("2 Bedrooms")
    kb.add("3 Bedrooms")

    bot.send_message(
        m.chat.id,
        style(
        "🏠 Bedrooms",
        "How many bedrooms?"
        ),
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

@bot.message_handler(func=lambda m: m.chat.id in user_data and user_data[m.chat.id].get("step") == "date")
def select_date(m):

    d = user_data[m.chat.id]

    if m.text == "📅 Enter another date":

        bot.send_message(
            m.chat.id,
            "Enter date in format MM-DD-YYYY\nExample: 06-25-2026"
        )

        d["step"] = "manual_date"
        return

    d["date"] = m.text

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Inside oven","Inside fridge","Windows")
    kb.add("Done","Skip")

    bot.send_message(
        m.chat.id,
        style(
            "✨ Extra Services",
            "Select additional services."
        ),
        reply_markup=kb
    )

    d["extras"] = []
    d["step"] = "extras"


# ---------- ADMIN PANEL ----------

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.text == "⚙ Admin panel")
def admin_panel(m):

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("📅 Today bookings")
    kb.add("📅 Tomorrow bookings")
    kb.add("💰 Income")

    bot.send_message(
        m.chat.id,
        "⚙ Admin panel",
        reply_markup=kb
    )

# ---------- TODAY ----------

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.text == "📅 Today bookings")
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

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.text == "📅 Tomorrow bookings")
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

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.text == "💰 Income")
def income(m):

    bookings = load_bookings()

    total = sum(i["price"] for i in bookings)

    bot.send_message(
        m.chat.id,
        f"💰 Total income: ${total}"
    )

# ---------- FLOW ----------

@bot.message_handler(content_types=["text","photo"])
def flow(m):
    
    if m.text in [
        "🧹 Book cleaning",
        "💰 Prices",
        "📞 Contact",
        "⚙ Admin panel",
        "📅 Today bookings",
        "📅 Tomorrow bookings",
        "💰 Income"
    ]:
        return
    if m.chat.id not in user_data:
        bot.send_message(
            m.chat.id,
        """
        🧼 *Cleaning Pros Team*

        👇 Tap *Menu* below to choose a service
        """,
            reply_markup=main_menu(m.chat.id)
        )
        
        return

    # QUICK ESTIMATE
    if m.text == "⚡ Quick estimate":

        user_data[m.chat.id] = {"step": "quick_estimate"}

        bot.send_message(
            m.chat.id,
            """
    ⚡ Quick estimate

        Please send a short description of the job and attach photos if possible.

        Example:
        Driveway power washing in Bellevue.

        This helps us give you a faster estimate.
        """,
            parse_mode="Markdown"
        )
        return
        
    d = user_data[m.chat.id]

    if "step" not in d:
        return

    step = d["step"]

    # QUICK ESTIMATE
    if step == "quick_estimate":

        name = m.from_user.first_name
        username = m.from_user.username or "no username"

        # ---------- PHOTO ----------
        if m.content_type == "photo":

            photo_id = m.photo[-1].file_id
            caption = m.caption if m.caption else ""

            if "photos" not in d:
                d["photos"] = []

            d["photos"].append(photo_id)

            # если есть caption — сразу отправляем заявку
            if caption:

                bot.send_message(
                    ADMIN_ID,
                    f"""
    ⚡ NEW QUICK REQUEST

    👤 {name}
    📞 @{username}

    📝 {caption}
    """
                )

                media = [types.InputMediaPhoto(p) for p in d["photos"]]
                bot.send_media_group(ADMIN_ID, media)

                bot.send_message(
                    m.chat.id,
                    "✅ Thank you! Your request has been sent. We will contact you soon.",
                    reply_markup=main_menu(m.chat.id)
                )

                del user_data[m.chat.id]
                return

            # иначе просто сохраняем фото
            if not d.get("photo_message_sent"):
                d["photo_message_sent"] = True
                bot.send_message(
                    m.chat.id,
                    "📸 Photos received.\n\nYou can send more photos or type description of the job."
                )

            return


        # ---------- TEXT ----------
        if m.content_type == "text":

            d["description"] = m.text

            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add("Skip")

            bot.send_message(
                m.chat.id,
                "📸 Send photos for a more accurate estimate or press Skip.",
                reply_markup=kb
            )

            d["step"] = "quick_photos"
            return

        # ---------- QUICK PHOTOS ----------
        if step == "quick_photos":

            name = m.from_user.first_name
            username = m.from_user.username or "no username"

            if m.content_type == "photo":

                photo_id = m.photo[-1].file_id

                if "photos" not in d:
                    d["photos"] = []

                d["photos"].append(photo_id)

                bot.send_message(
                    m.chat.id,
                    "📸 Photo added. Send more photos or press Skip."
                )
                return


            if m.text and m.text.lower() == "skip":

                bot.send_message(
                    ADMIN_ID,
                    f"""
        ⚡ NEW QUICK REQUEST

        👤 {name}
        📞 @{username}

        📝 {d['description']}
        """
                )

                if "photos" in d:

                    if len(d["photos"]) == 1:

                        bot.send_photo(
                            ADMIN_ID,
                            d["photos"][0]
                        )

                    else:

                        media = [types.InputMediaPhoto(p) for p in d["photos"]]

                        bot.send_media_group(
                            ADMIN_ID,
                            media
                        )

                bot.send_message(
                    m.chat.id,
                    "✅ Thank you! Your request has been sent. We will contact you soon.",
                    reply_markup=main_menu(m.chat.id)
                )

                del user_data[m.chat.id]
                return

            bot.send_message(
                m.chat.id,
                "📸 Send photos or press Skip."
            )
            return

    # DATE
    if step == "date":

        if m.text == "📅 Enter another date":

            bot.send_message(
                m.chat.id,
                "Enter date MM-DD-YYYY\nExample: 06-25-2026"
            )

            d["step"] = "manual_date"
            return

        d["date"] = m.text

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("Inside oven","Inside fridge","Windows")
        kb.add("Done","Skip")

        bot.send_message(
            m.chat.id,
            "✨ Select extra services",
            reply_markup=kb
        )

        d["extras"] = []
        d["step"] = "extras"
        return


    # MANUAL DATE
    if step == "manual_date":

        try:

            date = datetime.strptime(m.text,"%m-%d-%Y")

            if date.date() < datetime.now().date():

                bot.send_message(
                    m.chat.id,
                    "❌ Date cannot be in the past"
                )
                return

            d["date"] = m.text

            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add("Inside oven","Inside fridge","Windows")
            kb.add("Done","Skip")

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
        step = d["step"]

    # DRYER VENT DATE

    if step == "vent_date":

        d["date"] = m.text

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("Side wall")
        kb.add("Roof")
        kb.add("Not sure")

        bot.send_message(
            m.chat.id,
            "📍 Where is the dryer vent located?",
            reply_markup=kb
        )

        d["step"] = "vent_location"
        return

    # VENT LOCATION

    if step == "vent_location":

        d["location"] = m.text

        bot.send_message(
            m.chat.id,
            "👤 Enter your name"
        )

        d["step"] = "vent_name"
        return 

     # POWER SURFACE
    if step == "power_surface":

        d["surface"] = m.text

        price_range = power_prices.get(m.text,"")

        bot.send_message(
            m.chat.id,
            style(
                f"💧 {m.text} Power Washing",
                f"""

            💰 Estimated price: ${price_range}

            Final price depends on:

            • surface size  
            • moss removal  
            • surface type  
            • dirt buildup
            """
            ),
            
            parse_mode="Markdown"
        )

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("Skip")

        bot.send_message(
            m.chat.id,
            "📸 Send a photo for more accurate estimate or type skip",
            reply_markup=kb,
            parse_mode="Markdown"
        )

        d["step"] = "power_photo"
        return

    # POWER PHOTO
    if step == "power_photo":

        if m.content_type == "photo":

            d["photo"] = m.photo[-1].file_id

            bot.send_message(
                m.chat.id,
            """
            📅 *Enter preferred service date*

            Format: **MM-DD-YYYY**

            Example:
            06-25-2026
            """,
                parse_mode="Markdown"
            )

            d["step"] = "power_date"
            return


        elif m.text.lower() == "skip":

            bot.send_message(
                m.chat.id,
            """
            📅 *Enter preferred service date*

            Format: **MM-DD-YYYY**

            Example:
            06-25-2026
            """,
            parse_mode="Markdown"
            )

            d["step"] = "power_date"
            return

    # POWER DATE
    if step == "power_date":

        d["date"] = m.text

        bot.send_message(
            m.chat.id,
            "📍 Enter your address"
        )

        d["step"] = "power_address"
        return

    # POWER ADDRESS
    if step == "power_address":

        d["address"] = m.text

        bot.send_message(
            m.chat.id,
            "👤 Enter your name"
        )

        d["step"] = "power_name"
        return

    if step == "power_name":

        d["name"] = m.text

        bot.send_message(
            m.chat.id,
            "📞 Enter your phone number"
        )

        d["step"] = "power_phone"
        return
    
    # POWER PHONE
    if step == "power_phone":

        d["phone"] = m.text

        bot.send_message(
            ADMIN_ID,
    f"""
    💧 *NEW POWER WASH REQUEST*

    Surface: {d['surface']}
    
    📅 {d['date']}
    👤 {d['name']}
    📞 {d['phone']}

    📍 Address:
    {d['address']}
    """,
            parse_mode="Markdown"
        )
    if "photo" in d:
        bot.send_photo(
            ADMIN_ID,
            d["photo"],
            caption="📸 Power washing estimate photo"
        )

        bot.send_message(
            m.chat.id,
    """
    ✅ Thank you! Your request has been sent. We will contact you soon.
    """,
            reply_markup=main_menu(m.chat.id)
        )

        del user_data[m.chat.id]
        return
    
    # NAME
    if step == "vent_name":

        d["name"] = m.text

        bot.send_message(
            m.chat.id,
            "📞 Enter your phone number"
        )

        d["step"] = "vent_phone"
        return


    # PHONE
    if step == "vent_phone":

        d["phone"] = m.text

        bot.send_message(
            m.chat.id,
            "📍 Enter your address"
        )

        d["step"] = "vent_address"
        return


    # ADDRESS
    if step == "vent_address":

        d["address"] = m.text

        bot.send_message(
            ADMIN_ID,
        f"""
        🔥 *NEW DRYER VENT REQUEST*

        👤 {d['name']}
        📞 {d['phone']}

        📅 {d['date']}
        📍 Vent location: {d['location']}

        📍 Address:
        {d['address']}
        """,
            parse_mode="Markdown"
        )
        if "photo" in d:
            bot.send_photo(
                ADMIN_ID,
                d["photo"],
                caption="📸 Photo for estimate"
            )

        bot.send_message(
            m.chat.id,
"""
✅ Thank you! Your request has been sent. We will contact you soon.
"""
        )

        del user_data[m.chat.id]
        return
    
    # EXTRAS
    if step == "extras":

        if m.text in ["Done","Skip"]:

            bot.send_message(
                m.chat.id,
                "👤 Enter your name"
            )

            d["step"] = "name"
            return

        d["extras"].append(m.text)

        # добавляем цену extras
        if m.text in extras_prices:
            d["price"] += extras_prices[m.text]

        bot.send_message(
            m.chat.id,
            f"✅ {m.text} added (+${extras_prices.get(m.text,0)})"
        )

        return


    # NAME
    if step == "name":

        d["name"] = m.text

        bot.send_message(
            m.chat.id,
            "📞 Enter your phone number"
        )

        d["step"] = "phone"
        return


    # PHONE
    if step == "phone":

        d["phone"] = m.text

        bot.send_message(
            m.chat.id,
            "📍 Enter your address"
        )

        d["step"] = "address"
        return


    # ADDRESS
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
🆕 *NEW CLEANING REQUEST*

━━━━━━━━━━━━

🧾 Order #{order_id}

👤 {d['name']}
📞 {d['phone']}

🧹 {d['cleaning']}
🏠 {d['bedrooms']} bedrooms
📅 {d['date']}

✨ Extras: {extras}

📍 Address:
{d['address']}

━━━━━━━━━━━━

💰 Price: ${d['price']}
""",
            parse_mode="Markdown"
        )

        bot.send_message(
m.chat.id,
f"""
📋 *Booking Summary*

🧹 Service: {d['cleaning']}
🏠 Bedrooms: {d['bedrooms']}
📅 Date: {d['date']}

✨ Extras: {extras}

💰 Total price: ${d['price']}

━━━━━━━━━━━━

✅ *Booking confirmed*

Our manager will contact you shortly.
Thank you for choosing  
*Cleaning Pros Team* 🧼
""",
reply_markup=main_menu(m.chat.id),
parse_mode="Markdown"
)

        del user_data[m.chat.id]
        return


@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK"


if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEBHOOK_URL)

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
