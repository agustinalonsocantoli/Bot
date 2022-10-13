from datetime import datetime
from email import message
from lib2to3.pgen2 import token
import telebot
import threading
import locale 
from random import choice
from telebot.types import ReplyKeyboardMarkup # CREAR BOTONES
from telebot.types import ForceReply # RESPONDER A LOS MENSAJES DEL BOT
from telebot.types import ReplyKeyboardRemove # ELIMINAR BOTONES DESPUES DE USARLOS
from telebot.types import InlineKeyboardMarkup # CREAMOS BOTONERA
from telebot.types import InlineKeyboardButton # DEFINIMOS BOTONES

# TOKEN IDENTIFICACION
token = "5420608268:AAHmtRiwizz4Mpmbuy2GQEuHt4hZhT5Wsp0"
bot = telebot.TeleBot(token)     

# LENGUAJE ESPAÑOL
locale.setlocale(locale.LC_ALL, 'es_ES')

# VARIABLE FECHA Y HORA
fecha_hora = datetime.today() 

# LISTA USUARIOS
usuarios = {}

# LISTAS PARA DIVISION DE GASTOS
personas = []
gastos = []
personas_cargadas = []
gastos_divididos = []
personas_gastos_divididos = []

# LISTA SORTEO 
lista_sorteo = []


# COMANDO START SALUDA
@bot.message_handler(commands=["start"])  
def cmd_start(message):
    #BOT INICIA Y SALUDA
    markup = ReplyKeyboardRemove()
    bot.send_message(message.chat.id, f"Hola soy Botter!!\nEstoy aqui para ayudarte.",
    reply_markup=markup)
    cmd_usuario(message)


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
    bot.register_next_step_handler(datos, guardar_usuario)
    

def guardar_usuario(message):
    # COMPROBAMOS QUE LA ENTRADA SEA VALIDA
    markup = ReplyKeyboardRemove()

    if message.text != "Si" and message.text != "No":
        mensaje_usuario = bot.send_message(message.chat.id, "ERROR: Debe pulsar uno de los dos botoness!")
        bot.register_next_step_handler(mensaje_usuario, guardar_usuario)
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
        b1 = InlineKeyboardButton("SORTEO", callback_data="sorteo")
        b2 = InlineKeyboardButton("DIVISION DE GASTOS", callback_data="division")
        b3 = InlineKeyboardButton("LOCALIZACION FACIL", url="https://www.google.es/maps/?hl=es")
        b4 = InlineKeyboardButton("HORA", callback_data="hora")
        b5 = InlineKeyboardButton("FECHA", callback_data="fecha")
        b6 = InlineKeyboardButton("CERRAR", callback_data="cerrar")

        markup.add(b1, b2, b3, b4, b5, b6)
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
    elif call.data == "division":
        mensaje_division = bot.send_message(cid, "Podemos iniciar")
        preguntar_persona(mensaje_division)
    elif call.data == "sorteo":
        inicio_sorteo = bot.send_message(cid, "Es hora de comenzar")
        definir_marcador(inicio_sorteo)
        



def preguntar_persona(message):
    markup = ForceReply()
    mensaje_nombre = bot.send_message(message.chat.id, f"Ingrese nombre?", reply_markup=markup)
    bot.register_next_step_handler(mensaje_nombre, preguntar_gasto)

    
def preguntar_gasto(message):
    
    global nombre
    nombre = message.text
    personas.append(nombre)
    markup = ForceReply()
    mensaje_gasto = bot.send_message(message.chat.id, f"{nombre} Ingrese gasto!", reply_markup= markup)
    bot.register_next_step_handler(mensaje_gasto, continuar_finalizar)
        

def continuar_finalizar(message):

    try:
        # MOSTRAMOS DATOS, DEFINIMOS BOTONES DE CONFIRMACION
        global gasto
        gasto = float(message.text)
        gastos.append(gasto)
        markup = ReplyKeyboardMarkup(
        one_time_keyboard=True,
        input_field_placeholder="Pulsa un boton",
        resize_keyboard=True
        )
        markup.add("Agregar", "Finalizar")
        global datos
        datos = bot.send_message(message.chat.id, f"Nombre: {nombre}\nGasto: ${gasto}\n", reply_markup=markup)
        bot.register_next_step_handler(datos, guardar_personas)
    except:
        datos_error = bot.send_message(message.chat.id, "Debe ingresar un numero")
        preguntar_gasto(datos_error)


