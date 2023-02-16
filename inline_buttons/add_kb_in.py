from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


b1 = InlineKeyboardButton(text='Отмена', callback_data='/rollback')


kb_add_inline = InlineKeyboardMarkup(row_width=1)

kb_add_inline.add(b1)