from lib2to3.pgen2 import token
import telebot
from telebot.types import ReplyKeyboardMarkup # CREAR BOTONES
from telebot.types import ForceReply # RESPONDER A LOS MENSAJES DEL BOT
from telebot.types import ReplyKeyboardRemove # ELIMINAR BOTONES DESPUES DE USARLOS


personas = []
gastos = []
personas_cargadas = []
gastos_divididos = []
personas_gastos_divididos = []

# TOKEN IDENTIFICACION
token = "5420608268:AAHmtRiwizz4Mpmbuy2GQEuHt4hZhT5Wsp0"
bot = telebot.TeleBot(token)

# COMANDO START SALUDA
@bot.message_handler(commands=["start"])  
def cmd_start(message):
    # BOT INICIA Y SALUDA
    bot.send_message(message.chat.id, f"Hola")


## BOT REACCIONA AL TEXTO DEL USUARIO QUE NO SON COMANDOS
@bot.message_handler(func=lambda x: True)
def preguntar_nombre(message):
        markup = ForceReply()
        mensaje_nombre = bot.send_message(message.chat.id, f"Ingrese nombre?", reply_markup=markup)
        bot.register_next_step_handler(mensaje_nombre, preguntar_gasto)

    
def preguntar_gasto(message):
    
    global nombre
    nombre = message.text
    personas.append(nombre)
    markup = ForceReply()
    mensaje_gasto = bot.send_message(message.chat.id, f"{nombre} Ingrese gasto sin signo $", reply_markup= markup)
    bot.register_next_step_handler(mensaje_gasto, continuar_finalizar)
        

def continuar_finalizar(message):
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
    bot.register_next_step_handler(datos, guardar_datos)


def guardar_datos(message):
    # COMPROBAMOS QUE LA ENTRADA SEA VALIDA
    markup = ReplyKeyboardRemove()

    if message.text != "Agregar" and message.text != "Finalizar":
        mensaje_usuario = bot.send_message(message.chat.id, "ERROR: Debe pulsar uno de los dos botoness!")
        bot.register_next_step_handler(mensaje_usuario, guardar_datos)
    elif message.text == "Finalizar":
        indice = 0
        for n in personas:
            for g in gastos:
                if indice <= len(personas)-1 or indice <= len(gastos)-1:
                    personas_cargadas.append(f"Nombre: {personas[indice]} - Gasto: ${gastos[indice]}")
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
                        personas_gastos_divididos.append(f"{personas[indice]} - PAGAR (${gastos_divididos[indice] * -1})")
                    elif gastos_divididos[indice] > 0:
                        personas_gastos_divididos.append(f"{personas[indice]} - COBRAR (${gastos_divididos[indice]})")
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
                                mostrar_cancelaciones = f"{personas[comienzo]} le debe {final} a {personas[contador]}"
                                bot.send_message(message.chat.id, mostrar_cancelaciones)

                        contador += 1

                contador = 0
                comienzo += 1
            else:
                break

    elif message.text == "Agregar":
        mensaje_usuario = bot.send_message(message.chat.id, "Bien, continuemos", reply_markup=markup)
        bot.register_next_step_handler(mensaje_usuario, preguntar_nombre)
      




bot.infinity_polling()

