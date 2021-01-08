from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler
from telegram.ext import ConversationHandler, CallbackQueryHandler, Filters, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Location
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from time import sleep
from dotenv import load_dotenv

import pandas as pd
import logging
import random
import os

load_dotenv()

CURR_DIR = os.path.dirname(__file__)
LOC_DATA_FILE = os.path.join(CURR_DIR, 'NUS_Google_Coordinates.csv')

df = pd.read_csv(LOC_DATA_FILE)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class OrderDetails:
    def __init__(self, orderTime=None, foodQuantity=None, foodPrice=None, restaurant=None, deliveryFee=None, orderId=None, deliveryLocation=None):
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

LOGIN_STATE, CUSTOMER_STATE, DELIVERER_STATE = range(3)


def start(update: Update, context: CallbackContext) -> None:
    username = update.message.chat.username
    startMessage = "Hi, " + str(username) + ". Welcome to nusmakan_bot"
    update.message.reply_text(startMessage)

    chat_id = update.message.chat_id
    context.bot.send_photo(
        chat_id, "https://uci.nus.edu.sg/oca/wp-content/uploads/sites/9/2018/05/NUS_Roving_2015-73-Deck-1024x684.jpg")

    keyboard = [[InlineKeyboardButton("Login 😊", callback_data='login')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    loginMessage = "Please login to your NUSNET account"
    update.message.reply_text(loginMessage, reply_markup=reply_markup)
    return LOGIN_STATE


def login(update: Update, context: CallbackContext) -> None:
    # do login stuff
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


def userLocation(update: Update, context: CallbackContext) -> int:
    '''
    Use regular keyboard to send current location information.
    '''
    query = update.callback_query
    query.answer()

    chat_id = update.callback_query.message.chat.id
    message = "Agree to send your current location to deliver your order?"

    keyboard = [[KeyboardButton("Yes", request_location=True, request_contact=False), KeyboardButton(
        "No")]]

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)

    context.bot.send_message(
        chat_id, text=message, reply_markup=reply_markup)
    return CUSTOMER_STATE


def locationCallback(update: Update, context: CallbackContext) -> int:
    '''
    Separate callback function for noting down ALL location information.
    Probably be a bug, since it circumvents the login flow.
    '''
    logger.info('Location at: %s', update.effective_message.location)
    location = update.effective_message.location
    lat, lng = location.latitude, location.longitude

    sample_df = df[(df['Latitude'] - lat > 0.01) &
                   (df['Longitude'] - lng > 0.01)]
    logger.info(sample_df)

    chat_id = update.message.chat_id

    message = f'Confirm location?'

    if not sample_df.empty:
        message = message[::-1] + ' ' + sample_df['building'].iloc[0] + ', ' + \
            sample_df['Description'].iloc[0] + ', ' + \
            sample_df['Building_full_name'].iloc[0]

    keyboard = [[InlineKeyboardButton("Yes", callback_data='chooseCanteen'), InlineKeyboardButton(
        "No", callback_data='userLocation')]]

    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)

    context.bot.send_message(
        chat_id, text=message, reply_markup=reply_markup)

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
    keyboard = [[
        InlineKeyboardButton("Gong Cha Pearl Milk Tea $3.50",
                             callback_data='confirmOrder3.50'),
        InlineKeyboardButton("Shanghai Xiao Long Bao $4.50",
                             callback_data='confirmOrder4.50'),
        InlineKeyboardButton("Korean BBQ Beef Set $5.00",
                             callback_data='confirmOrder5.00'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "What food?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return CUSTOMER_STATE


def flavours(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[
        InlineKeyboardButton(
            "Roti John $4.50", callback_data='confirmOrder4.50'),
        InlineKeyboardButton("Taiwanese Chicken Chop Rice $5.00",
                             callback_data='confirmOrder5.00'),
        InlineKeyboardButton("Mala Hotpot $6.50",
                             callback_data='confirmOrder6.50'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "What food?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return CUSTOMER_STATE


def thedeck(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[
        InlineKeyboardButton("Chicken Rice $3.00",
                             callback_data='confirmOrder3.00'),
        InlineKeyboardButton("Yong Tau Foo $3.00",
                             callback_data='confirmOrder3.00'),
        InlineKeyboardButton("Japanese Chicken Cutlet Set $4.00",
                             callback_data='confirmOrder4.00'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "What food?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return CUSTOMER_STATE


def flavours(update, context):
    query = update.callback_query
    query.answer()
    # @Jun Hao populate this keyboard with nice emojis and real food/pricing
    keyboard = [[InlineKeyboardButton("A $1.50", callback_data='confirmOrder1.50'),
                 InlineKeyboardButton(
                     "B $2.00", callback_data='confirmOrder2.00'),
                 InlineKeyboardButton("C $3.00", callback_data='confirmOrder3.00')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "What food?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return CUSTOMER_STATE


def thedeck(update, context):
    query = update.callback_query
    query.answer()
    # @Jun Hao populate this keyboard with nice emojis and real food/pricing
    keyboard = [[InlineKeyboardButton("A $1.50", callback_data='confirmOrder1.50'),
                 InlineKeyboardButton(
                     "B $2.00", callback_data='confirmOrder2.00'),
                 InlineKeyboardButton("C $3.00", callback_data='confirmOrder3.00')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "What food?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return CUSTOMER_STATE


def confirmOrder(update, context):
    query = update.callback_query
    query.answer()
    foodCost = float(query.data[12:])
    deliveryCost = random.uniform(0.5, 1.9)
    totalCost = foodCost + deliveryCost

    keyboard = [[InlineKeyboardButton("Yes", callback_data='pushOrder'), InlineKeyboardButton(
        "No", callback_data='chooseCanteen')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "Food cost: $" + str(round(foodCost, 2)) + "\nDelivery cost: $" + str(
        round(deliveryCost, 2)) + "\nTotal cost: $" + str(round(totalCost, 2)) + "\nConfirm order?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return CUSTOMER_STATE


def pushOrder(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton("Start Menu", callback_data='login')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "Order pushed, please wait"
    query.edit_message_text(text=message)
    sleep(2)
    # found a deliverer algo
    message = "Your order has been picked up by a deliverer!"
    query.edit_message_text(text=message)
    sleep(2)
    # food delivered algo
    message = "Your order has been delivered!"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return LOGIN_STATE


def showOrder(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton(
        "Confirm orders", callback_data='completeOrder')]]
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
    keyboard = [[InlineKeyboardButton(
        "I have delivered", callback_data='deliveredOrder')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    message = "Have you delivered?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return DELIVERER_STATE


def deliveredOrder(update, context):
    query = update.callback_query
    query.answer()
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
    chat_id = update.message.chat_id
    logger.info("User %s canceled the conversation.", user.first_name)
    context.bot.send_message(chat_id=chat_id, text="See you next time!")
    return ConversationHandler.END


def bye(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id, text="See you again soon! Type /start to order again 😃")
    return LOGIN_STATE


def main(dev_token=False):
    """
    Main function.
    This function handles the conversation flow by setting
    states on each step of the flow. Each state has its own
    handler for the interaction with the user.
    """
    # Create the EventHandler and pass it your bot's token.
    token = None
    if dev_token:
        token = os.getenv('DEV_TOKEN')
    else:
        token = os.getenv('TOKEN')
    updater = Updater(token=token, use_context=True)

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
                CallbackQueryHandler(showOrder, pattern='showOrders'),
                CallbackQueryHandler(completeOrder, pattern='completeOrder'),
                CallbackQueryHandler(deliveredOrder, pattern='deliveredOrder'),
            ]
        },

        fallbacks=[CommandHandler('Cancel', bye)],
        per_user=False,
        allow_reentry=True
    )

    dp.add_handler(conv_handler)

    # Location Callback
    dp.add_handler(MessageHandler(Filters.location, locationCallback))

    # Log all errors:
    dp.add_error_handler(error)

    # Start DisAtBot:
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process
    # receives SIGINT, SIGTERM or SIGABRT:
    updater.idle()


if __name__ == '__main__':
    print("RUNNING NOW")
    main(dev_token=True)
