from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from WheelBoostBot.settings import CONSTANCE_CONFIG
import requests
import telebot
import time
from enum import Enum
from datetime import datetime


class MessageType(Enum):
    LOCATION = 1
    THANK = 2
    PHOTO = 3

TOKEN = CONSTANCE_CONFIG['TOKEN']
tbot = telebot.TeleBot(TOKEN)

events_url = CONSTANCE_CONFIG['EVENTS_URL']

@csrf_exempt
def bot(request):
    if request.META['CONTENT_TYPE'] == 'application/json':
        json_data = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_data)
        tbot.process_new_updates([update])
        return HttpResponse("")
    else:
        raise PermissionDenied

log_file = open('log.txt', 'a')
photo_file = open('photo.txt', 'a')

def log(message, type_of_message):
    date = message.date
    uid = message.from_user.id
    username = message.from_user.username
    latitude = 0
    longitude = 0
    if type_of_message == MessageType.LOCATION:
        loc = message.location
        latitude = loc.latitude
        longitude = loc.longitude
    log_file.write('{} {} {} {} {} {}\n'.format(date, uid, username, type_of_message, latitude, longitude))
    log_file.flush()

def check_whitelist(uid):
    with open('whitelist.txt', 'r') as whitelist:
        if str(uid) in whitelist.read():
            return True
        else:
            return False

def create_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_loc = telebot.types.KeyboardButton(text='Отправить местоположение', request_location=True)
    button_thanks = telebot.types.KeyboardButton(text='Спасибо! Я получил заказ.')
    keyboard.add(button_loc)
    keyboard.add(button_thanks)
    return keyboard

def pretty_date(ugly_date):
    date = time.strptime(ugly_date, '%Y-%m-%dT%H:%M:%SZ')
    return '{}:{}'.format(date.tm_hour, date.tm_min)

@tbot.message_handler(commands=['start'])
def start_message(message):
    keyboard = create_keyboard()
    tbot.send_message(message.chat.id, 'Привет! Отправляй своё местоположение, и я поищу для тебя ближайшие места, где может быть спрос на такси бизнес-класса',
                      reply_markup=keyboard)

@tbot.message_handler(commands=['logs'])
def get_logs(message):
    if check_whitelist(message.from_user.id):
        with open('log.txt') as logs:
            res = 'Отчет:\n'
            for line in logs:
                line_array = line.split()
                format_date = datetime.utcfromtimestamp(int(line_array[0])).strftime('%Y-%m-%d %H:%M:%S')

                res += '@' + line_array[2] + ' ' + line_array[1] + ' ' + format_date + ' ' + line_array[3] + '\n'
            tbot.send_message(message.chat.id, res, reply_markup=create_keyboard())

@tbot.message_handler(content_types=['location'])
def location(message):
    print(message.location)
    response = requests.post(events_url, json={'coordinates': '{};{}'.format(message.location.latitude, message.location.longitude)})
    keyboard = create_keyboard()
    notfing = True
    count = 0
    log(message, MessageType.LOCATION)
    for event in response.json()['events']:
        count += 1
        IsInfinite = event['isInfinite']
        title = 'Название: {}\n'.format(event['title'])
        price = 'Цена билета: {}\n'.format(event['price']) if float(event['price']) > 0 else ""
        peopleCount = 'Число посетителей: {}\n'.format(event['peopleCount']) if float(event['peopleCount']) > 0 else ""
        startTime = 'Время начала: {}\n'.format(pretty_date(event['startTime'])) if not IsInfinite else ""
        endTime = 'Время конца: {}\n'.format(pretty_date(event['endTime'])) if not IsInfinite else ""
        lat, lon = event['coordinates'].split(';')
        link = 'Карта: {}pt={},{}'.format('https://yandex.ru/maps?', lon, lat)
        response_text = title + price + startTime + endTime + peopleCount + link

        tbot.send_message(message.chat.id, response_text, reply_markup=keyboard)
        notfing = False

        if count > 3:
            break
    if notfing:
        tbot.send_message(message.chat.id, 'К сожалению, по близости ничего нет', reply_markup=keyboard)

@tbot.message_handler(content_types=['text'])
def text_handler(message):
    if message.text == 'Спасибо! Я получил заказ.':
        log(message, MessageType.THANK)
        tbot.send_message(message.chat.id, 'Помогите нам сделать сервис лучше. Пришлите скриншот, подтверждающий получение заказа',
                          reply_markup=create_keyboard())

@tbot.message_handler(content_types=['photo'])
def photo_handler(message):
    log(message, MessageType.PHOTO)
    file_id = message.photo[-1].file_id
    photo_file.write(file_id + '\n')
    photo_file.flush()

    tbot.send_message(message.chat.id, 'Спасибо!', reply_markup=create_keyboard())