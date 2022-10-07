from datetime import datetime
from distutils.log import error
from gc import callbacks
from lib2to3.pgen2 import token
import telebot
import threading
# import locale # LENGUAJE ESPAÑOL
# locale.setlocale(locale.LC_ALL, 'es-ES')
from telebot.types import ReplyKeyboardMarkup # CREAR BOTONES
from telebot.types import ForceReply # RESPONDER A LOS MENSAJES DEL BOT
from telebot.types import ReplyKeyboardRemove # ELIMINAR BOTONES DESPUES DE USARLOS
from telebot.types import InlineKeyboardMarkup # CREAMOS BOTONERA
from telebot.types import InlineKeyboardButton # DEFINIMOS BOTONES

# TOKEN IDENTIFICACION
token = "5420608268:AAHmtRiwizz4Mpmbuy2GQEuHt4hZhT5Wsp0"
bot = telebot.TeleBot(token)     


# VARIABLE FECHA Y HORA
fecha_hora = datetime.today() 

#LISTA USUARIOS
usuarios = {}


# COMANDO START SALUDA
@bot.message_handler(commands=["start"])  
def cmd_start(message):
    #BOT INICIA Y SALUDA
    markup = ReplyKeyboardRemove()
    bot.send_message(message.chat.id, f"Hola soy Botter!!\nEstoy aqui para ayudarle presione /usuario para cargar sus datos!",
    reply_markup=markup)


# COMANDO usuario
@bot.message_handler(commands=["usuario"])  
def cmd_usuario(message):
    #BOT PREGUNTA DATOS DEL USUARIO
    markup = ForceReply()
    mensaje_usuario = bot.send_message(message.chat.id, f"Como es tu nombre?", reply_markup=markup)
    bot.register_next_step_handler(mensaje_usuario, preguntar_apellido)

    
def preguntar_apellido(message):
    
    usuarios[message.chat.id] = {}
    usuarios[message.chat.id]["nombre"] = message.text
    global nombre 
    nombre = usuarios[message.chat.id]["nombre"]
    markup = ForceReply()
    mensaje_usuario = bot.send_message(message.chat.id, f"Un gusto {nombre}, como es tu apellido?", reply_markup= markup)
    bot.register_next_step_handler(mensaje_usuario, confirmar_datos)
        

def confirmar_datos(message):
    # MOSTRAMOS DATOS, DEFINIMOS BOTONES DE CONFIRMACION
    usuarios[message.chat.id]["apellido"] = message.text
    global apellido 
    apellido = usuarios[message.chat.id]["apellido"]
    markup = ReplyKeyboardMarkup(
       one_time_keyboard=True,
       input_field_placeholder="Pulsa un boton",
       resize_keyboard=True
       )
    markup.add("Si", "No")
    global datos
    datos = bot.send_message(message.chat.id, f"Nombre: {nombre}\nApellido: {apellido}\nTus datos son correcto?", reply_markup=markup)
    bot.register_next_step_handler(datos, guardar_datos)
    

def guardar_datos(message):
    # COMPROBAMOS QUE LA ENTRADA SEA VALIDA
    markup = ReplyKeyboardRemove()

    if message.text != "Si" and message.text != "No":
        mensaje_usuario = bot.send_message(message.chat.id, "ERROR: Debe pulsar uno de los dos botoness!")
        bot.register_next_step_handler(mensaje_usuario, guardar_datos)
    elif message.text == "Si":
        bot.send_message(message.chat.id, f"{nombre} {apellido} pulse /ayuda para ver las opciones", reply_markup=markup)
        del usuarios[message.chat.id]
    elif message.text == "No":
        bot.send_message(message.chat.id, "Porfavor vuelva a ingresar sus datos pulsando /usuario", reply_markup=markup)



# COMANDO OPCIONES
@bot.message_handler(commands=["ayuda"])  
def cmd_ayuda(message):
    try:
        #BOT DESPLEGA LAS OPCIONES CON BOTONES PARA QUE EL USUARIO SELECCIONE
        # markup = ReplyKeyboardRemove()
        markup = InlineKeyboardMarkup(row_width=1)
        b1 = InlineKeyboardButton("DIVISION DE GASTOS", url="https://www.splitwise.com/l/c/su/pauS8uxygQU")
        b2 = InlineKeyboardButton("LOCALIZACION FACIL", url="https://www.google.es/maps/?hl=es")
        b3 = InlineKeyboardButton("HORA", callback_data="hora")
        b4 = InlineKeyboardButton("FECHA", callback_data="fecha")
        b5 = InlineKeyboardButton("CERRAR", callback_data="cerrar")

        markup.add(b1, b2, b3, b4, b5)
        bot.send_message(message.chat.id, f"{nombre} {apellido} En que puedo ayudarlo", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "Debe ingresar sus datos, pulse /usuario")



@bot.callback_query_handler(func=lambda x: True)
def respuesta_botones(call):
    # VARIABLES PARA LA FECHA Y HORA
    dia = f"{fecha_hora.strftime('%A')} {fecha_hora.strftime('%d')}"
    hora = fecha_hora.strftime('%H:%M:%S')
    mes = fecha_hora.strftime('%B').capitalize()
    anio= fecha_hora.strftime('%Y')
    mensaje_fecha = f"Hoy es {dia} de {mes} Año {anio}"
    mensaje_hora = f"Son las {hora}"

    # GESTIONAR LAS ACCIONES DE LOS BOTONES CALLBACK DATA
    cid = call.from_user.id  # CHAT ID 
    mid = call.message.id  # MENSAJE ID
    if call.data == "cerrar":
        bot.delete_message(cid, mid)
    elif call.data == "hora":
        bot.send_message(cid, mensaje_hora)
    elif call.data == "fecha":
        bot.send_message(cid, mensaje_fecha)



## BOT REACCIONA AL TEXTO DEL USUARIO QUE NO SON COMANDOS
@bot.message_handler(content_types=["text"])
def bot_mensaje_texto(message):

    if message.text and message.text.startswith("/"):
        bot.send_message(message.chat.id, "Comando no definido")
    else:
        bot.send_message(message.chat.id, "No entiendo lo que quieres decir, ingresa /ayuda")



# FUNCION BUCLE INFINITO VERIFICA LA RECEPCION DE MENSAJES
def recibir_mensajes():
    bot.infinity_polling()

# INICIA BOT EN CLASE MAIN
if __name__ == '__main__':

    # MOSTRAR LOS COMANDOS EN TELEGRAM
    bot.set_my_commands([
        telebot.types.BotCommand("start", "Inicia el Bot"),
        telebot.types.BotCommand("usuario", "Completar Datos"),
        telebot.types.BotCommand("ayuda", "Opciones del Bot")
    ])

    # HILO BOT DEFINIDO PARA EJECUTAR LA FUNCION EN SEGUNDO PLANO Y CONTINUAR EL CODIGO 
    hilo_bot = threading.Thread(name="hilo_bot", target=recibir_mensajes)
    hilo_bot.start()

