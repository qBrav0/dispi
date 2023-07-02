import telebot
import utils
from config import token
from utils import UserStates

from telebot import types
from telebot import custom_filters
from telebot.storage import StateMemoryStorage

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(token, state_storage=state_storage)
list_fri = utils.Lists()

@bot.message_handler(commands=['start'])
def start(message):  
    print(list_fri.return_members())
    bot.set_state(message.from_user.id, UserStates.start_menu, message.chat.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    hello_button = types.KeyboardButton('Салют!')
    keyboard.add(hello_button)
    bot.send_message(message.chat.id, f'Салют, {message.from_user.first_name}! Мене звати Діспі <3', reply_markup=keyboard)

@bot.message_handler(state = UserStates.start_menu)
def start_menu(message):
    '''Стартове меню'''
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    registration_button = types.KeyboardButton('Реєстрація')
    login_button = types.KeyboardButton('Вхід')
    keyboard.add(registration_button, login_button)

    bot.set_state(message.from_user.id, UserStates.сheck_for_registration_or_login, message.chat.id)
    bot.send_message(message.chat.id, 'Обери: Вхід або Реєстрація', reply_markup=keyboard)


@bot.message_handler(state = UserStates.сheck_for_registration_or_login)
def сheck_for_registration_or_login(message):
    '''Вхід або реєстрація до ФРІ аккаунту в боті'''

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    back_button = types.KeyboardButton('Назад')
    keyboard.add(back_button)

    if message.text == 'Вхід': 
        bot.send_message(message.chat.id, 'Введіть логін:',reply_markup=keyboard)
        bot.set_state(message.from_user.id, UserStates.enter_login, message.chat.id)

    elif message.text == 'Реєстрація':
        bot.send_message(message.chat.id, 'Придумай login:',reply_markup=keyboard)
        bot.set_state(message.from_user.id, UserStates.reg_login, message.chat.id)

@bot.message_handler(state = UserStates.enter_login)
def enter_login(message):
    """Перевірка існування login та запит password"""
    
    if message.text == 'Назад':
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        registration_button = types.KeyboardButton('Реєстрація')
        login_button = types.KeyboardButton('Вхід')
        keyboard.add(registration_button, login_button)

        bot.send_message(message.chat.id, 'Обери: Вхід або Реєстрація', reply_markup=keyboard)
        bot.set_state(message.from_user.id, UserStates.сheck_for_registration_or_login, message.chat.id)

    elif list_fri.login_exist(message.text):
        bot.set_state(message.from_user.id, UserStates.enter_password, message.chat.id)
        bot.add_data(message.from_user.id, message.chat.id, password = list_fri.return_password_for_login(message.text))
        bot.send_message(message.chat.id, 'Введи пароль:')

    else:
        bot.send_message(message.chat.id, 'Такого логіну не існує, спробуй ще раз!')

@bot.message_handler(state = UserStates.enter_password)
def password_get(message):

    if message.text == 'Назад':
        bot.send_message(message.chat.id, 'Введіть логін:')
        bot.set_state(message.from_user.id, UserStates.enter_login, message.chat.id)
       

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if data['password'] == message.text:
            bot.send_message(message.chat.id, 'Вхід успішний')
            del data['password']
        else: 
            bot.send_message(message.chat.id, 'Пароль неправильний, спробуй ще раз!')

@bot.message_handler(state = UserStates.reg_login)
def reg_login(message):
    if message.text == 'Назад':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        registration_button = types.KeyboardButton('Реєстрація')
        login_button = types.KeyboardButton('Вхід')
        keyboard.add(registration_button, login_button)

        bot.send_message(message.chat.id, 'Обери: Вхід або Реєстрація', reply_markup=keyboard)
        bot.set_state(message.from_user.id, UserStates.сheck_for_registration_or_login, message.chat.id)
    else:
        bot.add_data(message.from_user.id, message.chat.id, reg_login = message.text)
        bot.set_state(message.from_user.id, UserStates.reg_password, message.chat.id)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_button = types.KeyboardButton('Назад')
        keyboard.add(back_button)

        bot.send_message(message.chat.id, f'Я записав {message.text} як твій логін. Тепер придумай пароль:', reply_markup=keyboard)
    
@bot.message_handler(state = UserStates.reg_password)
def reg_password(message):
    if message.text == 'Назад':
        bot.send_message(message.chat.id, 'Ти придумав ішний логін? Добренкько, напиши мені новий:')
        bot.set_state(message.from_user.id, UserStates.reg_login, message.chat.id)
    else:
        bot.add_data(message.from_user.id, message.chat.id, reg_password = message.text)
        bot.set_state(message.from_user.id, UserStates.reg_telegram_username, message.chat.id)
        bot.send_message(message.chat.id, f'Я записав {message.text} як твій пароль. Тепер напиши мені свій юзернейм в Telegram(@username):')

@bot.message_handler(state = UserStates.reg_telegram_username)
def reg_telegram_username(message):
    if message.text == 'Назад':
        bot.set_state(message.from_user.id, UserStates.reg_password, message.chat.id)
        bot.send_message(message.chat.id, 'Все ж таки вирішив, що пароль 1234 це не дуже надійно?) Ну тоді напиши, який новий пароль ти придумав:')

    else:
        bot.add_data(message.from_user.id, message.chat.id, reg_telegram_username = message.text)
        bot.set_state(message.from_user.id, UserStates.confirm_registration, message.chat.id)
        bot.send_message(message.chat.id, f'Я записав {message.text} як твій телеграм.')

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        yes_button = types.KeyboardButton('Так, підверджую')
        no_button = types.KeyboardButton('Ні, я передумав. Хочу ще подумати.')
        keyboard.add(yes_button, no_button)
        bot.send_message(message.chat.id, f'Я запам\'ятав твою базову інфломацію. залишилось тільки підтвердити реєстрацію, натиснувши на кнопку нижче.',reply_markup=keyboard)



@bot.message_handler(state = UserStates.confirm_registration)
def confirm_registration(message):    
    if message.text == 'Так, підверджую':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as member:
           utils.register_new_member(member, message.chat.id)

        bot.reset_data(message.from_user.id, message.chat.id)
        list_fri.update_all_lists()

        for chat_id in utils.return_admins_chat_ids(list_fri.return_members()):
            bot.send_message(chat_id, 'У вас нова заявка на реєстрацію')

        bot.send_message(message.chat.id, 'Реєсрація успішна, тепер ти можеш увійти.')
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        registration_button = types.KeyboardButton('Реєстрація')
        login_button = types.KeyboardButton('Вхід')
        keyboard.add(registration_button, login_button)

        bot.send_message(message.chat.id, 'Обери: Вхід або Реєстрація', reply_markup=keyboard)
        bot.set_state(message.from_user.id, UserStates.сheck_for_registration_or_login, message.chat.id)

    elif message.text == 'Ні, я передумав. Хочу ще подумати.':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        registration_button = types.KeyboardButton('Реєстрація')
        login_button = types.KeyboardButton('Вхід')
        keyboard.add(registration_button, login_button)

        bot.send_message(message.chat.id, 'Обери: Вхід або Реєстрація', reply_markup=keyboard)
        bot.set_state(message.from_user.id, UserStates.сheck_for_registration_or_login, message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Невідома команда')
      

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling()


