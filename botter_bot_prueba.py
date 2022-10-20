from config import * # IMPORTE EL TOKEN 
from datetime import datetime
import telebot
import threading
import locale # ASIGNAR IDIOMA
import urllib
from random import choice # PARA REALIZAR EL SORTEO 
from telebot.types import ReplyKeyboardMarkup # CREAR BOTONES
from telebot.types import ForceReply # RESPONDER A LOS MENSAJES DEL BOT
from telebot.types import ReplyKeyboardRemove # ELIMINAR BOTONES DESPUES DE USARLOS
from telebot.types import InlineKeyboardMarkup # CREAMOS BOTONERA
from telebot.types import InlineKeyboardButton # DEFINIMOS BOTONES
from requests import get # WEB SCRAPING 
from bs4 import BeautifulSoup # WEB SCRAPING

# TOKEN
bot = telebot.TeleBot(TELEGRAM_TOKEN)     

# NOMBRE DEL BOT
# nombre_bot = "Botter" # NOMBRE BOT TOKEN AGUS ACOSTA
nombre_bot = "EasyBot" # NOMBRE BOT TOKEN AGUS ALONSO

# LENGUAJE ESPAÑOL
locale.setlocale(locale.LC_ALL, 'es_ES')

# VARIABLES PARA LA FECHA Y HORA
fecha_hora = datetime.today() 
dia = f"{fecha_hora.strftime('%A')} {fecha_hora.strftime('%d')}"
hora = fecha_hora.strftime('%H:%M:%S')
mes = fecha_hora.strftime('%B')
anio= fecha_hora.strftime('%Y')
mensaje_fecha = f"Hoy es {dia.capitalize()} de {mes.capitalize()} del {anio}"
mensaje_hora = f"Hora actual {hora}"

# VARIABLE MENSAJE DE SALUDO 
mensaje_saludo = f"Bienvenido a {nombre_bot}!!\nPodras utilizar y aprovechar los elementos de ayuda de nuestra lista."

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

# CONSTANTES PARA LAS BUSQUEDAS DE GOOGLE
N_RES_PAG = 10 # NUMERO DE RESULTADOS A MOSTRAR EN CADA PAGINA
MAX_ANCHO_ROW = 5 # MAXIMO BOTONES POR FILA ( 8 LIMITACION TELEGRAM )

# VARIABLES PARA EL CLIMA
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather?"
WEATHER_KEY = "&appid=0b8141b26a23e743b2ada55752a3ec71"
lenguaje = "&lang=es"
unidad = "&units=metric"

# VARIABLES MAPS
api_url="http://www.mapquestapi.com/directions/v2/route?"
key = "AAS76Zb0bjeEQVKeGU04ZfVa3GOxVApG"  
origen_destino = []


# COMANDO START, INICIA EL BOT Y LLAMA LA FUNCION QUE SOLICITA NOMBRE DE USUARIO
@bot.message_handler(commands=["start"])  
def cmd_start(message):
    markup = ReplyKeyboardRemove()
    bot.send_message(message.chat.id, f'{mensaje_saludo}\n\n{mensaje_fecha}\n{mensaje_hora}', reply_markup=markup)
    cargar_nombre(message)


# <------------------   CADENA DE FUNCIONES NOMBRE DEL USUARIO -------------------->
def cargar_nombre(message):
    # PREGUNTA NOMBRE
    markup = ForceReply()
    mensaje_usuario = bot.send_message(message.chat.id, f"Dime como te llamas?", reply_markup=markup)
    bot.register_next_step_handler(mensaje_usuario, guardar_nombre)


def guardar_nombre(message):
    # GUARDA NOMBRE DEL USUARIO, NOS DIRIGE A LAS OPCIONES
    usuarios[message.chat.id] = {}
    usuarios[message.chat.id]["nombre"] = message.text
    global nombre 
    nombre = usuarios[message.chat.id]["nombre"]
    nombre = nombre.capitalize()
    datos = bot.send_message(message.chat.id, f"Continuemos {nombre}")
    cmd_ayuda(datos)
        

# <------------------   FUNCION PARA LAS OPCIONES DEL BOT -------------------->
def cmd_ayuda(message):
    # NOS MUESTRA LOS BOTONES DE LAS OPCIONES Y NOS DIRIGE AL SELECCIONADO CON UN CALLBACK
    markup = ReplyKeyboardRemove()
    markup = InlineKeyboardMarkup(row_width=1)
    b1 = InlineKeyboardButton("DIVISION DE GASTOS", callback_data="division")
    b2 = InlineKeyboardButton("SORTEO", callback_data="sorteo")
    b3 = InlineKeyboardButton("MERCADOS FINANCIEROS", callback_data="mercados")
    b4 = InlineKeyboardButton("BUSCADOR", callback_data="buscador")
    b5 = InlineKeyboardButton("LOCALIZACION", callback_data="localizacion")
    b6 = InlineKeyboardButton("CLIMA", callback_data="clima")
    b7 = InlineKeyboardButton("CERRAR", callback_data="cerrar")

    markup.add(b1, b2, b3, b4, b5, b6, b7)
    bot.send_message(message.chat.id, f"Seleccione la opcion que necesite utilizar", reply_markup=markup)


