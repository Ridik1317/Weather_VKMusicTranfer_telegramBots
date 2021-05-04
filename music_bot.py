import logging  # for loggers
import os  # for using environ variables
import vk_api
from vk_api.audio import VkAudio
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove, TelegramError
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from keyboard import *  # for using keyboards

# your telegram id for feedback
CREATOR = os.getenv('CREATOR')
# parameter
TOKEN = os.getenv("TOKEN")  # your telegram bot token

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# action bot point
(ACTION_CHOICE, VK_CHOICE, TAKE_VK_MES, SETTINGS_CHOICE, TAKE_MES_CREATOR) = map(chr, range(5))


# +++
def start_handler(update: Update, _: CallbackContext) -> None:
    logger.info("User {}, sent /start".format(update.effective_user["id"]))
    update.message.reply_text("Hi! \U0001F590 \nI am vk_music bot. \U0001F3A7 \nPress button to start) \U0001F447",
                              reply_markup=ReplyKeyboardMarkup(start_k.keyboard, resize_keyboard=True)
                              )


# +++
def stop_handler(update: Update, _: CallbackContext) -> None:
    logger.info("User {}, sent /stop".format(update.effective_user["id"]))
    update.message.reply_text("Ok, buy( \U0001F480",
                              reply_markup=ReplyKeyboardRemove()
                              )
    return ConversationHandler.END


# +++
def action_choice(update: Update, _: CallbackContext) -> str:
    logger.info("User {}, in main menu".format(update.effective_user["id"]))
    update.message.reply_text("What will you choose? \U0001F48A",
                              reply_markup=ReplyKeyboardMarkup(action_choice_k.keyboard, resize_keyboard=True)
                              )
    return ACTION_CHOICE


# +++
def back_to_action_choice(update: Update, _: CallbackContext):
    logger.info("User {}, return to main menu".format(update.effective_user["id"]))
    update.message.reply_text("Return. \U0001F519",
                              reply_markup=ReplyKeyboardMarkup(action_choice_k.keyboard, resize_keyboard=True)
                              )
    return ACTION_CHOICE


# +++
def vk_choice(update: Update, _: CallbackContext) -> str:
    global vk_flag
    logger.info("User {}, in vk menu".format(update.effective_user["id"]))
    update.message.reply_text("What method you want to use? \U0001F9D0",
                              reply_markup=ReplyKeyboardMarkup(vk_choice_k.keyboard, resize_keyboard=True)
                              )
    vk_flag = 0
    return VK_CHOICE


# +++
def ask_send_person_id(update: Update, _: CallbackContext) -> str:
    global vk_flag
    logger.info("User {}, choose person id".format(update.effective_user["id"]))
    update.message.reply_text("Write the person-id+first parsing song number[0-N]+quantity of songs. \U0000270F"
                              "\n\U00002B07Template\U00002B07"
                              "\n314159+0+17",
                              reply_markup=ReplyKeyboardRemove()
                              )
    vk_flag = 1
    return TAKE_VK_MES


# +++
def ask_send_album_id(update: Update, _: CallbackContext) -> str:
    global vk_flag
    logger.info("User {}, choose album id".format(update.effective_user["id"]))
    update.message.reply_text("Write the album-id+first parsing song number[0-N]+quantity of songs. \U0000270F"
                              "\n\U00002B07Template\U00002B07"
                              "\n314159+0+17",
                              reply_markup=ReplyKeyboardRemove()
                              )
    vk_flag = 2
    return TAKE_VK_MES


# +++
def ask_send_music_title(update: Update, _: CallbackContext) -> str:
    global vk_flag
    logger.info("User {}, choose find music".format(update.effective_user["id"]))
    update.message.reply_text("Write the song request+quantity of answers. \U0000270F"
                              "\n\U00002B07Template\U00002B07"
                              "\nSmash Mouth - All Star+7",
                              reply_markup=ReplyKeyboardRemove()
                              )
    vk_flag = 3
    return TAKE_VK_MES


