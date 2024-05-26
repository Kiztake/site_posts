from flask import render_template, url_for, request, session, redirect, Flask
import sqlite3, datetime, os

from flask_mail import Mail, Message
from random import randint



app = Flask(__name__)
app.config['SECRET_KEY'] = 'aergblkawjrglr1436klkj3647jlk24b2j53b6k27'
# Настройка почтового клиента
app.config['MAIL_SERVER'] = 'smtp.mail.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'ave34hy@mail.ru'
app.config['MAIL_DEFAULT_SENDER'] = 'ave34hy@mail.ru'
app.config['MAIL_PASSWORD'] = 'CTQhunMKt2qUSfjT7972'
mail= Mail(app)


def opendb():
    global db, cursor
    db = sqlite3.connect('file.db')
    cursor = db.cursor()

def closedb():
    cursor.close()
    db.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'isLogged' not in session:
        return redirect('/logout')
    else:
        return redirect('/home')
    
@app.route('/home', methods=['GET', 'POST'])
def home():
    opendb()
    cursor.execute('select * from posts')
    posts = cursor.fetchall()

    return render_template('home.html', posts = posts)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        # вернуть результат запроса к базу
        opendb()
        cursor.execute('select * from users where login=(?) and password=(?)', [login, password])
        response = cursor.fetchone()
        closedb()
        if response is not None:
            session['isLogged'] = response[0]
            return redirect('/profile')
        else:
            return render_template('logout.html', error='Такой пользователь не зарегистрирован!')
    return render_template('logout.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        login = request.form.get('login')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        username = request.form.get('username')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        if login != '' and password1 != '' and password2 != '' and email != '':
            if password1 == password2:
                opendb()
                # ! тут формируем запрос
                cursor.execute("select * from users where login=(?) and email=(?)", [login, email])
                if cursor.fetchone() is None:
                    conf_password = randint(100000, 999999)
                    session['user'] = {
                        'login': login,
                        'password': password1,
                        'username': username,
                        'lastname': lastname,
                        'email': email,
                        'conf_pass': conf_password
                    }
                    msg = Message('Текстовое сообщение', recipients=[email])
                    msg.body = f'Код подтверждения : {conf_password}'
                    try:
                        mail.send(msg)
                        return redirect('confirm_email')
                    except:
                        return 'Woops! Something went wrong'
    return render_template('reg.html')

@app.route('/confirm_email', methods=['GET','POST'])
def confirm_email():
    if request.method == 'POST':
        confirm_password = str(request.form.get('confirm_password'))
        if confirm_password == str(session['user']['conf_pass']):
            opendb()
            cursor.execute("insert into users (login, password, username, lastname, email) values(?,?,?,?,?)", [session['user']['login'], session['user']['password'], session['user']['username'], session['user']['lastname'], session['user']['email']])
            db.commit()
            print('Пользователь успешно зарегистрирован')
            cursor.execute('select * from users where login=(?) and password=(?)', [session['user']['login'], session['user']['password']])
            response = cursor.fetchone()
            closedb()
            session['isLogged'] = response[0]
            del session['user']
            return redirect('/home')
        else:
            return render_template('confirm_email.html', error='Пароль неверный')
    return render_template('confirm_email.html')

@app.route('/profile', methods=['GET','POST'])
def profile():
    if 'isLogged' not in session:
        return redirect('/logout')
    else:
        if request.method == 'POST':
            posts=None
            title = request.form.get('title')
            body = request.form.get('body')
            if title != '' and body != '':
                date = datetime.datetime.now()
                opendb()
                cursor.execute('insert into posts (user_id, post_title, post, date) values(?, ?, ?, ?)', [session['isLogged'], title, body, date])
                db.commit()
                closedb()
            return redirect('profile')

    opendb()
    cursor.execute('select * from posts where user_id = (?)', [session['isLogged']])
    posts = cursor.fetchall()
    cursor.execute('select * from user_profile_img where img_id = (?)', [session['isLogged']])
    us_p_img = cursor.fetchall()
    avatar = None
    try:
        avatar = us_p_img[-1][1]
    except:
        pass
    return render_template('profile.html', posts=posts, user_profile_img = avatar)

@app.route('/show_post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    if request.method == 'POST':
        comment = request.form.get('comment')
        if comment != '':
            opendb()
            cursor.execute('select * from users where id=(?)', [session['isLogged']])
            author = cursor.fetchone()
            cursor.execute('insert into comments (post_id, text, date, author) values(?, ?, ?, ?)', [post_id, comment, datetime.datetime.now().replace(microsecond=0), author[3]])
            db.commit()
            closedb()
        return redirect(f'/show_post/{post_id}')
    opendb()
    cursor.execute('select * from posts where id=(?)', [post_id])
    post = cursor.fetchone()
    cursor.execute('select * from comments where post_id=(?)', [post_id])
    comments = cursor.fetchall()

    cursor.execute('select * from users where id=(?)', [post[1]])
    author=cursor.fetchone()[3]
    closedb()

    return render_template('show_post.html', post=post, comments=comments, author=author, id=session['isLogged'])

# @app.route('/postpost/<int:num>/')
# def postpost(num):
#     return f'Post number {num}'
# квери параменры

@app.route('/del_post/<int:post_id>', methods=['GET', 'POST'])
def del_post(post_id):
    opendb()
    cursor.execute('select * from posts where id = (?)', [post_id])
    post = cursor.fetchone()

    if post != None:
        if post[1] == session['isLogged']:
            cursor.execute('delete from posts where id=(?)', [post_id])
            cursor.execute("""delete from comments where post_id=(?)""", [post_id])
            db.commit()
            closedb()
            return redirect('/profile')
    return redirect('/home')

@app.route('/sendmail', methods=['GET', 'POST'])
def send_mail():
    if request.method == 'POST':
        adress = request.form.get('recipient')
        message = request.form.get('message')

        send = Message(message, recipients=[adress])
        send.body = message
        try:
            mail.send(send)
            return render_template('test_mail.html', msg='успешно отправлено')
        except Exception:
            print(Exception)
            return render_template('test_mail.html', msg='Что-то пошло не так')
    return render_template('test_mail.html')
    # msg = Message('тестовое сообщение', recipients=['29oxuuw5j8jj@mail.ru'])
    # msg.body = f'Код поддтверждения {randint(100000, 9999999)}'
    # try:
    #     mail.send(msg)
    #     return 'Message is sent'
    # except:
    #     return 'Woops! Something went wrong'

@app.route('/set_avatar', methods=['GET', 'POST'])
def set_avatar():
    if request.method == 'POST':
        if 'avatar_img' in request.files:
            image = request.files['avatar_img']
            if image.filename != '':
                image.save(os.path.join('static/user_images', image.filename))
                opendb()
                cursor.execute('insert into user_profile_img (image_name, img_id) values(?, ?)', [image.filename, session['isLogged']])
                db.commit()
                closedb() 
                return redirect('/profile')
            return 'Файл не был добавлен'

if __name__ == '__main__':
    app.run(debug=True)