# <------------------   CADENA DE FUNCIONES PARA EL MODULO DE DIVISION DE GASTOS -------------------->
def preguntar_persona(message):
    # SE CARGA EL NOMBRE DE LA PERSONA
    markup = ForceReply()
    mensaje_nombre = bot.send_message(message.chat.id, f"Ingrese nombre?", reply_markup=markup)
    bot.register_next_step_handler(mensaje_nombre, preguntar_gasto)

    
def preguntar_gasto(message):
    # SE CARGA EL GASTO QUE REALIZO
    global nombre
    nombre = message.text
    nombre = nombre.capitalize()
    personas.append(nombre)
    markup = ForceReply()
    mensaje_gasto = bot.send_message(message.chat.id, f"{nombre} Ingrese gasto!", reply_markup= markup)
    bot.register_next_step_handler(mensaje_gasto, continuar_finalizar)
        

def continuar_finalizar(message):

    try:
        # MOSTRAMOS DATOS, DEFINIMOS BOTONES PARA AGREGAR MAS PERSONAS O FINALIZAR LAS CUENTAS
        global gasto
        gasto = float(message.text)
        gastos.append(gasto)
        markup = ReplyKeyboardMarkup(
        one_time_keyboard=True,
        input_field_placeholder="Pulsa un boton",
        resize_keyboard=True)
        markup.add("Agregar", "Finalizar")
        global datos
        datos = bot.send_message(message.chat.id, f"Nombre: {nombre}\nGasto: ${gasto}\n", reply_markup=markup)
        bot.register_next_step_handler(datos, guardar_personas)
    except:
        # SI EL USUARIO NO INGRESA UN NUMERO NOS TRAE LA EXCEPCION 
        datos_error = bot.send_message(message.chat.id, "Debe ingresar un numero")
        preguntar_gasto(datos_error)


def guardar_personas(message):
    # COMPROBAMOS QUE EL USUARIO PRESIONE UN BOTON Y NO INGRESE UN TEXTO 
    markup = ReplyKeyboardRemove()

    if message.text != "Agregar" and message.text != "Finalizar":
        mensaje_usuario = bot.send_message(message.chat.id, "ERROR: Debe pulsar uno de los dos botones!")
        bot.register_next_step_handler(mensaje_usuario, guardar_personas)
    elif message.text == "Finalizar":
        # SI EL USUARIO FINALIZA SE REALIZAN TODAS LAS FUNCIONES DE CALCULOS CORRESPONDIENTES
        # SE MUESTRAN USUARIOS Y GASTOS 
        indice = 0
        for n in personas:
            for g in gastos:
                if indice <= len(personas)-1 or indice <= len(gastos)-1:
                    personas_cargadas.append(f"{personas[indice]} - Gasto ${gastos[indice]}")
                    indice += 1
                else:
                    break
        
        mostrar_personas_cargadas = "\n".join(personas_cargadas)
        bot.send_message(message.chat.id, mostrar_personas_cargadas, reply_markup=markup)

        # SE SUMAN TODOS LOS GASTOS PARA OBTENER EL TOTAL Y SE DIVIDE POR LA CANTIDAD DE PERSONAS
        suma_gastos = 0
        for gasto in gastos:
            suma_gastos += gasto
        personas_a_dividir = len(personas)
        bot.send_message(message.chat.id, f"Total ${suma_gastos}, son {personas_a_dividir} para dividir")

        total_cada_uno = round(suma_gastos / personas_a_dividir, 2)
        bot.send_message(message.chat.id, f"${total_cada_uno} cada uno")

        # SE REALIZA LA COMPARACION DEL TOTAL QUE CORRESPONDE Y DE LO QUE LA PERSONA GASTO EN REALIDAD
        indice = 0
        for g in gastos:
            resultado = g - total_cada_uno
            indice += 1
            gastos_divididos.append(resultado)

        comienzo = 0
        contador = 0

        # SE INDICA SI LA PERSONA DEBE PAGAR O DEBE RECIBIR DETERMINADA SUMA
        indice = 0
        for n in personas:
            for g in gastos:
                if indice <= len(personas)-1 or indice <= len(gastos)-1:
                    if gastos_divididos[indice] < 0:
                        personas_gastos_divididos.append(f"{personas[indice]} - Abonar (${gastos_divididos[indice] * -1})")
                    elif gastos_divididos[indice] > 0:
                        personas_gastos_divididos.append(f"{personas[indice]} - Obtener (${gastos_divididos[indice]})")
                    indice += 1

        mostrar_division_final = "\n".join(personas_gastos_divididos)
        bot.send_message(message.chat.id, mostrar_division_final)

        # SE COMPARA CADA PERSONA INDIVIDUALMENTE CON TODAS LAS OTRAS PERSONA DE LA LISTA
        #  Y ASI SE DETERMINA EL MONTO EXACTO Y A QUIEN SE DEBE CANCELAR LOS GASTOS PARA QUEDAR TODOS IGUALES
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
                                mostrar_cancelaciones = f"{personas[comienzo]} cancelar ${final} a {personas[contador]}"
                                mensaje_opciones = bot.send_message(message.chat.id, mostrar_cancelaciones.upper())

                        contador += 1

                contador = 0
                comienzo += 1
            else:
                break

        boton_regresar(mensaje_opciones)

    elif message.text == "Agregar":
        preguntar_persona(message)
        

