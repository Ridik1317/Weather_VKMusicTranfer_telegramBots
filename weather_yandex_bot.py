import telebot
from pars import pars_day_now, pars_day_forecast, find_lanlon_city
from telebot import types
import json
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)


# обрабатывает команду хелп
@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(message.chat.id, 'Hi dude \U0001F600 \nThis is weather bot \U0001F300')


# обрабатывает команду старт, это основное меню
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, 'City or Location?\U0001F914', reply_markup=keyboard_main)


# меняет город по умолчанию
def change_city(message):
    if message.location is not None:
        try:
            city = {'adres': 'GPS', 'lat': message.location.latitude, 'lon': message.location.longitude}
            with open('data/city_now', 'w') as f:
                f.write(json.dumps(city, indent=1))
            bot.send_message(message.chat.id, '\U00002705 Success. City was changed.', reply_markup=keyboard_main)
        except:
            bot.send_message(message.chat.id, "\U000026A0 Error. City wasn't changed.", reply_markup=keyboard_main)
    elif message.text == '\U00002328 Find city':
        send = bot.send_message(message.chat.id, 'Write the name of the city you want to choose \U0000270F')
        bot.register_next_step_handler(send, change_city)
    else:
        try:
            with open('data/city_now', 'w') as f:
                f.write(json.dumps(find_lanlon_city(message.text), indent=1))
            bot.send_message(message.chat.id, '\U00002705 Success.City was changed.', reply_markup=keyboard_main)
        except:
            bot.send_message(message.chat.id, "\U000026A0 Error. Can't find city", reply_markup=keyboard_main)


# просто находит по имени долготу и широту сохраняет их глобально и далее отсылает на выбор прогноза
def find_city(message):
    global lat,  lon
    try:
        json_file = find_lanlon_city(message.text)
        lat = json_file['lat']
        lon = json_file['lon']
        bot.send_message(message.chat.id, 'Now or forecast? \U0001F9E0', reply_markup=keyboard_find_city)
    except:
        bot.send_message(message.chat.id, "\U000026A0 Error. Can't find city", reply_markup=keyboard_main)


# обрабатывает текст, точнее кнопки которые нажимаются по ходу пользования ботом
@bot.message_handler(content_types=['text'])
def text_handler(message):
    global lat, lon
    if message.text == '\U0001F3E2 City':
        bot.send_message(message.chat.id, 'What method you want to use? \U0001F9D0',
                         reply_markup=keyboard_choose_city)
    elif message.text == '\U0001F4DD File city':
        bot.send_message(message.chat.id, 'Now or forecast? \U0001F9E0', reply_markup=keyboard_file_city)
    elif message.text == '\U0001F50E Find city':
        send = bot.send_message(message.chat.id, 'Write the name of the city and '
                                                 'adres you want to choose \U0000270F')
        bot.register_next_step_handler(send, find_city)
    elif message.text == '\U0001F447 File.Fact':
        try:
            with open('data/city_now') as f:
                json_city = json.loads(f.read())
            lat = json_city['lat']
            lon = json_city['lon']
            answer = pars_day_now(lat, lon)
            bot.send_message(message.chat.id, answer, parse_mode='HTML', disable_web_page_preview=True,
                             reply_markup=keyboard_main)
        except:
            bot.send_message(message.chat.id, "\U000026A0 Error", reply_markup=keyboard_main)
    elif message.text == '\U0001F449 File.Forecast':
        try:
            with open('data/city_now') as f:
                json_city = json.loads(f.read())
            lat = json_city['lat']
            lon = json_city['lon']
            answer = pars_day_forecast(lat, lon)
            bot.send_message(message.chat.id, answer, parse_mode='HTML', disable_web_page_preview=True,
                             reply_markup=keyboard_main)
        except:
            bot.send_message(message.chat.id, "\U000026A0 Error", reply_markup=keyboard_main)
    elif message.text == '\U0001F447 Find.Fact':
        try:
            answer = pars_day_now(lat, lon)
            bot.send_message(message.chat.id, answer, parse_mode='HTML', disable_web_page_preview=True,
                             reply_markup=keyboard_main)
        except:
            bot.send_message(message.chat.id, "\U000026A0 Error", reply_markup=keyboard_main)
    elif message.text == '\U0001F449 Find.Forecast':
        try:
            answer = pars_day_forecast(lat, lon)
            bot.send_message(message.chat.id, answer, parse_mode='HTML', disable_web_page_preview=True,
                             reply_markup=keyboard_main)
        except:
            bot.send_message(message.chat.id, "\U000026A0 Error", reply_markup=keyboard_main)
    elif message.text == '\U0001F447 L.Fact':
        try:
            answer = pars_day_now(lat, lon)
            bot.send_message(message.chat.id, answer, parse_mode='HTML', disable_web_page_preview=True,
                             reply_markup=keyboard_main)
        except:
            bot.send_message(message.chat.id, "\U000026A0 Error", reply_markup=keyboard_main)
    elif message.text == '\U0001F449 L.Forecast':
        try:
            answer = pars_day_forecast(lat, lon)
            bot.send_message(message.chat.id, answer, parse_mode='HTML', disable_web_page_preview=True,
                             reply_markup=keyboard_main)
        except:
            bot.send_message(message.chat.id, "\U000026A0 Error", reply_markup=keyboard_main)
    elif message.text == '\U00002699 Settings':
        bot.send_message(message.chat.id, "What do you want? \U0001F913", reply_markup=keyboard_settings)
    elif message.text == '\U0000267B Change city':
        send = bot.send_message(message.chat.id, 'Your choice? \U0001F9D0', reply_markup=keyboard_change_city)
        bot.register_next_step_handler(send, change_city)
    else:
        bot.send_message(message.chat.id, "I don't understand \U0001F92A", reply_markup=keyboard_main)


########################################################################################################################
# обрабатывает локацию сохраняя данные в глобальные переменные, и предлагая варианты парса дальше
@bot.message_handler(content_types=['location'])
def command_handler(message):
    global lat, lon
    lon = message.location.longitude
    lat = message.location.latitude
    bot.send_message(message.chat.id, 'Now or forecast? \U0001F9E0', reply_markup=keyboard_location)


# эскизы клавиатур
keyboard_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
but1 = types.KeyboardButton('\U0001F3E2 City')
but2 = types.KeyboardButton('\U0001F4E1 Location', request_location=True)
but3 = types.KeyboardButton('\U00002699 Settings')
keyboard_main.row(but1, but2)
keyboard_main.row(but3)

keyboard_location = types.ReplyKeyboardMarkup(resize_keyboard=True)
but4 = types.KeyboardButton('\U0001F447 L.Fact')
but5 = types.KeyboardButton('\U0001F449 L.Forecast')
keyboard_location.row(but4, but5)

keyboard_file_city = types.ReplyKeyboardMarkup(resize_keyboard=True)
but61 = types.KeyboardButton('\U0001F447 File.Fact')
but71 = types.KeyboardButton('\U0001F449 File.Forecast')
keyboard_file_city.row(but61, but71)

keyboard_find_city = types.ReplyKeyboardMarkup(resize_keyboard=True)
but62 = types.KeyboardButton('\U0001F447 Find.Fact')
but72 = types.KeyboardButton('\U0001F449 Find.Forecast')
keyboard_find_city.row(but62, but72)

keyboard_settings = types.ReplyKeyboardMarkup(resize_keyboard=True)
but8 = types.KeyboardButton('\U0000267B Change city')
keyboard_settings.row(but8)

keyboard_change_city = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
but9 = types.KeyboardButton('\U00002328 Find city')
but10 = types.KeyboardButton('\U0001F6F0 Location point', request_location=True)
keyboard_change_city.row(but9, but10)

keyboard_choose_city = types.ReplyKeyboardMarkup(resize_keyboard=True)
but11 = types.KeyboardButton('\U0001F4DD File city')
but12 = types.KeyboardButton('\U0001F50E Find city')
keyboard_choose_city.row(but11, but12)


# глобальные переменные
lat = 56
lon = 37

"""
users = {}
if message.chat.id in users:
    <code>
else:
    bot.send_message(message.chat.id, '\U000026D4\U000026D4\U000026D4 '
                                      'Authorisation Error \U000026D4\U000026D4\U000026D4 \n'
                                      'If you want to use these bot or see how it works you can contact with '
                                      '@RUDIK1317')
"""

if __name__ == "__main__":
    bot.polling(none_stop=True)
