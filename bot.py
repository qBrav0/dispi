import telebot
import utils
from Config import token
from utils import UserStates

from telebot import types
from telebot import custom_filters
from telebot.storage import StateMemoryStorage
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(token, state_storage=state_storage)
list_fri = utils.Lists()

projects_factory = CallbackData('project_id', prefix='projects')

def projects_keyboard(projects4page, current_page=0):
    PROJECTS = list_fri.return_projects()

    total_buttons = len(PROJECTS)
    total_pages = (total_buttons + projects4page - 1) // projects4page  # Кількість сторінок з кнопками

    page_buttons = [
        [
            types.InlineKeyboardButton(
                text=PROJECTS[i][1],
                callback_data=projects_factory.new(project_id=PROJECTS[i][0])
            )
            for i in range(start_index, min(start_index + projects4page, total_buttons))
        ]
        for start_index in range(0, total_buttons, projects4page)
    ]

    pagination_buttons = []
    if current_page > 0:
        pagination_buttons.append(
            types.InlineKeyboardButton(
                text="Попередня",
                callback_data=f"prev_{current_page - 1}"
            )
        )
    if current_page < total_pages - 1:
        pagination_buttons.append(
            types.InlineKeyboardButton(
                text="Наступна",
                callback_data=f"next_{current_page + 1}"
            )
        )

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*page_buttons[0])
    keyboard.row(*pagination_buttons)

    return keyboard


def back_keyboard():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text='Назад',
                    callback_data='back'
                )
            ]
        ]
    )

class ProjectCallbackFilter(AdvancedCustomFilter):
    key = 'config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


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
        bot.add_data(message.from_user.id, message.chat.id, active_login = message.text, password = list_fri.return_password_for_login(message.text))
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
            bot.set_state(message.from_user.id, UserStates.main_menu, message.chat.id)

            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)   
            
            if message.chat.id in list_fri.return_admins_chat_ids():
                view_new_members_button = types.KeyboardButton('Нові заявки')
                keyboard.add(view_new_members_button)
            back_button = types.KeyboardButton('Назад')
            add_new_project_button = types.KeyboardButton('Додати новий проєкт')
            view_projects = types.KeyboardButton('Перегляд проєктів')
            keyboard.add(add_new_project_button, view_projects, back_button)
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

        if list_fri.uniqueness_of_the_login(message.text):
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
        bot.send_message(message.chat.id, f'Я запам\'ятав твою базову інфломацію. залишилось тільки підтвердити реєстрацію, натиснувши на кнопку нижче.',reply_markup=keyboard)



@bot.message_handler(state = UserStates.confirm_registration)
def confirm_registration(message):    
    if message.text == 'Так, підверджую':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as member:
           utils.register_new_member(member, message.chat.id)

        bot.reset_data(message.from_user.id, message.chat.id)
        list_fri.update_all_lists()

        for chat_id in list_fri.return_admins_chat_ids():
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
    if message.text == 'Назад':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        registration_button = types.KeyboardButton('Реєстрація')
        login_button = types.KeyboardButton('Вхід')
        keyboard.add(registration_button, login_button)

        bot.send_message(message.chat.id, 'Обери: Вхід або Реєстрація', reply_markup=keyboard)
        bot.set_state(message.from_user.id, UserStates.сheck_for_registration_or_login, message.chat.id)

    elif message.text == 'Нові заявки':
        bot.send_message(message.chat.id, 'Ти обрав нові заявки, далі нічого не буде')
    elif message.text == 'Додати новий проєкт':
        bot.send_message(message.chat.id, 'Напишіть назву нового проєкту')
        bot.set_state(message.from_user.id, UserStates.reg_new_project, message.chat.id)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton('Назад'))

    elif message.text == 'Перегляд проєктів':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back_button = types.KeyboardButton('Назад')
        all_project_button = types.KeyboardButton('Всі проєкти')
        need_stuff_button = types.KeyboardButton('Набирають команду')
        working_projects_button = types.KeyboardButton('В роботі')
        ended_projects_button = types.KeyboardButton('Завершені')
        keyboard.add(all_project_button,need_stuff_button,working_projects_button,ended_projects_button, back_button)
        bot.send_message(message.chat.id, 'Які проєкти хочеш подивитись?', reply_markup=keyboard)
        bot.set_state(message.from_user.id, UserStates.check_projects, message.chat.id)

        