# <------------------   CADENA DE FUNCIONES PARA EL MODULO DE LOCALIZACIÓN -------------------->
def localizacion(message):
    markup = ForceReply()
    mensaje = bot.send_message(message.chat.id, f"Ingrese datos del viaje\nOrigen: ", reply_markup=markup)
    bot.register_next_step_handler(mensaje, origin_destiny)
    
def origin_destiny(message):
    global origen
    origen = message.text
    markup = ForceReply()
    mensaje= bot.send_message(message.chat.id, "Imgrese destino:", reply_markup=markup)
    bot.register_next_step_handler(mensaje, viaje)

def viaje(message):
    global destino
    destino = message.text
    url = api_url + urllib.parse.urlencode({"key":key, "from":origen, "to":destino})
    json_data = get(url).json()
    status_code = json_data["info"]["statuscode"]
    
    if status_code == 0:
        global trip_duration
        global distance
        global fuel_used
        global latitude_destiny
        global longitude_destiny
        trip_duration = json_data["route"]["formattedTime"]
        distance = json_data["route"]["distance"] * 1.61
        latitude_destiny = json_data["route"]["locations"][1]["latLng"]["lat"]
        longitude_destiny = json_data["route"]["locations"][1]["latLng"]["lng"]
        mensaje_viaje = bot.send_message(message.chat.id,f"Información del viaje\nOrigen: {json_data['route']['locations'][0]['adminArea5']}\n Destino: {json_data['route']['locations'][1]['adminArea5']}")
        bot.send_message(message.chat.id, f"Duración del viaje: {trip_duration}\nDistancia: {distance:.2f} km")
        bot.send_location(message.chat.id, latitude=latitude_destiny, longitude=longitude_destiny)
        boton_regresar(mensaje_viaje)


# <------------------   CADENA DE FUNCIONES PARA EL MODULO DE SORTEO -------------------->
def definir_marcador(message):
    # ASIGNAMOS LOS NOMBRES DEL SORTEO 
    markup = ForceReply()
    mensaje_sorteo = bot.send_message(message.chat.id, f"Ingrese nombre", reply_markup=markup)
    bot.register_next_step_handler(mensaje_sorteo, agregar_sortear)


def agregar_sortear(message):
    # MOSTRAMOS NOMBRE, DEFINIMOS BOTONES PARA AGREGAR MAS NOMBRES O SORTEAR
    global marcador
    marcador = message.text
    marcador = marcador.capitalize()
    lista_sorteo.append(marcador)
    markup = ReplyKeyboardMarkup(
    one_time_keyboard=True,
    input_field_placeholder="Pulsa un boton",
    resize_keyboard=True
    )
    markup.add("Agregar", "Sortear")
    global eleccion
    eleccion = bot.send_message(message.chat.id, f"Ingreso a {marcador}", reply_markup=markup)
    bot.register_next_step_handler(eleccion, guardar_sorteo)


def guardar_sorteo(message):
    # COMPROBAMOS QUE LA ENTRADA SEA VALIDA, DEFINIMOS LA REDIRECCION DE FUNCION PARA AGREGAR Y LA FUNCION PARA SORTEAR
    if message.text != "Agregar" and message.text != "Sortear":
        mensaje_sorteo = bot.send_message(message.chat.id, "ERROR: Debe pulsar uno de los dos botones!")
        bot.register_next_step_handler(mensaje_sorteo, guardar_personas)
    elif message.text == "Sortear":
        mostrar_lista = "\n".join(lista_sorteo)
        resultado_sorteo = choice(lista_sorteo)
        mensaje_resultado = f"Ha salido sorteado \"{resultado_sorteo}\"".upper()
        mensaje_sorteo = bot.send_message(message.chat.id, f"{mostrar_lista}\n\n{mensaje_resultado}")
        boton_regresar(mensaje_sorteo)
    elif message.text == "Agregar":
        definir_marcador(message)


# <------------------   FUNCIONES PARA REGRESAR AL MENU -------------------->
def boton_regresar(message):
    # CREAMOS BOTON DE OPCIONES PARA REGRESAR AL MENU PRINCIPAL UNA VEZ FINALIZADA UNA OPERACION
    markup = ReplyKeyboardMarkup(
       one_time_keyboard=True,
       resize_keyboard=True
       )
    markup.add("Opciones")
    mensaje_opciones = bot.send_message(message.chat.id, f"Pulse Opciones para volver!", reply_markup=markup)
    bot.register_next_step_handler(mensaje_opciones, confirmar_regreso)

def confirmar_regreso(message):
    # CONFRIMAMOS QUE EL USUARIO PRESIONE EL BOTON Y LE ABRIMOS EL MENU
    if message.text != "Opciones":
        mensaje_opciones = bot.send_message(message.chat.id, "ERROR: Debe pulsar el boton!")
        bot.register_next_step_handler(mensaje_opciones, guardar_personas)
    elif message.text == "Opciones":
        mensaje_opciones = bot.send_message(message.chat.id, f"Regresemos...")
        cmd_ayuda(mensaje_opciones)


