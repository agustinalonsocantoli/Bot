from datetime import datetime
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
from requests import get
from bs4 import BeautifulSoup

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

# CONSTANTES
N_RES_PAG = 10 # NUMERO DE RESULTADOS A MOSTRAR EN CADA PAGINA
MAX_ANCHO_ROW = 5 # MAXIMO BOTONES POR FILA ( 8 LIMITACION TELEGRAM )

# COMANDO START SALUDA
@bot.message_handler(commands=["start"])  
def cmd_start(message):
    #BOT INICIA Y SALUDA
    markup = ReplyKeyboardRemove()
    bot.send_message(message.chat.id, f"Hola soy Botter!!\nEstoy aqui para ayudarte.",
    reply_markup=markup)
    cmd_usuario(message)


# COMANDO USUARIO
@bot.message_handler(commands=["usuario"])  
def cmd_usuario(message):
    #BOT PREGUNTA DATOS DEL USUARIO
    markup = ForceReply()
    mensaje_usuario = bot.send_message(message.chat.id, f"Como es tu nombre?", reply_markup=markup)
    bot.register_next_step_handler(mensaje_usuario, preguntar_apellido)

# <------------------   CADENA DE FUNCIONES PARA LOS DATOS DEL USUARIO -------------------->
    
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



# COMANDO AYUDA
@bot.message_handler(commands=["ayuda"])  
def cmd_ayuda(message):
    try:
        #BOT DESPLEGA LAS OPCIONES CON BOTONES PARA QUE EL USUARIO SELECCIONE
        markup = ReplyKeyboardRemove()
        markup = InlineKeyboardMarkup(row_width=1)
        b1 = InlineKeyboardButton("DIVISION DE GASTOS", callback_data="division")
        b2 = InlineKeyboardButton("SORTEO", callback_data="sorteo")
        b3 = InlineKeyboardButton("MERCADOS FINANCIEROS", callback_data="mercados")
        b4 = InlineKeyboardButton("BUSCADOR", callback_data="buscador")
        b5 = InlineKeyboardButton("LOCALIZACION", url="https://www.google.es/maps/?hl=es")
        b6 = InlineKeyboardButton("HORA", callback_data="hora")
        b7 = InlineKeyboardButton("FECHA", callback_data="fecha")
        b8 = InlineKeyboardButton("CERRAR", callback_data="cerrar")

        markup.add(b1, b2, b3, b4, b5, b6, b7, b8)
        bot.send_message(message.chat.id, f"{nombre} {apellido} En que puedo ayudarlo", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "Debe ingresar sus datos, pulse /usuario")


# <------------------   CADENA DE FUNCIONES PARA EL MODULO DE DIVISION DE GASTOS -------------------->

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
        resize_keyboard=True)
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
                                bot.send_message(message.chat.id, "Si desea continuar presione /ayuda")

                        contador += 1

                contador = 0
                comienzo += 1
            else:
                break

    elif message.text == "Agregar":
        preguntar_persona(message)


# <------------------   CADENA DE FUNCIONES PARA EL MODULO DE SORTEO -------------------->

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
        bot.send_message(message.chat.id, "Si desea continuar presione /ayuda")
    elif message.text == "Agregar":
        definir_marcador(message)


# <------------------   CADENA DE FUNCIONES PARA EL MODULO DE MERCADOS FINANCIEROS -------------------->

def elegir_mercado(message):
    #BOT DESPLEGA LAS OPCIONES CON BOTONES PARA QUE EL USUARIO SELECCIONE
    markup = InlineKeyboardMarkup(row_width=1)
    b_cripto = InlineKeyboardButton("Criptomonedas", callback_data="Criptomonedas")
    b_acciones = InlineKeyboardButton("Acciones", callback_data="Acciones")
    b_cerar_mercados = InlineKeyboardButton("Cerrar", callback_data="cerrar_ayuda")

    markup.add(b_cripto, b_acciones, b_cerar_mercados)
    bot.send_message(message.chat.id, f"Seleccione una opcion!", reply_markup=markup)


def mostrar_criptomoneda(message):
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
    #BOT DESPLEGA LAS OPCIONES CON BOTONES PARA QUE EL USUARIO SELECCIONE
    markup = ReplyKeyboardRemove()
    markup = InlineKeyboardMarkup(row_width=1)
    b_vuelos = InlineKeyboardButton("Vuelos Lowcost", callback_data="Vuelos")
    b_economia = InlineKeyboardButton("Noticias Economia", callback_data="Economia")
    b_noticias = InlineKeyboardButton("Noticias Generales", callback_data="Noticias")
    b_deportes = InlineKeyboardButton("Noticias Deportes", callback_data="Deportes")
    b_busqueda_usuario = InlineKeyboardButton("Otros Intereses", callback_data="busqueda_usuario")
    b_cerar_buscar = InlineKeyboardButton("Cerrar", callback_data="cerrar_ayuda")

    markup.add(b_vuelos, b_economia, b_noticias, b_deportes, b_busqueda_usuario, b_cerar_buscar)
    bot.send_message(message.chat.id, f"Seleccione una opcion!", reply_markup=markup)


def preguntar_busqueda(message):
    markup = ForceReply()
    mensaje_buscar = bot.send_message(message.chat.id, f"Que desea buscar?", reply_markup=markup)
    bot.register_next_step_handler(mensaje_buscar, realizar_busqueda)

def realizar_busqueda(message):
    
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
    # CREA O EDITA EL MENSAJE DE LA PAGINA QUE CORRESPONDE
    #CREAMOS BOTONERA
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
        

# <------------------ FUNCIONES DE TODOS LOS CALLBACK DATA RECIBIDOS -------------------->

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

    # <<<<<<<<<<<<<<<    CALLBACK DATA ACCIONES PRINCIPALES, OPCIONES DEL BOT    >>>>>>>>>>>>>>>
    if call.data == "cerrar":
        bot.delete_message(cid, mid)
    elif call.data == "cerrar_ayuda":
        bot.delete_message(cid, mid)
        mensaje_menu = bot.send_message(cid, "Menu")
        cmd_ayuda(mensaje_menu)
    elif call.data == "hora":
        bot.send_message(cid, mensaje_hora)
    elif call.data == "fecha":
        bot.send_message(cid, mensaje_fecha)
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
        msg_app = bot.send_message(cid, "APPLE")
        elegir_accion(msg_app)
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
        mensaje_busqueda = bot.send_message(cid, "Vuelos")
        realizar_busqueda(mensaje_busqueda)
    elif call.data == "Economia":
        mensaje_busqueda = bot.send_message(cid, "Economia")
        realizar_busqueda(mensaje_busqueda)
    elif call.data == "Noticias":
        mensaje_busqueda = bot.send_message(cid, "Noticias")
        realizar_busqueda(mensaje_busqueda)
    elif call.data == "Deportes":
        mensaje_busqueda = bot.send_message(cid, "Deportes")
        realizar_busqueda(mensaje_busqueda)
    elif call.data == "busqueda_usuario":
        mensaje_busqueda = bot.send_message(cid, "Nueva busqueda")
        preguntar_busqueda(mensaje_busqueda)
    elif call.data == "volver_buscador":
        bot.delete_message(cid, mid)
        mensaje_busqueda = bot.send_message(cid, "Nueva busqueda")
        opciones_busqueda(mensaje_busqueda)


# <------------------   BOT REACCIONA A LOS TEXTOS ENVIADOS POR EL USUARIO -------------------->

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