@bot.message_handler(state = UserStates.reg_new_project)
def reg_new_project(message):
    if message.text == 'Назад':
        if message.chat.id in list_fri.return_admins_chat_ids():
            view_new_members_button = types.KeyboardButton('Нові заявки')
            keyboard.add(view_new_members_button)
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back_button = types.KeyboardButton('Назад')
        add_new_project_button = types.KeyboardButton('Додати новий проєкт')
        view_projects = types.KeyboardButton('Перегляд проєктів')
        keyboard.add(add_new_project_button, view_projects, back_button)
        bot.send_message(message.chat.id, 'Обери, що хочеш', reply_markup=keyboard)
        bot.set_state(message.from_user.id, UserStates.main_menu, message.chat.id)

    else:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            project = {'project_name': message.text, 'curator_id': list_fri.return_user_id_by_login(data['active_login'])}
        utils.add_new_project(project)
        list_fri.update_all_lists()

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        if message.chat.id in list_fri.return_admins_chat_ids():
            view_new_members_button = types.KeyboardButton('Нові заявки')
            keyboard.add(view_new_members_button)
        back_button = types.KeyboardButton('Назад')
        add_new_project_button = types.KeyboardButton('Додати новий проєкт')
        view_projects = types.KeyboardButton('Перегляд проєктів')
        keyboard.add(add_new_project_button, view_projects, back_button)
        bot.set_state(message.from_user.id, UserStates.main_menu, message.chat.id)
        bot.send_message(message.chat.id, 'Проєкт успішно зареєстрований', reply_markup=keyboard)
       
@bot.message_handler(state = UserStates.project_filter)
def project_filter(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    back_button = types.KeyboardButton('Назад')
    all_project_button = types.KeyboardButton('Всі проєкти')
    need_stuff_button = types.KeyboardButton('Набирають команду')
    working_projects_button = types.KeyboardButton('В роботі')
    ended_projects_button = types.KeyboardButton('Завершені')
    keyboard.add(all_project_button,need_stuff_button,working_projects_button,ended_projects_button, back_button)
    bot.send_message(message.chat.id, 'Які проєкти хочеш подивитись?', reply_markup=keyboard)
    bot.set_state(message.from_user.id, UserStates.check_projects, message.chat.id)

@bot.message_handler(state = UserStates.check_projects)
def check_projects(message):
    if message.text == 'Назад':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        if message.chat.id in list_fri.return_admins_chat_ids():
            view_new_members_button = types.KeyboardButton('Нові заявки')
            keyboard.add(view_new_members_button)
        back_button = types.KeyboardButton('Назад')
        add_new_project_button = types.KeyboardButton('Додати новий проєкт')
        view_projects = types.KeyboardButton('Перегляд проєктів')
        keyboard.add(add_new_project_button, view_projects, back_button)
        bot.send_message(message.chat.id, 'Обери, що хочеш', reply_markup=keyboard)
        bot.set_state(message.from_user.id, UserStates.main_menu, message.chat.id)
    elif message.text == 'Всі проєкти':
        bot.send_message(message.chat.id, 'Оберіть проєкт:', reply_markup=projects_keyboard(3))

#Для обробки кнопок з проєктами
@bot.callback_query_handler(func=None, config=projects_factory.filter())
def projects_callback(call: types.CallbackQuery):
    PROJECTS = list_fri.return_projects()
    callback_data: dict = projects_factory.parse(callback_data=call.data)
    project_id = int(callback_data['project_id'])
    project = PROJECTS[project_id - 1]

    text = f"Project name: {project[1]}\n" \
           f"Curator id: {project[2]}"
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=text, reply_markup=back_keyboard())
        
#Для обробки кнопки назад(до списку проєктів)   
@bot.callback_query_handler(func=lambda c: c.data == 'back')
def back_callback(call: types.CallbackQuery):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Оберіть проєкт:', reply_markup=projects_keyboard(3))

@bot.callback_query_handler(func=lambda call: call.data.startswith(('prev_', 'next_')))
def handle_pagination_callback(call: types.CallbackQuery):
    callback_data = call.data.split('_')
    action = callback_data[0]
    current_page = int(callback_data[1])
    
    
    if action == 'prev':
        prev_page = max(current_page - 1, 0)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=projects_keyboard(projects4page=projects4page, current_page=prev_page))

    elif action == 'next':
        next_page = min(current_page + 1, total_pages - 1)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=projects_keyboard(projects4page=projects4page, current_page=next_page))


bot.add_custom_filter(ProjectCallbackFilter())
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling()


