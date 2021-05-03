import requests  # для работы с get запросами
import json  # для работы с джосоном
import datetime  # для перевода времени из юникс в норм
import os
from geopy.geocoders import Nominatim  # для определения адреса

YANDEX_TOKEN = os.getenv("YANDEX_TOKEN")


class WEATHER:
    def __init__(self, latitude: str, longitude: str):
        self.json = None
        self.lat = latitude
        self.lon = longitude

    def request(self) -> None:
        req = requests.get(f'https://api.weather.yandex.ru/v2/informers?lat={self.lat}&lon={self.lon}',
                           headers={'X-Yandex-API-Key': YANDEX_TOKEN})
        self.json = json.loads(req.text)

    def now(self) -> str:
        self.request()
        with open('data/emoji') as f:
            emoji = json.loads(f.read())

        url = f'''<a href="{self.json['info']['url']}">ЯНДЕКС.ПОГОДА</a>'''
        time = f'''{emoji['time']} {decode_unix_time(self.json['now'])}'''
        location = f'''{emoji['location']} {self.get_adress()}'''
        temp = self.json['fact']['temp']
        if temp > 0:
            temp = '+' + str(temp)
        temperature = f'''{emoji['temperature']} {temp} &#8451'''
        feels_like = self.json['fact']['feels_like']
        if feels_like > 0:
            feels_like = '+' + str(feels_like)
        feels = f'''{emoji['feels_like']} {feels_like} &#8451'''
        cond_type = self.json['fact']['condition']
        condition = f'''{emoji['condition'][cond_type]}''' * 5
        pressure_mm = f'''{emoji['pressure_mm']} {self.json['fact']['pressure_mm']} мм.рт.ст.'''
        wind_speed = f'''{emoji['wind_speed']} {self.json['fact']['wind_speed']} м/с'''
        wind_gust = f'''{emoji['wind_gust']} {self.json['fact']['wind_gust']} м/с'''
        humidity = f'''{emoji['humidity']} {self.json['fact']['humidity']} %'''

        weather_now_text = f'{url}\n' \
                           f'{time}\n' \
                           f'{location}\n' \
                           f'{temperature}\n' \
                           f'{feels}\n' \
                           f'{condition}\n' \
                           f'{pressure_mm}\n' \
                           f'{wind_speed}\n' \
                           f'{wind_gust}\n' \
                           f'{humidity}'
        return weather_now_text

    def part_of_day(self, json_part) -> str:
        with open('data/emoji') as f:
            emoji = json.loads(f.read())

        heading = f'''<a href="{self.json['info']['url']}">{json_part['part_name'].upper()}</a>'''
        temp_min = json_part['temp_min']
        if temp_min > 0:
            temp_min = '+' + str(temp_min)
        temp_max = json_part['temp_max']
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
        precipitation = f"{emoji['prec_mm']} {json_part['prec_mm']}мм {emoji['prec_prob']} {json_part['prec_prob']}%"

        weather_part_of_day = f'{heading}\n' \
                              f'{temperature}\n' \
                              f'{feels}\n' \
                              f'{condition}\n' \
                              f'{pressure_mm}\n' \
                              f'{wind_speed}\n' \
                              f'{wind_gust}\n' \
                              f'{humidity}\n' \
                              f'{precipitation}'
        return weather_part_of_day

    def day(self) -> str:
        self.request()
        with open('data/emoji') as f:
            emoji = json.loads(f.read())

        url = f'''<a href="{self.json['info']['url']}">ЯНДЕКС.ПОГОДА</a>'''
        time = f'''{emoji['time']} {decode_unix_time(self.json['now'])}'''
        location = f'''{emoji['location']} {self.get_adress()}'''
        sun_move = f'''{emoji['sunrise']} {self.json['forecast']['sunrise']} {emoji['sunset']} {self.json['forecast']['sunset']}'''

        weather_day_text = f'{url}\n' \
                           f'{time}\n' \
                           f'{location}\n' \
                           f'{sun_move}\n\n'
        for i in self.json['forecast']['parts']:
            weather_day_text = weather_day_text + self.part_of_day(i) + '\n\n'
        return weather_day_text

    def get_adress(self) -> str:
        geolocator = Nominatim(user_agent="weather")
        location = geolocator.reverse(self.lat + ',' + self.lon)
        address = location.raw['address']
        address_text = ''
        if 'house_number' in address:
            address_text += 'дом ' + address['house_number'] + '-'
        if 'road' in address:
            address_text += address['road'] + '-'
        if 'suburb' in address:
            address_text += address['suburb'] + '-'
        if 'city' in address:
            address_text += address['city'] + '-'
        if 'state' in address:
            address_text += address['state'] + '-'
        if 'country' in address:
            address_text += address['country']
        return address_text


def decode_unix_time(timestamp=0) -> str:
    """
        Convert unix_time to normal string_time.
        '%Y-%m-%d %H:%M:%S'
    """
    value = datetime.datetime.fromtimestamp(timestamp)
    time_text = value.strftime('%Y-%m-%d %H:%M:%S')
    return time_text


def find_city(city_name: str) -> dict:
    """
    Find city using City_name.
    And get dict{'address': address, 'lat': lat, 'lon': lon}
    """
    geolocator = Nominatim(user_agent="weather")
    location = geolocator.geocode(city_name)
    address = location.address
    lat = str(location.latitude)
    lon = str(location.longitude)
    return {'address': address, 'lat': lat, 'lon': lon}


if __name__ == "__main__":
    pass
    x = find_city('1')
    print(type(x['lat']))
