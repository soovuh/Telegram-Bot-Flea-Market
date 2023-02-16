from aiogram import types, Dispatcher
from create_bot import dp, bot
from inline_buttons import kb_client_inline
from dataBase import sqlite_db


async def start_commands(message : types.Message):
    try:
        await bot.send_message(message.from_user.id, 'Добро пожаловать!', reply_markup=kb_client_inline)
        await message.delete()
    except:
        await message.reply(
            'Общение с ботом через лс, напишите ему:\nhttps://t.me/soovuh_bot')

async def info_command(callback : types.CallbackQuery):
    await bot.send_message(callback.from_user.id,
'''Я бот, который создан в формате онлайн барахолки.
Для загрузки объявлений используй кнопку добавить объявление, для удаления - удалить объявление.
Категорий товаров нет, это же барахолка, поэтому для просмотра товаров просто жми на кнопку Смотреть объявления!
В случае, если объвление неприемлимое, просто отправь жалобу нажав на кнопку Жалоба.
Просьба относится с уважением к другим пользователям, и не размещать объвления с неприемлимым содержимым.
Я - всего лишь бот для комуникации, поэтому процесс покупки обсуждается на прямую с продавцом!
Администрация бота не несет ответственности за ваши деньги и товары!
Удачи ;)''', reply_markup=kb_client_inline)
    await callback.answer('Окей!')

async def see_my_products(callback: types.CallbackQuery):
    mes = await sqlite_db.sql_read_my_products(callback.from_user.id, callback)
    await bot.send_message(callback.from_user.id, 'Окей!', reply_markup=kb_client_inline)
    if mes == None:
        await callback.answer('Ваши объявления')
    else:
        await callback.answer(mes, show_alert=True)

async def see_other_products(callback: types.CallbackQuery):
    await callback.answer('Внимание! Мы не несем ответственности за представленные объявления!\
    Все объявления размещаются другими людьми, поэтому усиленно советуем оформлять доставку наложенным платежом!', show_alert=True)
    await next_product(callback)

async def next_product(callback: types.CallbackQuery):
    global product
    await callback.answer('Следующий товар')
    product = await sqlite_db.sql_read_other_products(callback.from_user.id, callback)

async def exit_from_seen_other_products(callback: types.CallbackQuery):
    await callback.answer('Выход из режима просмотра')
    await bot.send_message(callback.from_user.id, 'Выход..', reply_markup=kb_client_inline)

async def report_product(callback: types.CallbackQuery):
    await sqlite_db.report(product, callback)
    await callback.answer('Жалоба отправлена')

# registration client handlers
def register_handlers_client(dp : Dispatcher):  
    dp.register_message_handler(start_commands, commands=['start'])
    dp.register_callback_query_handler(info_command, text='/info')
    dp.register_callback_query_handler(see_my_products, text='/my_products')
    dp.register_callback_query_handler(next_product, text = '/next')
    dp.register_callback_query_handler(see_other_products, text='/watch_products')
    dp.register_callback_query_handler(exit_from_seen_other_products, text='/exit')
    dp.register_callback_query_handler(report_product, text='/report')