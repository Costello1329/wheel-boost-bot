from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from WheelBoostBot.settings import CONSTANCE_CONFIG
import requests
import telebot


TOKEN = CONSTANCE_CONFIG['TOKEN']
tbot = telebot.TeleBot(TOKEN)

def create_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = telebot.types.KeyboardButton(text='Отправить местоположение', request_location=True)
    keyboard.add(button)
    return keyboard

def create_maps_link(lat, lon):
    return '{}pt={},{}'.format(CONSTANCE_CONFIG['MAP_URL'], lat, lon)

@csrf_exempt
def bot(request):
    if request.META['CONTENT_TYPE'] == 'application/json':
        json_data = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_data)
        tbot.process_new_updates([update])
        return HttpResponse("")
    else:
        raise PermissionDenied

@tbot.message_handler(commands=['start'])
def start(message):
    keyboard = create_keyboard()
    tbot.send_message(message.chat.id, 'Привет! Нет заказов? Передай мне свое местоположение и я постараюсь помочь!',
                      reply_markup=keyboard)

@tbot.message_handler(content_types=['location'])
def location(message):
    # TODO: add empty response handler
    response = requests.post(CONSTANCE_CONFIG['EVENTS_URL'] + 'get_events_service',
                             json={'coordinates': '{}, {}'.format(message.location.latitude,
                                                                  message.location.longitude)})
    keyboard = create_keyboard()
    for event in response.json():
        # TODO: validation
        title = event.title
        description = event.description
        price = event.price
        peopleCount = event.peopleCount
        startTime = event.sttartTime
        endTime = event.endTime
        lat, lon = event.coordinates.split(', ')
        link = create_maps_link(lat, lon)
        response_text = 'Название: {}\n' \
                        'Описание: {}\n' \
                        'Цена билета: {}\n' \
                        'Время начала: {}\n' \
                        'Время конца: {}\n' \
                        'Число посетителей: {}\n' \
                        'Карта: {}'.format(
            title, description, price, startTime, endTime, peopleCount, link
        )
        tbot.send_message(message.chat.id, response_text, reply_markup=keyboard)