# +++
def vk_parsing(update: Update, _: CallbackContext) -> str:
    global vk_flag
    if vk_flag == 1:
        logger.info("User {}, sent person-id".format(update.effective_user["id"]))
        message = update.message.text.split(sep='+')
        return vk_pars_person_id(message[0], message[1], message[2], update)
    elif vk_flag == 2:
        logger.info("User {}, sent album-id".format(update.effective_user["id"]))
        message = update.message.text.split(sep='+')
        return vk_pars_album_id(message[0], message[1], message[2], update)
    elif vk_flag == 3:
        logger.info("User {}, sent song title".format(update.effective_user["id"]))
        message = update.message.text.split(sep='+')
        return vk_find(message[0], message[1], update)


# +++
def vk_pars_person_id(pers_id: str, start: str, quantity: str, update: Update):
    vk_session = vk_api.VkApi(os.getenv("LOGIN"), os.getenv("PASSWORD"))

    try:
        vk_session.auth()
        logger.info("User {}, log in VK".format(update.effective_user["id"]))
    except vk_api.AuthError as error_msg:
        logger.info("User {}, VK connecting ERROR {}".format(update.effective_user["id"], error_msg))
        update.message.reply_text(f"VK connecting error. \U000026A0")
        return ConversationHandler.END

    # module for audio
    audio = VkAudio(vk_session)

    if pers_id == '0':
        pers_id = os.getenv("MY_ID")

    # for audio send
    bot = Updater(TOKEN, use_context=True).bot

    track = audio.get_iter(owner_id=pers_id)
    # skip
    for i in range(int(start)):
        next(track)
    # pars
    update.message.reply_text("Start. \U000025B6")
    for i in range(int(quantity)):
        song = next(track)
        try:
            bot.send_audio(str(update.message.from_user['id']), song['url'],
                           caption=f'''<b>{song['artist']}:</b>\n<u><i>"{song['title']}"</i></u>''',
                           parse_mode='HTML')
        except (Exception, TelegramError) as err:
            logger.info("User {}, audio sending ERROR {}".format(update.effective_user["id"], err))
            update.message.reply_text(f"Can't pars song:{i}. \U000026D4")

    logger.info("User {}, pars stopped".format(update.effective_user["id"]))
    update.message.reply_text("The End. \U000023F9",
                              reply_markup=ReplyKeyboardMarkup(start_k.keyboard, resize_keyboard=True)
                              )
    return ConversationHandler.END


# +++
def vk_pars_album_id(alb_id: str, start: str, quantity: str, update: Update):
    vk_session = vk_api.VkApi(os.getenv("LOGIN"), os.getenv("PASSWORD"))

    try:
        vk_session.auth()
        logger.info("User {}, log in VK".format(update.effective_user["id"]))
    except vk_api.AuthError as error_msg:
        logger.info("User {}, VK connecting ERROR {}".format(update.effective_user["id"], error_msg))
        update.message.reply_text(f"VK connecting error. \U000026A0")
        return ConversationHandler.END

    # module for audio
    audio = VkAudio(vk_session)

    # for audio send
    bot = Updater(TOKEN, use_context=True).bot
    track = audio.get_albums_iter(owner_id=alb_id)
    # skip
    for i in range(int(start)):
        next(track)
    # pars
    update.message.reply_text("Start. \U000025B6")
    for i in range(int(quantity)):
        song = next(track)
        try:
            bot.send_audio(str(update.message.from_user['id']), song['url'],
                           caption=f'''<b>{song['artist']}:</b>\n<u><i>"{song['title']}"</i></u>''',
                           parse_mode='HTML')
        except (Exception, TelegramError) as err:
            logger.info("User {}, audio sending ERROR {}".format(update.effective_user["id"], err))
            update.message.reply_text(f"Can't pars number:{i}.  \U000026D4")

    logger.info("User {}, pars stopped".format(update.effective_user["id"]))
    update.message.reply_text("The End. \U000023F9",
                              reply_markup=ReplyKeyboardMarkup(start_k.keyboard, resize_keyboard=True)
                              )
    return ConversationHandler.END


