from datetime import datetime
from tkinter import Button
import types
import telebot
import requests

bot = telebot.TeleBot("5420608268:AAHmtRiwizz4Mpmbuy2GQEuHt4hZhT5Wsp0")     #Token de indetificación

hora = datetime.today() #Creo variable de current date


@bot.message_handler(commands=["hora"])  #Se estable comando '/hora'
def enviar(message):
    bot.reply_to(message, hora.time().strftime('%H:%M')) #Se aplica formato a la respuesta
    
bot.infinity_polling() #Mantiene actividad del bot