# <------------------   CADENA DE FUNCIONES PARA EL MODULO DE MERCADOS FINANCIEROS -------------------->
def elegir_mercado(message):
    # SE DESPLEGAN LAS OPCIONES DEL MERCADO QUE SE DESEA CONSULTAR O SI SE DESEA VOLVER AL MENU
    markup = InlineKeyboardMarkup(row_width=1)
    b_cripto = InlineKeyboardButton("Criptomonedas", callback_data="Criptomonedas")
    b_acciones = InlineKeyboardButton("Acciones", callback_data="Acciones")
    b_cerar_mercados = InlineKeyboardButton("Cerrar", callback_data="cerrar_ayuda")

    markup.add(b_cripto, b_acciones, b_cerar_mercados)
    bot.send_message(message.chat.id, f"Seleccione una opcion!", reply_markup=markup)


def mostrar_criptomoneda(message):
    # MOSTRAMOS AL USUARIO BOTONES CON LOS DISTINTOS TIPOS DE MONEDAS PARA CONSULTAR SU PRECIO
    markup = InlineKeyboardMarkup(row_width=1)
    btn1_c = InlineKeyboardButton("BTC", callback_data="BTC")
    btn2_c = InlineKeyboardButton("ETH", callback_data="ETH")
    btn3_c = InlineKeyboardButton("BNB", callback_data="BNB")
    btn4_c = InlineKeyboardButton("ADA", callback_data="ADA")
    btn5_c = InlineKeyboardButton("SOL", callback_data="SOL")
    btn6_c = InlineKeyboardButton("ETC", callback_data="ETC")
    btn7_c = InlineKeyboardButton("DOT", callback_data="DOT")
    btn8_c = InlineKeyboardButton("LTC", callback_data="LTC")
    btn9_c = InlineKeyboardButton("SAND", callback_data="SAND")
    btn10_c = InlineKeyboardButton("MATIC", callback_data="MATIC")
    btn11_c = InlineKeyboardButton("DOGE", callback_data="DOGE")
    btn12_c = InlineKeyboardButton("XRP", callback_data="XRP")
    btn13_c = InlineKeyboardButton("LUNC", callback_data="LUNC")
    btn14_c = InlineKeyboardButton("AVAX", callback_data="AVAX")
    btn15_c = InlineKeyboardButton("MANA", callback_data="MANA")
    b_volver_c = InlineKeyboardButton("Volver", callback_data="volver_mercados")

    markup.add(btn1_c, btn2_c, btn3_c, btn4_c, btn5_c, btn6_c, btn7_c, btn8_c, btn9_c, btn10_c, btn11_c, btn12_c, btn13_c, btn14_c, btn15_c, b_volver_c)
    mensaje_cripto = bot.send_message(message.chat.id, f"Seleccione una opcion!", reply_markup=markup)
    bot.register_next_step_handler(mensaje_cripto, elegir_criptomoneda)


def mostrar_accion(message):
    # MOSTRAMOS AL USUARIO BOTONES CON LOS DISTINTOS TIPOS DE ACCIONES PARA CONSULTAR SU PRECIO
    markup = InlineKeyboardMarkup(row_width=1)
    btn1_a = InlineKeyboardButton("NVIDIA", callback_data="NVIDIA")
    btn2_a = InlineKeyboardButton("INTEL", callback_data="INTEL")
    btn3_a = InlineKeyboardButton("AMD", callback_data="AMD")
    btn4_a = InlineKeyboardButton("APPLE", callback_data="APPLE")
    btn5_a = InlineKeyboardButton("TESLA", callback_data="TESLA")
    btn6_a = InlineKeyboardButton("NETFLIX", callback_data="NETFLIX")
    btn7_a = InlineKeyboardButton("PEPSICO", callback_data="PEPSICO")
    btn8_a = InlineKeyboardButton("COCA-COLA", callback_data="COCA-COLA")
    btn9_a = InlineKeyboardButton("AMAZON", callback_data="AMAZON")
    btn10_a = InlineKeyboardButton("EBAY", callback_data="EBAY")
    btn11_a = InlineKeyboardButton("NIKE", callback_data="NIKE")
    btn12_a = InlineKeyboardButton("DISNEY", callback_data="DISNEY")
    btn13_a = InlineKeyboardButton("IBM", callback_data="IBM")
    btn14_a = InlineKeyboardButton("MC DONALS", callback_data="MC DONALS")
    btn15_a = InlineKeyboardButton("AMERICAN EXPRESS", callback_data="AMERICAN EXPRESS")
    b_volver_a = InlineKeyboardButton("Volver", callback_data="volver_mercados")

    markup.add(btn1_a, btn2_a, btn3_a, btn4_a, btn5_a, btn6_a, btn7_a, btn8_a, btn9_a, btn10_a, btn11_a, btn12_a, btn13_a, btn14_a, btn15_a, b_volver_a)
    mensaje_accion = bot.send_message(message.chat.id, f"Seleccione una opcion!", reply_markup=markup)
    bot.register_next_step_handler(mensaje_accion, elegir_accion)


