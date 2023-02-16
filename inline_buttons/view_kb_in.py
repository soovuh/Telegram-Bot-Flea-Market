from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

b1 = InlineKeyboardButton(text='Следующий', callback_data='/next')
b2 = InlineKeyboardButton(text = 'Выход', callback_data='/exit')
b3 = InlineKeyboardButton(text = 'Жалоба', callback_data='/report')

kb_view_inline = InlineKeyboardMarkup(row_width=2)

kb_view_inline.add(b1).row(b2, b3)