# +++
def vk_find(request: str, quantity: str, update: Update):
    vk_session = vk_api.VkApi(os.getenv("LOGIN"), os.getenv("PASSWORD"))

    try:
        vk_session.auth()
        logger.info("User {}, log in VK".format(update.effective_user["id"]))
    except vk_api.AuthError as error_msg:
        logger.info("User {}, VK connecting ERROR {}".format(update.effective_user["id"], error_msg))
        update.message.reply_text(f"VK connecting error. \U000026A0")
        return ConversationHandler.END

    # module for audio
    audio = VkAudio(vk_session)

    # for audio send
    bot = Updater(TOKEN, use_context=True).bot
    track = audio.search_iter(request)
    # pars
    update.message.reply_text("Start. \U000025B6")
    for i in range(int(quantity)):
        song = next(track)
        try:
            bot.send_audio(str(update.message.from_user['id']), song['url'],
                           caption=f'''<b>{song['artist']}:</b>\n<u><i>"{song['title']}"</i></u>''',
                           parse_mode='HTML')
        except (Exception, TelegramError) as err:
            logger.info("User {}, audio sending ERROR {}".format(update.effective_user["id"], err))
            update.message.reply_text(f"Can't pars number:{i}. \U000026D4")

    update.message.reply_text("The End. \U000023F9",
                              reply_markup=ReplyKeyboardMarkup(start_k.keyboard, resize_keyboard=True)
                              )
    return ConversationHandler.END


# +++
def settings_choice(update: Update, _: CallbackContext) -> str:
    logger.info("User {}, are in settings menu".format(update.effective_user["id"]))
    update.message.reply_text("What do you want, pretty? \U0001F60D",
                              reply_markup=ReplyKeyboardMarkup(settings_choice_k.keyboard, resize_keyboard=True))
    return SETTINGS_CHOICE


# +++
def ask_send_mes_to_creator(update: Update, _: CallbackContext) -> str:
    update.message.reply_text("Write the text and I will forward it to my master. \U0001F4EB",
                              reply_markup=ReplyKeyboardRemove()
                              )
    return TAKE_MES_CREATOR


# +++
def take_mes_to_creator(update: Update, _: CallbackContext) -> str:
    sender = update.message.from_user['username']
    text = update.message.text
    Updater(TOKEN, use_context=True).bot.send_message(CREATOR, f"From @{sender}:\n{text}")
    update.message.reply_text("Delivered. \U00002705 \n Thank you. \U00002764",
                              reply_markup=ReplyKeyboardMarkup(start_k.keyboard, resize_keyboard=True)
                              )
    logger.info("User {}, sent text for master".format(update.effective_user["id"]))
    return ConversationHandler.END


# +++
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


# +++
def main(local=0) -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Conversation handler
    con_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(start_k.keyboard[0][0].text), action_choice)],
        states={ACTION_CHOICE: [
            MessageHandler(Filters.regex(action_choice_k.keyboard[0][0].text), vk_choice),
            MessageHandler(Filters.regex(action_choice_k.keyboard[1][0].text), settings_choice)],
            VK_CHOICE: [
                MessageHandler(Filters.regex(vk_choice_k.keyboard[0][0].text), ask_send_person_id),
                MessageHandler(Filters.regex(vk_choice_k.keyboard[0][1].text), ask_send_music_title),
                MessageHandler(Filters.regex(vk_choice_k.keyboard[1][0].text), ask_send_album_id),
                MessageHandler(Filters.regex(vk_choice_k.keyboard[1][1].text), back_to_action_choice)],
            TAKE_VK_MES: [MessageHandler(Filters.text, vk_parsing)],
            SETTINGS_CHOICE: [
                MessageHandler(Filters.regex(settings_choice_k.keyboard[0][0].text), ask_send_mes_to_creator),
                MessageHandler(Filters.regex(settings_choice_k.keyboard[1][0].text), back_to_action_choice)],
            TAKE_MES_CREATOR: [
                MessageHandler(Filters.text & ~Filters.command, take_mes_to_creator)]},
        fallbacks=[CommandHandler('stop', stop_handler)]
    )

    # handlers of other messages
    dp.add_handler(CommandHandler('start', start_handler))
    dp.add_handler(con_handler)
    dp.add_error_handler(error)

    # switcher between local and heroku machine
    if local == 1:
        # Start the Bot
        # your database
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()
    else:
        # Start the Bot
        PORT = int(os.environ.get('PORT', 5000))
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.bot.setWebhook(f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}")

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


vk_flag = 0

if __name__ == "__main__":
    main()
