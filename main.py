#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import hashlib
import pymysql.cursors
import datetime

#Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect( unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock',
 					    host='localhost',
                        user='root',
                        password='root',
                        db='findfolks',
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)

#conn = pymysql.connect(
#					   host='localhost',
#                      user='root',
#                      password='',
#                      db='findfolks',
#                      charset='utf8mb4',
#                      cursorclass=pymysql.cursors.Dictcursor
#                      )


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
	starttime = "%s-%s-%s %s:%s:%s" % (str(now.year), str(now.month), str(now.day), str(now.hour), str(now.minute), str(now.second))
	endtime =  "%s-%s-%s %s:%s:%s" % (str(now.year), str(now.month), str(now.day+3), str(now.hour), str(now.minute), str(now.second))
	query = 'SELECT * FROM an_event WHERE start_time BETWEEN \'' + starttime + '\' AND \'' + endtime + "\'"
	cursor.execute(query)
	data = cursor.fetchall()
	cursor.close()
	return render_template('index.html', events=data)

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
	password = request.form['password'].encode('utf-8')
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
	password = request.form['password'].encode('utf-8')
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
	now = datetime.datetime.now()
	cursor = conn.cursor()
	starttime = "%s-%s-%s %s:%s:%s" % (str(now.year), str(now.month), str(now.day), str(now.hour), str(now.minute), str(now.second))
	endtime =  "%s-%s-%s %s:%s:%s" % (str(now.year), str(now.month), str(now.day+3), str(now.hour), str(now.minute), str(now.second))
	query = 'SELECT * FROM an_event WHERE start_time BETWEEN \'' + starttime + '\' AND \'' + endtime + "\'"
	cursor.execute(query)
	data = cursor.fetchall()
	cursor.close()
	return render_template('home.html', username = username, logged_in = logged_in, events = data)

@app.route('/view_my_events')
def view_my_events():
	username = session['username']
	now = datetime.datetime.now()
	cursor = conn.cursor()
	starttime = "%s-%s-%s %s:%s:%s" % (str(now.year), str(now.month), str(now.day), str(now.hour), str(now.minute), str(now.second))
	endtime =  "%s-%s-%s %s:%s:%s" % (str(now.year), str(now.month), str(now.day+3), str(now.hour), str(now.minute), str(now.second))
#	query = 'SELECT * FROM an_event WHERE start_time BETWEEN \'' + starttime + '\' AND \'' + endtime + "\'"
	query = 'SELECT * FROM an_event NATURAL JOIN sign_up WHERE username = %s AND start_time BETWEEN \'' + starttime + '\' AND \'' + endtime + "\'"
	cursor.execute(query, (username))
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
	#if it is a valid event
	if data:
		cursor2 = conn.cursor()
		query = 'SELECT * FROM sign_up WHERE event_id = %s AND username = %s'
		cursor2.execute(query, (event_id, session['username']))
		result = cursor2.fetchone()
		print result
		cursor2.close()
		#if not already registered
		if result == None:
			cursor3 = conn.cursor()
			insert = "INSERT INTO sign_up VALUES (%s, %s, NULL)"
			cursor3.execute(insert, (event_id, session['username']))
			conn.commit()
#			data = cursor2.fetchone()
			cursor3.close()
			successmessage = "Registered for Event ID: " + event_id
			return render_template('event_signup.html', logged_in = session['logged_in'], success = successmessage)
		#if already registered
		else:
			successmessage = "Already registered for Event ID: " + event_id
			return render_template('event_signup.html', logged_in = session['logged_in'], success = successmessage)
	#non valid event
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
	description = request.form['description']
	start_time = request.form['start_time']
	end_time = request.form['end_time']
	location_name = request.form['location_name']
	zipcode = request.form['zipcode']
	cursor = conn.cursor()
	query = 'SELECT authorized FROM belongs_to WHERE username = %s AND group_id = %s'
	cursor.execute(query, (username, group_id))
	data = cursor.fetchone()
	#if in group
	if data:
		#if authorized
		if data == 1:
			cursor = conn.cursor()
			query1 = 'INSERT INTO an_event VALUES (NULL, %s, %s, %s, %s, %s, %s)'
			cursor.execute(query1, (title, description, start_time, end_time, location_name, zipcode))
			conn.commit()
			query2 = 'SELECT max(event_id) FROM an_event'
			cursor.execute(query2)
			event_id = cursor.fetchone()
			query3 = 'INSERT INTO organize VALUES (%s, %s)'
			conn.commit()
			cursor.execute(query3, (event_id, group_id))
			cursor.close()
			success = 'Congrats! Event created, your Event ID is ' + event_id
			return render_template('create_event.html', logged_in = session['logged_in'], success = success)
		#not auth
		else:
			cursor.close()
			error = 'You are not authorized to create events, ask for authorization.'
			return render_template('create_event.html', logged_in = session['logged_in'], error = error)
	#not in group LOL
	else:
		cursor.close()
		error = 'You are not not in this group. Join the group and ask for authorization to create events.'
		return render_template('create_event.html', logged_in = session['logged_in'], error = error)
	
@app.route('/event_rating')
def rateEvent():
	return render_template('event_rating.html', logged_in = session['logged_in'])
	
@app.route('/rate', methods=['GET', 'POST'])
def rate():
	username = session['username']
	event_id = request.form['event_id']
	rating = request.form['rating']
	cursor = conn.cursor()
	query = 'SELECT * FROM sign_up WHERE username = %s AND event_id = %s'
	cursor.execute(query, (username, event_id))
	data = cursor.fetchone()
	#if signed up
	if data:
		#check if event has already passed
		now = datetime.datetime.now()
		endtime = "%s-%s-%s %s:%s:%s" % (str(now.year), str(now.month), str(now.day), str(now.hour), str(now.minute), str(now.second))
		query2 = "SELECT * FROM an_event WHERE event_id = %s AND end_time < %s"
		cursor.execute(query2, (event_id, endtime))
		elapsed = cursor.fetchone()
		#if passed
		if elapsed:
			query3 = 'UPDATE table_name SET rating = %s WHERE username = %s AND event_id = %s'
			cursor.execute(query3, (rating, username, event_id))
			conn.commit()
			cursor.close()
			success = "Your event " + event_id + " has been rated as " + rating
			return render_template('event_rating.html', logged_in = session['logged_in'], success = success)
		#not passed
		else:
			error = "Your event has not ended yet!"
			return render_template('event_rating.html', logged_in = session['logged_in'], error = error)
	else:
		error = "You are not signed up for this event!"
		return render_template('event_rating.html', logged_in = session['logged_in'], error = error)


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
