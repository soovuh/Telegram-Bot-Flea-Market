from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup 
from aiogram import types, Dispatcher
from create_bot import bot
from dataBase import sqlite_db
from inline_buttons import kb_client_inline, kb_cancel_inline
from handlers import client


class FSMDelete(StatesGroup):
    name = State()

async def delete_start(callback : types.CallbackQuery):
    mes = await sqlite_db.sql_read_my_products(callback.from_user.id, callback)
    if mes == None:
        await FSMDelete.name.set()
        await bot.send_message(callback.from_user.id, 
                            'Какой из продуктов вы хотите удалить?\nВведите название продукта',
                            reply_markup=kb_cancel_inline)
        await callback.answer('Удаление объявления')
    else:
        
        await callback.answer(mes,show_alert=True)

async def cancel_handler_delete(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await bot.send_message(callback.from_user.id, 'Выход', reply_markup=kb_client_inline)
        return
    await state.finish()
    await bot.send_message(callback.from_user.id,'Откат', reply_markup=kb_client_inline)
    await callback.answer('Откат')

async def delete_product(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    status = await sqlite_db.delete_from_sql(data['name'], message.from_user.id)
    await bot.send_message(message.from_user.id, status, reply_markup=kb_client_inline)
    await state.finish()

# registration
def register_handlers_delete(dp : Dispatcher):
    dp.register_callback_query_handler(delete_start, text = '/delete', state = None)
    dp.register_callback_query_handler(cancel_handler_delete, state='*', text = '/cancel')
    dp.register_message_handler(delete_product, state = FSMDelete.name)
    