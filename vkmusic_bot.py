import telebot  # библиотека работы с ботом
import data_mining  # файл для парсинга информации с файла
from telebot import types  # импортирует типы из бота для использования кнопок
import sys  # для обработки ошибок
import os

# бот просто считывает файл тхт и отправляет ссылки музыки пользователю
# heroku->settings->Config Vars
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)


########################################################################################################################
# обработка команд
@bot.message_handler(commands=['help'])
def help_handler(message):
    # print(message)
    # print(message.chat.id)
    bot.send_message(message.chat.id,
                     'Hi dude. This bot help to pars vk music from two txt files(links and names) \U0001F590')


@bot.message_handler(commands=['start'])
def help_handler(message):
    if message.chat.id in users:
        bot.send_message(message.chat.id, 'What do you want? \U0001F611', reply_markup=keyboard_main)
    else:
        bot.send_message(message.chat.id, '\U000026D4\U000026D4\U000026D4 '
                                          'Authorisation Error \U000026D4\U000026D4\U000026D4 \n'
                                          'If you want to use these bot or see how it works you can contact with '
                                          '@RUDIK1317')


@bot.message_handler(commands=['y'])
def help_handler(message):
    if message.chat.id in users:
        global links_file, names_file
        bot.send_message(message.chat.id, ' Start', reply_markup=keyboard_main)
        bot.send_message(message.chat.id, 'Start parsing \U0000267B')
        links = data_mining.lists_of_track_links(links_file)
        names = data_mining.lists_of_track_names(names_file)
        # отрабатываем ошибку
        if len(names) != len(links):
            bot.send_message(message.chat.id,
                             '\U000026A0 Error. Number_Links=' + str(len(links)) +
                             '; Number_Names=' + str(len(names)))
        else:
            for i in range(0, len(links)):
                try:
                    print(i)
                    bot.send_audio(message.chat.id, links[i], caption=names[i], parse_mode='HTML')
                except Exception:
                    bot.send_message(message.chat.id, 'Error with ' + names[i], parse_mode='HTML')
                    err = '\U000026A0 ' * 3 + str(sys.exc_info()) + '\U000026A0 ' * 3
                    bot.send_message(message.chat.id,
                                     err + '\nError when pars. Check link working or name.txt line order')
            bot.send_message(message.chat.id, '\U0000270B\U0000270B\U0000270B\U0000270B\U0000270B\U0000270B')
    else:
        bot.send_message(message.chat.id, '\U000026D4\U000026D4\U000026D4 '
                                          'Authorisation Error \U000026D4\U000026D4\U000026D4 \n'
                                          'If you want to use these bot or see how it works you can contact with '
                                          '@RUDIK1317')


########################################################################################################################
# обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def text_handler(message):
    if message.chat.id in users:
        if message.text == '\U00002B07 Pars music from two file \U00002B07':
            image_file = open("doc/sample.png", 'rb')
            capt = 'Send two txt file in series: \U0001F4D5 links(savefrom..net) and ' \
                   '\U0001F4D7 titles(which was coppied from vk).This is how they should look \U0001F441'
            send = bot.send_photo(message.chat.id, image_file, caption=capt)
            bot.register_next_step_handler(send, take_links)
        else:
            bot.send_message(message.chat.id, "I don't understand \U0001F92A")
    else:
        bot.send_message(message.chat.id, '\U000026D4\U000026D4\U000026D4 '
                                          'Authorisation Error \U000026D4\U000026D4\U000026D4 \n'
                                          'If you want to use these bot or see how it works you can contact with '
                                          '@RUDIK1317')


########################################################################################################################
# мы скачиваем файл ссылок что бы потом его использовать
def take_links(message):
    if message.chat.id in users:
        global links_file
        if message.content_type == 'document':
            f_id = message.document.file_id
            get = bot.get_file(f_id)
            url = f'https://api.telegram.org/file/bot{TOKEN}/{get.file_path}'
            links_file = data_mining.download_file(url, 'doc/links.txt')
            send = bot.send_message(message.chat.id, '\U00002705 Accepted links file.Send me the names file')
            bot.register_next_step_handler(send, take_names)
        elif message.text in ['/start', '/help', '\U00002B07 Pars music from two file \U00002B07']:
            bot.send_message(message.chat.id, '\U0001F480\U0001F480\U0001F480 Reload')
        else:
            send = bot.send_message(message.chat.id, '\U0001F6AB Not document.Try again')
            bot.register_next_step_handler(send, take_names)
    else:
        bot.send_message(message.chat.id, '\U000026D4\U000026D4\U000026D4 '
                                          'Authorisation Error \U000026D4\U000026D4\U000026D4 \n'
                                          'If you want to use these bot or see how it works you can contact with '
                                          '@RUDIK1317')


# мы скачиваем файл названий что бы потом его использовать
def take_names(message):
    if message.chat.id in users:
        global links_file, names_file
        if message.content_type == 'document':
            f_id = message.document.file_id
            get = bot.get_file(f_id)
            url = f'https://api.telegram.org/file/bot{TOKEN}/{get.file_path}'
            names_file = data_mining.download_file(url, 'doc/titles.txt')
            bot.send_message(message.chat.id, '\U00002705 Accepted names file')
            bot.send_message(message.chat.id, 'If you ready write /y')
        elif message.text in ['/start', '/help', '\U00002B07 Pars music from two file \U00002B07']:
            bot.send_message(message.chat.id, '\U0001F480\U0001F480\U0001F480 Reload')
        else:
            send = bot.send_message(message.chat.id, '\U0001F6AB Not document.Try again')
            bot.register_next_step_handler(send, take_names)
    else:
        bot.send_message(message.chat.id, '\U000026D4\U000026D4\U000026D4 '
                                          'Authorisation Error \U000026D4\U000026D4\U000026D4 \n'
                                          'If you want to use these bot or see how it works you can contact with '
                                          '@RUDIK1317')


########################################################################################################################
# Шаблоны клавиатур
but1_text = '\U00002B07 Pars music from two file \U00002B07'
keyboard_main = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
but1 = types.KeyboardButton(but1_text)
keyboard_main.row(but1)

# Глобальные переменные
links_file = 'doc/test_link.txt'
names_file = 'doc/test_name.txt'

# допустимые пользователи
users = {416555145: 'Dima', 353516260: 'Vincent'}

if __name__ == "__main__":
    bot.polling(none_stop=True)
