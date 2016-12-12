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
@app.route('/index',  methods=['GET', 'POST'])
def index():
	groups = None
	now = datetime.datetime.now()
	cursor = conn.cursor()
	starttime = "%s-%s-%s %s:%s:%s" % (str(now.year), str(now.month), str(now.day), str(now.hour), str(now.minute), str(now.second))
	endtime =  "%s-%s-%s %s:%s:%s" % (str(now.year), str(now.month), str(now.day+3), str(now.hour), str(now.minute), str(now.second))
	query = 'SELECT * FROM an_event WHERE start_time BETWEEN \'' + starttime + '\' AND \'' + endtime + "\'"
	cursor.execute(query)
	data = cursor.fetchall()
	query = 'SELECT * FROM interest'
	cursor.execute(query)
	interests = cursor.fetchall()
	if request.method == "POST":
		interest = request.form.get('select_interest')
		interest = interest.split(', ')
		category = interest[0]
		keyword = interest[1]
		query = 'SELECT * FROM a_group NATURAL JOIN about WHERE category = %s AND keyword = %s'
		cursor.execute(query, (category, keyword))
		groups = cursor.fetchall()
		cursor.close()
		return render_template('index.html', events=data, interests = interests, groups = groups)
	return render_template('index.html', events=data, interests = interests)
	


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


@app.route('/home', methods=['GET', 'POST'])
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
	cursor.execute(query)
	data = cursor.fetchall()
	query = 'SELECT * FROM interest'
	cursor.execute(query)
	interests = cursor.fetchall()
	if request.method == "POST":
		interest = request.form.get('select_interest')
		interest = interest.split(', ')
		category = interest[0]
		keyword = interest[1]
		query = 'SELECT * FROM a_group NATURAL JOIN about WHERE category = %s AND keyword = %s'
		cursor.execute(query, (category, keyword))
		groups = cursor.fetchall()
		cursor.close()
		return render_template('home.html', username = username, logged_in = logged_in, events = data, interests = interests, groups = groups)
	return render_template('home.html', username = username, logged_in = logged_in, events = data, interests = interests)

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

@app.route('/view_all_events')
def view_all_events():
		username = session['username']
		now = datetime.datetime.now()
		cursor = conn.cursor()
		query = 'SELECT * FROM an_event'
		cursor.execute(query)
		data = cursor.fetchall()
		cursor.close()
		return render_template('view_all_events.html', username = username, events = data, logged_in = session['logged_in'])

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
#	SELECT * FROM an_event NATURAL JOIN organize NATURAL JOIN about WHERE (category, keyword) IN (SELECT category, keyword FROM interested_in WHERE username = '2')
	username = session['username']
	cursor = conn.cursor()
	query = 'SELECT * FROM an_event NATURAL JOIN organize NATURAL JOIN about WHERE (category, keyword) IN (SELECT category, keyword FROM interested_in WHERE username = %s)'
	cursor.execute(query, username)
	data = cursor.fetchall()
	cursor.close()
	return render_template('event_interests.html', logged_in = session['logged_in'], events = data)

@app.route('/friends_events')
def friendsEvents():
	#SELECT * FROM sign_up NATURAL JOIN an_event WHERE username IN (SELECT friend_to AS username FROM friend WHERE friend_of = '2')
	username = session['username']
	cursor = conn.cursor()
	query = 'SELECT * FROM sign_up NATURAL JOIN an_event WHERE username IN (SELECT friend_to AS username FROM friend WHERE friend_of = %s)'
	cursor.execute(query, username)
	data = cursor.fetchall()
	cursor.close()
	return render_template('friends_events.html', logged_in = session['logged_in'], events = data)
	
@app.route('/view_join_group')
def viewJoinGroup():
	username = session['username']
	cursor = conn.cursor()
	query = 'SELECT * FROM a_group'
	cursor.execute(query)
	data = cursor.fetchall()
	query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE username = %s'
	cursor.execute(query, username)
	data1 = cursor.fetchall()
	cursor.close()
	return render_template('view_join_group.html', logged_in = session['logged_in'], groups = data, mygroups = data1)

