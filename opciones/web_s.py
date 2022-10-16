from lib2to3.pgen2 import token
import telebot
from telebot.types import ForceReply # RESPONDER A LOS MENSAJES DEL BOT
from telebot.types import InlineKeyboardMarkup # CREAMOS BOTONERA
from telebot.types import InlineKeyboardButton # DEFINIMOS BOTONES
import requests
from bs4 import BeautifulSoup


# CONSTANTES
N_RES_PAG = 10 # NUMERO DE RESULTADOS A MOSTRAR EN CADA PAGINA
MAX_ANCHO_ROW = 5 # MAXIMO BOTONES POR FILA ( 8 LIMITACION TELEGRAM )


# TOKEN IDENTIFICACION
token = "5420608268:AAHmtRiwizz4Mpmbuy2GQEuHt4hZhT5Wsp0"
bot = telebot.TeleBot(token)

      
# COMANDO START SALUDA
@bot.message_handler(commands=["start"])  
def cmd_start(message):
    # BOT INICIA Y SALUDA
    bot.send_message(message.chat.id, f"Hola!!")
    cmd_busqueda(message)


def cmd_busqueda(message):
    #BOT DESPLEGA LAS OPCIONES CON BOTONES PARA QUE EL USUARIO SELECCIONE
    # markup = ReplyKeyboardRemove()
    markup = InlineKeyboardMarkup(row_width=1)
    b_vuelos = InlineKeyboardButton("Vuelos Lowcost", callback_data="Vuelos")
    b_economia = InlineKeyboardButton("Noticias Economia", callback_data="Economia")
    b_noticias = InlineKeyboardButton("Noticias Generales", callback_data="Noticias")
    b_deportes = InlineKeyboardButton("Noticias Deportes", callback_data="Deportes")
    b_busqueda_usuario = InlineKeyboardButton("Otros Intereses", callback_data="busqueda_usuario")
    b_cerar_inicio = InlineKeyboardButton("Cerrar", callback_data="cerrar_inicio")

    markup.add(b_vuelos, b_economia, b_noticias, b_deportes, b_busqueda_usuario, b_cerar_inicio)
    bot.send_message(message.chat.id, f"Seleccione una opcion!", reply_markup=markup)


def preguntar_busqueda(message):
    markup = ForceReply()
    mensaje_buscar = bot.send_message(message.chat.id, f"Que desea buscar?", reply_markup=markup)
    bot.register_next_step_handler(mensaje_buscar, realizar_busqueda)

def realizar_busqueda(message):
    print(message)
    mensaje_recibido = message.text
    print(mensaje_recibido)

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

    print(texto_buscar)
    url = f'https://www.google.com.ar/search?q={texto_buscar.replace(" ","+")}&num=12'
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    headers = {"user-agent" : user_agent}
    res = requests.get(url, headers=headers, timeout=10)
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
    b_volver = InlineKeyboardButton("Nueva Busqueda", callback_data="volver")
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


@bot.callback_query_handler(func=lambda x: True)
def respuesta_inicio(call):
    # GESTIONAR LAS ACCIONES DE LOS BOTONES CALLBACK DATA
    cid = call.from_user.id  # CHAT ID 
    mid = call.message.id  # MENSAJE ID
    if call.data == "cerrar_inicio":
        bot.delete_message(cid, mid)
        return
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
    elif call.data == "volver":
        bot.delete_message(cid, mid)
        mensaje_busqueda = bot.send_message(cid, "Nueva busqueda")
        preguntar_busqueda(mensaje_busqueda)




bot.infinity_polling()