def elegir_criptomoneda(message):
    # ASIGNAMOS LA SELECCION A LA BUSQUEDA WEB SCRAPING
    # DEVOLVEMOS COMO RESPUESTA SEGUN EL BOTON PRESIONADO EL PRESIO DE LA CRIPTOMONEDA
    ingreso_c = message.text
    coin = ''

    if ingreso_c == "BTC":
        coin = 'bitcoin'
    elif ingreso_c == "ETH":
        coin = 'ethereum'
    elif ingreso_c == "BNB":
        coin = 'binance-coin'
    elif ingreso_c == "ADA":
        coin = 'cardano'
    elif ingreso_c == "SOL":
        coin = 'solana'
    elif ingreso_c == "ETC":
        coin = 'ethereum-classic'
    elif ingreso_c == "AVAX":
        coin = 'avax'
    elif ingreso_c == "DOT":
        coin = 'polkadot'
    elif ingreso_c == "LTC":
        coin = 'litecoin'
    elif ingreso_c == "SAND":
        coin = 'the-sandbox'
    elif ingreso_c == "MANA":
        coin = 'decentraland'
    elif ingreso_c == "MATIC":
        coin = 'polygon'
    elif ingreso_c == "DOGE":
        coin = 'dogecoin'
    elif ingreso_c == "XRP":
        coin = 'xrp'
    elif ingreso_c == "LUNC":
        coin = 'luna-classic'
    
    url_criptos = f'https://www.coindesk.com/price/{coin}/'
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    headers = {"user-agent" : user_agent}
    response = get(url_criptos, headers=headers, timeout=10)
    html_soup_mercados = BeautifulSoup(response.text, 'html.parser')
    cripto = html_soup_mercados.find(class_="typography__StyledTypography-owin6q-0 jvRAOp")
    precio_cripto = cripto.get_text()
    bot.send_message(message.chat.id, f"USD{precio_cripto}")
    


def elegir_accion(message):
    # ASIGNAMOS LA SELECCION A LA BUSQUEDA WEB SCRAPING
    # DEVOLVEMOS COMO RESPUESTA SEGUN EL BOTON PRESIONADO EL PRESIO DE LA ACCION
    ingreso_a = message.text
    accion = ''

    if ingreso_a == "AMD":
        accion = 'adv-micro-device'
    elif ingreso_a == "NVIDIA":
        accion = 'nvidia-corp'
    elif ingreso_a == "INTEL":
        accion = 'intel-corp'
    elif ingreso_a == "APPLE":
        accion = 'apple-computer-inc'
    elif ingreso_a == "TESLA":
        accion = 'tesla-motors'
    elif ingreso_a == "NETFLIX":
        accion = 'netflix,-inc.'
    elif ingreso_a == "PEPSICO":
        accion = 'pepsico'
    elif ingreso_a == "COCA-COLA":
        accion = 'coca-cola-co'
    elif ingreso_a == "AMAZON":
        accion = 'amazon-com-inc'
    elif ingreso_a == "EBAY":
        accion = 'ebay-inc'
    elif ingreso_a == "NIKE":
        accion = 'nike'
    elif ingreso_a == "DISNEY":
        accion = 'disney'
    elif ingreso_a == "AMERICAN EXPRESS":
        accion = 'american-express'
    elif ingreso_a == "IBM":
        accion = 'ibm'
    elif ingreso_a == "MC DONALS":
        accion = 'mcdonalds'

    url_acciones = f'https://es.investing.com/equities/{accion}'
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    headers = {"user-agent" : user_agent}
    response = get(url_acciones, headers=headers, timeout=10)
    html_soup_mercados = BeautifulSoup(response.text, 'html.parser')
    acc = html_soup_mercados.find('span', class_="text-2xl")
    precio_acc = acc.get_text()
    bot.send_message(message.chat.id, f"USD{precio_acc}")


# <------------------   CADENA DE FUNCIONES PARA EL MODULO DE BUSCADOR GOOGLE WEB SCRAPING -------------------->
def opciones_busqueda(message):
    # SE DESPLEGAN LAS OPCIONES DE BUSQUEDA O SI SE DESEA VOLVER AL MENU
    markup = ReplyKeyboardRemove()
    markup = InlineKeyboardMarkup(row_width=1)
    b_vuelos = InlineKeyboardButton("Vuelos Lowcost", callback_data="Vuelos")
    b_economia = InlineKeyboardButton("Noticias Economia", callback_data="Economia")
    b_noticias = InlineKeyboardButton("Noticias Generales", callback_data="Noticias")
    b_deportes = InlineKeyboardButton("Noticias Deportes", callback_data="Deportes")
    b_busqueda_usuario = InlineKeyboardButton("Otros Intereses", callback_data="busqueda_usuario")
    b_cerar_buscar = InlineKeyboardButton("Cerrar", callback_data="cerrar_busqueda")

    markup.add(b_vuelos, b_economia, b_noticias, b_deportes, b_busqueda_usuario, b_cerar_buscar)
    bot.send_message(message.chat.id, f"Seleccione una opcion!", reply_markup=markup)


