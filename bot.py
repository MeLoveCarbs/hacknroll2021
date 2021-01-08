from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler
from telegram.ext import ConversationHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import os
from os.path import join, dirname
from dotenv import load_dotenv
import logging

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

LOGIN_STATE, CHOOSE_ROLE_STATE, CUSTOMER_CHOOSE_CANTEEN_STATE, CUSTOMER_CONFIRM_ORDER_STATE, CUSTOMER_DECK_MENU_STATE, \
CUSTOMER_FINEFOOD_MENU_STATE, CUSTOMER_FLAVOUR_MENU_STATE, CUSTOMER_PUSH_ORDER_STATE, CUSTOMER_USER_LOCATION_STATE, CUSTOMER_WAIT_STATE, \
DELIVERER_COMPLETE_ORDER_STATE, DELIVERER_SHOW_ORDER_STATE = range(12)

def start(update, context):
    keyboard = [['3', '4', '5', '6']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "Welcome to nusmakan_bot"
    update.message.reply_text(message, reply_markup=reply_markup) 
    return LOGIN_STATE

def login(update, context):
    keyboard = [['3', '4', '5', '6']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "login state"
    update.message.reply_text(message, reply_markup=reply_markup) 
    return CHOOSE_ROLE_STATE

def chooseRole(update, context):
    keyboard = [['3', '4', '5', '6']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "choose role state"
    update.message.reply_text(message, reply_markup=reply_markup) 
    if customer :
        return CUSTOMER_USER_LOCATION_STATE
    else:
        return DELIVERER_SHOW_ORDER_STATE

def userLocation(update, context):
    keyboard = [['3', '4', '5', '6']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "choose location state"
    update.message.reply_text(message, reply_markup=reply_markup) 

    return CUSTOMER_CHOOSE_CANTEEN_STATE

def chooseCanteen(update, context):
    keyboard = [['3', '4', '5', '6']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "choose canteen state"
    update.message.reply_text(message, reply_markup=reply_markup) 
    
    if fineFood:
        return CUSTOMER_FINEFOOD_MENU_STATE
    elif deck:
        return CUSTOMER_DECK_MENU_STATE
    elif flavour:
        return CUSTOMER_FLAVOUR_MENU_STATE

def finefoodMenu(update, context):
    keyboard = [['3', '4', '5', '6']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "fine food menu state"
    update.message.reply_text(message, reply_markup=reply_markup) 
    return CUSTOMER_CONFIRM_ORDER_STATE
def flavourMenu(update, context):
    keyboard = [['3', '4', '5', '6']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "flavour menu state"
    update.message.reply_text(message, reply_markup=reply_markup) 
    return CUSTOMER_CONFIRM_ORDER_STATE
def deckMenu(update, context):
    keyboard = [['3', '4', '5', '6']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "deck menu state"
    update.message.reply_text(message, reply_markup=reply_markup) 
    return CUSTOMER_CONFIRM_ORDER_STATE

def confirmOrder(update, context):
    keyboard = [['3', '4', '5', '6']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "confirm order state"
    update.message.reply_text(message, reply_markup=reply_markup) 
    if confirm:
        return CUSTOMER_PUSH_ORDER_STATE
    else: 
        return CUSTOMER_CHOOSE_CANTEEN_STATE

def pushOrder(update, context):
    keyboard = [['3', '4', '5', '6']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "push order state"
    update.message.reply_text(message, reply_markup=reply_markup) 
    return CUSTOMER_WAIT_STATE

def customerWait(update, context):
    keyboard = [['3', '4', '5', '6']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "customer wait state"
    update.message.reply_text(message, reply_markup=reply_markup) 
    
    if orderIsComplete:
        # prepare a complete message
        return CHOOSE_ROLE_STATE
    else:
        # prepare waiting message
        return CUSTOMER_WAIT_STATE

def showOrder(update, context):
    keyboard = [['3', '4', '5', '6']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "show order state"
    update.message.reply_text(message, reply_markup=reply_markup) 

    if acceptOrder:
        return DELIVERER_COMPLETE_ORDER_STATE
    else:
        return DELIVERER_SHOW_ORDER_STATE

def completeOrder(update, context):
    keyboard = [['3', '4', '5', '6']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "complete order state"
    update.message.reply_text(message, reply_markup=reply_markup) 
    if deliveryGuyPressOkay:
        #modify order details
        return CHOOSE_ROLE_STATE


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! /start to begin again',
                              reply_markup=ReplyKeyboardRemove())

def main():
    """
    Main function.
    This function handles the conversation flow by setting
    states on each step of the flow. Each state has its own
    handler for the interaction with the user.
    """
    # Create the EventHandler and pass it your bot's token.
    myToken = os.environ.get("TOKEN") 
    updater = Updater(token=myToken, use_context=True)

    # Get the dispatcher to register handlers:
    dp = updater.dispatcher

    # Add conversation handler with predefined states:
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            LOGIN_STATE: [CommandHandler('login', login)],

            CHOOSE_ROLE_STATE: [CommandHandler('chooseRole', chooseRole)],

            CUSTOMER_USER_LOCATION_STATE: [CommandHandler('userLocation', userLocation)],

            CUSTOMER_CHOOSE_CANTEEN_STATE: [CommandHandler('chooseCanteen', chooseCanteen)],

            CUSTOMER_DECK_MENU_STATE: [CommandHandler('deckMenu', deckMenu)],

            CUSTOMER_FINEFOOD_MENU_STATE: [CommandHandler('finefoodMenu', finefoodMenu)],

            CUSTOMER_FLAVOUR_MENU_STATE: [CommandHandler('flavourMenu', flavourMenu)],

            CUSTOMER_CONFIRM_ORDER_STATE: [CommandHandler('confirmOrder', confirmOrder)],

            CUSTOMER_PUSH_ORDER_STATE: [CommandHandler('pushOrder', pushOrder)],

            CUSTOMER_WAIT_STATE: [CommandHandler('wait', customerWait)],

            DELIVERER_SHOW_ORDER_STATE: [CommandHandler('showOrder', showOrder)],

            DELIVERER_COMPLETE_ORDER_STATE: [CommandHandler('completeOrder', completeOrder)],
        },

        fallbacks=[CommandHandler('Cancel', cancel)],
        per_user = False
    )

    dp.add_handler(conv_handler)

    # Log all errors:
    dp.add_error_handler(error)

    # Start DisAtBot:
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process
    # receives SIGINT, SIGTERM or SIGABRT:
    # updater.idle()

if __name__ == '__main__':
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path) 
    main()