@app.route('/joinGroup', methods=['GET', 'POST'])
def joinGroup():
	username = session['username']
	group_id = request.form['group_id']
	cursor = conn.cursor()
	#check if group exists
	query = 'SELECT * FROM a_group WHERE group_id = %s'
	cursor.execute(query, group_id)
	data = cursor.fetchall()
	if data:
		#check if already in group
		query = 'SELECT * FROM belongs_to WHERE group_id = %s AND username = %s'
		cursor.execute(query, (group_id, username))
		data = cursor.fetchall()
		if data:
			query = 'SELECT * FROM a_group'
			cursor.execute(query)
			data = cursor.fetchall()
			query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE username = %s'
			cursor.execute(query, username)
			data1 = cursor.fetchall()
			cursor.close()
			success = 'Already in Group'
			return render_template('view_join_group.html', logged_in = session['logged_in'], groups = data, mygroups = data1, success = success)
		#add
		else:
			query = 'INSERT INTO belongs_to VALUES (%s, %s, 0)'
			cursor.execute(query, (group_id, username))
			conn.commit()
			query = 'SELECT * FROM a_group'
			cursor.execute(query)
			data = cursor.fetchall()
			query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE username = %s'
			cursor.execute(query, username)
			data1 = cursor.fetchall()
			cursor.close()
			success	= 'Added to group!'
			return render_template('view_join_group.html', logged_in = session['logged_in'], groups = data, mygroups = data1, success = success)
	else:
		query = 'SELECT * FROM a_group'
		cursor.execute(query)
		data = cursor.fetchall()
		query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE username = %s'
		cursor.execute(query, username)
		data1 = cursor.fetchall()
		cursor.close()
		error = 'That is an invalid group id'
		return render_template('view_join_group.html', logged_in = session['logged_in'], groups = data, mygroups = data1, error = error)
	

@app.route('/create_group')
def createGroup():
	return render_template('create_group.html', logged_in = session['logged_in'])

@app.route('/makeGroup', methods=['GET', 'POST'])
def makeGroup():
	username = session['username']
	group_name = request.form['group_name']
	description = request.form['description']
	category = request.form['category']
	keyword = request.form['keyword']
	cursor = conn.cursor()
	query = 'INSERT INTO a_group VALUES (NULL, %s, %s, %s)'
	cursor.execute(query, (group_name, description, username))
	conn.commit()
	query2 = 'SELECT max(group_id) FROM a_group'
	cursor.execute(query2)
	group_id = cursor.fetchone()
	query = 'INSERT INTO belongs_to VALUES (%s, %s, 1)'
	cursor.execute(query, (group_id[max(group_id)], username))
	conn.commit()
	query = "SELECT * FROM interest WHERE category = %s AND keyword = %s"
	cursor.execute(query, (category, keyword))
	data = cursor.fetchone()
	if data == None:
		query = 'INSERT INTO interest VALUES (%s, %s)'
		cursor.execute(query, (category, keyword))
		conn.commit()
	query = 'INSERT INTO about VALUES (%s, %s, %s)'
	cursor.execute(query, (category, keyword, group_id[max(group_id)]))
	conn.commit()
	success = 'Congrats! Group created, your Group ID is ' + str(group_id[max(group_id)])
	return render_template('create_group.html', logged_in = session['logged_in'], success = success)
		
@app.route('/interests')
def interests():
	username = session['username']
	cursor = conn.cursor()
	query = 'SELECT * FROM interested_in WHERE username = %s'
	cursor.execute(query, username)
	data = cursor.fetchall()
	return render_template('interests.html', logged_in = session['logged_in'], interests = data)

@app.route('/addInterest', methods=['GET', 'POST'])
def addInterest():
	username = session['username']
	keyword = request.form['keyword']
	category = request.form['category']
	cursor = conn.cursor()
	query = "SELECT * FROM interest WHERE category = %s AND keyword = %s"
	cursor.execute(query, (category, keyword))
	data = cursor.fetchone()
	if data == None:
		query = 'INSERT INTO interest VALUES (%s, %s)'
		cursor.execute(query, (category, keyword))
		conn.commit()
	query = 'INSERT INTO interested_in VALUES (%s, %s, %s)'
	cursor.execute(query, (username, category, keyword))
	conn.commit()
	success = 'Interest added'
	cursor = conn.cursor()
	query = 'SELECT * FROM interested_in WHERE username = %s'
	cursor.execute(query, username)
	data = cursor.fetchall()
	return render_template('interests.html', logged_in = session['logged_in'], interests = data, success = success)

