import psycopg2


def del_db(cursor, db_name):
    """Функция удаляет базу данных"""
    cursor.execute(f"""DROP DATABASE {db_name};""")
    conn.commit()
    print(f'База данных {db_name} удалена!')


def del_table(cursor, table_name):
    """Функуия удаляет таблицу из базы данных"""
    cursor.execute(f"""DROP TABLE {table_name};""")
    conn.commit()
    print(f'Таблица {table_name} удалена!')


def create_client_db(cursor):
    """Функция создает базу данных клиентов"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client(
            id serial PRIMARY KEY, 
            name VARCHAR(40) NOT NULL, 
            surname VARCHAR(40) NOT NULL, 
            email VARCHAR(60) UNIQUE, 
            phones VARCHAR(100) UNIQUE);
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phone_number(
            id serial PRIMARY KEY, 
            number BIGINT UNIQUE NOT NULL, 
            client_id INTEGER NOT NULL REFERENCES client(id));
        ''')
    conn.commit()
    print('База данных создана!')


def add_client(cursor, name, surname, email=None, phones=None):
    """Функция добавляет в базу данных нового клиента"""
    insert = ''
    if email is not None:
        insert += f", email"
    if phones is not None:
        insert += f", phones"
    values = ''
    if email is not None:
        values += f", '{email}'"
    if phones is not None:
        values += f", '{phones}'"
    cursor.execute(f'''
        INSERT INTO client(name, surname{insert})
        VALUES('{name}', '{surname}'{values})
        RETURNING id, name, surname, email, phones;
        ''')
    conn.commit()
    print(f'Клиент добавлен в базу данных: {cursor.fetchall()}')


def add_ph_number(cursor, number, client_id):
    """Функция добавляет в базу данных номер телефона клиента"""
    cursor.execute(f'''SELECT id FROM client WHERE id = {client_id};''')
    if cursor.fetchone() is None:
        print(f'Клиента с id = {client_id} нет в базе данных!')
    else:
        cursor.execute(f'''
                INSERT INTO phone_number(number, client_id)
                VALUES({number}, {client_id})
                RETURNING id, number, client_id;
                ''')
        conn.commit()
        print(f'Номер телефона для клинта с id = {client_id} добавлен: {cursor.fetchall()}')


def change_client(cursor, client_id, name=None, surname=None, email=None, phones=None):
    """Функция изменяет данные клиента в базе данных"""
    cursor.execute(f'''SELECT id FROM client WHERE id = {client_id};''')
    if cursor.fetchone() is None:
        print(f'Клиента с id = {client_id} нет в базе данных!')
    else:
        ch_string = f'''UPDATE client SET'''
        if name is not None:
            ch_string += f" name = '{name}',"
        if surname is not None:
            ch_string += f" surname = '{surname}',"
        if email is not None:
            ch_string += f" email = '{email}',"
        if phones is not None:
            ch_string += f" phones = '{phones}',"
        cursor.execute(ch_string[:-1] + f' WHERE id = {client_id};')
        conn.commit()
        print(f'Данные пользователя с id = {client_id} изменены')


def del_ph_number(cursor, client_id, number):
    """Функция удаляет номер телефона клиента из базы данных."""
    cursor.execute(f'''SELECT id FROM client WHERE id = {client_id};''')
    if cursor.fetchone() is None:
        print(f'Клиента с id = {client_id} нет в базе данных!')
    else:
        cursor.execute(f'''SELECT id FROM phone_number WHERE client_id = {client_id};''')
        if cursor.fetchone() is None:
            print(f'Номера {number} у клиента с id = {client_id} нет в базе данных!')
        else:
            cursor.execute(f'''DELETE FROM phone_number WHERE client_id = {client_id};''')
            conn.commit()
            print(f'Номер телефона: {number} клиента с id = {client_id} удален из базы данных!')


def del_client(cursor, client_id):
    """Функция удаляет клиента из базы данных."""
    cursor.execute(f'''SELECT id FROM client WHERE id = {client_id};''')
    if cursor.fetchone() is None:
        print(f'Клиента с id = {client_id} нет в базе данных!')
    else:
        cursor.execute(f'''DELETE FROM phone_number WHERE client_id = {client_id}''')
        cursor.execute(f'''DELETE FROM client WHERE id = {client_id}''')
        conn.commit()
        print(f'Клиент с id = {client_id} удалён из базы данных!')


def client_info(cursor, name=None, surname=None, email=None, phone=None):
    """Функция находит клиента по его данным."""
    ch_string = f'''SELECT c.id, c.name, c.surname, c.email, p.number FROM client c 
    JOIN phone_number p ON c.id = p.client_id WHERE'''
    if name is not None:
        ch_string += f" c.name = '{name}' AND"
    if surname is not None:
        ch_string += f" c.surname = '{surname}' AND"
    if email is not None:
        ch_string += f" c.email = '{email}' AND"
    if phone is not None:
        ch_string += f" p.number = '{phone}' AND"
    cursor.execute(ch_string[:-4] + ';')
    if cursor.fetchone() is None:
        print('Клиент не найден!')
    else:
        cursor.execute(ch_string[:-4] + ';')
        print(f'Найден клиент: {cursor.fetchall()}')


if __name__ == '__main__':
    conn = psycopg2.connect(database='clients_db', user='postgres', password='...')
    with conn.cursor() as cur:
        # del_table(cur, 'phone_number')
        # del_table(cur, 'client')
        create_client_db(cur)
        add_client(cur, 'Ivan', 'Nikto', 'pochta@po', '98989898, 2123123123')
        add_client(cur, 'Petr', 'Petrov')
        add_client(cur, 'Ivan', 'Ivanov', phones='565656')
        add_ph_number(cur, 2123123123, 1)
        add_ph_number(cur, 565656, 3)
        change_client(cur, 3, surname='Petruccho', phones='1212')
        del_ph_number(cur, 1, 2123123123)
        del_client(cur, client_id=2)
        client_info(cur, phone=565656)
        client_info(cur, name='Ivan', surname='Ivanov')
    conn.close()
