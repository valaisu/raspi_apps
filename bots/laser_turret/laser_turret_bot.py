from typing import final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from secret_info import users, token

from gpiozero import LED
from time import sleep


TOKEN: final = token
BOT_USERNAME = "@MayhemskyBot"


def activate_turret(seconds: int = 300):
    led = LED(23)
    led.on()  # activate pin 23
    sleep(seconds)
    led.off()


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Do you want to play with Mayhem?")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("git gud")


async def turret_5(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.username in users:
        await update.message.reply_text("I'll activate the turret for 5 minutes!")
        activate_turret()
    else:
        await update.message.reply_text("You are not authorized to activate the turret")


# Responses
def handle_response(text: str) -> str:
    text: str = text.lower()
    return text


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.from_user.username} in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused the following error: {context.error}')


if __name__ == '__main__':
    print('Starting bot')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('turret5', turret_5))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=5)

