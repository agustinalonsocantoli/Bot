from datetime import datetime
from lib2to3.pgen2 import token
import telebot
import threading
import locale
locale.setlocale(locale.LC_ALL, 'es-ES')

# Token de indetificación
token = "5420608268:AAHmtRiwizz4Mpmbuy2GQEuHt4hZhT5Wsp0"
bot = telebot.TeleBot(token)     


# Creo variable de current date
fecha_hora = datetime.today() 

# def informar_dia():

#     # crear variable para el dia de semana
#     dia_semana = fecha_hora.weekday()

#     # diccionario con nombres de dias
#     calendario = {0: 'Lunes',
#                   1: 'Martes',
#                   2: 'Miércoles',
#                   3: 'Jueves',
#                   4: 'Viernes',
#                   5: 'Sábado',
#                   6: 'Domingo'}

#     # decir el dia de la semana
#     dia = calendario[dia_semana]
#     return dia


#Se aplica saludo a comando start
@bot.message_handler(commands=["start"])  
def cmd_start(message):

    mensaje_inicio = f"Hola soy Botter!!\nEstoy para ayudarte, dime que deseas?"
    bot.send_chat_action(message.chat.id, "typing")
    bot.send_message(message.chat.id, mensaje_inicio)
    


## BOT REACCIONA AL TEXTO DEL USUARIO QUE NO SON COMANDOS
@bot.message_handler(content_types=["text"])
def bot_mensaje_texto(message):

    mensaje_datetime = f"Hoy es {fecha_hora.strftime('%A')} {fecha_hora.strftime('%d')} de {fecha_hora.strftime('%B').capitalize()} Año {fecha_hora.strftime('%Y')}\nSon las {fecha_hora.strftime('%H:%M:%S')}"

    if message.text and message.text.startswith("/"):
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, "Comando no definido")
    elif message.text.lower() == 'fecha' or message.text.lower() == 'hora':
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, mensaje_datetime)
    else:
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, "No entiendo lo que quieres decir, ingresa hora o fecha y te brindare informacion")


# Bucle infinito, verifica la recepcion de los mensajes del usuario
def recibir_mensajes():
    bot.infinity_polling()

# Inicia el bot en class main
if __name__ == '__main__':

    # Hilo BOT lo defino para ejecutar la funcion en segundo plano 
    # nos permite arrancar el bot y poder seguir haciendo cosas desde el main para que se ejecuten
    hilo_bot = threading.Thread(name="hilo_bot", target=recibir_mensajes)
    hilo_bot.start()


