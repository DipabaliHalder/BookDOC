from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re,datetime

app=Flask(__name__)

app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'doctor'

mysql = MySQL(app)

@app.route('/',methods=['GET','POST'])
def home():
    cursor=mysql.connection.cursor()
    cursor.execute('select count(*) from doctors')
    d=cursor.fetchone()[0]
    cursor.execute('select count(*) from user')
    u=cursor.fetchone()[0]
    cursor.execute('select count(*) from booking')
    b=cursor.fetchone()[0]
    cursor.execute('select count(distinct(patname)) from booking')
    p=cursor.fetchone()[0]
    return render_template('homepage.html',d=d,u=u,b=b,p=p)


@app.route('/login',methods=['GET','POST'])
def login():
    msg=''
    if request.method=='POST' and 'email' in request.form and 'psw' in request.form:
        email=request.form['email']
        password=request.form['psw']
        cursor=mysql.connection.cursor()
        cursor.execute('select * from user where email=%s and password=%s',(email,password))
        user=cursor.fetchone()
        
        if user:
            session['username']=user[1]
            session['password']=user[3]
            if(email=='dipabalihalder0802@gmail.com' and password=='admin'):
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('user',user=user))
                msg="Done"
        else:
            msg='Incorrect email or password!'
        cursor.close()
    elif request.method == 'POST':
        msg='Please fill in the details.'
    return render_template('login.html',msg=msg)

@app.route('/admin',methods=['GET','POST'])
def admin():
    cursor=mysql.connection.cursor()
    cursor.execute('select count(*) from doctors')
    d=cursor.fetchone()[0]
    cursor.execute('select count(*) from user')
    u=cursor.fetchone()[0]
    cursor.execute('select count(*) from booking')
    b=cursor.fetchone()[0]
    cursor.execute('select count(distinct(patname)) from booking')
    p=cursor.fetchone()[0]
    return render_template('adminpage.html',d=d,u=u,b=b,p=p)

@app.route('/forgot',methods=['GET','POST'])
def forgot():
    msg=''
    if request.method=='POST' and 'email' in request.form and 'password' in request.form and 'cnfrm-password' in request.form:
        email=request.form['email']
        password=request.form['password']
        cnfrm=request.form['cnfrm-password']
        cursor=mysql.connection.cursor()
        cursor.execute('select email from user');
        e=list(cursor.fetchall())
        em=[]
        for i in e:
            em.append(i[0])
        print(em)
        if(email not in em):
            msg='This email is not registed.'
        elif(password!=cnfrm):
            msg="Passwords must be same."
        elif(email in em and password==cnfrm):
            cursor.execute('select id from user where email=%s',(str(email),))
            id=cursor.fetchone()[0]
            cursor.execute('update user set password=%s where id=%s',(password,id))
            mysql.connection.commit()
            msg="Password Changed Successfully..."
    return render_template('forgot.html',msg=msg)

@app.route('/register',methods=['GET','POST'])
def register():
    msg=''
    if request.method=='POST' and 'username' in request.form and 'email' in request.form and 'psw' in request.form and 'psw-repeat' in request.form :
        username=request.form['username']
        email=request.form['email']
        password=request.form['psw']
        cnfrm=request.form['psw-repeat']
        if(password==cnfrm):
            cursor=mysql.connection.cursor()
            cursor.execute('select * from user where username=%s',(username, ))
            account=cursor.fetchone()
            cursor.execute('select * from user where email=%s',(email, ))
            account1=cursor.fetchone()    
            if account:
                msg='This user is already registered.'
            elif account1:
                msg='This email is already in use.'
            else:
                cursor.execute('Insert into user values (NULL,%s,%s,%s)',(username,email,password, ))
                mysql.connection.commit()
                cursor.close()
                msg='You have successfully registered!!!'
        else:
            msg='Passwords must be same.'
    elif request.method == 'POST':
        msg='Please fill in the details.'
    return render_template('register.html',msg=msg)

@app.route('/doctor',methods=['GET','POST'])
def doctor():
    try:
        cursor=mysql.connection.cursor()
        cursor.execute('select * from doctors')
        doctors=cursor.fetchall()
        cursor.close()
        c = ['Mumbai','Delhi','Karnataka']
        return render_template('doctor.html',doctors=doctors,c=c)
    except Exception as e:
        print(e)
        return 'none'

@app.route('/adddoctor',methods=['POST','GET'])
def adddoctor():
    msgd=''
    if request.method=='POST' and 'name' in request.form and 'mobile' in request.form and 'email' in request.form and 'category' in request.form:
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        category=request.form['category']
        amount=request.form['amount']
        clinic=request.form['clinic']
        print(clinic)
        if name=='' or mobile=='' or email=='' or category=='' or amount=='':
            msgd="Please fill in the details."
        else:
            cursor=mysql.connection.cursor()
            cursor.execute('insert into doctors values (NULL,%s,%s,%s,%s,%s,%s)',(name,mobile,email,category,amount,clinic,))
            mysql.connection.commit()
            cursor.close()
            msgd='Doctor Added'
            return redirect(url_for('doctor'))
    return render_template('adddoctor.html',msgd=msgd)

