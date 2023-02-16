from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

b1 = InlineKeyboardButton( text='Информация', callback_data='/info')
b2 = InlineKeyboardButton( text=  'Добавить объявление', callback_data='/add')
b3 = InlineKeyboardButton( text=  'Удалить объявление', callback_data='/delete')
b4 = InlineKeyboardButton( text=  'Смотреть объявления', callback_data='/watch_products')
b5 = InlineKeyboardButton( text=  'Мои объявления', callback_data='/my_products')

kb_client_inline = InlineKeyboardMarkup(row_width=2)

kb_client_inline.add(b1).row(b2, b5).row(b3, b4)