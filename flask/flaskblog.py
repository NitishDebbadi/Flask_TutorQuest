from flask import Flask, render_template, url_for, flash, redirect, request, session
from forms import RegistrationForm, LoginForm
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = "9100716055nit"
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'mysql'
app.config['MYSQL_DATABASE_DB'] = 'court'
mysql = MySQL()
mysql.init_app(app)

#home page before login
@app.route('/')
@app.route('/home')
def home():
    if 'login' in session:
        if session['login']:
            return redirect(url_for('index'))
    return render_template("home.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/register', methods=["GET", 'POST'])
def register():
    if 'login' in session:
        if session['login']:
            return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            conn = mysql.connect()
            cur = conn.cursor()
            em = form.email.data
            pas = generate_password_hash(form.password.data)
            un = form.username.data
            type = form.usertype.data
            if type == 2:
                cur.execute('INSERT INTO user(email,password,username) VALUES(%s,%s,%s)', (em, pas, un))
            else:
                cur.execute('INSERT INTO tutor(email,password,username) VALUES(%s,%s,%s)', (em, pas, un))
            conn.commit()
            conn.close()
            cur.close()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('home'))
    return render_template("register.html", title="register", form=form)


@app.route('/login', methods=["GET", 'POST'])
def login():
    if 'login' in session:
        if session['login']:
            return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            conn = mysql.connect()
            cur = conn.cursor()
            em = form.email.data
            type = form.usertype.data
            if type == 2:
                result = cur.execute('SELECT * FROM user WHERE email = %s', em)
            else:
                result = cur.execute('SELECT * FROM tutor WHERE email = %s', em)
            if result > 0:
                user = cur.fetchone()
                if check_password_hash(user[2], form.password.data):
                    session['login'] = True
                    session['firstName'] = user[3]
                    session['email'] = user[1]
                    session['id'] = user[0]
                    session['usertype'] = type
                    flash('Welcome ' + session['firstName'] + ' login successful!', 'success')
                else:
                    cur.close()
                    flash('password is incorrect', 'danger')
                    return render_template("login.html", title="login", form=form)
            else:
                cur.close()
                flash('User not found', 'danger')
                return render_template("login.html", title="login", form=form)

            cur.close()
            return redirect(url_for('index'))
    return render_template("login.html", title="login", form=form)


@app.route('/logout')
def logout():
    session['login'] = False
    session['firstName'] = None
    session['id'] = None
    session['usertype'] = None
    session['email'] = None
    return redirect(url_for('home'))


@app.route('/account', methods=["GET", 'POST'])
def account():
    if 'login' in session and 'usertype' in session:
        if session['login'] and session['usertype'] == 1:
            pass
        else:
            return redirect(url_for('home')),401
    n = None
    s = None
    e = None
    f = None
    st = None
    a = None
    ph = None
    tutorid=None
    image_file = url_for('static', filename='profile_pictures/default.jpg')
    conn = mysql.connect()
    cur = conn.cursor()
    if 'id' in session:
        tutorid = session['id']
        username = session['firstName']
    query = cur.execute(' select * from tutordetails where tutorid = %s ', tutorid)
    if query > 0:
        us = cur.fetchone()
        n = us[2]
        s = us[3]
        e = us[4]
        f = us[5]
        st = us[6]
        a = us[7]
        ph = us[8]

    if request.method == 'POST':
        noerror = True
        form = request.form

        name = form['name']
        subject = form['subject']
        experience = form['experience']
        fee = form['fee']
        statelist = form['statelist']
        area = form['area']
        phonenumber = form['phonenumber']
        if name == '' or subject == '' or experience == '' or statelist == '' or area == '' or phonenumber == '':
            noerror = False
            flash('* Fields cannot be empty', 'danger')
        if name not in username:
            noerror = False
            flash('Name did not match with username', 'danger')
        if phonenumber.isalpha() or len(phonenumber) != 10:
            noerror = False
            flash('Enter valid Phone Number', 'danger')

        if noerror:
            result = cur.execute("select * from tutordetails where tutorid=%s", tutorid)
            if result == 0:
                cur.execute(
                    'INSERT INTO tutordetails(tutorid,name,subject,experience,fee,state,area,phoneno) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
                    (tutorid, name, subject, experience, fee, statelist, area, phonenumber))

            else:
                cur.execute(
                    f'UPDATE tutordetails SET name="{name}",subject="{subject}",experience="{experience}",fee="{fee}",state="{statelist}",area="{area}",phoneno="{phonenumber}" WHERE tutorid="{tutorid}"')
            flash(f'Account edited successfully!', 'success')
        conn.commit()
        conn.close()
        cur.close()

    return render_template('account.html', title='Account', image_file=image_file, name=n, subject=s, experience=e,
                           fee=f, state=st, area=a, phonenumber=ph)

