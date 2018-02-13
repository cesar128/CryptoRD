from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, InlineQueryHandler, MessageHandler, CommandHandler, Filters, CallbackQueryHandler, Job
import logging
from pymongo import MongoClient
from datetime import date, datetime
from jinja2 import Environment, FileSystemLoader
import imgkit
import os


telegramToken = "TELEGRAM_BOT_TOKEN"

uri = 'mongodb://IP:PUERTO/'
client = MongoClient(uri)
client.chopobot.authenticate(USER, PASSWD, mechanism='MONGODB-CR')
crrd = client.chopobot.crrd


def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))


def help(bot, update):
    # Mensaje de /help
    mens = """Dar TRUST a alguien:
-Dar reply a un mensaje de esa persona aca en el grupo y responder con '+1 (mensaje opcional sobre la transaccion)'
Ej: '+1 Venta 2 ETH transaccion rapida y sin problemas'

Ver la reputacion de alguien:
-Dar reply a un mensaje de esa persona aca en el grupo y responder con 'stats'
-Escribir 'stats @usuario' (buggy as hell, might not work)"""
    bot.sendMessage(chat_id=update.message.chat_id, text=mens)


def button(bot, update):
    # Callback de los botones
    query = update.callback_query
    id = query.message.text.split("\n")[0][15:].split()[0]
    if query.data.split("-")[0] == "1":
        if query.from_user.id == int(id): #Paso 1, confirmar la transaccion
            boton = InlineKeyboardMarkup([[InlineKeyboardButton("No especificar.",
                                                                callback_data="2-0")
                                           ],
                                          [InlineKeyboardButton("1-250",
                                                                callback_data="2-250"),
                                           InlineKeyboardButton("251-500",
                                                                callback_data="2-500"),
                                           ],
                                          [InlineKeyboardButton("501-750",
                                                                callback_data="2-750"),
                                           InlineKeyboardButton("751-1,000",
                                                                callback_data="2-1000"),
                                           ],
                                          [InlineKeyboardButton("1,001-1,500",
                                                                callback_data="2-1500"),
                                           InlineKeyboardButton("1,501-2,000",
                                                                callback_data="2-2000"),
                                           ],
                                          [InlineKeyboardButton("2,001-3,000",
                                                                callback_data="2-3000"),
                                           InlineKeyboardButton("3,001-5,000",
                                                                callback_data="2-5000"),
                                           ],
                                          [InlineKeyboardButton("5,001-7,500",
                                                                callback_data="2-7500"),
                                           InlineKeyboardButton("7,501-10,000",
                                                                callback_data="2-10000")
                                           ],
                                          [InlineKeyboardButton("10,001-15,000",
                                                                callback_data="2-7500"),
                                           InlineKeyboardButton("15,001+",
                                                                callback_data="2-10000")
                                           ]
                                          ])
            bot.edit_message_text(text="{}\nMonto (USD):".format(query.message.text),
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  reply_markup=boton)
    elif query.data.split("-")[0] == "2": #Paso 2, guardar el monto
        if query.message.reply_to_message.from_user.username is not None:
            userr = "@" + query.message.reply_to_message.from_user.username
        else:
            userr = query.message.reply_to_message.from_user.first_name
        texto = query.message.text.split("\n")
        de = query.message.text.split("\n")[1][5:].split()[0]
        para = query.message.text.split("\n")[0][15:].split()[0]
        user_para = query.message.text.split("\n")[0][15:].split()[1]
        user = userr
        mensaje = query.message.reply_to_message.text[3:]
        monto = query.data.split("-")[1]
        up_user(de,
                para,
                user,
                mensaje,
                user_para,
                monto)
        bot.edit_message_text(text="{} {}  \n\nCompletado.".format(query.message.text, query.data.split("-")[1]),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id
                              )


