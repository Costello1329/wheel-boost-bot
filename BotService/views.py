from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from WheelBoostBot.settings import CONSTANCE_CONFIG
import telebot

TOKEN = CONSTANCE_CONFIG['TOKEN']
tbot = telebot.TeleBot(TOKEN)

@csrf_exempt
def bot(request):
    if request.META['CONTENT_TYPE'] == 'application/json':
        json_data = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_data)
        tbot.process_new_updates([update])
        return HttpResponse("")
    else:
        raise PermissionDenied

@tbot.message_handler(content_types=["text"])
def get_echo(message):
    tbot.send_message(message.chat.id, message.text)