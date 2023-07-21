PRODUCTS = [
    {'id': '0', 'name': 'xiaomi mi 10', 'price': 400},
    {'id': '1', 'name': 'samsung s20', 'price': 800},
    {'id': '2', 'name': 'iphone 13', 'price': 1300}
]

bot = TeleBot(API_TOKEN)
products_factory = CallbackData('product_id', prefix='products')


def products_keyboard():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text=product['name'],
                    callback_data=products_factory.new(product_id=product["id"])
                )
            ]
            for product in PRODUCTS
        ]
    )


def back_keyboard():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text='⬅',
                    callback_data='back'
                )
            ]
        ]
    )


class ProjectCallbackFilter(AdvancedCustomFilter):
    key = 'config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


@bot.message_handler(commands=['products'])
def products_command_handler(message: types.Message):
    bot.send_message(message.chat.id, 'Products:', reply_markup=products_keyboard())


# Only product with field - product_id = 2
@bot.callback_query_handler(func=None, config=products_factory.filter(product_id='2'))
def product_one_callback(call: types.CallbackQuery):
    bot.answer_callback_query(callback_query_id=call.id, text='Not available :(', show_alert=True)


# Any other products
@bot.callback_query_handler(func=None, config=products_factory.filter())
def products_callback(call: types.CallbackQuery):
    callback_data: dict = products_factory.parse(callback_data=call.data)
    product_id = int(callback_data['product_id'])
    product = PRODUCTS[product_id]

    text = f"Product name: {product['name']}\n" \
           f"Product price: {product['price']}"
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=text, reply_markup=back_keyboard())


@bot.callback_query_handler(func=lambda c: c.data == 'back')
def back_callback(call: types.CallbackQuery):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Products:', reply_markup=products_keyboard())


bot.add_custom_filter(ProjectCallbackFilter())
#=========================================================================================================================================
def projects_keyboard(projects4page, current_page = 0):
    PROJECTS = list_fri.return_projects()

    buttons_per_page = projects4page  # Кількість кнопок на сторінці
    total_buttons = len(PROJECTS)
    total_pages = (total_buttons + buttons_per_page - 1) // buttons_per_page  # Кількість сторінок з кнопками

      # Початкова сторінка

    while current_page < total_pages:
        start_index = current_page * buttons_per_page
        end_index = min(start_index + buttons_per_page, total_buttons)

        page_buttons = [
            types.InlineKeyboardButton(
                text=PROJECTS[i][1],
                callback_data=projects_factory.new(project_id=PROJECTS[i][0])
            )
            for i in range(start_index, end_index)
        ]

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*page_buttons)

        if current_page > 0:
            keyboard.row(
                types.InlineKeyboardButton(
                    text='Попередня',
                    callback_data=f"prev_{current_page - 1}"
                )
            )

        if current_page < total_pages - 1:
            keyboard.row(
                types.InlineKeyboardButton(
                    text='Наступна',
                    callback_data=f"next_{current_page + 1}"
                )
            )

        yield keyboard

        current_page += 1


@bot.callback_query_handler(func=lambda call: call.data.startswith(('prev_', 'next_')))
def handle_pagination_callback(call: types.CallbackQuery):
    callback_data = call.data.split('_')
    action = callback_data[0]
    current_page = int(callback_data[1])

    if action == 'prev':
        prev_page = max(current_page - 1, 0)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=next(projects_keyboard(projects4page=3, current_page=prev_page)))

    elif action == 'next':
        next_page = min(current_page + 1, total_pages - 1)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=next(projects_keyboard(projects4page=3, current_page=next_page)))