def echo(bot, update):
    if update.message.text.lower().startswith("+1"):
        if update.message.chat_id in [-1001183135282, 9891761]:  # -1001183135282, El grupo o yo (Para pruebas)
            if update.message.reply_to_message is not None:
                if update.message.from_user.id != update.message.reply_to_message.from_user.id \
                        or update.message.from_user.id == 9891761:
                    if update.message.from_user.username is not None:
                        userr = "@" + update.message.from_user.username
                    else:
                        userr = update.message.from_user.first_name
                    boton = InlineKeyboardMarkup([[InlineKeyboardButton("Confirmar transaccion",
                                                                        callback_data="1-" +
                                                                            str(update.message.reply_to_message.from_user.id))
                                                   ]])
                    bot.sendMessage(chat_id=update.message.chat_id,
                                    text="Trust given to: {} {}".format(
                                        str(update.message.reply_to_message.from_user.id),
                                        update.message.reply_to_message.from_user.first_name) +
                                    "\nFrom: {} {}".format(str(update.message.from_user.id), userr) +
                                    "\nConcept: " + update.message.text[3:],
                                    reply_markup=boton,
                                    reply_to_message_id=update.message.message_id)
                else:
                    bot.sendMessage(chat_id=update.message.chat_id, text="autopayoleo.... ashi noooo")
            else:
                bot.sendMessage(chat_id=update.message.chat_id, text="Se te olvido dar reply...")

    if "stats" == update.message.text.lower():
        if update.message.reply_to_message is not None:
            tg_id = update.message.reply_to_message.from_user.id
            nombre = update.message.reply_to_message.from_user.first_name
        else:
            nombre = update.message.from_user.first_name
            tg_id = update.message.from_user.id
        stats(tg_id, nombre)
        flag = True
        err_ct = 0
        while flag:
            try:
                # imgkit.from_url(stats, str(tg_id) + ".jpeg", options={"quality": 50})
                bot.sendPhoto(chat_id=update.message.chat_id, photo=open(str(tg_id) + ".jpeg", "rb"))
                flag = False
            except Exception as ee:
                err_ct += 1
                if err_ct >= 10:
                    flag = False
    elif "stats" in update.message.text.lower():
        string = update.message.text.lower()
        splitted = string.split(" ")
        user = None
        for word in splitted:
            if word.startswith("@"):
                user = word[1:]
        if user is not None:
            flag = True
            while flag:
                try:
                    lista = crrd.find_one({"aux": "lista"})
                    nombre = lista[user]["nombre"]
                    tg_id = lista[user]["tg_id"]
                    stats(tg_id, nombre)
                    bot.sendPhoto(chat_id=update.message.chat_id, photo=open(str(tg_id) + ".jpeg", "rb"))
                    flag = False
                except TimeoutError:
                    logging.warning("TimeOut, trying again...")
                except Exception as ee:
                    logging.warning("Error en Reply!")
                    logging.warning(ee)
                    bot.sendMessage(chat_id=update.message.chat_id,
                                    text="uhmm... no, intenta dandole reply mejor a ver")
                    flag = False

    try:
        crrd.update_one({"aux": "lista"},
                        {"$set": {update.message.from_user.username.lower(): {"tg_id": update.message.from_user.id,
                                                                      "nombre": update.message.from_user.first_name}
                                 }
                         },
                        True)
    except Exception as ee:
        logging.warning("error updating lista")
        logging.warning(ee)

    pass


def up_user(de, para, user, mensaje, user_para, monto):
    crrd.update_one({"tg_id": int(para)},
                    {"$push": {"truster": {"id": de,
                                           "fecha": datetime.now(),
                                           "username": user,
                                           "mensaje": mensaje,
                                           "monto": monto}}},
                    True)
    crrd.update_one({"tg_id": int(de)},
                    {"$push": {"truster": {"id": para,
                                           "fecha": datetime.now(),
                                           "username": user_para,
                                           "mensaje": mensaje,
                                           "monto": monto}}},
                    True)
    pass


def stats(tg_id, name):
    trusters = crrd.find_one({"tg_id": tg_id})
    if trusters is None:
        truster = [{"fecha": "N/A", "username": "N/A", "id": "N/A", "mensaje": "N/A"}]
        qty = 0
    else:
        truster = trusters["truster"]
        qty = len(truster)
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)
    b = j2_env.get_template('template.html')
    try:
        a = b.render(users=truster, trusted=name, numeros=qty)
        imgkit.from_string(a,
                           str(tg_id) + ".jpeg",
                           # options={"xvfb": ""}
                           )
    except Exception as ee:
        logging.warning(ee)
    pass


def chatid(bot, update):
    '''Return chat id to the user who asked for it'''
    bot.sendMessage(update.message.chat_id, update.message.chat_id)

def main():
    updater = Updater(telegramToken)
    dp = updater.dispatcher

    # Comandos
    dp.add_handler(CommandHandler("chatid", chatid))
    dp.add_handler(CommandHandler("help", help))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