@app.route('/delete/<id>',methods=['POST','GET'])
def delete(id):
    try:
        cur=mysql.connection.cursor()
        cur.execute('delete from doctors where doctorid=%s',(id,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('doctor'))
    except Exception as e:
        print(e)
        return "none"
    
@app.route('/editdoctor/<id>',methods=['POST','GET'])
def editdoctor(id):
    try:
        cursor=mysql.connection.cursor()
        cursor.execute('select * from doctors where doctorid= %s',(id,))
        doctor=cursor.fetchone()
        #cursor.execute('select category from doctors where doctorid=%s',(id,))
        #ctg=cursor.fetchone()
        cursor.close()
        return render_template('editdoctor.html',id=id,doctor=doctor,loc=['Mumbai','Delhi','Karnataka'])
    except Exception as e:
        print(e)
        return "error"


@app.route('/updatedoctor/<id>',methods=['POST','GET'])
def updatedoctor(id):
    try:
        #if not request.form['name'] or not request.form['mobile'] or not request.form['email'] or not request.form['description']:
        #    raise Exception
        cursor=mysql.connection.cursor()
        cursor.execute('update doctors set name=%s, mobile=%s, email=%s, category=%s, amount=%s, clinic=%s where doctorid=%s',(request.form['name'],request.form['mobile'],request.form['email'],request.form['category'],request.form['amount'],request.form['clinic'],id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('doctor'))
    except Exception as e:
        return "error1"

@app.route('/userslist',methods=['GET','POST'])
def userslist():
    try:
        cursor=mysql.connection.cursor()
        cursor.execute('select * from user')
        users=cursor.fetchall()
        cursor.close()
        return render_template('userslist.html',users=users)
    except Exception as e:
        print(e)
        return "none"

@app.route('/clinics',methods=['GET','POST'])
def clinics():
    try:
        cursor=mysql.connection.cursor()
        cursor.execute('select * from clinic')
        clinic=cursor.fetchall()
        cursor.close()
        return render_template('clinics.html',clinic=clinic)
    except Exception as e:
        print(e)
        return "none"

@app.route('/user/<user>',methods=['POST','GET'])
def user(user):
    cursor=mysql.connection.cursor()
    cursor.execute('select * from user where username=%s',(str(session['username']),))
    u=list(cursor.fetchall())
    print(u)
    cursor.execute('select count(*) from booking where userid=(select id from user where username=%s)',(str(session['username']),))
    a=cursor.fetchone()[0]
    cursor.execute('select count(*) from booking where userid=(select id from user where username=%s) and date(date)>=(select date(sysdate()) from dual) and status="App. Booked"',(str(session['username']),))
    cnt=cursor.fetchone()[0]
    return render_template('userpage.html',user=user,u=u,cnt=cnt,a=a)

@app.route('/location/<user>',methods=['POST','GET'])
def location(user):
    if request.method=='POST' and 'clinic' in request.form:
        cursor=mysql.connection.cursor()
        cursor.execute('select doctorid, name, category from doctors where clinic=%s',(request.form['clinic'],))
        doctor=list(cursor.fetchall())
        doctor.insert(0,(0,'Select any one','None'))
        return render_template('book.html',user=user,doctor=doctor)
    return render_template('location.html',user=user)

@app.route('/bookapp/<user>',methods=['POST','GET'])
def bookapp(user):
    msg=''
    if request.method=='POST' and 'doctor' in request.form and 'date' in request.form and 'time' in request.form and 'patname' in request.form and 'gender' in request.form and 'age' in request.form: 
        doctorid=request.form.get('doctor')
        cursor=mysql.connection.cursor()
        cursor.execute('select id from user where username=%s',(user, ))
        userid=str(list(cursor.fetchone())[0])
        cursor.execute('select clinic from doctors where doctorid=%s',(str(doctorid),))
        clinic=list(cursor.fetchone())[0]
        cursor.execute('select doctorid, name, category from doctors where clinic=%s',(clinic,))
        doctor=list(cursor.fetchall())
        doctor.insert(0,(0,'Select any one','None'))
        date=request.form.get('date')
        time=request.form['time']
        patname=request.form['patname']
        gender=request.form['gender']
        age=request.form['age']
        cursor.execute('select amount from doctors where doctorid=%s',(str(doctorid),))
        amount=list(cursor.fetchone())[0]+200
        print(amount)
        cursor.execute("select time from booking where date=%s and status='App. Booked' and doctorid=%s and clinic=%s",(date,doctorid,clinic))
        s=list(cursor.fetchall())
        slots=[]
        for t in s:
            slots.append(t[0])
        print(slots)
        status="App. Booked"
        if time in slots:
            msg="Sorry! The slots "+' , '.join(slots)+"\n are already booked."
            return render_template('book.html',user=user,doctor=doctor,msg=msg)
        else:
            msg="Done"
            cursor.execute('Insert into booking values(NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(doctorid,userid,clinic,date,time,patname,gender,age,status,amount))
            mysql.connection.commit()  
            cursor.close()
            return redirect(url_for('booked',user=user))
    elif request.method=='POST':
        return "none"
    return render_template('book.html',user=user,s=s,msg=msg)
    
@app.route('/booked/<user>',methods=['POST','GET'])
def booked(user):
    cursor=mysql.connection.cursor()
    cursor.execute('select id from user where username=%s',(session['username'],))
    id=str(list(cursor.fetchone())[0])
    cursor.execute('select b.appid,d.name,b.clinic,b.date,b.time,b.patname,b.gender,c.street,c.city,c.pin,c.phn,c.state,b.amount from booking b inner join doctors d on d.doctorid=b.doctorid inner join clinic c on c.state=b.clinic where userid=%s order by appid desc limit 1',(id))
    book=cursor.fetchone()
    print(book)
    cursor.close()  
    return render_template('booked.html',book=book,user=user)

@app.route('/cancel/<user>',methods=['POST','GET'])
def cancel(user):
    msg=''
    if request.method=='POST' and 'id' in request.form:
        id=request.form['id']
        cursor=mysql.connection.cursor()
        cursor.execute('select id from user where username=%s',(session['username'],))
        userid=str(list(cursor.fetchone())[0])
        cursor.execute('select count(*) from booking where userid=%s and appid=%s',(userid,str(id)))
        count=int(list(cursor.fetchone())[0])
        if count == 1:            
            cursor.execute('select status from booking where appid=%s and userid=%s',(str(id),userid))
            status=str(list(cursor.fetchone())[0])
            if status=="App. Booked":
                status="Canceled"
                cursor.execute('update booking set status=%s where appid=%s and userid=%s',(status,str(id),userid))
                mysql.connection.commit()
                msg='Appointment Canceled!'
            else:
                msg='Appointment is already canceled'
        else:
            msg='You entered an Incorrect ID.'
        cursor.close()
    elif request.method=='POST':
        msg='Please fill in the id.'
    return render_template('cancelapp.html',user=user,msg=msg)

@app.route('/bookings',methods=['POST','GET'])
def bookings():
    try:
        cursor=mysql.connection.cursor()
        cursor.execute('select b.appid,b.clinic,u.username,u.email,d.name,b.patname,b.gender,b.date,b.time,b.amount,b.status from booking b inner join doctors d on d.doctorid=b.doctorid inner join user u on u.id=b.userid order by date(date) desc')
        book=cursor.fetchall()
        cursor.close()
        c = ['Mumbai','Delhi','Karnataka']
        return render_template('bookings.html',book=book,c=c)
    except Exception as e:
        print(e) 
        return "none"

@app.route('/appointment/<user>',methods=['POST','GET'])
def appointment(user):
    cursor=mysql.connection.cursor()
    cursor.execute('select id from user where username=%s',(session['username'],))
    id=str(list(cursor.fetchone())[0])
    cursor.execute('select b.appid,d.name,b.clinic,b.date,b.time,b.patname,b.amount,b.status from booking b inner join doctors d on d.doctorid=b.doctorid where userid=%s order by date desc',(id,))
    app=cursor.fetchall()
    l=len(app)
    return render_template('myapp.html',user=user,app=app,l=l)

@app.route('/feedback/<user>',methods=['POST','GET'])
def feedback(user):
    msg=''
    feedback=request.form.get('feedback')
    if feedback:
        cursor=mysql.connection.cursor()
        cursor.execute('insert into feedback values(NULL,%s,%s)',(session['username'],feedback))
        mysql.connection.commit()
        msg="Thanks for your feedback!"
    elif feedback=='':
        msg="Kindly provide your feedback..."
    return render_template('feedback.html',user=user,msg=msg)

@app.route('/allfeeds',methods=['POST','GET'])
def allfeeds():
    cursor=mysql.connection.cursor()
    cursor.execute('select f.username,u.email,f.feed from feedback f inner join user u on f.username=u.username order by f.id desc')
    feeds=cursor.fetchall()
    cursor.close()
    return render_template('allfeeds.html',feeds=feeds)

@app.route('/profile/<user>',methods=['POST','GET'])
def profile(user):
    cursor=mysql.connection.cursor()
    cursor.execute('select * from user where username=%s',(str(session['username']),))
    user=cursor.fetchone()
    cursor.close()
    return render_template('profile.html',user=user)

@app.route('/profileupdate/<user>',methods=['POST','GET'])
def profileupdate(user):
    msg=''
    try:
        cursor=mysql.connection.cursor()
        cursor.execute('update user set email=%s, password=%s where username=%s',(request.form['email'],request.form['pass'],session['username']))
        mysql.connection.commit()
        cursor.close()
        msg="Profile Updated"
        return redirect(url_for('user',user=user))
    except Exception as e:
        return "error4"
    
@app.route('/logout')
def logout():
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)






