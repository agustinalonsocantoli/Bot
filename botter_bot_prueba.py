import telebot

bot = telebot.TeleBot("5420608268:AAHmtRiwizz4Mpmbuy2GQEuHt4hZhT5Wsp0")

@bot.message_handler(commands=["help", "start"])

def enviar(message):
    bot.reply_to(message, "Hola, ¿Cómo estas?")
    
bot.polling()