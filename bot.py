from os.path import defpath

from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler 

from gpt import *
from util import *

from dotenv import load_dotenv 
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
OPEN_AI_TOKEN = os.getenv("OPEN_AI_TOKEN")

async def start(update, context):
    msg = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, msg)

    await show_main_menu(update, context, {
        "start": "Main menu",
        "profile": "Generating a Tinder profile \uD83D\uDE0E",
        "opener": "Messages about dating \uD83E\uDD70",
        "message": "Correspondence on your behalf \uD83D\uDE08",
        "date": "Communicating with the stars \uD83D\uDD25",
        "gpt": "Ask a question to ChatGPT \uD83E\uDDE0",
    })

async def gpt(update, context):
    dialog.mode = "gpt"
    await send_photo(update, context, "gpt")
    msg = load_message("gpt")
    await send_text(update, context, msg)

async def gpt_dialog(update, context):
    text = update.message.text

    prompt = load_prompt("gpt")
    answer = await chatgpt.send_question(prompt, text)

    await send_text(update, context, answer)

async def date(update, context):
    dialog.mode = "date"

    msg = load_message("date")

    await send_photo(update, context, "date")
    await send_text_buttons(update, context, msg, {
        "date_grande": "Ariana Grande",
        "date_robbie": "Margot Robbie",
        "date_zendaya": "Zendaya",
        "date_gosling": "Ryan Gosling",
        "date_hardy": "Tom Hardy",
    })

async def date_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    await send_photo(update, context, query)
    await send_text(update, context, "A good choice.\uD83D\uDE05 Your task is to ask a girl/guy on a date in 5 messages! ❤️")

    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)

async def date_dialog(update, context):
    text = update.message.text
    my_message = await send_text(update, context, "Dialing a message...")

    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)

async def message(update, context):
    dialog.mode = "message"
    msg = load_message("message")

    await send_photo(update, context, "message")
    await send_text_buttons(update, context, msg, {
        "message_next": "Send a message",
        "message_date": "Ask for a date",
    })
    dialog.list.clear()

async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)

async def message_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)

    my_message = await send_text(update, context, "I'm thinking about options...")
    answer = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)

async def profile(update, context):
    dialog.mode = "profile"
    msg = load_message("profile")
    await send_photo(update, context, "profile")
    await send_text(update, context, msg)

    dialog.user.clear()
    dialog.counter = 0

    await send_text(update, context, "What is your name?")

async def profile_dialog(update, context):
    text = update.message.text
    dialog.counter += 1

    if dialog.counter == 1:
        dialog.user["name"] = text
        await send_text(update, context, "What do you do for a living?")
    if dialog.counter == 2:
        dialog.user["occupation"] = text
        await send_text(update, context, "Do you have any hobbies?")
    if dialog.counter == 3:
        dialog.user["hobby"] = text
        await send_text(update, context, "What do you NOT like in people?")
    if dialog.counter == 4:
        dialog.user["annoys"] = text
        await send_text(update, context, "The purpose of dating?")
    if dialog.counter == 5:
        dialog.user["goal"] = text
        await send_text(update, context, "How old are you?")
    if dialog.counter == 6:
        dialog.user["age"] = text

        prompt = load_prompt("profile")
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, "ChatGPT 🧠 is generating your profile. Please wait a few seconds")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)

async def opener(update, context):
    dialog.mode = "opener"
    msg = load_message("opener")
    await send_photo(update, context, "opener")
    await send_text(update, context, msg)

    dialog.user.clear()
    dialog.counter = 0
    await send_text(update, context, "Partner's name?")

async def opener_dialog(update, context):
    text = update.message.text
    dialog.counter += 1

    if dialog.counter == 1:
        dialog.user["name"] = text
        await send_text(update, context, "How old is your partner?")
    if dialog.counter == 2:
        dialog.user["age"] = text
        await send_text(update, context, "Rate the appearance 1-10 points")
    if dialog.counter == 3:
        dialog.user["handsome"] = text
        await send_text(update, context, "What does he/she do for a living?")
    if dialog.counter == 4:
        dialog.user["occupation"] = text
        await send_text(update, context, "The purpose of dating?")
    if dialog.counter == 5:
        dialog.user["goal"] = text

        prompt = load_prompt("opener")
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, "ChatGPT 🧠 generates your message. Please wait a few seconds...")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)

async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "date":
        await date_dialog(update, context)
    elif dialog.mode == "message":
        await message_dialog(update, context)
    elif dialog.mode == "profile":
        await profile_dialog(update, context)
    elif dialog.mode == "opener":
        await opener_dialog(update, context)

dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.user = {}
dialog.counter = 0

chatgpt = ChatGptService(OPEN_AI_TOKEN)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))
app.add_handler(CommandHandler("message", message))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("opener", opener))


app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))

app.run_polling()