#student(user) details edit
@app.route('/useraccount', methods=["GET", 'POST'])
def useraccount():
    if 'login' in session and 'usertype' in session:
        if session['login'] and session['usertype'] == 2:
            pass
        else:
            return redirect(url_for('home'))
    n = None
    s = None
    st = None
    a = None
    ph = None
    image_file = url_for('static', filename='profile_pictures/default.jpg')
    if 'id' in session:
        id = session['id']
        username = session['firstName']
    conn = mysql.connect()
    cur = conn.cursor()
    query = cur.execute(' select * from userdetails where id = %s ', id)
    if query > 0:
        us = cur.fetchone()
        n = us[2]
        s = us[3]
        st = us[4]
        a = us[5]
        ph = us[6]
    if request.method == 'POST':
        noerror = True
        form = request.form
        name = form['name']
        std=form['std']
        statelist = form['statelist']
        area = form['area']
        phonenumber = form['phonenumber']
        if name == '' or std == '' or statelist == '' or area == '' or phonenumber == '':
            noerror = False
            flash('* Fields cannot be empty', 'danger')
        if name not in username:
            noerror = False
            flash('Name did not match with username', 'danger')
        if phonenumber.isalpha() or len(phonenumber) != 10:
            noerror = False
            flash('Enter valid Phone Number', 'danger')

        if noerror:
            result = cur.execute("select * from userdetails where id=%s", id)
            if result == 0:
                cur.execute(
                    'INSERT INTO userdetails(id,name,std,state,area,phoneno) VALUES(%s,%s,%s,%s,%s,%s)',
                    (id, name, std, statelist, area, phonenumber))

            else:
                cur.execute(
                    f'UPDATE userdetails SET name="{name}",std="{std}",state="{statelist}",area="{area}",phoneno="{phonenumber}" WHERE id="{id}"')
            flash(f'Account edited successfully!', 'success')
        conn.commit()
        conn.close()
        cur.close()
    return render_template('useraccount.html', title='User Account',name=n, image_file=image_file, std=s, state=st, area=a, phonenumber=ph)

#waste (just for testing)
@app.route('/userindex')
def userindex():
    return render_template('userindex.html', title='User')

#student or tutor homepage after login
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/searchtutors', methods=["GET", 'POST'])
def searchtutors():
    lst=''
    if request.method == 'POST':
        conn = mysql.connect()
        cur = conn.cursor()
        form = request.form
        subject = form['subject']
        experience = int(form['experience'])
        fee = int(form['fee'])
        state = form['statelist']
        results = cur.execute(
            'SELECT td.name,td.subject,td.experience,td.fee,td.state,td.area,td.phoneno,t.email,td.tutorid FROM tutor AS t,'
            'tutordetails AS td WHERE t.id=td.tutorid AND td.subject=%s AND td.experience>=%s AND td.fee<=%s AND '
            'td.state=%s',
            (subject, experience, fee, state))
        if results>=1:
            lst=cur.fetchall()
        else:
            flash("Sorry no tutor found for mentioned details", 'danger')
        conn.commit()
        conn.close()
        cur.close()
    return render_template('searchtutors.html',lst=lst)

@app.route('/tutor_select/<int:tutorid>', methods=["GET", 'POST'])
def tutor_select(tutorid):
    conn = mysql.connect()
    cur = conn.cursor()
    phoneno=''
    state=""
    std=''
    name=''
    result = cur.execute('SELECT phoneno,state,std,name FROM userdetails WHERE id = %s', session['id'])
    if result > 0:
        user = cur.fetchone()
        name=user[3]
        phoneno = user[0]
        state = user[1]
        std = user[2]
    check = cur.execute('SELECT * FROM studentrequests WHERE tutorid = %s AND studentid = %s',(tutorid,session['id']))
    if check > 0:
        flash(f'Request sent already', 'danger')
    else:
        res= cur.execute('INSERT INTO studentrequests(tutorid,studentid,name,std,email,state,phoneno) VALUES(%s,%s,%s,%s,%s,%s,%s)',(tutorid,session['id'],name,std,session['email'],state,phoneno))
        flash(f'Request sent successfully!', 'success')
    conn.commit()
    conn.close()
    cur.close()
    return render_template('index.html', title='User')


@app.route('/requests')
def requests():
    lst=[]
    conn = mysql.connect()
    cur = conn.cursor()
    res=cur.execute("SELECT name,std,state,phoneno,email FROM studentrequests WHERE tutorid = %s",session['id'])
    if res > 0:
        lst=cur.fetchall()
    return render_template('requests.html', title='Home',lst=lst)


if __name__ == "__main__":
    app.run(debug=True)
