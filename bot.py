import os
import sys
import logging

from uuid import uuid4
from os.path import join, dirname
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler, CallbackContext
from telegram.ext import ConversationHandler, CallbackQueryHandler, Filters, InlineQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto, InputTextMessageContent
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Update, ParseMode

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class OrderDetails:
    def __init__(self, orderTime, foodQuantity, foodPrice, restaurant, deliveryFee, orderId, deliveryLocation):
        self.orderTime = orderTime
        self.foodQuantity = foodQuantity
        self.foodPrice = foodPrice
        self.restaurant = restaurant
        self.deliveryFee = deliveryFee
        self.orderId = orderId
        self.deliveryLocation = deliveryLocation


# global vars
TID_OID = {}
OID_DETAILS = {}
CANTEEN_IMG_MAP = {
    'deck': 'https://uci.nus.edu.sg/oca/wp-content/uploads/sites/9/2018/05/NUS_Roving_2015-73-Deck-1024x684.jpg',
    'flavours': 'https://uci.nus.edu.sg/oca/wp-content/uploads/sites/9/2018/05/Flavours-Edited-1024x684.jpg',
    'finefoods': 'https://uci.nus.edu.sg/oca/wp-content/uploads/sites/9/2018/05/Fine-Food-1-1024x684.jpg'
}

LOGIN_STATE, CHOOSE_ROLE_STATE, CUSTOMER_CHOOSE_CANTEEN_STATE, CUSTOMER_CONFIRM_ORDER_STATE, \
    CUSTOMER_PUSH_ORDER_STATE, CUSTOMER_USER_LOCATION_STATE, \
    DELIVERER_COMPLETE_ORDER_STATE, DELIVERER_SHOW_ORDER_STATE, DELIVERER_DELIVERED_STATE = range(
        9)


