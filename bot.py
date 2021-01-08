from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler
from telegram.ext import ConversationHandler, CallbackQueryHandler, Filters, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

import logging
import random

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

LOGIN_STATE, CHOOSE_STATE, CUSTOMER_CHOOSE_CANTEEN_STATE, CUSTOMER_CONFIRM_ORDER_STATE, \
CUSTOMER_PUSH_ORDER_STATE, CUSTOMER_USER_LOCATION_STATE, \
DELIVERER_COMPLETE_ORDER_STATE, DELIVERER_SHOW_ORDER_STATE, DELIVERER_DELIVERED_STATE = range(9)

def start(update: Update, context: CallbackContext) -> None:
    username = update.message.chat.username
    startMessage = "Hi, " + str(username) + ". Welcome to nusmakan_bot"
    update.message.reply_text(startMessage) 
    
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id, "https://uci.nus.edu.sg/oca/wp-content/uploads/sites/9/2018/05/NUS_Roving_2015-73-Deck-1024x684.jpg")
    
    keyboard = [[ InlineKeyboardButton("Login 😊", callback_data='login')]]
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
    keyboard = [[ InlineKeyboardButton("Customer 💁", callback_data='userLocation'), InlineKeyboardButton("Deliverer 🚚", callback_data='showOrder')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "Are you a customer or a deliverer"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    
    return CHOOSE_STATE

# def chooseRole(update, context):
#     USER_REPLY = update.message.text
#     print(USER_REPLY)
#     keyboard_location = [['location']]
#     reply_markup_location = ReplyKeyboardMarkup(keyboard_location,
#                                                one_time_keyboard=True,
#                                                resize_keyboard=True)

#     keyboard_show_orders = [['showorders']]
#     reply_markup_show_orders = ReplyKeyboardMarkup(keyboard_show_orders,
#                                             one_time_keyboard=True,
#                                             resize_keyboard=True)
#     chat_id = update.message.chat_id
#     if USER_REPLY == "customer":
#         context.bot.send_message(
#             chat_id=chat_id, text="Please input your location", reply_markup=reply_markup_location)
#         return CUSTOMER_USER_LOCATION_STATE
#     elif USER_REPLY == "deliverer":
#         context.bot.send_message(
#             chat_id=chat_id, text="Here are the orders", reply_markup=reply_markup_show_orders)
#         return DELIVERER_SHOW_ORDER_STATE
#     else: 
#         return LOGIN_STATE

def userLocation(update: Update, context: CallbackContext) -> None:
    # get user location
    query = update.callback_query
    query.answer()

    # user = update.callback_query.message.from_user
    # user_location = update.callback_query.message.location
    # print(user_location)

    chat_id = update.callback_query.message.chat.id
    message = "Where do you want the food to be delivered to?"
    context.bot.send_message(chat_id, text=message)

    keyboard = [[ InlineKeyboardButton("Yes", callback_data='chooseCanteen'), InlineKeyboardButton("No", callback_data='userLocation') ]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "Confirm your location is at SOC Programming Lab 4?"
    context.bot.send_message(chat_id, text=message, reply_markup=reply_markup)
    return CHOOSE_STATE

def chooseCanteen(update, context):
    query = update.callback_query
    query.answer()

    chat_id = update.callback_query.message.chat.id
    context.bot.send_photo(chat_id, "https://uci.nus.edu.sg/oca/wp-content/uploads/sites/9/2018/05/NUS_Roving_2015-73-Deck-1024x684.jpg")
    context.bot.send_photo(chat_id, "https://uci.nus.edu.sg/oca/wp-content/uploads/sites/9/2018/05/Flavours-Edited-1024x684.jpg")
    context.bot.send_photo(chat_id, "https://uci.nus.edu.sg/oca/wp-content/uploads/sites/9/2018/05/Fine-Food-1-1024x684.jpg")

    keyboard = [[ InlineKeyboardButton("Fine Foods 🍔", callback_data='finefoods'), InlineKeyboardButton("Flavours 🍇", callback_data='flavours'), InlineKeyboardButton("The Deck 🚢", callback_data='thedeck')]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "Which food court do you wish to order from"
    context.bot.send_message(chat_id, text=message, reply_markup=reply_markup)
    return CHOOSE_STATE

def finefoods(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[ 
        InlineKeyboardButton("Gong Cha Pearl Milk Tea $3.50", callback_data='confirmOrder3.50'),
        InlineKeyboardButton("Shanghai Xiao Long Bao $4.50", callback_data='confirmOrder4.50'), 
        InlineKeyboardButton("Korean BBQ Beef Set $5.00", callback_data='confirmOrder5.00'), 
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "What food?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return CHOOSE_STATE

def flavours(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[ 
        InlineKeyboardButton("Roti John $4.50", callback_data='confirmOrder4.50'),
        InlineKeyboardButton("Taiwanese Chicken Chop Rice $5.00", callback_data='confirmOrder5.00'), 
        InlineKeyboardButton("Mala Hotpot $6.50", callback_data='confirmOrder6.50'), 
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "What food?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return CHOOSE_STATE

def thedeck(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[ 
        InlineKeyboardButton("Chicken Rice $3.00", callback_data='confirmOrder3.00'),
        InlineKeyboardButton("Yong Tau Foo $3.00", callback_data='confirmOrder3.00'), 
        InlineKeyboardButton("Japanese Chicken Cutlet Set $4.00", callback_data='confirmOrder4.00'), 
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "What food?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return CHOOSE_STATE

def confirmOrder(update, context):
    query = update.callback_query
    query.answer()
    foodCost = float(query.data[12:])
    deliveryCost = random.uniform(0.5, 1.9)
    totalCost = foodCost + deliveryCost

    keyboard = [[ InlineKeyboardButton("Yes", callback_data='pushOrder'), InlineKeyboardButton("No", callback_data='chooseCanteen') ]]
    reply_markup = InlineKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    message = "Food cost: $" + str(foodCost) + "\nDelivery cost: $" + str(deliveryCost) + "\nTotal cost: $" + str(totalCost) + "\nConfirm order?"
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return CHOOSE_STATE

def pushOrder(update, context):
    query = update.callback_query
    query.answer()

    #check if order exist
    #if doesn't exist, create order & push
    #else check if order is complete
    orderIsComplete = False
    if random.uniform(0.5, 1.9) > 1.3:
        orderIsComplete = True

    message = "The restaurant has been notified of your order. Please wait "
    if orderIsComplete:
        chat_id = query.message.chat.id
        keyboard = [[ InlineKeyboardButton("Yes", callback_data='userLocation'), InlineKeyboardButton("No", callback_data='bye') ]]
        reply_markup = InlineKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
        message = "Thank you! ❤️ Do you want to order again?"
        context.bot.send_message(chat_id, text=message, reply_markup=reply_markup)
    else:
        if random.uniform(0.0, 1.0) > 0.5:
            message += "🙏🙏"
        keyboard = [[ InlineKeyboardButton("Refresh", callback_data='pushOrder')]]
        reply_markup = InlineKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
        query.edit_message_text(text=message, reply_markup=reply_markup)
    return CHOOSE_STATE
    

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
        context.bot.send_message(chat_id=chat_id, text="Weee! Your customer is grateful for the food", reply_markup=reply_markup)
        return LOGIN_STATE

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! /start to begin again',
                              reply_markup=ReplyKeyboardRemove())

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
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token="1519714958:AAEoXv4mFqM2wXkCVNDOnXUh_IH8Sgr6tG4", use_context=True)

    # Get the dispatcher to register handlers:
    dp = updater.dispatcher

    # Add conversation handler with predefined states:
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            LOGIN_STATE: [CallbackQueryHandler(login, pattern='login|startmenu')],

            CHOOSE_STATE: [CallbackQueryHandler(userLocation, pattern='userLocation'), CallbackQueryHandler(showOrder, pattern='showOrder'), CallbackQueryHandler(chooseCanteen, pattern='chooseCanteen'), CallbackQueryHandler(userLocation, pattern='userLocation'), CallbackQueryHandler(finefoods, pattern='finefoods'), CallbackQueryHandler(confirmOrder, pattern='confirmOrder'), CallbackQueryHandler(pushOrder, pattern='pushOrder'), CallbackQueryHandler(bye, pattern='bye')],

            CUSTOMER_CHOOSE_CANTEEN_STATE: [MessageHandler(Filters.regex('finefoods|flavours|thedeck|goback'), chooseCanteen)],

            CUSTOMER_CONFIRM_ORDER_STATE: [MessageHandler(Filters.regex('confirmorder'), confirmOrder)],

            CUSTOMER_PUSH_ORDER_STATE: [MessageHandler(Filters.regex('pushorder|goback'), pushOrder)],

            DELIVERER_SHOW_ORDER_STATE: [MessageHandler(Filters.regex('showorders'), showOrder)],

            DELIVERER_COMPLETE_ORDER_STATE: [MessageHandler(Filters.regex('confirm'), completeOrder)],

            DELIVERER_DELIVERED_STATE: [MessageHandler(Filters.regex('delivered'), deliveredOrder)],
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
    updater.idle()

if __name__ == '__main__':
    print("RUNNING NOW")
    main()
