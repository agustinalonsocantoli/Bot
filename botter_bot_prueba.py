from datetime import datetime
from email import message
from lib2to3.pgen2 import token
from unicodedata import name
import telebot
import threading
# Se establece lenguaje Español
import locale
locale.setlocale(locale.LC_ALL, 'es-ES')
from telebot.types import ReplyKeyboardMarkup # Para crear botones
from telebot.types import ForceReply # Se utiliza para responder a los mensajes del bot

# Token de indetificación
token = "5420608268:AAHmtRiwizz4Mpmbuy2GQEuHt4hZhT5Wsp0"
bot = telebot.TeleBot(token)     


# Creo variable de current date
fecha_hora = datetime.today() 
#Variable global para guardar datos de usuarios
usuarios = {}

#Se aplica saludo a comando start
@bot.message_handler(commands=["start"])  
def cmd_start(message):
    #Incio del bot saludando y preguntando nombre
    markup = ForceReply()
    mensaje = bot.send_message(message.chat.id, f"Hola soy Botter!!\nCómo te llamas?", reply_markup= markup)
    bot.send_chat_action(message.chat.id, "typing")
    bot.register_next_step_handler(mensaje, preguntar_edad)
    

def preguntar_edad(message):
    # Se Pregunta la edad
    usuarios[message.chat.id]={}
    usuarios[message.chat.id]["nombre"]= message.text
    bot.send_chat_action(message.chat.id, "typing")
    markup = ForceReply()
    mensaje = bot.send_message(message.chat.id, f"Un gusto "+ usuarios[message.chat.id]["nombre"]+"\nQué edad tienes?", reply_markup= markup)
    bot.register_next_step_handler(mensaje, corroborar_datos)
        
def corroborar_datos(message):
    #Se verifica que los datos para edad sean numéricos
    if not message.text.isdigit():
        #Informamos el error
        markup = ForceReply()
        mensaje = bot.send_message(message.chat.id, "Debes ingresar solo números para tu edad")  
        bot.register_next_step_handler(mensaje, corroborar_datos)
    else:
        # Guardamos la edad correcta
        usuarios[message.chat.id]["edad"]= int(message.text)
        # Creamos un markup para el formato de botonera
        markup = ReplyKeyboardMarkup(
            one_time_keyboard=True, 
            input_field_placeholder="Pulsa un botón"
            )
        #Añadimos los botones
        markup.add("Si", "No")
        mensaje = bot.send_message(message.chat.id, f"Genial!\nEstos son tus Datos?\n{usuarios[message.chat.id]['nombre']}\n{usuarios[message.chat.id]['edad']}", reply_markup=markup)
        bot.register_next_step_handler(mensaje, guardar_datos)

def guardar_datos(message):
    #Comprobamos que la entrada de opciones sea válida 
    if message.text != "Si" and message.text != "No":
        mensaje = bot.send_message(message.chat.id, "ERROR: Debe pulsar uno de los dos botoness!")
        bot.register_next_step_handler(mensaje, guardar_datos)
    #Si elegimos 'No' comenzaremos desde el inicio (a optimizar)
    elif not message.text == "Si":
         bot.register_next_step_handler(message, cmd_start)

             
        
## CONTINUA MANTENIENDO LA FUNCIONALIDA AL ESCRIBIR 'HORA' O "FECHA"
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