def start(update, context):
    username = update.message.chat.username
    startMessage = "Hi, " + username + ". Welcome to nusmakan_bot"
    # put logo pic
    logger.info('%s: started order', username)
    update.message.reply_text(startMessage)
    keyboard = [['login']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    loginMessage = "Please login to your NUSNET account"
    chat_id = update.message.chat_id
    update.message.reply_text(loginMessage, reply_markup=reply_markup)
    return LOGIN_STATE


def login(update, context):
    # do login stuff

    keyboard = [['customer', 'deliverer']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "Are you a customer or a deliverer"
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id=chat_id, text=message, reply_markup=reply_markup)
    return CHOOSE_ROLE_STATE


def chooseRole(update, context):
    USER_REPLY = update.message.text
    print(USER_REPLY)
    keyboard_location = [['location']]
    reply_markup_location = ReplyKeyboardMarkup(keyboard_location,
                                                one_time_keyboard=True,
                                                resize_keyboard=True)

    keyboard_show_orders = [['showorders']]
    reply_markup_show_orders = ReplyKeyboardMarkup(keyboard_show_orders,
                                                   one_time_keyboard=True,
                                                   resize_keyboard=True)
    chat_id = update.message.chat_id
    if USER_REPLY == "customer":
        context.bot.send_message(
            chat_id=chat_id, text="Please input your location", reply_markup=reply_markup_location)
        return CUSTOMER_USER_LOCATION_STATE
    elif USER_REPLY == "deliverer":
        context.bot.send_message(
            chat_id=chat_id, text="Here are the orders", reply_markup=reply_markup_show_orders)
        return DELIVERER_SHOW_ORDER_STATE
    else:
        return LOGIN_STATE


def userLocation(update: Update, context: CallbackContext) -> int:
    # get user location
    chat_id = update.message.chat_id

    context.bot.send_photo(
        chat_id=chat_id, photo=CANTEEN_IMG_MAP['finefoods'], caption='Fine Food')
    context.bot.send_photo(
        chat_id=chat_id, photo=CANTEEN_IMG_MAP['flavours'], caption='Flavours@UTown')
    context.bot.send_photo(
        chat_id=chat_id, photo=CANTEEN_IMG_MAP['deck'], caption='The Deck')

    keyboard = [['finefoods', 'flavours', 'thedeck']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "Which food court do you wish to order from?"

    context.bot.send_message(
        chat_id=chat_id, text=message, reply_markup=reply_markup)

    return CUSTOMER_CHOOSE_CANTEEN_STATE


def chooseCanteen(update, context):
    CANTEEN = update.message.text
    chat_id = update.message.chat_id
    message = "Choose your food to order"
    keyboard = [['confirmorder']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat_id, text=message, reply_markup=reply_markup)

    if CANTEEN == 'finefoods':
        # show menu
        finefoodsMessage = "finefood menu"
        context.bot.send_message(chat_id=chat_id, text=finefoodsMessage)
        return CUSTOMER_CONFIRM_ORDER_STATE
    elif CANTEEN == 'flavours':
        # show menu
        flavoursMessage = "flavours menu"
        context.bot.send_message(chat_id=chat_id, text=flavoursMessage)
        return CUSTOMER_CONFIRM_ORDER_STATE
    elif CANTEEN == 'thedeck':
        # show menu
        deckMessage = "deck menu"
        context.bot.send_message(
            chat_id=chat_id, text=deckMessage, reply_markup=reply_markup)
        return CUSTOMER_CONFIRM_ORDER_STATE


def confirmOrder(update, context):
    keyboard = [['pushorder', 'goback']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "Push order?"
    update.message.reply_text(message, reply_markup=reply_markup)
    return CUSTOMER_PUSH_ORDER_STATE


def pushOrder(update, context):
    MESSAGE = update.message.text
    keyboard_startmenu = [['startmenu']]
    reply_markup_startmenu = ReplyKeyboardMarkup(keyboard_startmenu,
                                                 one_time_keyboard=True,
                                                 resize_keyboard=True)
    keyboard_foodmenu = [['confirmorder']]
    reply_markup_foodmenu = ReplyKeyboardMarkup(keyboard_foodmenu,
                                                one_time_keyboard=True,
                                                resize_keyboard=True)
    if MESSAGE == "pushorder":
        message = "Order pushed, please wait"
        update.message.reply_text(message, reply_markup=reply_markup_startmenu)
        # wait for delivery here
        return LOGIN_STATE
    elif MESSAGE == "goback":
        message = "Choose your food to order"
        update.message.reply_text(message, reply_markup=reply_markup_foodmenu)
        return CUSTOMER_CONFIRM_ORDER_STATE


def showOrder(update, context):
    keyboard = [['confirm']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "Confirm to deliver these?"
    update.message.reply_text(message, reply_markup=reply_markup)
    return DELIVERER_COMPLETE_ORDER_STATE


def completeOrder(update, context):
    keyboard = [['delivered']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "Delivered?"
    update.message.reply_text(message, reply_markup=reply_markup)
    return DELIVERER_DELIVERED_STATE


def deliveredOrder(update, context):
    MESSAGE = update.message.text
    keyboard = [['startmenu']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    if MESSAGE == 'delivered':
        chat_id = update.message.chat_id
        context.bot.send_message(
            chat_id=chat_id, text="Weee! Your customer is grateful for the food", reply_markup=reply_markup)
        return LOGIN_STATE


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! /start to begin again',
                              reply_markup=ReplyKeyboardRemove())


def main(dev=True):
    """
    Main function.
    This function handles the conversation flow by setting
    states on each step of the flow. Each state has its own
    handler for the interaction with the user.
    """
    # Create the EventHandler and pass it your bot's token.
    myToken = None
    if dev:
        myToken = os.environ.get('DEV_TOKEN')
    else:
        myToken = os.environ.get('TOKEN')

    updater = Updater(token=myToken, use_context=True)

    # Get the dispatcher to register handlers:
    dp = updater.dispatcher

    # Add conversation handler with predefined states:
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            LOGIN_STATE: [MessageHandler(Filters.regex('login|startmenu'), login)],

            CHOOSE_ROLE_STATE: [MessageHandler(Filters.regex('customer|deliverer'), chooseRole)],

            CUSTOMER_USER_LOCATION_STATE: [MessageHandler(Filters.regex('location'), userLocation)],

            CUSTOMER_CHOOSE_CANTEEN_STATE: [MessageHandler(Filters.regex('finefoods|flavours|thedeck|goback'), chooseCanteen)],

            CUSTOMER_CONFIRM_ORDER_STATE: [MessageHandler(Filters.regex('confirmorder'), confirmOrder)],

            CUSTOMER_PUSH_ORDER_STATE: [MessageHandler(Filters.regex('pushorder|goback'), pushOrder)],

            DELIVERER_SHOW_ORDER_STATE: [MessageHandler(Filters.regex('showorders'), showOrder)],

            DELIVERER_COMPLETE_ORDER_STATE: [MessageHandler(Filters.regex('confirm'), completeOrder)],

            DELIVERER_DELIVERED_STATE: [MessageHandler(Filters.regex('delivered'), deliveredOrder)],
        },

        fallbacks=[CommandHandler('Cancel', cancel)],
        per_user=False
    )

    dp.add_handler(conv_handler)

    # Log all errors:
    dp.add_error_handler(error)

    # Start DisAtBot:
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process
    # receives SIGINT, SIGTERM or SIGABRT:
    updater.idle()


if __name__ == '__main__':
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    print("RUNNING NOW")
    main()
