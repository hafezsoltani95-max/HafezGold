from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests

BOT_TOKEN = "7287339925:AAFxyI-8-2nlYE4HAZ6JvgkK_aG-bhcG5qA"
CHANNEL_ID = "@rezaee_jewellery"

def get_gold_price():
    try:
        url = "https://api.tgju.online/v1/market/price/gold"
        r = requests.get(url).json()
        price = int(r["gold"]["p"])
        return price
    except:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋 برای ارسال پست به کانال از دستور زیر استفاده کن:\n\n"
        "`/post لینک_عکس | متن پست | وزن(گرم) | درصد اجرت | درصد سود`",
        parse_mode="Markdown"
    )

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = " ".join(context.args)
        photo_url, caption, weight, wage_percent, profit_percent = [x.strip() for x in args.split("|")]

        weight = float(weight)
        wage_percent = float(wage_percent)/100
        profit_percent = float(profit_percent)/100

        context.chat_data["product"] = {
            "weight": weight,
            "wage_percent": wage_percent,
            "profit_percent": profit_percent
        }

        keyboard = [
            [InlineKeyboardButton("💰 قیمت لحظه‌ای", callback_data="price")],
            [InlineKeyboardButton("📊 محاسبه با اجرت و سود", callback_data="calc")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        bot = Bot(token=BOT_TOKEN)
        bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=photo_url,
            caption=caption,
            reply_markup=reply_markup
        )

        await update.message.reply_text("✅ پست با موفقیت به کانال ارسال شد.")

    except Exception as e:
        await update.message.reply_text(
            "❌ خطا در ارسال پست.\nفرمت درست:\n"
            "`/post لینک_عکس | متن پست | وزن(گرم) | درصد اجرت | درصد سود`",
            parse_mode="Markdown"
        )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product = context.chat_data.get("product", None)

    if query.data == "price":
        price = get_gold_price()
        if price:
            await query.edit_message_text(f"💰 قیمت لحظه‌ای طلا: {price:,} ریال")
        else:
            await query.edit_message_text("❌ خطا در دریافت قیمت")

    elif query.data == "calc":
        if not product:
            await query.edit_message_text("❌ اطلاعات محصول موجود نیست.")
            return

        price = get_gold_price()
        if price:
            base_price = price * product["weight"]
            total_with_wage = base_price * (1 + product["wage_percent"])
            total_with_profit = total_with_wage * (1 + product["profit_percent"])
            await query.edit_message_text(
                f"""📊 محاسبه با درصد اجرت و سود:
وزن: {product["weight"]} گرم
قیمت پایه: {base_price:,} ریال
اجرت: {product["wage_percent"]*100:.0f}٪
سود: {product["profit_percent"]*100:.0f}٪
➡️ قیمت نهایی: {int(total_with_profit):,} ریال"""
            )
        else:
            await query.edit_message_text("❌ خطا در دریافت قیمت")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", post))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
