import requests  # для работы с get запросами
import json  # для работы с джосоном
import datetime  # для перевода времени из юникс в норм
from geopy.geocoders import Nominatim  # для определения адреса
import geopy
import os

YANDEX_TOKEN = os.getenv("YANDEX_TOKEN")


# делает запрос яндексу и получает json +
def yandex_weather(lat='55.75396', lon='37.620393', show=0):
    req = requests.get(f'https://api.weather.yandex.ru/v2/informers?lat={lat}&lon={lon}',
                       headers={'X-Yandex-API-Key': YANDEX_TOKEN})
    req_json = json.loads(req.text)
    if show == 1:
        print(req)
        print('YANDEX\n', json.dumps(req_json, indent=1))
    return req_json


# по юниксу дает строку даты со свременем
def decode_unix_time(timestamp=0, show=0):
    value = datetime.datetime.fromtimestamp(timestamp + 3 * 60 * 60)  # тк сервер не в россии то надо прибавить 3 часа
    time = value.strftime('%Y-%m-%d %H:%M:%S')
    if show == 1:
        print(time)
    return time


# по координатам дает строку адреса
def get_adres(lat='55.7539', lon='37.620393', show=0):
    geolocator = Nominatim(user_agent="weather")
    location = geolocator.reverse(lat + ',' + lon)
    address = ''
    try:
        country = location.raw['address']['country']
        address += country
    except:
        pass
    try:
        state = location.raw['address']['state']
        address += '-'
        address += state
    except:
        pass
    try:
        city = location.raw['address']['city']
        address += '-'
        address += city
    except:
        pass
    try:
        suburb = location.raw['address']['suburb']
        address += '-'
        address += suburb
    except:
        pass
    try:
        road = location.raw['address']['road']
        address += '-'
        address += road
    except:
        pass
    try:
        house_number = location.raw['address']['house_number']
        address += '-дом.'
        address += house_number
    except:
        pass

    if show == 1:
        print(location.raw)
        print(address)
    return address


# из джейсона формирует текстовый ответ о погоде на дынный момент
def text_day_now_from_json(json_data):
    with open('data/emoji') as f:
        emoji = json.loads(f.read())

    url = f'''<a href="{json_data['info']['url']}">ЯНДЕКС.ПОГОДА</a>'''

    time = f'''{emoji['time']} {decode_unix_time(json_data['now'])}'''

    lat = str(json_data['info']['lat'])
    lon = str(json_data['info']['lon'])
    adres = get_adres(lat, lon)
    location = f'''{emoji['location']} {adres}'''

    temp = json_data['fact']['temp']
    if temp > 0:
        temp = '+' + str(temp)
    temperature = f'''{emoji['temperature']} {temp} &#8451'''

    feels_like = json_data['fact']['feels_like']
    if feels_like > 0:
        feels_like = '+' + str(feels_like)
    feels = f'''{emoji['feels_like']} {feels_like} &#8451'''

    cond_type = json_data['fact']['condition']
    condition = f'''{emoji['condition'][cond_type]}''' * 5
    pressure_mm = f'''{emoji['pressure_mm']} {json_data['fact']['pressure_mm']} мм.рт.ст.'''

    wind_speed = f'''{emoji['wind_speed']} {json_data['fact']['wind_speed']} м/с'''
    wind_gust = f'''{emoji['wind_gust']} {json_data['fact']['wind_gust']} м/с'''
    humidity = f'''{emoji['humidity']} {json_data['fact']['humidity']} %'''

    answer = url + '\n' + time + '\n' + location + '\n' + temperature + '\n' + feels + '\n' \
        + condition + '\n' + pressure_mm + '\n' + wind_speed + '\n' + wind_gust + '\n' + humidity
    return answer


# парсит погоду которая сейчас, выдает текстом
def pars_day_now(lat='55.75396', lon='37.620393'):
    json_from_file = yandex_weather(lat, lon)
    answer = text_day_now_from_json(json_from_file)
    return answer


# он обрабатывает джейсон с данными о погоде части дня и выддает текст
def part_day_handler(json_part):
    with open('data/emoji') as f:
        emoji = json.loads(f.read())

    heading = f'''<a href="https://yandex.ru/pogoda/">{json_part['part_name'].upper()}</a>'''

    temp_min = json_part['temp_min']
    temp_max = json_part['temp_max']
    if temp_min > 0:
        temp_min = '+' + str(temp_min)
    if temp_max > 0:
        temp_max = '+' + str(temp_max)

    temperature = f'''{emoji['temp_min']} {temp_min} &#8451 {emoji['temp_max']} {temp_max} &#8451'''

    feels_like = json_part['feels_like']
    if feels_like > 0:
        feels_like = '+' + str(feels_like)
    feels = f'''{emoji['feels_like']} {feels_like} &#8451'''

    cond_type = json_part['condition']
    condition = f'''{emoji['condition'][cond_type]}''' * 5

    pressure_mm = f'''{emoji['pressure_mm']} {json_part['pressure_mm']} мм.рт.ст.'''
    wind_speed = f'''{emoji['wind_speed']} {json_part['wind_speed']} м/с'''
    wind_gust = f'''{emoji['wind_gust']} {json_part['wind_gust']} м/с'''
    humidity = f'''{emoji['humidity']} {json_part['humidity']} %'''

    precipitation = f'''{emoji['prec_mm']} {json_part['prec_mm']}мм {emoji['prec_prob']} {json_part['prec_prob']}%'''
    answer = heading + '\n' + temperature + '\n' + feels + '\n' + condition + '\n' + pressure_mm + '\n' \
        + wind_speed + '\n' + wind_gust + '\n' + humidity + '\n' + precipitation
    return answer


# из джейсона формирует текстовый ответ о погоде на весь день
def text_day_forecast_from_json(json_data):
    with open('data/emoji') as f:
        emoji = json.loads(f.read())

    url = f'''<a href="{json_data['info']['url']}">ЯНДЕКС.ПОГОДА</a>'''

    time = f'''{emoji['time']} {decode_unix_time(json_data['now'])}'''
    lat = str(json_data['info']['lat'])
    lon = str(json_data['info']['lon'])
    adres = get_adres(lat, lon)
    location = f'''{emoji['location']} {adres}'''
    sun_move = f'''{emoji['sunrise']} {json_data['forecast']['sunrise']} {emoji['sunset']} 
                   {json_data['forecast']['sunset']}'''
    answer = url + '\n' + time + '\n' + location + '\n' + sun_move + '\n\n'
    for i in json_data['forecast']['parts']:
        tmp = part_day_handler(i)
        answer = answer + tmp + '\n\n'
    return answer


# парсит погоду на целый день, выдает текстом
def pars_day_forecast(lat='55.75396', lon='37.620393'):
    json_from_file = yandex_weather(lat, lon)
    answer = text_day_forecast_from_json(json_from_file)
    return answer


def test_forecast():
    with open('data/req') as f:
        json_from_file = json.loads(f.read())
    x = text_day_forecast_from_json(json_from_file)
    return x


def test_now():
    with open('data/req') as f:
        json_from_file = json.loads(f.read())
    x = text_day_now_from_json(json_from_file)
    return x


# ищет город в базе данных и в файле конфигурации города меняет город
def find_lanlon_city(city_name='Moscow', show=0):
    geolocator = Nominatim(user_agent="weather")
    location = geolocator.geocode(city_name)
    if show == 1:
        print(location.address)
        print(location.latitude, location.longitude)
    adres = location.address
    lat = location.latitude
    lon = location.longitude
    return {'adres': adres, 'lat': lat, 'lon': lon}


if __name__ == "__main__":
    pass
