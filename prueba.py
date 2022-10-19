import time
from config import * # IMPORTE EL TOKEN 
from datetime import datetime
import telebot
import locale # ASIGNAR IDIOMA

# <<---------------------------------------------------------------------------------------------------->>
from flask import Flask, request # CREAR SERVIDOR WEB
from pyngrok import ngrok, conf # CREAR UN TUNEL ENTRE NUESTRO SERVIDOR WEB LOCAL E INTERNET (OBTENIENDO URL PUBLICA)
# <<---------------------------------------------------------------------------------------------------->>


# TOKEN
bot = telebot.TeleBot(TELEGRAM_TOKEN)     

# SERVIDOR WEB
web_server = Flask(__name__)

# GESTIONA LAS PETICIONES POST ENVIADAS AL SERVIDOR WEB
@web_server.route('/', methods=['POST'])
def webhook():
    # SI EL POST RECIBIDO ES UN JSON
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200

# NOMBRE DEL BOT
# nombre_bot = "Botter" # NOMBRE BOT TOKEN AGUS ACOSTA
nombre_bot = "EasyBot" # NOMBRE BOT TOKEN AGUS ALONSO

# LENGUAJE ESPAÑOL
locale.setlocale(locale.LC_ALL, 'es_ES')

# LISTA USUARIOS
usuarios = {}

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

# COMANDO START, INICIA EL BOT Y LLAMA LA FUNCION QUE SOLICITA NOMBRE DE USUARIO
@bot.message_handler(commands=["start"])  
def cmd_start(message):
    bot.send_message(message.chat.id, f'{mensaje_saludo}\n\n{mensaje_fecha}\n{mensaje_hora}')


@bot.message_handler(content_types=["text"])
def bot_mensaje_texto(message):
    # RESPONDE A UN COMANDO NO VALIDO O A UN INGRESO DEL USUARIO CUANDO NO SE LO SOLICITA
    if message.text and message.text.startswith("/"):
        bot.send_message(message.chat.id, "Comando no definido")
    else:
        bot.send_message(message.chat.id, message.text, parse_mode="html")

if __name__ == '__main__':
    conf.get_default().config_path = "/Users/agustinalonso/Desarrollador/Ngrok/config_ngrok_bot.yml"
    conf.get_default().region = "sa"
    # CREAMOS ARCHIVO DE CREDENCIALES DE LA API DE NGROK
    ngrok.set_auth_token(NGROK_TOKEN)
    # CREAMOS TUNEL HTTPS EN EL PUERTO 5000
    ngrok_tunel = ngrok.connect(9000, bind_tls=True)
    # URL DEL TUNEL CREADO
    ngrok_url = ngrok_tunel.public_url
    # ELIMINAMOS WEB HOOK
    bot.remove_webhook()
    # PAUSA PARA QUE NO SE PRODUZCA ERROR AL ELIMINAR WEEB HOOK Y CREAR OTRO
    time.sleep(1)
    # DEFINIMOS WEB HOOK
    bot.set_webhook(url=ngrok_url)
    # ARRANCAR SERVIDOR WEB
    web_server.run(host="0.0.0.0", port=9000)

