import sqlite3 as sq
from create_bot import bot
from inline_buttons import kb_view_inline, kb_client_inline

def sql_start():
    global base, cur
    base = sq.connect('sovbot_db.db')
    cur = base.cursor()
    if base:
        print('Data Base connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS\
                 views(user_id, product_id)')
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS\
                 users(id PRIMARY KEY UNIQUE, username TEXT, deleted_products, ban BOOLEAN)')
    base.commit()
    base.execute(
        '''CREATE TABLE IF NOT EXISTS products
        (product_id INTEGER PRIMARY KEY, img TEXT, 
        product_name, description TEXT, price TEXT, 
        user_id INT, report_count INT,
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE)''')
    base.commit()

async def ban_check(ID):
    check = cur.execute(f'''
                SELECT ban FROM users WHERE id = {ID}
                ''').fetchone()
    if check == None:
        return True
    if check[0] == 1:
        return  False
    else:
        return True

async def sql_add_command(state, ID, USERNAME):
    async with state.proxy() as data:
        check = cur.execute(f'SELECT username FROM users WHERE id = {ID}').fetchone()
        if check != None:
            cur.execute(
                f'INSERT INTO products(\
                img, product_name, description, \
                price, user_id, report_count) VALUES (?, ?, ?, ?, ?, 0)', 
                tuple(data.values()))
            base.commit()
        else:
            if USERNAME == None:
                link = f"https://t.me/user?id={ID}"
            else:
                link = f"https://t.me/{USERNAME}"
            cur.execute(
                'INSERT INTO users VALUES(?, ?, ?, ?)', 
                (ID, link, 0, False))
            base.commit()
            cur.execute('INSERT INTO products(img, product_name, description, price, user_id, report_count)\
                        VALUES (?, ?, ?, ?, ?, 0)', 
                        tuple(data.values()))
            base.commit()


async def sql_read_my_products(ID, message):
    if cur.execute(f'SELECT p.img, p.product_name, p.description, p.price, u.username\
                            FROM products p, users u \
                            WHERE p.user_id = {ID} AND u.id = p.user_id').fetchall() == []:
                            return 'У вас нет товаров!'
    else:
        for ret in cur.execute(f'SELECT p.img, p.product_name, p.description, p.price, u.username\
                                FROM products p, users u \
                                WHERE p.user_id = {ID} AND u.id = p.user_id').fetchall():
            await bot.send_photo(message.from_user.id, ret[0],
            f'{ret[1]}\nОписание: {ret[2]}\nЦена: {ret[3]}\nВладелец: {ret[4]}')


async def delete_from_sql(product_name, ID):
    view = cur.execute(f"SELECT * FROM products \
                        WHERE product_name = '{product_name}' \
                        AND user_id = {ID}").fetchall()
    if view == []:
        return 'Такого товара нет!'
    else:
        cur.execute(f"DELETE FROM products \
                    WHERE product_name = '{product_name}' AND user_id = {ID}")
        base.commit()
        return 'Удаление товара прошло успешно!'


async def sql_read_other_products(ID, message):
    from random import choice
    not_user_products = []
    view = cur.execute(f'SELECT product_id FROM products WHERE user_id != {ID} AND product_id NOT IN \
                        (SELECT product_id from views WHERE user_id = {ID})').fetchall()

    if view == []:
        cur.execute(f'DELETE FROM views WHERE user_id = {ID}')
        base.commit()
        view = cur.execute(f'SELECT product_id FROM products WHERE user_id != {ID} AND product_id NOT IN \
        (SELECT product_id from views WHERE user_id = {ID})').fetchall()

    for ret in view:
        not_user_products.append(ret[0])
    if not_user_products == []:

        return await bot.send_message(message.from_user.id, 'К сожалению, товаров на продажу нет(', reply_markup=kb_client_inline)
    random_choice = choice(not_user_products)
    cur.execute(f'INSERT INTO views(user_id, product_id) VALUES ({ID}, {random_choice})')
    base.commit()
    product = cur.execute(
        f'SELECT p.img, p.product_name, p.description, p.price, u.username , p.product_id\
        FROM products p, users u \
        WHERE product_id = {random_choice} AND u.id = p.user_id').fetchall()

    await bot.send_photo(message.from_user.id, product[0][0], 
    f'{product[0][1]}\nОписание: {product[0][2]}\nЦена: {product[0][3]}\nВладелец: {product[0][4]}', reply_markup=kb_view_inline)
    return (product[0][2], product[0][5])


async def delete_all_products(user_id, message):
    cur.execute(f'''
                DELETE FROM PRODUCTS
                WHERE user_id = {user_id}
                ''')
    base.commit()


async def check_bans(id, message):
    ready_to_ban = cur.execute(f'SELECT id FROM users WHERE deleted_products >= 3').fetchall()
    if ready_to_ban == []:
        return
    ready_to_ban = ready_to_ban[0][0]
    if ready_to_ban:
        cur.execute(f'UPDATE users SET ban = True WHERE id = {ready_to_ban}')
        base.commit()
        await delete_all_products(ready_to_ban, message)


async def check_report(id, message):
    if cur.execute(f'SELECT report_count FROM products WHERE report_count >= 5 AND product_id = {id}').fetchone():
        cur.execute(f'''
                    UPDATE users
                    SET deleted_products = deleted_products + 1
                    WHERE id = (SELECT user_id from products WHERE product_id = {id})
                    ''')
        base.commit()
        cur.execute(f"DELETE FROM products \
                    WHERE product_id = '{id}'")
        base.commit()
        await check_bans(id, message)


async def report(product_id_name, message):
    cur.execute(f'UPDATE products\
                SET report_count = report_count + 1\
                WHERE product_id = {product_id_name[1]}')
    base.commit()
    await check_report(product_id_name[1],  message)
    await sql_read_other_products(message.from_user.id, message)


