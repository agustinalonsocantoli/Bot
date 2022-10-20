from turtle import width
import requests
import telebot
import datetime as dt
import threading


TOKEN = "5420608268:AAHmtRiwizz4Mpmbuy2GQEuHt4hZhT5Wsp0"
BOT = telebot.TeleBot(TOKEN)     

MAPS_URL="http://www.mapquestapi.com/directions/v2/route?"
MAPS_KEY = "AAS76Zb0bjeEQVKeGU04ZfVa3GOxVApG"

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather?"
WEATHER_KEY = "0b8141b26a23e743b2ada55752a3ec71"
CITY = "Zárate"



def kelvin_to_celsius(kelvin):
    celsius = kelvin - 273.15
    return celsius


@BOT.message_handler(commands=['tiempo'])
def weather(message):
    url = WEATHER_URL + "appid=" + WEATHER_KEY + "&q=" + CITY + "&lang=es"
    response = requests.get(url).json()

    temp_kelvin = response['main']['temp']
    temp_celsius = kelvin_to_celsius(temp_kelvin)
    BOT.send_message(message.chat.id,f"Temperatura actual {temp_celsius:.1f}°C")
    feels_like_kelvin = response['main']['feels_like']
    feels_like_celsius = kelvin_to_celsius(feels_like_kelvin)
    BOT.send_message(message.chat.id, f"Sensación térmica {feels_like_celsius:.1f}°C")
    description = response['weather'][0]['description']
    icon = response['weather'][0]['icon']
    BOT.send_message(message.chat.id,f"El pronóstico es: {description}")
    BOT.send_sticker(message.chat.id,sticker=f'http://openweathermap.org/img/wn/{icon}@2x.png')

def recibir_mensajes():
    BOT.infinity_polling()

# Inicia el bot en class main
if __name__ == '__main__':

    # Hilo BOT lo defino para ejecutar la funcion en segundo plano 
    # nos permite arrancar el bot y poder seguir haciendo cosas desde el main para que se ejecuten
    hilo_bot = threading.Thread(name="hilo_bot", target=recibir_mensajes)
    hilo_bot.start()


