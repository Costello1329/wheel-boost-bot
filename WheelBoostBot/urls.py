from django.urls import path
from BotService.views import bot
from WheelBoostBot.settings import CONSTANCE_CONFIG


urlpatterns = [
    path(CONSTANCE_CONFIG['BOT_URL'], bot, name='bot')
]