@app.route('/create_event')
def createEvent():
	cursor = conn.cursor()
	query = 'SELECT * FROM location'
	cursor.execute(query)
	data = cursor.fetchall()
	return render_template('create_event.html', logged_in = session['logged_in'], locations = data)

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
	query = 'SELECT * FROM belongs_to WHERE username = %s AND group_id = %s'
	cursor.execute(query, (username, group_id))
	data = cursor.fetchone()
	#if in group
	if data:
		#if authorized
		if data['authorized'] == 1:
			cursor = conn.cursor()
			query = "SELECT * FROM location WHERE location_name = %s AND zipcode = %s"
			cursor.execute(query, (location_name, zipcode))
			data = cursor.fetchone()
			if data == None:
				cursor = conn.cursor()
				query = 'SELECT * FROM location'
				cursor.execute(query)
				data = cursor.fetchall()
				error = 'invalid location'
				return render_template('create_event.html', logged_in = session['logged_in'], locations = data, error = error)
			query1 = 'INSERT INTO an_event VALUES (NULL, %s, %s, %s, %s, %s, %s)'
			cursor.execute(query1, (title, description, start_time, end_time, location_name, zipcode))
			conn.commit()
			query2 = 'SELECT max(event_id) FROM an_event'
			cursor.execute(query2)
			event_id = cursor.fetchone()
			query3 = 'INSERT INTO organize VALUES (%s, %s)'
			cursor.execute(query3, (event_id['max(event_id)'], group_id))
			conn.commit()
			success = 'Congrats! Event created, your Event ID is ' + str(event_id['max(event_id)'])
			query = 'SELECT * FROM location'
			cursor.execute(query)
			data = cursor.fetchall()
			cursor.close()
			return render_template('create_event.html', logged_in = session['logged_in'], locations = data, success = success)
		#not auth
		else:
			query = 'SELECT * FROM location'
			cursor.execute(query)
			data = cursor.fetchall()
			cursor.close()
			error = 'You are not authorized to create events, ask for authorization.'
			return render_template('create_event.html', logged_in = session['logged_in'], locations = data, error = error)
	#not in group LOL
	else:
		query = 'SELECT * FROM location'
		cursor.execute(query)
		data = cursor.fetchall()
		cursor.close()
		error = 'You are not not in this group. Join the group and ask for authorization to create events.'
		return render_template('create_event.html', logged_in = session['logged_in'], locations = data, error = error)
	
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
			query3 = 'UPDATE sign_up SET rating = %s WHERE username = %s AND event_id = %s'
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

@app.route('/friends')
def friends():
	username = session['username']
	cursor = conn.cursor()
	query = 'SELECT * FROM friend WHERE friend_of = %s'
	cursor.execute(query, (username))
	data = cursor.fetchall()
	cursor.close()
	return render_template('friends.html', logged_in = session['logged_in'], friends = data)
	
@app.route('/friending', methods=['GET', 'POST'])
def addRemoveFriends():
	username = session['username']
	friendUsername = request.form['username']
	addOrRemove = request.form['addOrRemove']
	#check if friends username exists
	cursor = conn.cursor()
	query = 'SELECT * FROM member WHERE username = %s'
	cursor.execute(query, friendUsername)
	data = cursor.fetchone()
	#if exists
	if data:
		#add friend
		if addOrRemove == 'friend':
			#check if already a friend
			query = 'SELECT * FROM friend WHERE friend_of = %s AND friend_to = %s'
			cursor.execute(query, (username, friendUsername))
			data = cursor.fetchone()
			#already friend
			if data:
				query = 'SELECT * FROM friend WHERE friend_of = %s'
				cursor.execute(query, (username))
				data = cursor.fetchall()
				cursor.close()
				success = 'That user is already your friend! :)'
				return render_template('friends.html', logged_in = session['logged_in'], friends = data, success = success)
			#add friend!
			else:
				query = 'INSERT INTO friend VALUES (%s, %s)'
				cursor.execute(query, (username, friendUsername))
				conn.commit()
				query = 'SELECT * FROM friend WHERE friend_of = %s'
				cursor.execute(query, (username))
				data = cursor.fetchall()
				cursor.close()
				success = 'Friend added! :)'
				return render_template('friends.html', logged_in = session['logged_in'], friends = data, success = success)
		#remove friend
		else:
			#check if already a friend
			query = 'SELECT * FROM friend WHERE friend_of = %s AND friend_to = %s'
			cursor.execute(query, (username, friendUsername))
			data = cursor.fetchone()
			#already friend
			if not data:
				query = 'SELECT * FROM friend WHERE friend_of = %s'
				cursor.execute(query, (username))
				data = cursor.fetchall()
				cursor.close()
				success = 'That user is already not your friend! :('
				return render_template('friends.html', logged_in = session['logged_in'], friends = data, success = success)
			#add friend!
			else:
				query = 'DELETE FROM friend WHERE friend_of = %s AND friend_to = %s'
				cursor.execute(query, (username, friendUsername))
				conn.commit()
				query = 'SELECT * FROM friend WHERE friend_of = %s'
				cursor.execute(query, (username))
				data = cursor.fetchall()
				cursor.close()
				success = 'Friend removed! :('
				return render_template('friends.html', logged_in = session['logged_in'], friends = data, success = success)
	#if not exists
	else:
		cursor.close()
		error = 'That username doesnt exist.'
		return render_template('friends.html', error = error)
	
