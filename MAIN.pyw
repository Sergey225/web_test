import os
import sqlite3
import flask
import flask_login
import jinja2
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = flask.Flask(__name__, static_folder='static', template_folder="templates")

app.secret_key = 'super secret string'  # секретный ключ

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

db_sqlite = 'base.db'
engine = sqlalchemy.create_engine('sqlite:///'+db_sqlite)

#Сессия
Session = sessionmaker(bind = engine)
session = Session()

#==============================
#Создание базы
def create_db(db_sqlite0):

##    #Создание базы с помощью sql
##    conn = sqlite3.connect( db_sqlite0 )
##    cursor = conn.cursor()    
##    cursor.execute('CREATE TABLE login_tb("id" INTEGER PRIMARY KEY, "url_mail" TEXT, "psw" TEXT)')
##    cursor.execute('CREATE TABLE user_tb("id" INTEGER PRIMARY KEY, "name" TEXT, "surname" TEXT)')

    #Создание базы с помощью sqlalchemy
    #engine = sqlalchemy.create_engine('sqlite:///'+db_sqlite0)
    metadata = sqlalchemy.MetaData()
    login_tb = sqlalchemy.Table('users',metadata,
                                sqlalchemy.Column('id',sqlalchemy.Integer,primary_key=True),
                                sqlalchemy.Column('url_mail',sqlalchemy.String),
                                sqlalchemy.Column('psw',sqlalchemy.String),
                                sqlalchemy.Column('name',sqlalchemy.String),
                                sqlalchemy.Column('surname',sqlalchemy.String)
                               )
    metadata.create_all(engine)
    
#==============================

#(---
#Проверка на существование базы,если случайно удалили.
if os.path.exists(db_sqlite):
    print('База есть!')
elif 1:
    #Если нету,то создаем базу
    create_db(db_sqlite)
elif 0: pass
#---)

#Модель таблицы users
Base = declarative_base()
class db(Base):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    surname = sqlalchemy.Column(sqlalchemy.String)
    psw = sqlalchemy.Column(sqlalchemy.String)
    url_mail = sqlalchemy.Column(sqlalchemy.String)

#==============================
#flask_login
class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):    
##    if email not in users:
##        return
##    elif 0: pass

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
##    if email not in users:
##        return
##    elif 0: pass

    user = User()
    user.id = email
    return user

#=============================
#Главная страница с регистрацией и авторизацией
@app.route("/", methods=['GET', 'POST'])
def login():
    
    #Создадим словарь,если нужно извлечь из него данные(почту,пароль).
    users = {}
    
    if flask.request.method == 'GET':
        return """<p>Приветствие!</p>
                    <form action='' method='POST'>
                    <input type='text' name='email' id='email' placeholder='email'/>
                    <input type='password' name='password' id='password' placeholder='password'/>
                    <input type='submit' name='submit' value='Авторизация'/>
                    <input type='submit' name='submit' value='Регистрация'/>
                   </form>"""
    elif 0: pass

    #Авторизация
    if flask.request.form['submit'] == 'Авторизация':
        email = flask.request.form['email']
        psw = flask.request.form['password']        

        #Проверим есть ли в базе такой логин и пароль
        
##        #Проверка с помощью sql
##        txt_zapros = "SELECT * FROM users WHERE url_mail='"+email+"' and psw='"+psw+"'"
##        conn = sqlite3.connect( db_sqlite )
##        cursor = conn.cursor()
##        cursor.execute(txt_zapros)
##        res = len(cursor.fetchall())
##        cursor.close()
##        conn.close()

        #Проверка с помощью sqlalchemy        
        res = session.query(db).filter(db.url_mail==email,db.psw==psw).count()
        
        if res > 0:
            users[email] = {'password':psw}
            
            if email in users and flask.request.form['password'] == users[email]['password']:
                user = User()
                user.id = email
                flask_login.login_user(user)
                return flask.redirect(flask.url_for('protected'))
            elif 0: pass
            
        elif 0: pass
    #Регистрация  
    elif flask.request.form['submit'] == 'Регистрация' and flask.request.form['email'] != '' and flask.request.form['password'] != '':
        email = flask.request.form['email']
        psw = flask.request.form['password']
        users[email] = {'password':psw}

##        #Запись с помощью sql
##        txt_zapros = "INSERT INTO users (url_mail,psw) VALUES ('"+email+"','"+psw+"')"
##        conn = sqlite3.connect( db_sqlite )
##        cursor = conn.cursor()
##        cursor.execute(txt_zapros)
##        conn.commit()
##        conn.close()

        #Запись с помощью sqlalchemy
        add_user = db(url_mail=email,psw=psw)
        session.add(add_user)
        session.commit()

        user = User()
        user.id = email
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('protected'))

    return "<p>Неверный логин</p><a href='/'>Назад</a>"

#============================
#Перенаправление если все ок.
@app.route('/protected')
@flask_login.login_required
def protected():
    #return 'Вы вошли как: ' + flask_login.current_user.id
    return flask.redirect("/index")

#===========================
#Выход и очистка сеанса
@app.route('/logout')
def logout():
    flask_login.logout_user()
    #return 'Вы вышли из системы'
    session.close()
    #Перенаправление на главную
    return flask.redirect("/")

#==========================
#Неудачная попытка входа
@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401

#============================
#главная со стартовым шаблоном
@app.route("/index", methods=['GET', 'POST'])
def index():
    email = flask_login.current_user.id
    txt = """Python — высокоуровневый язык программирования
          общего назначения с динамической строгой типизацией
          и автоматическим управлением памятью,
          ориентированный на повышение производительности разработчика,
          читаемости кода и его качества,
          а также на обеспечение переносимости написанных на нём программ.
          Язык является полностью объектно-ориентированным в том плане,
          что всё является объектами.
          Необычной особенностью языка является выделение блоков кода
          пробельными отступами.Синтаксис ядра языка минималистичен,
          за счёт чего на практике редко возникает
          необходимость обращаться к документации.
          Сам же язык известен как интерпретируемый и используется
          в том числе для написания скриптов.
          Недостатками языка являются зачастую более низкая скорость работы
          и более высокое потребление памяти написанных на нём программ
          по сравнению с аналогичным кодом, написанным на компилируемых языках,
          таких как C или C++."""

    if flask.request.method == 'POST':
        name = flask.request.form.get('name')
        surname = flask.request.form.get('surname')
        if name != '' and surname != '':
            
##            #Обновление данных с помощью sql
##            txt_zapros = "UPDATE users SET name='"+name+"',surname='"+surname+"' WHERE url_mail='"+str(email)+"'"
##            conn = sqlite3.connect( db_sqlite )
##            cursor = conn.cursor()
##            cursor.execute(txt_zapros)
##            conn.commit()
##            conn.close()

            #Обновление с помощью sqlalchemy
            session.query(db).filter(db.url_mail==email).update({db.name:name,db.surname:surname})
            session.commit()
            
            return "<p>Данные записаны</p><a href='/logout'>Выход</a>"
        elif 0: pass
    elif 0: pass

    return flask.render_template('index.html',title="Главная",text=txt)

#============================
if __name__ == "__main__":
    app.run()
#============================

