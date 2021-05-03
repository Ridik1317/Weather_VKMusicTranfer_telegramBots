import logging  # for loggers
import psycopg2  # for using DB
import os  # for using environ variables
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from pars import WEATHER, find_city
from keyboard import *  # for using keyboards

# your telegram id for feedback
CREATOR = os.getenv('CREATOR')
# parameter
TOKEN = os.getenv("TOKEN")  # your telegram bot token
DATABASE_URL = os.environ["DATABASE_URL"]  # your DB

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# action bot point
(ACTION_CHOICE, CITY_CHOICE, WEATHER_CHOICE, SETTINGS_CHOICE,
 CHANGE_CITY_CHOICE, TAKE_CITY, TAKE_MES_CREATOR, TAKE_CHANGE_CITY) = map(chr, range(8))


# +++
def start_handler(update: Update, _: CallbackContext) -> None:
    logger.info("User {}, sent /start".format(update.effective_user["id"]))
    update.message.reply_text("Hi! \U0001F590 \nI am weather bot. \U00002602 \nPress button to start) \U0001F447",
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
def city_choice(update: Update, _: CallbackContext) -> str:
    logger.info("User {}, in city menu".format(update.effective_user["id"]))
    update.message.reply_text("What method you want to use? \U0001F9D0",
                              reply_markup=ReplyKeyboardMarkup(city_choice_k.keyboard, resize_keyboard=True)
                              )
    return CITY_CHOICE


# +++
def file_city(update: Update, _: CallbackContext) -> str:
    user = update.message.from_user['id']
    try:
        # connecting to data_base
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        logger.info("User {}, connecting to db {}".format(update.effective_user["id"], cursor.fetchall()))
        # check user
        cursor.execute(f"SELECT * FROM CITIES WHERE id = {user}")
        user_raw = cursor.fetchone()
        if not user_raw:
            # add user to DB
            logger.info("User {} is not in DB, create new raw".format(update.effective_user["id"]))
            cursor.execute("SELECT Now()")
            time = cursor.fetchone()[0]
            cursor.execute(f"INSERT INTO CITIES (id, lat, lon, last_changing) "
                           f"VALUES ({user}, {main_wthr.lat}, {main_wthr.lon}, '{time}')")
            logger.info("User {} added to DB, create new raw".format(update.effective_user["id"]))
        else:
            cursor.execute(f"SELECT lat, lon FROM CITIES WHERE id = {user}")
            main_wthr.lat, main_wthr.lon = cursor.fetchone()
            logger.info("User {} was found in DB".format(update.effective_user["id"]))
        # close DB
        cursor.close()
        connection.commit()
        connection.close()

        update.message.reply_text("\U00002754"*5,
                                  reply_markup=ReplyKeyboardMarkup(weather_choice_k.keyboard, resize_keyboard=True))
        return WEATHER_CHOICE

    except (Exception, psycopg2.Error) as err:
        logger.info("User {}, DB connecting ERROR {}".format(update.effective_user["id"], err))
        update.message.reply_text("Error with DB connection. \U000026A0",
                                  reply_markup=ReplyKeyboardMarkup(start_k.keyboard, resize_keyboard=True)
                                  )
    return ConversationHandler.END


# +++
def ask_send_name_city(update: Update, _: CallbackContext) -> str:
    update.message.reply_text("Write the name of the city. \U0000270F",
                              reply_markup=ReplyKeyboardRemove()
                              )
    return TAKE_CITY


# +++
def take_name_city(update: Update, _: CallbackContext) -> str:
    logger.info("User {}, sent city name".format(update.effective_user["id"]))
    try:
        city = find_city(update.message.text)
        main_wthr.lat = city['lat']
        main_wthr.lon = city['lon']
    except Exception as err:
        logger.info("User {}, can't find city {}".format(update.effective_user["id"], err))
        update.message.reply_text("I can't find city. \U000026D4\nTry again. \U00002712")
        return TAKE_CITY

    update.message.reply_text("Accepted. \U00002705")
    update.message.reply_text("\U00002754"*5,
                              reply_markup=ReplyKeyboardMarkup(weather_choice_k.keyboard, resize_keyboard=True))
    return WEATHER_CHOICE


# +++
def get_location(update: Update, _: CallbackContext):
    if update.message.location:
        logger.info("User {}, sent location".format(update.effective_user["id"]))
        main_wthr.lat = str(update.message.location['latitude'])
        main_wthr.lon = str(update.message.location['longitude'])

        update.message.reply_text("Accepted. \U00002705")
        update.message.reply_text("\U00002754"*5,
                                  reply_markup=ReplyKeyboardMarkup(weather_choice_k.keyboard, resize_keyboard=True))
        return WEATHER_CHOICE
    else:
        logger.info("User {}, didn't sent location".format(update.effective_user["id"]))
        update.message.reply_text("It's not location. \U000026D4 \nTry again. \U00002712",
                                  reply_markup=ReplyKeyboardMarkup(start_k.keyboard, resize_keyboard=True))
        return ConversationHandler.END


# +++
def weather_now(update: Update, _: CallbackContext) -> str:
    try:
        answer = main_wthr.now()
        update.message.reply_text(answer,
                                  parse_mode='HTML',
                                  disable_web_page_preview=True,
                                  reply_markup=ReplyKeyboardMarkup(start_k.keyboard, resize_keyboard=True)
                                  )
        logger.info("User {} got now_weather".format(update.effective_user["id"]))
    except Exception as err:
        logger.info("User {}, can't make request {}".format(update.effective_user["id"], err))
        update.message.reply_text("I can't make a request. \U000026A0",
                                  reply_markup=ReplyKeyboardMarkup(start_k.keyboard, resize_keyboard=True)
                                  )
    return ConversationHandler.END


# +++
def weather_forecast(update: Update, _: CallbackContext) -> str:
    try:
        answer = main_wthr.day()
        update.message.reply_text(answer,
                                  parse_mode='HTML',
                                  disable_web_page_preview=True,
                                  reply_markup=ReplyKeyboardMarkup(start_k.keyboard, resize_keyboard=True)
                                  )
        logger.info("User {} got forecast_weather".format(update.effective_user["id"]))
    except Exception as err:
        logger.info("User {}, can't make request {}".format(update.effective_user["id"], err))
        update.message.reply_text("I can't make a request. \U000026A0",
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
def change_city_choice(update: Update, _: CallbackContext) -> str:
    logger.info("User {}, are in change_city menu".format(update.effective_user["id"]))
    update.message.reply_text("How do you want to change your city? \U0001F914",
                              reply_markup=ReplyKeyboardMarkup(change_city_choice_k.keyboard, resize_keyboard=True))
    return CHANGE_CITY_CHOICE


# +++
def back_to_settings_choice(update: Update, _: CallbackContext) -> str:
    logger.info("User {}, return to settings menu".format(update.effective_user["id"]))
    update.message.reply_text("Return. \U0001F519",
                              reply_markup=ReplyKeyboardMarkup(settings_choice_k.keyboard, resize_keyboard=True)
                              )
    return SETTINGS_CHOICE


# +++
def ask_change_name_city(update: Update, _: CallbackContext) -> str:
    update.message.reply_text("Write the name of the city you want to choose. \U0000270F",
                              reply_markup=ReplyKeyboardRemove()
                              )
    return TAKE_CHANGE_CITY


# +++
def take_change_name_city(update: Update, _: CallbackContext) -> str:
    logger.info("User {}, sent change city name".format(update.effective_user["id"]))
    try:
        city = find_city(update.message.text)
        main_wthr.lat = city['lat']
        main_wthr.lon = city['lon']
    except Exception as err:
        logger.info("User {}, can't find city {}".format(update.effective_user["id"], err))
        update.message.reply_text("I can't find city. \U000026D4 \nTry again. \U00002712")
        return TAKE_CHANGE_CITY

    update.message.reply_text("Accepted. \U00002705")
    return change_city(update)


# +++
def get_change_city_location(update: Update, _: CallbackContext) -> str:
    if update.message.location:
        logger.info("User {}, sent location for change city".format(update.effective_user["id"]))
        main_wthr.lat = str(update.message.location['latitude'])
        main_wthr.lon = str(update.message.location['longitude'])

        update.message.reply_text("Accepted. \U00002705")

        return change_city(update)
    else:
        logger.info("User {}, didn't sent location".format(update.effective_user["id"]))
        update.message.reply_text("It's not location. \U000026D4 \nTry again. \U00002712",
                                  reply_markup=ReplyKeyboardMarkup(change_city_choice_k.keyboard, resize_keyboard=True))
        return CHANGE_CITY_CHOICE


# +++
def change_city(update: Update):
    user = update.message.from_user['id']
    try:
        # connecting to data_base
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        logger.info("User {}, connecting to db for city changing {}".format(update.effective_user["id"],
                                                                            cursor.fetchall()))
        # check user
        cursor.execute(f"SELECT * FROM CITIES WHERE id = {user}")
        user_raw = cursor.fetchone()
        if not user_raw:
            # add user to DB
            logger.info("User {} is not in DB, create new raw".format(update.effective_user["id"]))
            cursor.execute("SELECT Now()")
            time = cursor.fetchone()[0]
            cursor.execute(f"INSERT INTO CITIES (id, lat, lon, last_changing) "
                           f"VALUES ({user}, {main_wthr.lat}, {main_wthr.lon}, '{time}')")
            logger.info("User {} added to DB, create new raw".format(update.effective_user["id"]))
        else:
            cursor.execute("SELECT Now()")
            time = cursor.fetchone()[0]
            cursor.execute(f"UPDATE CITIES "
                           f"SET lat={main_wthr.lat}, lon={main_wthr.lon}, last_changing='{time}' "
                           f"WHERE id= {user}")
            logger.info("User {} changed city in DB".format(update.effective_user["id"]))
        # close DB
        cursor.close()
        connection.commit()
        connection.close()

        update.message.reply_text("City was saved. \U0001F3DB",
                                  reply_markup=ReplyKeyboardMarkup(start_k.keyboard, resize_keyboard=True))
        return ConversationHandler.END

    except (Exception, psycopg2.Error) as err:
        logger.info("User {}, DB connecting ERROR {}".format(update.effective_user["id"], err))
        update.message.reply_text("Error with DB connection. \U000026A0",
                                  reply_markup=ReplyKeyboardMarkup(start_k.keyboard, resize_keyboard=True)
                                  )
    return ConversationHandler.END


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
                    MessageHandler(Filters.regex(action_choice_k.keyboard[0][0].text), city_choice),
                    MessageHandler(Filters.location, get_location),
                    MessageHandler(Filters.regex(action_choice_k.keyboard[1][0].text), settings_choice)],
                CITY_CHOICE: [
                    MessageHandler(Filters.regex(city_choice_k.keyboard[0][0].text), file_city),
                    MessageHandler(Filters.regex(city_choice_k.keyboard[0][1].text), ask_send_name_city),
                    MessageHandler(Filters.regex(city_choice_k.keyboard[1][0].text), back_to_action_choice)],
                TAKE_CITY: [
                    MessageHandler(Filters.text & ~Filters.command, take_name_city)],
                WEATHER_CHOICE: [
                    MessageHandler(Filters.regex(weather_choice_k.keyboard[0][0].text), weather_now),
                    MessageHandler(Filters.regex(weather_choice_k.keyboard[0][1].text), weather_forecast)],
                SETTINGS_CHOICE: [
                    MessageHandler(Filters.regex(settings_choice_k.keyboard[0][0].text), change_city_choice),
                    MessageHandler(Filters.regex(settings_choice_k.keyboard[0][1].text), ask_send_mes_to_creator),
                    MessageHandler(Filters.regex(settings_choice_k.keyboard[1][0].text), back_to_action_choice)],
                TAKE_MES_CREATOR: [
                    MessageHandler(Filters.text & ~Filters.command, take_mes_to_creator)],
                CHANGE_CITY_CHOICE: [
                    MessageHandler(Filters.regex(change_city_choice_k.keyboard[0][0].text), ask_change_name_city),
                    MessageHandler(Filters.location, get_change_city_location),
                    MessageHandler(Filters.regex(change_city_choice_k.keyboard[1][0].text), back_to_settings_choice)],
                TAKE_CHANGE_CITY: [
                    MessageHandler(Filters.text & ~Filters.command, take_change_name_city)]},
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


main_wthr = WEATHER('17', '17')

if __name__ == "__main__":
    main()