@app.route('/authorized')
def authorized():
	username = session['username']
	cursor = conn.cursor()
	query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE authorized = 1'
	cursor.execute(query)
	data = cursor.fetchall()
	cursor.close()
	return render_template('authorized.html', logged_in = session['logged_in'], authorized = data)
		
@app.route('/authorizing', methods=['GET', 'POST'])
def authorizeUser():
	username = session['username']
	group_id = request.form['group_id']
	otherUsername = request.form['username']
	addOrRemove = request.form['addOrRemove']
	cursor = conn.cursor()
	query = 'SELECT * FROM a_group WHERE group_id = %s AND creator = %s'
	cursor.execute(query, (group_id, username))
	creatorFlag = cursor.fetchone()
	if creatorFlag == None:
		query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE authorized = 1'
		cursor.execute(query)
		data = cursor.fetchall()
		cursor.close()
		error = 'you are not the creator'
		return render_template('authorized.html', logged_in = session['logged_in'], authorized = data, error = error)
	#check if other username exists
	query = 'SELECT * FROM member WHERE username = %s'
	cursor.execute(query, otherUsername)
	otherUserExist = cursor.fetchone()
	#check if group exists
	cursor = conn.cursor()
	query = 'SELECT * FROM a_group WHERE group_id = %s'
	cursor.execute(query, group_id)
	data = cursor.fetchone()
	#group exists
	if data:
		#if other username exists
		if otherUserExist:
			#add
			if addOrRemove == 'authorize':
				#check if in belongs to/already authorized
				query = 'SELECT * FROM belongs_to WHERE group_id = %s AND username = %s'
				cursor.execute(query, (group_id, otherUsername))
				data = cursor.fetchone()
				#in belongs to
				if data:
					#if already authorized
					if data['authorized'] == 1:
						query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE authorized = 1'
						cursor.execute(query)
						data = cursor.fetchall()
						cursor.close()
						success = 'That user is already your authorized! :)'
						return render_template('authorized.html', logged_in = session['logged_in'], authorized = data, success = success)
					#authorize!
					else:
						query = 'UPDATE belongs_to SET authorized = 1 WHERE group_id = %s AND username = %s'
						cursor.execute(query, (group_id, otherUsername))
						conn.commit()
						query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE authorized = 1'
						cursor.execute(query)
						data = cursor.fetchall()
						cursor.close()
						success = 'That user is now authorized! :)'
						return render_template('authorized.html', logged_in = session['logged_in'], authorized = data, success = success)
				#not in belongs to
				else:
					query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE authorized = 1'
					cursor.execute(query)
					data = cursor.fetchall()
					cursor.close()
					error = 'That user is not even part of the group!'
					return render_template('authorized.html', logged_in = session['logged_in'], authorized = data, error = error)
			#remove
			else:
				#check if in belongs to/already authorized
				query = 'SELECT * FROM belongs_to WHERE group_id = %s AND username = %s'
				cursor.execute(query, (group_id, otherUsername))
				data = cursor.fetchone()
				#in belongs to
				if data:
					#if already authorized
					if data['authorized'] != 1:
						query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE authorized = 1'
						cursor.execute(query)
						data = cursor.fetchall()
						cursor.close()
						success = 'That user is already not authorized!'
						return render_template('authorized.html', logged_in = session['logged_in'], authorized = data, success = success)
					#deauthorize
					else:
						#check to see if creator removal himself
						if creatorFlag != None and otherUsername == username:
							query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE authorized = 1'
							cursor.execute(query)
							data = cursor.fetchall()
							cursor.close()
							error = 'you are the creator and cannot deauthorize yourself'
							return render_template('authorized.html', logged_in = session['logged_in'], authorized = data, error = error)
						query = 'UPDATE belongs_to SET authorized = 0 WHERE group_id = %s AND username = %s'
						cursor.execute(query, (group_id, otherUsername))
						conn.commit()
						query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE authorized = 1'
						cursor.execute(query)
						data = cursor.fetchall()
						cursor.close()
						success = 'That user is now deauthorized!'
						return render_template('authorized.html', logged_in = session['logged_in'], authorized = data, success = success)
				#not in belongs to
				else:
					query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE authorized = 1'
					cursor.execute(query)
					data = cursor.fetchall()
					cursor.close()
					error = 'That user is not even part of the group!'
					return render_template('authorized.html', logged_in = session['logged_in'], authorized = data, error = error)	
		#other user doesnt exist	
		else:
			query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE authorized = 1'
			cursor.execute(query)
			data = cursor.fetchall()
			cursor.close()
			error = 'That user doesnt exist!'
			return render_template('authorized.html', logged_in = session['logged_in'], authorized = data, error = error)
	#group doesnt exist
	else:
		query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE authorized = 1'
		cursor.execute(query)
		data = cursor.fetchall()
		cursor.close()
		error = 'That group doesnt exist!'
		return render_template('authorized.html', logged_in = session['logged_in'], authorized = data, error = error)

