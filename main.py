import psycopg2

def create_db(conn):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS client(
                id_client SERIAL PRIMARY KEY,
                name VARCHAR(60),
                last_name VARCHAR(60),
                email VARCHAR(60)
                    );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS client_phone( 
            phone_id SERIAL PRIMARY KEY,
            phone VARCHAR(60) );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Client_client_phone(
            id_client INTEGER REFERENCES  client(id_client) ,
            phone_id INTEGER REFERENCES  client_phone(phone_id),
            CONSTRAINT pk PRIMARY KEY (id_client, phone_id)) ;
    """)
    return conn.commit
def add_client(conn, name:str, last_name:str, email:str, phone=None):
    cur.execute(f""" INSERT INTO client(name, last_name, email)
    VALUES ('{name}', '{last_name}', '{email}') ;
     """)
    conn.commit()
    if phone!= None:
        cur.execute(f"""INSERT INTO  client_phone (phone)
            VALUES ('{phone}');
             """)
        conn.commit()
        cur.execute(f"""INSERT INTO  Client_client_phone(id_client, phone_id )
        VALUES ((SELECT client.id_client FROM client  
        WHERE client.name= '{name}' AND client.last_name = '{last_name}'), 
        (SELECT client_phone.phone_id FROM client_phone 
        WHERE client_phone.phone= '{phone}')) RETURNING id_client;
         """)
        return cur.fetchone()
def add_phone(conn, client_id, phone):
    cur.execute(f"""INSERT INTO  client_phone (phone)
        VALUES ('{phone}');
         """)
    conn.commit()
    cur.execute(f"""INSERT INTO  Client_client_phone(id_client, phone_id )
    VALUES ('{client_id}', 
    (SELECT client_phone.phone_id FROM client_phone 
    WHERE client_phone.phone= '{phone}')) RETURNING id_client,'{phone}';
     """)

    return cur.fetchone()
def change_client(conn, client_id, name=None, last_name=None, email=None, phone=None, phone_st=None):

    if name != None:
        cur.execute(f""" UPDATE client SET name = '{name}' 
        WHERE id_client = '{client_id}'; """)
    if last_name != None:
        cur.execute(f""" UPDATE client SET last_name = '{last_name}' 
        WHERE id_client = '{client_id}';""")
    if email != None:
        cur.execute(f""" UPDATE client SET email = '{email}'
        WHERE id_client = '{client_id}';""")
    if phone != None:
        cur.execute(f""" UPDATE client_phone SET phone  = '{phone}'  
        WHERE phone_id  = (SELECT id_client FROM Client_client_phone 
        WHERE Client_client_phone.id_client= '{client_id}' and phone ='{phone_st}' and '{phone_st}'!= '{None}') 
        ;""")
    cur.execute(f""" SELECT * FROM client WHERE id_client = '{client_id}' ;
         """)
    print(cur.fetchall())
def delete_phone(conn, client_id, phone):
    cur.execute(f""" DELETE FROM Client_client_phone
        WHERE phone_id  = (SELECT phone_id FROM Client_client_phone 
            WHERE Client_client_phone.id_client= '{client_id}') AND 
            phone_id = (SELECT phone_id FROM client_phone 
            WHERE phone = '{phone}')
             """)
    conn.commit
    cur.execute(f""" DELETE FROM client_phone 
    WHERE phone  = '{phone}' """)
    cur.execute(f""" SELECT * FROM Client_client_phone WHERE id_client  = '{client_id}' ; """)
    return cur.fetchone()
def delete_client(conn, client_id):
    delete_phone(conn, client_id, phone = "*")
    cur.execute(f""" DELETE FROM client WHERE id_client  = '{client_id}' """)
    cur.execute(""" SELECT * FROM client; """)
    return cur.fetchone()

def find_client(conn, name=None, last_name=None, email=None, phone=None):
    cur.execute(f""" SELECT client.id_client, client.name, client.last_name, client.email, client_phone.phone FROM client
    JOIN Client_client_phone ON Client_client_phone.id_client =client.id_client
    JOIN client_phone ON client_phone.phone_id =Client_client_phone.phone_id
    GROUP BY client.id_client, client.name, client.last_name, client.email, client_phone.phone
    HAVING name =  '{name}' OR last_name = '{last_name}' OR email = '{email}' OR phone = '{phone}'
     """)
    print(cur.fetchone())

with psycopg2.connect(database="client_db", user="postgres", password = "Qwerty1!") as conn:
    with conn.cursor() as cur:
        # cur.execute(""" DROP TABLE Client_client_phone;
        # DROP TABLE client_phone;
        # DROP TABLE client;
        # """)
        print(create_db(conn))
        cur.execute(""" SELECT * FROM client_phone; """)
        print(cur.fetchall())
        cur.execute(""" SELECT * FROM client; """)
        print(cur.fetchall())
        print("Список команд")
        print('''1 - Функция, позволяющая добавить нового клиента
        2 - Функция, позволяющая добавить телефон для существующего клиента
        3 - Функция, позволяющая изменить данные о клиенте
        4 - Функция, позволяющая удалить телефон для существующего клиента
        5 - Функция, позволяющая удалить существующего клиента
        6 - Функция, позволяющая найти клиента по его данным (имени, фамилии, email-у или телефону)''')
        command = input('Введите команду: ')
        if command == '1':
            name = input("Введите имя: ")
            last_name = input("Введите фамилию: ")
            email = input("Введите email: ")
            phone = input("Введите номер телефона : ")
            if phone == "":
                phone = None
            print(add_client(conn, name, last_name, email, phone))
        elif command == '2':
            client_id = input("Введите id: ")
            phone = input("Введите номер телефона : ")
            print(add_phone(conn, client_id, phone))
        elif command == '3':
            client_id = input("Введите id: ")
            name = input("Введите имя: ")
            if name == "":
                name = None
            last_name = input("Введите фамилию: ")
            if last_name == "":
                last_name = None
            email = input("Введите email: ")
            if email == "":
                email = None
            phone_st = input("Введите номер телефона который нужно заменить : ")
            if phone_st == "":
                phone_st = None
            phone = input("Введите новый номер телефона : ")
            if phone == "":
                phone = None
            print(change_client(conn, client_id, name, last_name, email, phone, phone_st))
        elif command == '4':
            client_id = input("Введите id: ")
            phone = input("Введите номер телефона : ")
            print(delete_phone(conn, client_id, phone))
        elif command == '5':
            client_id = input("Введите id: ")
            print(delete_client(conn, client_id))
        elif command == '6':
            name = input("Введите имя: ")
            if name == "":
                name = None
            last_name = input("Введите фамилию: ")
            if last_name == "":
                last_name = None
            email = input("Введите email: ")
            if email == "":
                email = None
            phone = input("Введите номер телефона : ")
            if phone == "":
                phone = None
            print(find_client(conn, name, last_name, email, phone))
        else:
            print("Введена неверная команда")

conn.close()
