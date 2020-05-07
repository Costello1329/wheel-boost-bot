from django.urls import path
from BotService.views import bot


urlpatterns = [
    path('', bot, name='bot')
]
