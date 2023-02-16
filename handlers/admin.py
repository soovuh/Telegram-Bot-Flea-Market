from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup 
from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher
from create_bot import bot
from dataBase import sqlite_db
from inline_buttons import kb_client_inline, kb_add_inline


class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()

#Начало диалога загрузки    
async def cm_start(callback : types.CallbackQuery):
    check = await sqlite_db.ban_check(callback.from_user.id)
    if check == True:
        await FSMAdmin.photo.set()
        await bot.send_message(callback.from_user.id, 'Загрузи фото', reply_markup=kb_add_inline)
        await callback.answer('Внимание, при размещение объвлений, учитывайте, что в данном боте запрещены продажа запрещенных веществ, оружие, и т.д.', show_alert=True )
    else:
        await bot.send_message(callback.from_user.id, 'Выход..', reply_markup=kb_client_inline)
        await callback.answer('К сожалению, вы были забанены за многочисленные жалобы.\nДобваление публикаций недоступно.', show_alert=True)

#В случае отмены
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await bot.send_message(callback.from_user.id,'Откат', reply_markup=kb_client_inline)
    await callback.answer('Если вы загрузили часть данных, они не сохранились', show_alert=True)

#Ловим первый ответ и пишем в словарь
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await FSMAdmin.next()
    await bot.send_message(message.from_user.id,'Теперь введи название', reply_markup=kb_add_inline)

#Ловим второй ответ
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMAdmin.next()
    await bot.send_message(message.from_user.id,'Введи описание', reply_markup=kb_add_inline)

#Ловим трертий
async def load_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await FSMAdmin.next()
    return await bot.send_message(message.from_user.id,'Теперь назначь цену (в грн.)', reply_markup=kb_add_inline)

#Ловим последний ответ
async def load_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not message.text.isdigit():
            await bot.send_message(message.from_user.id, 'Введите число', reply_markup=kb_add_inline)
        data['price'] = float(message.text)
        data['user_id'] = message.from_user.id

    await sqlite_db.sql_add_command(state, message.from_user.id, message.from_user.username)
    await bot.send_message(message.from_user.id,'Готово', reply_markup=kb_client_inline)
    await state.finish()

# registration admin handlers
def register_handlers_admin(dp : Dispatcher):
    dp.register_callback_query_handler(cm_start, text='/add', state=None)
    dp.register_callback_query_handler(cancel_handler, state = "*", text = '/rollback')
    dp.register_message_handler(load_photo, content_types = ['photo'], state = FSMAdmin.photo)
    dp.register_message_handler(load_name, state = FSMAdmin.name)
    dp.register_message_handler(load_description, state = FSMAdmin.description)
    dp.register_message_handler(load_price, state = FSMAdmin.price)