def preguntar_busqueda(message):
    # SI SE SELECCIONA LA OPCION OTROS INTERESES, CON ESTA FUNCION PERMITIMOS EL INGRESO DEL USUARIO Y ASI BUSCAR LO QUE DESEE 
    markup = ForceReply()
    mensaje_buscar = bot.send_message(message.chat.id, f"Que desea buscar?", reply_markup=markup)
    bot.register_next_step_handler(mensaje_buscar, realizar_busqueda)

def realizar_busqueda(message):
    # REALIZAMOS LA BUSQUEDA DE LO INGRESADO O DE LAS FUNCIONES YA DEFINIDAS
    # REALIZAMOS EL WEB SCRAPING FILTRANDO LOS ENLACES Y LOS TITULOS
    mensaje_recibido = message.text

    if mensaje_recibido == "Vuelos":
        texto_buscar = "vuelos lowcost"
    elif mensaje_recibido == "Economia":
        texto_buscar = "noticias de economia"
    elif mensaje_recibido == "Noticias":
        texto_buscar = "noticias generales"
    elif mensaje_recibido == "Deportes":
        texto_buscar = "noticias de deportes"
    else:
        texto_buscar = message.text

    url = f'https://www.google.com.ar/search?q={texto_buscar.replace(" ","+")}&num=12'
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    headers = {"user-agent" : user_agent}
    res = get(url, headers=headers, timeout=10)
    if res.status_code != 200:
        bot.send_message(message.chat.id, f"Error al buscar")
        return 1
    else:
        soup = BeautifulSoup(res.text, "html.parser")
        elementos = soup.find_all('div', class_='g')
        lista_elementos = []
        for elemento in elementos:
            try:
                titulo = elemento.find('h3').text
                url = elemento.find('a').attrs.get('href')
                if not url.startswith('http'):
                    url = 'https://google.es' + url
                if [titulo, url] in lista_elementos:
                    continue
                lista_elementos.append([titulo, url])
            except:
                continue       

    mostrar_pagina(lista_elementos, message.chat.id)


def mostrar_pagina(lista, cid, pag=0, mid=None):
    # CREAMOS BOTONERA CORRESPONDIENTE PARA CADA ENLACE 
    markup = InlineKeyboardMarkup(row_width=MAX_ANCHO_ROW)
    b_volver = InlineKeyboardButton("Nueva Busqueda", callback_data="volver_buscador")
    inicio = pag*N_RES_PAG # NUMERO DE RESULTADOS INICIO DE PAGINA
    fin = inicio + N_RES_PAG # NUMERO DE RESULTADOS FIN DE PAGINA 
    mensaje = f'Resultados {inicio + 1}-{len(lista)}\n\n'
    n = 1
    botones = []
    for item in lista[inicio:fin]:
        botones.append(InlineKeyboardButton(str(n), url=item[1]))
        mensaje += f'[<b>{n}</b>] - {item[0]}\n'
        n += 1
    markup.add(*botones)
    markup.row(b_volver)
    if mid:
        bot.edit_message_text(mensaje, cid, mid, reply_markup=markup, parse_mode='html', disable_web_page_preview=True)
    else:
        bot.send_message(cid, mensaje, reply_markup=markup, parse_mode="html", disable_web_page_preview=True)
        

# <------------------   CADENA DE FUNCIONES PARA EL MODULO DEL CLIMA -------------------->
def ingresar_ciudad(message):
    markup = ForceReply()
    mensaje_ciudad = bot.send_message(message.chat.id, f"Ciudad", reply_markup=markup)
    bot.register_next_step_handler(mensaje_ciudad, ingresar_pais)


def ingresar_pais(message):
    global ciudad
    ciudad = message.text
    ciudad = ciudad.capitalize()

    markup = ForceReply()
    mensaje_pais = bot.send_message(message.chat.id, f"Pais", reply_markup=markup)
    bot.register_next_step_handler(mensaje_pais, mostrar_clima)


def mostrar_clima(message):
    global pais
    pais = message.text 
    pais = pais.capitalize()
    
    url_final = f'{WEATHER_URL}{WEATHER_KEY}&q={ciudad}, {pais}{lenguaje}{unidad}'
    resp = get(url_final).json()


    temp = resp['main']['temp']
    mensaje_temp = bot.send_message(message.chat.id,f"{ciudad}, {pais}\nTemperatura actual {round(temp, 1)}°C")

    temp_min = resp['main']['temp_min']
    temp_max = resp['main']['temp_max']
    bot.send_message(message.chat.id,f"Minima {round(temp_min, 1)}°C - Maxima {round(temp_max, 1)}°C")

    sensacion_termica = resp['main']['feels_like']
    bot.send_message(message.chat.id, f"Sensación térmica {round(sensacion_termica, 1)}°C")

    humedad = resp['main']['humidity']
    bot.send_message(message.chat.id,f"Humedad {humedad}%")
    
    description = resp['weather'][0]['description']
    icon = resp['weather'][0]['icon']
    bot.send_photo(message.chat.id, f"http://openweathermap.org/img/wn/{icon}@2x.png")
    bot.send_message(message.chat.id,f"Se pronóstica \"{description}\"")
    boton_regresar(mensaje_temp)

