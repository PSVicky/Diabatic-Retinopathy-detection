from flask import Flask, render_template, g,request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = '123564'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'Doctor'


mysql = MySQL(app)
@app.before_request
def load_user():
    if "id" in session:
        g.record = 1
        g.id = session['id']
        # g.firstname =session['firstname']
    else:
        g.record = 0

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s', (email, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        print(email,password)
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['firstname'] = account['firstname']
            session['lastname'] = account['lastname']
            session['email'] = account['email']
            # Redirect to home page
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("""SELECT * FROM Patient WHERE doctorId = %s""", (session['id'],))
            data = cursor.fetchall()
            
            return render_template('doctor.html',name=session['firstname'],data=data)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            
    return render_template('index.html')


# Logout
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('firstname', None)
   # Redirect to login page
   return render_template('index.html')

@app.route('/Register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s,%s)', (firstname,lastname, password, email,))
            mysql.connection.commit()
            return render_template('register.html',)
    return render_template('register.html')

@app.route('/add_record',methods=['GET','POST'])
def add_record():
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        gender = request.form.get('gender')
        phone = request.form['phone']
        email = request.form['email']
        image = request.files['image']
        print(type(age),type(phone),type(g.id))
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Patient WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account Already exists'
        else:
            cursor.execute('INSERT INTO Patient VALUES (Null, %s, %s, %s,%s,%s,%s)', (name,int(age), gender, phone,email,int(g.id)))
            mysql.connection.commit()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("""SELECT * FROM Patient WHERE doctorId = %s""", (g.id,))
            data = cursor.fetchall()
            mysql.connection.commit()
            
            return render_template('doctor.html',name=session['firstname'],data=data)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""SELECT * FROM Patient WHERE doctorId = %s""", (g.id,))
    data = cursor.fetchall()
    mysql.connection.commit()
    return render_template('doctor.html',name=session['firstname'],data=data)
 
@app.route('/update/<string:id>',methods = ['GET','POST'])
def update(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""SELECT * FROM Patient WHERE PatientId = %s""", (id,))
    data = cursor.fetchone()
    mysql.connection.commit()
    
    if request.method =="POST":
        name = request.form['name']
        print(name)
        age = int(request.form['age'])
        gender = request.form.get('gender')
        phone = request.form['phone']
        email = request.form['email']
        image = request.files['image']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE Patient SET name = %s, age = %s,gender=%s,phone=%s,email=%s WHERE PatientId = %s", (name,age,gender,phone,email,id,))
        mysql.connection.commit()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""SELECT * FROM Patient WHERE doctorId = %s""", (g.id,))
        data = cursor.fetchall()
        mysql.connection.commit()
        return render_template('doctor.html',name=session['firstname'],data=data)
    return render_template('update.html',name=session['firstname'],data = data)
@app.route('/delete/<string:id>')
def delete(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"DELETE FROM Patient WHERE PatientId = {id}")
    cursor.execute("""SELECT * FROM Patient WHERE doctorId = %s""", (g.id,))
    data = cursor.fetchall()
    mysql.connection.commit()
    return render_template('doctor.html',name=session['firstname'],data=data)
 
    return render_template('doctor.html')     
if __name__=='__main__':
    app.run(debug=True)
    
    
    
    
# CREATE TABLE Patient( PatientId INT PRIMARY KEY NOT NULL, name VARCHAR(50), age int, gender VARCHAR(255), phone VARCHAR(30), email VARCHAR(255), doctorId int );