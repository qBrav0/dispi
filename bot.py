import telebot
import utils
from Config import token
from utils import UserStates

from telebot import types
from telebot import custom_filters
from telebot.storage import StateMemoryStorage

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(token, state_storage=state_storage)
list_fri = utils.Lists()
new_users_info = None
new_users = None


def next_or_back(message_id, chat_id, deleted = 0):
    """Відправляє виправлене повідомлення з слідуючою або попередньою новою заявкою"""

    keyboard = types.InlineKeyboardMarkup()
    if new_users_info != 0:
        back_button = types.InlineKeyboardButton(text='Попередня', callback_data='back')
    no_button = types.InlineKeyboardButton(text='Відхилити', callback_data='no')
    yes_button = types.InlineKeyboardButton(text='Підтвердити', callback_data='yes')
    if (len(new_users) - 1 > new_users_info and deleted == 0) or (len(new_users) - 2 > new_users_info and deleted == 1):
        next_button = types.InlineKeyboardButton(text='Наступна', callback_data='next')
    if new_users_info != 0 and len(new_users) - 1 > new_users_info:
        keyboard.add(back_button, next_button)
    elif new_users_info != 0:
        keyboard.add(back_button)
    elif (len(new_users) - 1 > new_users_info and deleted == 0) or (len(new_users) - 2 > new_users_info and deleted == 1):
        keyboard.add(next_button)
    keyboard.add(no_button, yes_button)
    if deleted == 1:
        if len(new_users) == 1:
            bot.edit_message_text(message_id = message_id, chat_id = chat_id, text = 'Немає більше нових заявок')
        elif len(new_users) - 1 == new_users_info:
            nu_info = new_users_info - 1
        else:
            nu_info = new_users_info + 1
    elif deleted == 0:
        nu_info = new_users_info
    if len(new_users) != 1:
        bot.edit_message_text(message_id = message_id, chat_id = chat_id, text =  new_users[nu_info][0] + ' ' + new_users[nu_info][1],
                        reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start(message):  
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
            bot.reset_data(message.from_user.id, message.chat.id)
            bot.set_state(message.from_user.id, UserStates.main_menu, message.chat.id)

            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)   
            if message.chat.id in utils.return_admins_chat_ids(list_fri.return_members()):
                view_new_members_button = types.KeyboardButton('Нові заявки')
                keyboard.add(view_new_members_button)

            test_buuton = types.KeyboardButton('Тестовий батон')
            keyboard.add(test_buuton)
            bot.send_message(message.chat.id, 'Обери, що хочеш', reply_markup=keyboard)
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

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_button = types.KeyboardButton('Назад')
        keyboard.add(back_button)

        if utils.uniqueness_of_the_login(message.text, list_fri.return_members()):
            bot.send_message(message.chat.id, f'Я записав {message.text} як твій логін. Тепер придумай пароль:',
                             reply_markup=keyboard)
            bot.set_state(message.from_user.id, UserStates.reg_password, message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Вже існує користувач з таким логіном, виберіть інший логін:',
                             reply_markup=keyboard)
    
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
        bot.send_message(message.chat.id, f'Я запам\'ятав твою базову інформацію. залишилось тільки підтвердити реєстрацію, натиснувши на кнопку нижче.',reply_markup=keyboard)



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
      
@bot.message_handler(state = UserStates.main_menu)
def main_menu(message):    
    if message.text == 'Нові заявки':
        bot.send_message(message.chat.id, 'Введи пароль від свого акаунту, щоб ми були впевнені що ти маєш право на перегляд заяв')    #просто щоб він ввів текст і
                                                                                                                           #перейти на повідомлення те що нам треба
        bot.set_state(message.from_user.id, UserStates.new_application, message.chat.id)
    elif message.text == 'Тестовий батон':
        bot.send_message(message.chat.id, 'Ти обрав тестовий батон, батона немає')


@bot.message_handler(state = UserStates.new_application)
def confirm_reg(message):
    global new_users_info
    global new_users

    list_fri.update_all_lists()
    new_users = utils.return_new_users_info(list_fri.return_members())

    if new_users == []:
        bot.send_message(message.chat.id, 'Немає нових заявок')
    else:
        keyboard = types.InlineKeyboardMarkup()
        no_button = types.InlineKeyboardButton(text='Відхилити', callback_data='no')
        yes_button = types.InlineKeyboardButton(text='Підтвердити', callback_data='yes')
        if len(new_users) > 1:
            next_button = types.InlineKeyboardButton(text='Наступна', callback_data='next')
            keyboard.add(next_button)
        keyboard.add(no_button, yes_button)
        bot.send_message(message.chat.id, new_users[0][0] + ' ' + new_users[0][1], reply_markup=keyboard)
        new_users_info = 0


@bot.callback_query_handler(func = lambda call: True)
def callback(call):
    global new_users_info
    global new_users

    if call.data == 'back':
        new_users_info = new_users_info - 1
        next_or_back(call.message.message_id, call.message.chat.id)
    elif call.data == 'no':
        utils.change_delete(new_users[new_users_info][1], 1)
        next_or_back(call.message.message_id, call.message.chat.id, 1)
        del new_users[new_users_info]
        if len(new_users) == new_users_info:
            new_users_info = new_users_info - 1
    elif call.data == 'yes':
        utils.change_delete(new_users[new_users_info][1], 0)
        next_or_back(call.message.message_id, call.message.chat.id, 1)
        del new_users[new_users_info]
        if len(new_users) == new_users_info:
            new_users_info = new_users_info - 1
    elif call.data == 'next':
        new_users_info = new_users_info + 1
        next_or_back(call.message.message_id, call.message.chat.id)

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling()