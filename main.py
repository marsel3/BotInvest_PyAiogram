import sqlite3

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def all_type_id():     # Список всех типов
    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute('SELECT type_id FROM type')
    results = cursor.fetchall()
    conn.close()

    return [str(i[0]) for i in results]


def all_country_id():     # Список всех типов по странам
    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute('SELECT country_id FROM country')
    results = cursor.fetchall()
    conn.close()

    return [str(i[0]) for i in results]


def all_paper_id():     # Список всех ценных бумаг
    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute('SELECT paper_id FROM papers')
    results = cursor.fetchall()
    conn.close()

    return [str(i[0]) for i in results]



bot = Bot(token="1672438859:AAFjoueNYWY2ZwUM1UqNIBC_USPJ2N4hE48")
dp = Dispatcher(bot)

all_type_id = all_type_id()
all_country_id = all_country_id()
all_paper_id = all_paper_id()
number = 1
tov_id = ''



@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btns = [KeyboardButton('Рынок ценных бумаг'),
            KeyboardButton('Просмотр портфель'),
            KeyboardButton('Информация о нашем брокере'),
            KeyboardButton('💬 Помощь')]
    markup.add(*btns)

    await message.answer(str(message.from_user.first_name) + ', добро пожаловать!')
    await message.answer('Наш БОТ предоставляет возможность операций по ценным бумагам.', reply_markup=markup)


@dp.message_handler()
async def echo_message(message: types.Message):

    if message.text.lower() == "рынок ценных бумаг":
        await bot.send_message(message.from_user.id, 'Выерите вид ценной бумаги:\n', reply_markup=type_id())

    if message.text.lower() == "просмотр портфель":
        text, markup = portfel(message.from_user.id)
        await bot.send_message(message.chat.id, text, reply_markup=markup)

    if message.text.lower() == "информация о нашем брокере":
        await bot.send_message(message.from_user.id, 'Наш Брокер ХаероФФ удерживает 1% cо всех операций!')


    if message.text[0:5] == 'fill_':
        code = message.text[5:]
        text = add_balance(message.chat.id, code)[1]
        await bot.delete_message(message.chat.id, message.message_id)
        if text == "ERROR":
            await bot.send_message(message.chat.id, f'а-а-а! Нельзя снимать больше, чем сумма на балансе!')
        else:
            if int(code) > 0:
                await bot.send_message(message.chat.id, f'Баланс пополнен на {int(code) * 0.99} рублей!\n{text}')
            else:
                await bot.send_message(message.chat.id, f'С баланса списано {int(code) * 0.99} рублей!\n{text}')


    if message.text == "💬 Помощь" or message.text.lower() == "помощь":
        await bot.send_message(message.chat.id, 'При возникновении проблем при работе данного telegram-бота '
                                          'обращаться по контактным данным:\nTelegram: @demagina'
                                          '\nПочта: demagina@gmail.com \nТелефон: 2-31-54')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('edit_'))
async def process_callback_kb1btn1(call: types.CallbackQuery):
    global number, tov_id
    create_user_bd(call.message.from_user.id)

    code = call.data[5:]

    tov_id = code
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.message.chat.id

    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT paper_count, paper_name, price FROM "{user_id}" WHERE paper_id="{code}"')
    results = cursor.fetchall()
    conn.close()

    number = int(results[0][0])

    markup = types.InlineKeyboardMarkup()
    btns = [InlineKeyboardButton(text=f'➖', callback_data=f'minus'),
            InlineKeyboardButton(text=f'{number}', callback_data=f'call_number'),
            InlineKeyboardButton(text=f'➕', callback_data=f'plus')]

    markup.add(*btns)
    markup.add(InlineKeyboardButton(text=f'✔', callback_data=f'confirm'))


    await bot.delete_message(chat_id, message_id)
    await bot.send_message(chat_id, f"{results[0][1]} {results[0][2]} руб. за 1шт", reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data)
# async def answer(call: types.CallbackQuery, message: types.Message):
async def answer(call: types.CallbackQuery):
    global all_type_id, number, tov_id

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.message.chat.id

    if call.data == 'back_to_type':
        await bot.delete_message(chat_id, message_id)
        await bot.send_message(chat_id, 'Выерите вид ценной бумаги:\n', reply_markup=type_id())

    if call.data == 'minus':    # Уменьшить число на 1
        if number > 0:
            number -= 1
            call.message.reply_markup.inline_keyboard[0][1].text = number
            await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=call.message.reply_markup)

    if call.data == 'plus':     # Увеличить число на 1
        number += 1
        call.message.reply_markup.inline_keyboard[0][1].text = number
        await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=call.message.reply_markup)


    if call.data in all_type_id:
        await bot.delete_message(chat_id, message_id)
        await bot.send_message(chat_id, 'Выберите вид ценной бумаги',  reply_markup=name_in_country(call.data))


    if call.data in all_country_id:
        await bot.delete_message(chat_id, message_id)
        await bot.send_message(chat_id, 'Выберите тип ценной бумаги', reply_markup=name_paper(call.data))

    if call.data in all_paper_id:
        tov_id = call.data
        string, markup = paper_card(call.data)
        await bot.delete_message(chat_id, message_id)
        await bot.send_message(chat_id, string, reply_markup=markup)

    if call.data == 'add_to_basket':
        string = add_to_basket(user_id, tov_id, number)
        number = 1
        await bot.delete_message(chat_id, message_id)
        await bot.send_message(chat_id, string)

    if call.data == 'add_balance':
        await bot.delete_message(chat_id, message_id)
        await bot.send_message(chat_id, 'Введите сумму пополнения в формате: \nfill_{cумма_пополнения}'
                                        '\nЕсли перед суммой добавить "-", то сумма спишется'
                                        '\nДля пополнения на 100 рублей: fill_100')

    if call.data == 'confirm':      # Подтварждение действий
        string = edit_confirm(user_id, number, tov_id)
        text, markup = portfel(user_id)
        number = 1
        await bot.send_message(chat_id, f'{text}\n{string}', reply_markup=markup)


def type_id():     # Выводит кнопки из таблицы type текст=название
    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM type')
    results = cursor.fetchall()
    conn.close()

    markup = types.InlineKeyboardMarkup(row_width=1)
    btns = [InlineKeyboardButton(text=f'{i[1]}', callback_data=f'{i[0]}') for i in results]
    markup.add(*btns)

    return markup


def name_in_country(type):  # Выводит ценные бумаги в кнопки по виду
    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT country_id, country_name FROM country WHERE type_id="{type}"')
    results = cursor.fetchall()
    conn.close()

    markup = types.InlineKeyboardMarkup(row_width=1)
    btns = [InlineKeyboardButton(text=f'{i[1]}', callback_data=f'{i[0]}') for i in results]
    markup.add(*btns, InlineKeyboardButton(text=f'Назад', callback_data=f'back_to_type'))
    return markup


def name_paper(paper):  # Выводит названия ценных бумаг в кнопки по типу
    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT paper_name, paper_id FROM papers WHERE country_id="{paper}"')
    results = cursor.fetchall()
    conn.close()

    markup = types.InlineKeyboardMarkup(row_width=1)
    btns = [InlineKeyboardButton(text=f'{i[0]}', callback_data=f'{i[1]}') for i in results]
    markup.add(*btns, InlineKeyboardButton(text=f'Назад', callback_data=f'back_to_type'))
    return markup


def paper_card(paper):
    global number

    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM papers WHERE paper_id="{paper}"')
    results = cursor.fetchall()[0]

    conn.close()
    string = f'{results[3]}\n\nОписание: {results[6]}\nРиск: {results[7]}\n\nЦена: {results[5]} руб. = {results[4]} $'

    markup = types.InlineKeyboardMarkup()
    btns = [InlineKeyboardButton(text=f'➖', callback_data=f'minus'),
            InlineKeyboardButton(text=f'{number}', callback_data=f'call_number'),
            InlineKeyboardButton(text=f'➕', callback_data=f'plus')]
    markup.add(*btns)

    markup.add(InlineKeyboardButton(text=f'Купить', callback_data=f'add_to_basket'))
    markup.add(InlineKeyboardButton(text=f'Назад', callback_data=f'back_to_type'))

    return string, markup


def create_user_bd(user):   # Cоздаёт БД с id юзера, для корзины
    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()
    cursor.execute(f'CREATE TABLE IF NOT EXISTS "{user}" (paper_id text, paper_name text, price text, paper_count text)')
    cursor.execute(f'CREATE TABLE IF NOT EXISTS users_info (user_id text, user_balance text)')
    conn.commit()
    conn.close()


def add_balance(user, money):
    create_user_bd(user)

    string = f'Комиссия брокера {abs(float(money) / 100)} руб.'
    if int(money) > 0:
        money = float(money) * 0.99
    else:
        money = float(money) + float(money) / 100

    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT user_id, user_balance FROM users_info WHERE user_id="{user}"')
    result = cursor.fetchall()
    try:
        if float(result[0][1]) + float(money) < 0:
            return 0, 'ERROR'
    except:
        pass

    if len(result) == 0:
        balance = float(money)
    else:
        balance = float(result[0][1]) + float(money)
        cursor.execute(f'DELETE FROM users_info WHERE user_id="{user}"')
    cursor.execute(f'INSERT INTO users_info VALUES ("{user}", "{str(balance)}")')
    conn.commit()
    conn.close()

    return balance, string



def add_to_basket(user, paper_id, count):  # Добавление, перезапись в БД юзера товары
    create_user_bd(user)

    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT paper_id, paper_name, paper_price_rub FROM papers WHERE paper_id="{paper_id}"')
    results = cursor.fetchall()[0]
    conn.close()

    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT paper_count, price FROM "{user}" WHERE paper_id="{paper_id}"')
    results_2 = cursor.fetchall()
    price = results[2]

    tek = 0
    if len(results_2) > 0:
        tek = int(results_2[0][0])
        if add_balance(user, 0)[0] >= (float(price) * (int(count) - int(results_2[0][0]))):
            cursor.execute(f'DELETE FROM "{user}" where paper_id="{paper_id}"')
            conn.commit()

        count_start = count
        count = str(int(count_start) + int(results_2[0][0]))
        price = str((float(results_2[0][1]) * int(results_2[0][0]) + float(results[2]) * int(count_start)) / int(count))


    if add_balance(user, 0)[0] >= (float(price) * (int(count) - tek)):
        cursor.execute(f'INSERT INTO "{user}" VALUES ("{results[0]}", "{results[1]}", "{price}", {count})')
        conn.commit()
        text = add_balance(user, int(-float(price) * (int(count) - tek)))[1]
        string = 'Бумага добавлена в ваш портфель!' + '\n' + text
    else:
        string = 'Операция не прошла, недостаточно средств!'
    conn.commit()
    conn.close()

    return string


def portfel(user):
    create_user_bd(user)
    add_balance(user, 0)

    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT user_id, user_balance FROM users_info WHERE user_id="{user}"')
    results_1 = cursor.fetchall()[0]

    cursor.execute(f'SELECT * FROM "{user}"')
    results = cursor.fetchall()

    markup = types.InlineKeyboardMarkup(resize_button=True)
    for i in results:
        btns = [InlineKeyboardButton(text=f'{i[1]}', callback_data=f'{i[0]}'),
                InlineKeyboardButton(text=f'{i[3]} шт.', callback_data=f'edit_{i[0]}'),
                InlineKeyboardButton(text=f'✏', callback_data=f'edit_{i[0]}')]
        markup.add(*btns)
    markup.add(InlineKeyboardButton(text=f'Пополнить баланс', callback_data=f'add_balance'))

    summ = 0
    count = 1
    string = ''
    if len(results) > 0:
        for i in results:
            string += f"\n{count}.  {i[1]} \n{i[2]} * {i[3]}  =  {float(i[2]) * int(i[3])} рублей"
            summ += (float(i[2]) * int(i[3]))
            count += 1
        string += '\n______________________________' + '_' * len(str(summ))

    text = f'СВОБОДНЫЙ БАЛАНС: {round(float(results_1[1]), 2)} руб.\n\nБАЛАНС АКТИВАМИ: {summ} руб.' + string

    return text, markup


def del_cat_basket(user, tov_id):   # Удаляет строку товаров по id
    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM "{user}" WHERE paper_id="{tov_id}"')
    conn.commit()
    conn.close()


def edit_confirm(user, number, tov_id):  # Сохраняет увеличение или уменьшение количества товаров
    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT paper_count, price FROM "{user}" WHERE paper_id="{tov_id}"')
    count, price = cursor.fetchall()[0]
    conn.close()
    count, number = int(count), int(number)

    text = add_balance(user, float(price) * (count - number))[1]

    if number == 0:
        del_cat_basket(user, tov_id)
    else:
        conn = sqlite3.connect('db/users.db')
        cursor = conn.cursor()
        cursor.execute(f'UPDATE "{user}" SET paper_count="{number}" WHERE paper_id="{tov_id}"')
        conn.commit()
        conn.close()

    return text

if __name__ == '__main__':
    executor.start_polling(dp)