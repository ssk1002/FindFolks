#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import hashlib
import pymysql.cursors
import datetime

#Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock',
					   host='localhost',
                       user='root',
                       password='root',
                       db='findfolks',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	if session.get('logged_in') is True:
		return redirect(url_for('home'))
	return redirect(url_for('index'))

#Define route for index
@app.route('/index')
def index():
	now = datetime.datetime.now()
	cursor = conn.cursor()
	query = "SELECT * FROM an_event WHERE start_time >= %s-%s-%s AND end_time <= %s-%s-%s"
	cursor.execute(query, (str(now.month), str(now.day), str(now.year), str(now.month), str(now.day + 3), str(now.year)))
	data = cursor.fetchall()
	cursor.close()
	return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')


#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')


#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	md5password = hashlib.md5(password).hexdigest()
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM member WHERE username = %s and password = %s'
	cursor.execute(query, (username, md5password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	if data:
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		session['logged_in'] = True
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)


#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	firstname = request.form['firstname']
	lastname = request.form['lastname']
	email = request.form['email']
	zipcode = request.form['zipcode']
	md5password = hashlib.md5(password).hexdigest()
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM member WHERE username = %s'
	cursor.execute(query, username)
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if data:
		#If the previous query returns data, then user exists
		error = "This user already exists."
		return render_template('register.html', error=error)
	else:
		ins = 'INSERT INTO member VALUES(%s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (username, md5password, firstname, lastname, email, zipcode))
		conn.commit()
		cursor.close()
		success = "Registration Sucessful! Log in below to get started!"
		return render_template('login.html', success = success)


@app.route('/home')
def home():
	username = session['username']
	logged_in = session['logged_in']
#	cursor = conn.cursor()
#	query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
#	cursor.execute(query, username)
#	data = cursor.fetchall()
#	cursor.close()
	return render_template('home.html', username = username, logged_in = logged_in)

@app.route('/view_my_events')
def view_my_events():
	now = datetime.datetime.now()
	cursor = conn.cursor()
	username = session['username']
	query = 'SELECT * FROM an_event NATURAL JOIN sign_up WHERE username = %s AND start_time >= %s-%s-%s AND end_time <= %s-%s-%s'
	cursor.execute(query, (username, str(now.month), str(now.day), str(now.year), str(now.month), str(now.day + 3), str(now.year)))
	data = cursor.fetchall()
	cursor.close()
	return render_template('view_my_events.html', username = username, events = data, logged_in = session['logged_in'])

@app.route('/event_signup')
def event_signup():
	return render_template('event_signup.html', logged_in = session['logged_in'])
	
@app.route('/eventEnroll', methods=['GET', 'POST'])
def eventEnroll():
	event_id = request.form['event_id']
	cursor = conn.cursor()
	query = 'SELECT * FROM an_event WHERE event_id = %s'
	cursor.execute(query, event_id)
	data = cursor.fetchone()
	cursor.close()
	if data:
		cursor2 = conn.cursor()
		query = 'SELECT * FROM sign_up WHERE event_id = %s AND username = %s'
		cursor2.execute(query, (event_id, session['username']))
		result = cursor.fetchone()
		cursor2.close()
		if result:
			cursor3 = conn.cursor()
			insert = "INSERT INTO sign_up VALUES (%s, %s, NULL)"
			cursor3.execute(insert, (event_id, session['username']))
#			data = cursor2.fetchone()
			cursor3.close()
			successmessage = "Registered for Event ID: " + event_id
			return render_template('home.html', username = session['username'], logged_in = session['logged_in'], success = successmessage)
		else:
			successmessage = "Already registered for Event ID: " + event_id
			return render_template('home.html', username = session['username'], logged_in = session['logged_in'], success = successmessage)
	else:
		#returns an error message to the html page
		error = 'Invalid event ID'
		return render_template('event_signup.html', logged_in = session['logged_in'], error=error)
		
@app.route('/event_interests')
def eventSimilarInterests():
#	cursor = conn.cursor()
#	query = 'SELECT * FROM interest NATURAL JOIN interested_in NATURAL JOIN  WHERE event_id = %s'
#	cursor.execute(query, event_id)
#	data = cursor.fetchall()
#	cursor.close()
	if data:
		return render_template('event_signup.html', logged_in = session['logged_in'], events=data)
	else:
		error = "You have no interests in common with any groups! Try adding other interests or create your own group with events."
		return render_template('event_signup.html', logged_in = session['logged_in'], error=error)
		
@app.route('/create_event')
def createEvent():
	return render_template('create_event.html', logged_in = session['logged_in'])

@app.route('/makeEvent', methods=['GET', 'POST'])
def makeEvent():
	username = session['username']
	group_id = request.form['group_id']
	title = request.form['title']
	start_time = request.form['start_time']
	end_time = request.form['end_time']
	location_name = request.form['location_name']
	zipcode = request.form['zipcode']
	cursor = conn.cursor()
	query = 'SELECT authorized FROM belongs_to WHERE username = %s AND group_id = %s'
	cursor.execute(query, (username, group_id))
	data = cursor.fetchone()
	cursor.close()
	#if in group
	if data:
		#if authorized
		if data == 1:
			pass
		#not auth
		else:
	#not in group LOL
	else
	
	

@app.route('/remove_account')
def removeacct():
	username = session['username']
	cursor = conn.cursor()
	query = 'DELETE FROM member WHERE username = %s'
	cursor.execute(query, username)
	conn.commit()
	cursor.close()
	session.pop('username')
	session.pop('logged_in')
	success = "Account removal sucessful, we are sad to see you go :("
	return render_template('index.html', success = success)

@app.route('/logout')
def logout():
	session.pop('username')
	session.pop('logged_in')
	return redirect('/')


app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)