#SELECT event_id, title, AVG(rating) FROM sign_up NATURAL JOIN an_event WHERE username = '1' AND end_time BETWEEN '2016-12-8 17:55:44' AND '2016-12-11 17:55:44' GROUP BY event_id, title
@app.route('/view_event_ratings')
def view_event_ratings():
	username = session['username']
	now = datetime.datetime.now()
	cursor = conn.cursor()
	endtime = "%s-%s-%s %s:%s:%s" % (str(now.year), str(now.month), str(now.day), str(now.hour), str(now.minute), str(now.second))
	starttime =  "%s-%s-%s %s:%s:%s" % (str(now.year), str(now.month), str(now.day-3), str(now.hour), str(now.minute), str(now.second))
	query = 'SELECT event_id, title, AVG(rating) AS rating FROM sign_up NATURAL JOIN an_event WHERE username = %s AND end_time BETWEEN \'' + starttime + '\' AND \'' + endtime + "\' GROUP BY event_id, title"
	cursor.execute(query, username)
	data = cursor.fetchall()
	cursor.close()
	return render_template('view_event_ratings.html', logged_in = session['logged_in'], events = data)



@app.route('/remove_account')
def removeacct():
	username = session['username']
	cursor = conn.cursor()
	query = 'DELETE FROM member WHERE username = %s'
	try:
		cursor.execute(query, username)
		conn.commit()
		cursor.close()
	except (pymysql.Error, pymysql.Warning) as e:
		error = "You have too much data in other in the database, please clear that to remove account!"
		return render_template('error.html', logged_in = session['logged_in'], error = error)
	else:
		session.pop('username')
		session.pop('logged_in')
		success = "Account removal sucessful, we are sad to see you go :("
		return render_template('index.html', success = success)

@app.route('/logout')
def logout():
	session.pop('username')
	session.pop('logged_in')
	now = datetime.datetime.now()
	cursor = conn.cursor()
	starttime = "%s-%s-%s %s:%s:%s" % (str(now.year), str(now.month), str(now.day), str(now.hour), str(now.minute), str(now.second))
	endtime =  "%s-%s-%s %s:%s:%s" % (str(now.year), str(now.month), str(now.day+3), str(now.hour), str(now.minute), str(now.second))
	query = 'SELECT * FROM an_event WHERE start_time BETWEEN \'' + starttime + '\' AND \'' + endtime + "\'"
	cursor.execute(query)
	data = cursor.fetchall()
	cursor.close()
	success = 'logged out!'
	return render_template('index.html', events=data, success = success)


app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
