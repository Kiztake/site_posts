import sqlite3

user = [
    ('pepper', 5377468, 'Inna',' Alekseeva', 1),
    ('coconat', 2734927, 'Matvey', 'Petrov', 23),
    ('country', 35636356, 'Angelina', 'Antonova', 78),
    ('Mat', 35636536, 'Zahar', 'Ivanov', 100),
]


# Подключаем базу данных
db = sqlite3.connect('dbase.db')

# создаём объект для запроса
cursor = db.cursor()


# Создаём таблицу с полями если такой нет в базе данных
cursor.execute(''' create table if not exists users (
    login TEXT,
    password TEXT,
    name TEXT,
    lastname TEXT,
    age INTEGER
)''')

cursor.executemany(""" insert into users (login, password, name, lastname, age) values (?,?,?,?,?)""", user)

db.commit()
#SQLite Viewer


# Получить одну строку из базы данных
cursor.execute('select * from users')
result = cursor.fetchone()
# print(result)

# Запросить все строки из базы данных
cursor.execute('select * from users')
result1 = cursor.fetchall()
# print(result1)

# Запросить конкретное количество строк из базы данных
cursor.execute('select * from users')
result2 = cursor.fetchmany(3)
# print(result2)


# Запрос с условием НЕБЕЗОПАСНЫЙ
cursor.execute('select * from users where name="Inna"')
result3 = cursor.fetchone()
# print(result3)

name = 'Inna'
cursor.execute('select * from users where name=(?)', [name])
result3 = cursor.fetchone()
# print(result3)
db.commit()


# Добавлять данные 
# user = ('admin', 242646, 'Ad', 'Min', 1)
# cursor.execute("insert into users (login, password, name, lastname, age) values (?,?,?,?,?)", user)
# db.commit()

# Удалять данные
# name = 'admin'
# cursor.execute('delete from users where name=(?)', [name])
# db.commit()

# Проверка вхождения
login = input('Введите логин \n')
password = input('Введите пароль \n')
cursor.execute('select * from users where login=(?) and password=(?)', [login, password])
def reg():
    if input('Хотите зарегестрироваться? \n') == 'Да':
        name = input('Введите имя \n')
        lastname = input('Введите фамилию \n')
        age = int(input('Введите возраст \n'))
        user = (login, password, name, lastname, age)
        cursor.execute("insert into users (login, password, name, lastname, age) values (?,?,?,?,?)", user)
        db.commit() 
        print('Пользователь зарегестрирован')

if cursor.fetchone() is None:
    print('Пользователь не зарегестрирован')
    reg()

else:
    print('Пользователь зарегестрирован')