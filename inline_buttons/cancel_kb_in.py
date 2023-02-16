from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


b1 = InlineKeyboardButton(text='Отмена', callback_data='/cancel')


kb_cancel_inline = InlineKeyboardMarkup(row_width=1)

kb_cancel_inline.add(b1)