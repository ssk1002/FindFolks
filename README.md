# FindFolks

This is a group project for the databases class, coded by Sahir Karani and Sundeep Kaler.

Files and Folders


main.py – Contains all of the Flask and Python code to execute and run the website.
README.md – README file which contains info about the program.
static – Folder containing css, fonts, and javascript files to show front end look and design.
templates – Folder containing all of the HTML files which are to be displayed:
_sidebar.html – Contains the sidebar which allows for navigation of website and access of features.
authorized.html – Contains html which has the feature to view authorized users and authorize/de-authorize users.
create_event.html – Contains html to fill out a form to create events and displays all possible places you can have an event.
create_group.html – Contains html to fill out a form to create a group.
error.html – Returns an error message which can be changed, used mainly for the remove account error.
event_interests.html – Contains html to display a table of all events that match the user's interests.
event_rating.html – Contains html to a form which allows users to rate any event which has already passed.
event_signup.html - Contains html to a form which allows users to sign up for any event with the event ID.
friends_events.html - Contains html to a table which shows all events which friends are going to.
friends.html - Contains html to a table which shows all of the users friends and an option to add or remove friends.
home.html - Contains html to the landing page when users log on, it shows all the events upcoming in the next 3 days and filters groups by interest.
index.html - Contains html to the landing page when users are logged off, it shows all the events upcoming in the next 3 days and filters groups by interest.
interests.html - Contains the html for the with a table of users current interests and allows for addition of interests.
login.html - Contains the html for the login form.
register.html - Contains the html for the registration form of the users.
view_all_events.html - Contains the html with a table of all the events which are taking place on FindFolks.
view_event_ratings.html - Contains the html with a table of the average event rating for events which the user is a member of.
view_join_group.html - Contains the html with tables of all the groups, all of the users groups and a form to join a group.
view_my_events.html - Contains the html with a table of all the events upcoming for the user in the next 3 days.


Queries for Use Cases


1. View public info
SELECT * FROM an_event WHERE start_time BETWEEN \'' + starttime + '\' AND \'' + endtime + "\'"
This query selects all of the events which are in the time now and now + 3 days.


SELECT * FROM interest
This query selects all of the keywords and categories from interests.


SELECT * FROM a_group NATURAL JOIN about WHERE category = %s AND keyword = %s
This query selects all of the groups where the category and keyword match user input.


2. Login
SELECT * FROM member WHERE username = %s and password = %s
This query checks if there is a user with the given credentials.


3. View my upcoming events
SELECT * FROM an_event NATURAL JOIN sign_up WHERE username = %s AND start_time BETWEEN \'' + starttime + '\' AND \'' + endtime + "\'"
This query finds the events which this user is registered for in the next 3 days.


4. Sign up for an event
SELECT * FROM an_event WHERE event_id = %s
This query gets the event where the event id is user input.


SELECT * FROM sign_up WHERE event_id = %s AND username = %s
This query checks to see if the user has signed up already for said event id.


INSERT INTO sign_up VALUES (%s, %s, NULL)
This query inserts the values of the event and username, signing up the user for the event.


5. Search for events of interest
SELECT * FROM an_event NATURAL JOIN organize NATURAL JOIN about WHERE (category, keyword) IN (SELECT category, keyword FROM interested_in WHERE username = %s)
This query searches and finds all of the events organized by groups which have the same interest as the user.


6. Create an event
SELECT * FROM location
This query selects all of the locations.


SELECT * FROM belongs_to WHERE username = %s AND group_id = %s
This query checks if the user in the group or not.


SELECT * FROM location WHERE location_name = %s AND zipcode = %s
This query checks if the location for the event is valid.


INSERT INTO an_event VALUES (NULL, %s, %s, %s, %s, %s, %s)
This query inserts values into the event making the event.


SELECT max(event_id) FROM an_event
This query finds the max event id giving the last event id which was created.


INSERT INTO organize VALUES (%s, %s)
This query adds the event id and group id into organize finalizing the event creation.


7. Rate an event
SELECT * FROM sign_up WHERE username = %s AND event_id = %s
This query checks if the user was signed up for the event.


SELECT * FROM an_event WHERE event_id = %s AND end_time < %s
This query checks if the event time has passed or not.


UPDATE sign_up SET rating = %s WHERE username = %s AND event_id = %s
This query updated the rating if the time has passed.


8. See average ratings
SELECT event_id, title, AVG(rating) AS rating FROM sign_up NATURAL JOIN an_event WHERE username = %s AND end_time BETWEEN \'' + starttime + '\' AND \'' + endtime + "\' GROUP BY event_id, title
This query gets the average rating of the events that the user is a group member of for the last 3 days.


9. See friends’ events
SELECT * FROM sign_up NATURAL JOIN an_event WHERE username IN (SELECT friend_to AS username FROM friend WHERE friend_of = %s)
This query finds the events that the user's friends are a part of.


10. Logout
SELECT * FROM an_event WHERE start_time BETWEEN \'' + starttime + '\' AND \'' + endtime + "\’”
This query is for the home page and gets the event information for public use.


Additional Features


1. Add Friends - This feature allows for the user to add friends


2. Remove Friends - This feature allows for the user to remove friends.


3. Authorize Users - This feature allows for the user to authorize users from the group they are the creator of.


4. De-Authorize Users - This feature allows for the user to de-authorize users from the group they are the creator of.


5. Join Groups - This feature allows for the user to join groups.


6. Create Groups - This feature allows for the user to create groups.


7. Add User Interests - This feature allows users to add their interests.


8. Remove Account - This feature allows for the user to remove their account only there is no data attached with it on other tables.