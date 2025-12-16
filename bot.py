from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import re

TOKEN = "8071245147:AAE7xBxPT39cF8pVu12D7pKkGxSDu8vquag"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 Calculator Bot\n\n"
        "Send me a calculation like:\n"
        "2 + 3\n"
        "10 - 5\n"
        "6 * 4\n"
        "8 / 2"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Supported operations:\n"
        "+  Addition\n"
        "-  Subtraction\n"
        "*  Multiplication\n"
        "/  Division\n\n"
        "Example: 12 * 5"
    )


def calculate(expression: str):
    match = re.match(r"^\s*(-?\d+\.?\d*)\s*([+\-*/])\s*(-?\d+\.?\d*)\s*$", expression)
    if not match:
        return "❌ Invalid format"

    a, operator, b = match.groups()
    a, b = float(a), float(b)

    if operator == "+":
        return a + b
    if operator == "-":
        return a - b
    if operator == "*":
        return a * b
    if operator == "/":
        if b == 0:
            return "❌ Division by zero"
        return a / b


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    result = calculate(text)
    await update.message.reply_text(f"✅ Result: {result}")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