# <------------------ FUNCIONES DE TODOS LOS CALLBACK DATA RECIBIDOS -------------------->
@bot.callback_query_handler(func=lambda x: True)
def respuesta_botones(call):
    # GESTIONAR LAS ACCIONES DE LOS BOTONES CALLBACK DATA
    cid = call.from_user.id  # CHAT ID 
    mid = call.message.id  # MENSAJE ID


    # <<<<<<<<<<<<<<<    CALLBACK DATA ACCIONES PRINCIPALES, OPCIONES DEL BOT    >>>>>>>>>>>>>>>
    if call.data == "cerrar":
        bot.delete_message(cid, mid)
        mensaje_cerrar = bot.send_message(cid, "...")
        boton_regresar(mensaje_cerrar)
    elif call.data == "cerrar_busqueda":
        bot.delete_message(cid, mid)
        mensaje_menu = bot.send_message(cid, "Menu")
        boton_regresar(mensaje_menu)
    elif call.data == "division":
        bot.delete_message(cid, mid)
        mensaje_division = bot.send_message(cid, "Iniciar")
        preguntar_persona(mensaje_division)
    elif call.data == "sorteo":
        bot.delete_message(cid, mid)
        inicio_sorteo = bot.send_message(cid, "Es hora de comenzar")
        definir_marcador(inicio_sorteo)
    elif call.data == "mercados":
        bot.delete_message(cid, mid)
        inicio_mercados = bot.send_message(cid, "Precios de Criptomonedas y Acciones")
        elegir_mercado(inicio_mercados)
    elif call.data == "buscador":
        bot.delete_message(cid, mid)
        inicio_buscador = bot.send_message(cid, "Selecciona tu opcion o busca lo que desees")
        opciones_busqueda(inicio_buscador)
    elif call.data == "localizacion":
        bot.delete_message(cid, mid)
        inicio_localizacion = bot.send_message(cid, "Comencemos con tu viaje")
        localizacion(inicio_localizacion)
    elif call.data == "clima":
        bot.delete_message(cid, mid)
        inicio_clima = bot.send_message(cid, "Informacion del Clima")
        ingresar_ciudad(inicio_clima)


    # <<<<<<<<<<<<<<<    CALLBACK DATA PARA LAS OPCIONES DE MERCADOS FINANCIEROS    >>>>>>>>>>>>>>>
    if call.data == "Criptomonedas":
        bot.delete_message(cid, mid)
        mensaje_cripto = bot.send_message(cid, "Criptomonedas")
        mostrar_criptomoneda(mensaje_cripto)
    elif call.data == "Acciones":
        bot.delete_message(cid, mid)
        mensaje_accion = bot.send_message(cid, "Acciones")
        mostrar_accion(mensaje_accion)
    elif call.data == "volver_mercados":
        bot.delete_message(cid, mid)
        mensaje_busqueda = bot.send_message(cid, "Inicio")
        elegir_mercado(mensaje_busqueda)
   

    # <<<<<<<<<<<<<<<    CALLBACK DATA PARA LOS RESULTADOS DE LAS CRIPTOMONEDAS   >>>>>>>>>>>>>>>
    if call.data == "BTC":
        msg_btc = bot.send_message(cid, "BTC")
        elegir_criptomoneda(msg_btc)
    elif call.data == "ETH":
        msg_eth = bot.send_message(cid, "ETH")
        elegir_criptomoneda(msg_eth)
    elif call.data == "BNB":
        msg_bnb = bot.send_message(cid, "BNB")
        elegir_criptomoneda(msg_bnb)
    elif call.data == "ADA":
        msg_ada = bot.send_message(cid, "ADA")
        elegir_criptomoneda(msg_ada)
    elif call.data == "SOL":
        msg_sol = bot.send_message(cid, "SOL")
        elegir_criptomoneda(msg_sol)
    elif call.data == "ETC":
        msg_etc = bot.send_message(cid, "ETC")
        elegir_criptomoneda(msg_etc)
    elif call.data == "DOT":
        msg_dot = bot.send_message(cid, "DOT")
        elegir_criptomoneda(msg_dot)
    elif call.data == "LTC":
        msg_ltc = bot.send_message(cid, "LTC")
        elegir_criptomoneda(msg_ltc)
    elif call.data == "SAND":
        msg_sand = bot.send_message(cid, "SAND")
        elegir_criptomoneda(msg_sand)
    elif call.data == "MATIC":
        msg_matic = bot.send_message(cid, "MATIC")
        elegir_criptomoneda(msg_matic)
    elif call.data == "DOGE":
        msg_doge = bot.send_message(cid, "DOGE")
        elegir_criptomoneda(msg_doge)
    elif call.data == "XRP":
        msg_xrp = bot.send_message(cid, "XRP")
        elegir_criptomoneda(msg_xrp)
    elif call.data == "LUNC":
        msg_lun = bot.send_message(cid, "LUNC")
        elegir_criptomoneda(msg_lun)
    elif call.data == "AVAX":
        msg_avax = bot.send_message(cid, "AVAX")
        elegir_criptomoneda(msg_avax)
    elif call.data == "MANA":
        msg_mana = bot.send_message(cid, "MANA")
        elegir_criptomoneda(msg_mana)


    # <<<<<<<<<<<<<<<    CALLBACK DATA PARA LOS RESULTADOS DE LAS ACCIONES   >>>>>>>>>>>>>>>
    if call.data == "NVIDIA":
        msg_nvidia = bot.send_message(cid, "NVIDIA")
        elegir_accion(msg_nvidia)
    elif call.data == "INTEL":
        msg_intel = bot.send_message(cid, "INTEL")
        elegir_accion(msg_intel)
    elif call.data == "AMD":
        msg_amd = bot.send_message(cid, "AMD")
        elegir_accion(msg_amd)
    elif call.data == "APPLE":
        msg_apple = bot.send_message(cid, "APPLE")
        elegir_accion(msg_apple)
    elif call.data == "TESLA":
        msg_tesla = bot.send_message(cid, "TESLA")
        elegir_accion(msg_tesla)
    elif call.data == "NETFLIX":
        msg_net = bot.send_message(cid, "NETFLIX")
        elegir_accion(msg_net)
    elif call.data == "PEPSICO":
        msg_pep = bot.send_message(cid, "PEPSICO")
        elegir_accion(msg_pep)
    elif call.data == "COCA-COLA":
        msg_coca = bot.send_message(cid, "COCA-COLA")
        elegir_accion(msg_coca)
    elif call.data == "AMAZON":
        msg_amz = bot.send_message(cid, "AMAZON")
        elegir_accion(msg_amz)
    elif call.data == "EBAY":
        msg_ebay = bot.send_message(cid, "EBAY")
        elegir_accion(msg_ebay)
    elif call.data == "NIKE":
        msg_nike = bot.send_message(cid, "NIKE")
        elegir_accion(msg_nike)
    elif call.data == "DISNEY":
        msg_dis = bot.send_message(cid, "DISNEY")
        elegir_accion(msg_dis)
    elif call.data == "IBM":
        msg_ibm = bot.send_message(cid, "IBM")
        elegir_accion(msg_ibm)
    elif call.data == "MC DONALS":
        msg_mc = bot.send_message(cid, "MC DONALS")
        elegir_accion(msg_mc)
    elif call.data == "AMERICAN EXPRESS":
        msg_american = bot.send_message(cid, "AMERICAN EXPRESS")
        elegir_accion(msg_american)
    
    
    # <<<<<<<<<<<<<<<    CALLBACK DATA PARA BUSCADOR DE GOOGLES   >>>>>>>>>>>>>>>
    if call.data == "Vuelos":
        bot.delete_message(cid, mid)
        mensaje_busqueda = bot.send_message(cid, "Vuelos")
        realizar_busqueda(mensaje_busqueda)
    elif call.data == "Economia":
        bot.delete_message(cid, mid)
        mensaje_busqueda = bot.send_message(cid, "Economia")
        realizar_busqueda(mensaje_busqueda)
    elif call.data == "Noticias":
        bot.delete_message(cid, mid)
        mensaje_busqueda = bot.send_message(cid, "Noticias")
        realizar_busqueda(mensaje_busqueda)
    elif call.data == "Deportes":
        bot.delete_message(cid, mid)
        mensaje_busqueda = bot.send_message(cid, "Deportes")
        realizar_busqueda(mensaje_busqueda)
    elif call.data == "busqueda_usuario":
        bot.delete_message(cid, mid)
        mensaje_busqueda = bot.send_message(cid, "Nueva busqueda")
        preguntar_busqueda(mensaje_busqueda)
    elif call.data == "volver_buscador":
        bot.delete_message(cid, mid)
        mensaje_busqueda = bot.send_message(cid, "Nueva busqueda")
        opciones_busqueda(mensaje_busqueda)


# <------------------   BOT REACCIONA A LOS TEXTOS ENVIADOS POR EL USUARIO -------------------->
@bot.message_handler(content_types=["text"])
def bot_mensaje_texto(message):
    # RESPONDE A UN COMANDO NO VALIDO O A UN INGRESO DEL USUARIO CUANDO NO SE LO SOLICITA
    if message.text and message.text.startswith("/"):
        bot.send_message(message.chat.id, "Comando no definido")
    else:
        bot.send_message(message.chat.id, "No entiendo lo que quieres decir, continue...")



# FUNCION BUCLE INFINITO VERIFICA LA RECEPCION DE MENSAJES
def recibir_mensajes():
    bot.infinity_polling()

# INICIA BOT EN CLASE MAIN
if __name__ == '__main__':

    # MOSTRAR LOS COMANDOS EN TELEGRAM
    bot.set_my_commands([
        telebot.types.BotCommand("start", "Inicia el Bot")
        ])

    # HILO BOT DEFINIDO PARA EJECUTAR LA FUNCION EN SEGUNDO PLANO Y CONTINUAR EL CODIGO 
    hilo_bot = threading.Thread(name="hilo_bot", target=recibir_mensajes)
    hilo_bot.start()
