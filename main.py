import psycopg2

def create_db(database, user, password, host='localhost', port='5432'):
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clients(
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(40) NOT NULL,
                    last_name VARCHAR(40) NOT NULL,
                    email VARCHAR(80) NOT NULL UNIQUE
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS client_phones(
                    id SERIAL PRIMARY KEY,
                    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
                    phone VARCHAR(20) NOT NULL
                );
            """)
            conn.commit()

def add_client(database, user, password, name, last_name, email, phones=None):
    conn = psycopg2.connect(database=database, user=user, password=password)
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO clients (name, last_name, email)
                VALUES (%s, %s, %s)
                RETURNING id;
            """, (name, last_name, email))
            client_id = cur.fetchone()[0]

            if phones:
                for phone in phones:
                    cur.execute("""
                        INSERT INTO client_phones (client_id, phone)
                        VALUES (%s, %s);
                    """, (client_id, phone))
            conn.commit()
    return client_id

def add_phone(database, user, password, email, new_phone):
    conn = psycopg2.connect(database=database, user=user, password=password)
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM clients WHERE email = %s;
            """, (email, ))
            result = cur.fetchone()

            if result:
                client_id = result[0]
                cur.execute("""
                    INSERT INTO client_phones(client_id, phone)
                    VALUES (%s, %s);
                """, (client_id, new_phone))
                conn.commit()
                print(f'Телефон {new_phone} добавлен для клиента с email: {email}')
            else:
                print(f'Клиент с email: {email} не найден.')

def update_info(database, user, password, email, first_name=None, last_name=None, new_email=None, phones=None):
    conn = psycopg2.connect(database=database, user=user, password=password)
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM clients WHERE email = %s;
            """, (email,))
            result = cur.fetchone()
            if result:
                client_id = result[0]
                if first_name:
                    cur.execute("""
                        UPDATE clients SET name = %s WHERE id = %s;
                    """, (first_name, client_id))
                if last_name:
                    cur.execute("""
                        UPDATE clients SET last_name = %s WHERE id = %s;
                    """, (last_name, client_id))
                if new_email:
                    cur.execute("""
                        UPDATE clients SET email = %s WHERE id = %s;
                    """, (new_email, client_id))
                if phones:
                    for phone in phones:
                        cur.execute("""
                            INSERT INTO client_phones (client_id, phone)
                            VALUES (%s, %s);
                        """, (client_id, phone))
                conn.commit()

                print(f'Данные клиента с email {email} успешно изменены.')
            else:
                print(f'Клиент с email {email} не найден.')

def delete_phone(database, user, password, email, del_phone):
    conn = psycopg2.connect(database=database, user=user, password=password)
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM clients WHERE email = %s;
            """, (email,))
            result = cur.fetchone()
            if result:
                client_id = result[0]
                cur.execute("""
                    DELETE FROM client_phones WHERE phone = %s AND client_id = %s;
                """, (del_phone, client_id))
                conn.commit()
                print(f'Телефон {del_phone} клиента с email {email} успешно удален')
            else:
                print(f'Клиент с email {email} не найден')

def delete_user(database, user, password, email):
    conn = psycopg2.connect(database=database, user=user, password=password)
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM clients WHERE email = %s;
            """, (email,))
            result = cur.fetchone()

            if result:
                client_id = result[0]
                cur.execute("""
                    DELETE FROM clients WHERE id = %s;
                """, (client_id, ))
                conn.commit()
                print(f'Клиент с email {email} успешно удален')
            else:
                print(f'Клиент с email {email} не найден')

def find_client(database, user, password, name=None, last_name=None, email=None, phone=None):
    conn = psycopg2.connect(database=database, user=user, password=password)
    with conn:
        with conn.cursor() as cur:
            base_query = """
                SELECT clients.id, clients.name, clients.last_name, clients.email, client_phones.phone
                FROM clients
                LEFT JOIN client_phones ON clients.id = client_phones.client_id
                WHERE 1=1
            """
            conditions = []
            params = []

            if name:
                conditions.append("clients.name = %s")
                params.append(name)
            if last_name:
                conditions.append("clients.last_name = %s")
                params.append(last_name)
            if email:
                conditions.append("clients.email = %s")
                params.append(email)
            if phone:
                conditions.append("client_phones.phone = %s")
                params.append(phone)

            if conditions:
                base_query += " AND " + " AND ".join(conditions)

            cur.execute(base_query, tuple(params))
            results = cur.fetchall()

            if results:
                for row in results:
                    print(f"ID: {row[0]}, Имя: {row[1]}, Фамилия: {row[2]}, Email: {row[3]}, Телефон: {row[4]}")
            else:
                print("Клиенты, соответствующие заданным параметрам, не найдены.")



database = 'netology_hw3'
user = 'postgres'
password = ''

create_db(database, user, password)

client_id1 = add_client(database, user, password, 'John', 'Doe', 'john.doe@example.com', ['1234567890'])
client_id2 = add_client(database, user, password, 'Jane', 'Smith', 'jane.smith@example.com', ['0987654321'])

add_phone(database, user, password, 'john.doe@example.com', '5555555555')

update_info(database, user, password, 'john.doe@example.com', first_name='Jonathan', last_name='Doe', new_email='jon.doe@example.com', phones=['1111111111'])

delete_phone(database, user, password, 'jon.doe@example.com', '5555555555')

delete_user(database, user, password, 'jon.doe@example.com')

find_client(database, user, password, name='Jane')
find_client(database, user, password, phone='0987654321')

