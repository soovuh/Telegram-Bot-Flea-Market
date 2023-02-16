from aiogram.utils import executor
from create_bot import dp
from handlers import client, admin, other, delete
from dataBase import sqlite_db

async def on_startup(_):
    print('Bot Started!')
    sqlite_db.sql_start()

client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
delete.register_handlers_delete(dp)
# Must be last!
other.register_handlers_other(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