def guardar_personas(message):
    # COMPROBAMOS QUE LA ENTRADA SEA VALIDA
    markup = ReplyKeyboardRemove()

    if message.text != "Agregar" and message.text != "Finalizar":
        mensaje_usuario = bot.send_message(message.chat.id, "ERROR: Debe pulsar uno de los dos botoness!")
        bot.register_next_step_handler(mensaje_usuario, guardar_personas)
    elif message.text == "Finalizar":
        indice = 0
        for n in personas:
            for g in gastos:
                if indice <= len(personas)-1 or indice <= len(gastos)-1:
                    personas_cargadas.append(f"{personas[indice]} - Gasto: ${gastos[indice]}")
                    indice += 1
                else:
                    break
        
        mostrar_personas_cargadas = "\n".join(personas_cargadas)
        bot.send_message(message.chat.id, mostrar_personas_cargadas, reply_markup=markup)

        suma_gastos = 0
        for gasto in gastos:
            suma_gastos += gasto
        personas_a_dividir = len(personas)
        bot.send_message(message.chat.id, f"Total ${suma_gastos}, son {personas_a_dividir} para dividir")

        total_cada_uno = round(suma_gastos / personas_a_dividir, 2)
        bot.send_message(message.chat.id, f"${total_cada_uno} cada uno")

        indice = 0
        for g in gastos:
            resultado = g - total_cada_uno
            indice += 1
            gastos_divididos.append(resultado)

        comienzo = 0
        contador = 0

        indice = 0
        for n in personas:
            for g in gastos:
                if indice <= len(personas)-1 or indice <= len(gastos)-1:
                    if gastos_divididos[indice] < 0:
                        personas_gastos_divididos.append(f"{personas[indice]} - PAGA (${gastos_divididos[indice] * -1})")
                    elif gastos_divididos[indice] > 0:
                        personas_gastos_divididos.append(f"{personas[indice]} - RECIBE (${gastos_divididos[indice]})")
                    indice += 1

        mostrar_division_final = "\n".join(personas_gastos_divididos)
        bot.send_message(message.chat.id, mostrar_division_final)

        while True:
            if comienzo <= personas_a_dividir - 1:
                for g in gastos_divididos:
                    if contador <= personas_a_dividir - 1:
                        
                        if gastos_divididos[comienzo] != 0 and gastos_divididos[contador] != 0:
                            if gastos_divididos[comienzo] < 0 and gastos_divididos[contador] > 0:
                                comparacion = gastos_divididos[comienzo] + gastos_divididos[contador]
                                if comparacion < 0:
                                    final = gastos_divididos[contador]
                                    gastos_divididos[comienzo] = comparacion
                                    gastos_divididos[contador] = 0.0
                                elif comparacion > 0:
                                    final = gastos_divididos[comienzo] * -1
                                    gastos_divididos[contador] = comparacion
                                    gastos_divididos[comienzo] = 0.0
                                elif comparacion == 0:
                                    final = gastos_divididos[comienzo] * -1
                                    gastos_divididos[contador] = 0.0
                                    gastos_divididos[comienzo] = 0.0
                                mostrar_cancelaciones = f"{personas[comienzo]} debe {final} a {personas[contador]}"
                                bot.send_message(message.chat.id, mostrar_cancelaciones)

                        contador += 1

                contador = 0
                comienzo += 1
            else:
                break

    elif message.text == "Agregar":
        preguntar_persona(message)
        

def definir_marcador(message):
    markup = ForceReply()
    mensaje_sorteo = bot.send_message(message.chat.id, f"Nombre o Inicial", reply_markup=markup)
    bot.register_next_step_handler(mensaje_sorteo, agregar_sortear)


def agregar_sortear(message):
    # MOSTRAMOS DATOS, DEFINIMOS BOTONES DE CONFIRMACION
    global marcador
    marcador = message.text
    lista_sorteo.append(marcador)
    markup = ReplyKeyboardMarkup(
    one_time_keyboard=True,
    input_field_placeholder="Pulsa un boton",
    resize_keyboard=True
    )
    markup.add("Agregar", "Sortear")
    global eleccion
    eleccion = bot.send_message(message.chat.id, f"Cargo a: {marcador}", reply_markup=markup)
    bot.register_next_step_handler(eleccion, guardar_sorteo)


def guardar_sorteo(message):
    # COMPROBAMOS QUE LA ENTRADA SEA VALIDA
    if message.text != "Agregar" and message.text != "Sortear":
        mensaje_sorteo = bot.send_message(message.chat.id, "ERROR: Debe pulsar uno de los dos botoness!")
        bot.register_next_step_handler(mensaje_sorteo, guardar_personas)
    elif message.text == "Sortear":
        mostrar_lista = "\n".join(lista_sorteo)
        resultado_sorteo = choice(lista_sorteo)
        bot.send_message(message.chat.id, f"{mostrar_lista}\n\nHa salido sorteado \"{resultado_sorteo}\"")
    elif message.text == "Agregar":
        definir_marcador(message)



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

