from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler
from telegram.ext import ConversationHandler, CallbackQueryHandler, Filters, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import os
from os.path import join, dirname
from dotenv import load_dotenv
import logging
import random
from time import sleep
import datetime
import threading
from decimal import Decimal

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class OrderDetails:
    def __init__(self, orderTime=None, foodQuantity=None, foodPrice=None, restaurant=None, deliveryFee=None, orderId=None, deliveryLocation=None, isComplete=False, isPickUp=False):
        self.orderTime = orderTime
        self.foodQuantity = foodQuantity
        self.foodPrice = foodPrice
        self.restaurant = restaurant
        self.deliveryFee = deliveryFee
        self.orderId = orderId
        self.deliveryLocation = deliveryLocation
        self.isComplete = isComplete
        self.isPickUp = isPickUp


# global vars
GLOBAL_USERS_DB = {}
# dictionary of the OrderDetails class
GLOBAL_ORDERS = {}

LOGIN_STATE, CUSTOMER_STATE, DELIVERER_STATE = range(3)


def start(update: Update, context: CallbackContext) -> None:
    username = update.message.chat.username
    startMessage = "Hi, " + str(username) + ". Welcome to nusmakan_bot"
    update.message.reply_text(startMessage)

    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id, photo=open(
        'public/nusmakan_bot_image.png', 'rb'))
    keyboard = [[InlineKeyboardButton("Login 😊", callback_data='login')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    loginMessage = "Please login to your NUSNET account"
    update.message.reply_text(loginMessage, reply_markup=reply_markup)
    return LOGIN_STATE


def login(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton("Customer 💁", callback_data='userLocation'), InlineKeyboardButton(
        "Deliverer 🚚", callback_data='showOrder')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "Are you a customer or a deliverer"
    query.edit_message_text(text=message, reply_markup=reply_markup)

    return CUSTOMER_STATE


def userLocation(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    # user_location = update.callback_query.message.location
    # print(user_location)

    chat_id = update.callback_query.message.chat.id
    message = "Where do you want the food to be delivered to?"
    context.bot.send_message(chat_id, text=message)

    keyboard = [[InlineKeyboardButton("Yes", callback_data='chooseCanteen'), InlineKeyboardButton(
        "No", callback_data='userLocation')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "Confirm your location is at SOC Programming Lab 4?"
    context.bot.send_message(chat_id, text=message, reply_markup=reply_markup)
    return CUSTOMER_STATE


def chooseCanteen(update, context):
    query = update.callback_query
    query.answer()
    chat_id = update.callback_query.message.chat.id

    context.bot.send_photo(
        chat_id, "https://uci.nus.edu.sg/oca/wp-content/uploads/sites/9/2018/05/NUS_Roving_2015-73-Deck-1024x684.jpg")
    context.bot.send_photo(
        chat_id, "https://uci.nus.edu.sg/oca/wp-content/uploads/sites/9/2018/05/Flavours-Edited-1024x684.jpg")
    context.bot.send_photo(
        chat_id, "https://uci.nus.edu.sg/oca/wp-content/uploads/sites/9/2018/05/Fine-Food-1-1024x684.jpg")

    keyboard = [[InlineKeyboardButton("Fine Foods 🍔", callback_data='finefoods'), InlineKeyboardButton(
        "Flavours 🍇", callback_data='flavours'), InlineKeyboardButton("The Deck 🚢", callback_data='thedeck')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "Which food court do you wish to order from"
    context.bot.send_message(chat_id, text=message, reply_markup=reply_markup)
    return CUSTOMER_STATE


def finefoods(update, context):
    query = update.callback_query
    query.answer()

    keyboard = [
        [InlineKeyboardButton("Gong Cha Pearl Milk Tea $3.50",
                              callback_data='confirmOrder3.50', resize_keyboard=True)],
        [InlineKeyboardButton("Shanghai Xiao Long Bao $4.50",
                              callback_data='confirmOrder4.50', resize_keyboard=True)],
        [InlineKeyboardButton("Korean BBQ Beef Set $5.00",
                              callback_data='confirmOrder5.00', resize_keyboard=True)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "What FineFood food?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return CUSTOMER_STATE


def flavours(update, context):
    query = update.callback_query
    query.answer()

    keyboard = [
        [InlineKeyboardButton(
            "Roti John $4.50", callback_data='confirmOrder4.50')],
        [InlineKeyboardButton(
            "Taiwanese Chicken Chop Rice $5.00", callback_data='confirmOrder5.00')],
        [InlineKeyboardButton("Mala Hotpot $6.50",
                              callback_data='confirmOrder6.50')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "What Flavours food?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return CUSTOMER_STATE


def thedeck(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Chicken Rice $3.00",
                              callback_data='confirmOrder3.00')],
        [InlineKeyboardButton("Yong Tau Foo $3.00",
                              callback_data='confirmOrder3.00')],
        [InlineKeyboardButton(
            "Japanese Chicken Cutlet Set $4.00", callback_data='confirmOrder4.00')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "What TheDeck food?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return CUSTOMER_STATE


def confirmOrder(update, context):
    query = update.callback_query
    query.answer()
    print(query.message.text)
    restaurant = query.message.text.split()[1]
    foodCost = float(query.data[12:])
    deliveryCost = random.uniform(0.5, 1.9)
    totalCost = round(Decimal(foodCost + deliveryCost), 2)

    keyboard = [[InlineKeyboardButton("Yes", callback_data='pushOrder'), InlineKeyboardButton(
        "No", callback_data='chooseCanteen')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "Restaurant: " + restaurant + "\nFood cost: $" + str(foodCost) + "\nDelivery cost: $" + str(
        deliveryCost) + "\nTotal cost: $" + str(totalCost) + "\nConfirm order?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return CUSTOMER_STATE


iid = 1
iid_lock = threading.Lock()


def next_id():
    global iid
    with iid_lock:
        result = iid
        iid += 1
    return result


def pushOrder(update, context):
    query = update.callback_query
    query.answer()

    arrayOfInfo = query.message.text.split()
    print(arrayOfInfo)
    orderId = next_id()

    # push into user's database as CURRENT ORDER waiting to be picked up
    global GLOBAL_USERS_DB
    chat_id = update.callback_query.message.chat.id
    order = {'foodQuantity': 1, 'orderId': orderId,
             'restaurant': arrayOfInfo[1], 'deliveryFee': arrayOfInfo[7], 'foodPrice': arrayOfInfo[4],
             'isComplete': False, 'isPickup': False, 'orderTime': str(datetime.datetime.now()), 'deliveryLocation': 'Programming Lab 4'}
    # 2 array: as CUSTOMER and as DELIVERER
    GLOBAL_USERS_DB[chat_id] = [[], []]
    GLOBAL_USERS_DB[chat_id][0].append(orderId)

    # push into order database
    global GLOBAL_ORDERS
    GLOBAL_ORDERS[orderId] = order

    message = "Order pushed, please wait"
    query.edit_message_text(text=message)
    print(GLOBAL_ORDERS[orderId])
    while GLOBAL_ORDERS[orderId]['isPickup'] == False:
        sleep(5)
    message = "Your order has been picked up by a deliverer!"
    query.edit_message_text(text=message)
    while GLOBAL_ORDERS[orderId]['isComplete'] == False:
        sleep(5)
    message = "Your order has been delivered!"
    keyboard = [[InlineKeyboardButton("Start Menu", callback_data='login')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return LOGIN_STATE


def showOrder(update, context):
    query = update.callback_query
    query.answer()
    buttons = []

    for key in GLOBAL_ORDERS:
        if GLOBAL_ORDERS[key]['isPickup'] == False:
            text = "Order " + \
                str(GLOBAL_ORDERS[key].restaurant) + " price" + \
                str(GLOBAL_ORDERS[key].foodQuantity)
            buttons.append(InlineKeyboardButton(
                text, callback_data='completeOrder' + str(key)))
    keyboard = [buttons]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    # text box with selection
    message = "These are the orders waiting to be picked up: \n"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return DELIVERER_STATE


def completeOrder(update, context):
    query = update.callback_query
    query.answer()
    global GLOBAL_ORDERS
    key = int(query.data[13:])
    GLOBAL_ORDERS[key]['isPickup'] = True

    keyboard = [[InlineKeyboardButton(
        "I have delivered", callback_data='deliveredOrder' + str(key))]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "Have you delivered?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return DELIVERER_STATE


def deliveredOrder(update, context):
    query = update.callback_query
    query.answer()
    chat_id = update.callback_query.message.chat.id

    global GLOBAL_ORDERS
    key = int(query.data[14:])
    GLOBAL_ORDERS[key]['isComplete'] = True

    global GLOBAL_USERS_DB
    # 2 array: as CUSTOMER and as DELIVERER
    GLOBAL_USERS_DB[chat_id] = [[], []]
    GLOBAL_USERS_DB[chat_id][1].append(key)

    keyboard = [[InlineKeyboardButton("Start Menu", callback_data='login')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "Weee! Your customer is grateful for the food!"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return LOGIN_STATE


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def bye(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat.id
    context.bot.send_message(chat_id, text="Hope to see you again soon! 😃")
    return LOGIN_STATE


def main():
    """
    Main function.
    This function handles the conversation flow by setting
    states on each step of the flow. Each state has its own
    handler for the interaction with the user.
    """
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    myToken = os.environ.get('TOKEN')
    updater = Updater(
        token=myToken, use_context=True)

    # Get the dispatcher to register handlers:
    dp = updater.dispatcher

    # Add conversation handler with predefined states:
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            LOGIN_STATE: [CallbackQueryHandler(login, pattern='login')],

            CUSTOMER_STATE: [
                CallbackQueryHandler(userLocation, pattern='userLocation'),
                CallbackQueryHandler(chooseCanteen, pattern='chooseCanteen'),
                CallbackQueryHandler(finefoods, pattern='finefoods'),
                CallbackQueryHandler(flavours, pattern='flavours'),
                CallbackQueryHandler(thedeck, pattern='thedeck'),
                CallbackQueryHandler(confirmOrder, pattern='confirmOrder'),
                CallbackQueryHandler(pushOrder, pattern='pushOrder'),
                CallbackQueryHandler(showOrder, pattern='showOrder'),
            ],

            DELIVERER_STATE: [
                CallbackQueryHandler(completeOrder, pattern='completeOrder'),
                CallbackQueryHandler(deliveredOrder, pattern='deliveredOrder'),
            ]
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
    print("RUNNING NOW")
    main()
