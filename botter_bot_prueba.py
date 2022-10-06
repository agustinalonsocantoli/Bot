from datetime import datetime
from email import message
from lib2to3.pgen2 import token
from tkinter import Button
import types
import telebot
import requests


#Token de indetificación
token = "5420608268:AAHmtRiwizz4Mpmbuy2GQEuHt4hZhT5Wsp0"
bot = telebot.TeleBot(token)     


#Creo variable de current date
fecha_hora = datetime.today() 

def informar_dia():

    # crear variable para el dia de semana
    dia_semana = fecha_hora.weekday()

    # diccionario con nombres de dias
    calendario = {0: 'Lunes',
                  1: 'Martes',
                  2: 'Miércoles',
                  3: 'Jueves',
                  4: 'Viernes',
                  5: 'Sábado',
                  6: 'Domingo'}

    # decir el dia de la semana
    dia = calendario[dia_semana]
    return dia


#Se estable comando '/hora'
@bot.message_handler(commands=["start"])  
def enviar(message):
    #Se aplica formato a la respuesta
    bot.reply_to(message, f"Hola!!\nHoy es {informar_dia()} {fecha_hora.strftime('%d')} del {fecha_hora.strftime('%m')} y son las {fecha_hora.strftime('%H:%M:%S')}")


@bot.message_handler(commands=["ayuda"])
def mensaje(message):
    bot.reply_to(message, 'En que puedo ayudarte')

    
#Mantiene actividad del bot
bot.polling() 