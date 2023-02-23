######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
from flask_login import current_user
from operator import itemgetter

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Simon200560'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		firstName=request.form.get('firstName')
		lastName=request.form.get('lastName')
		dob=request.form.get('dob')
		hometown=request.form.get('hometown')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register', supress='True'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (email, password, fname, lname, dob, hometown) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(email, password, firstName, lastName, dob, hometown)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

def getUserFirstName(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT fname FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()[0]

def getUserLastName(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT lname FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()[0]

def getUserDateOfBirth(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT dob FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()[0]

def getUserHometown(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT hometown FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()[0]

def getUsersPhotosFromAlbum(aid):
	cursor = conn.cursor()
	cursor.execute("SELECT P.imgdata, P.picture_id, P.caption FROM Pictures P, Albums A WHERE A.album_id = '{0}' AND A.album_id = P.album_id".format(aid))
	return cursor.fetchall()

def getUsersFriends(uid):
	cursor = conn.cursor()
	cursor.execute(f"SELECT U.user_id, U.fname, U.lname FROM Users U, Friendship F WHERE F.UID1 = {uid} AND F.UID2 = U.user_id")
	return cursor.fetchall()

def getUserEmailFromUid(uid):
	cursor = conn.cursor()
	cursor.execute(f"SELECT email FROM Users WHERE user_id = {uid}")
	return cursor.fetchone()

#returns (user_id, contribution_score, fname, lname)
def getMostContributedUser():
	cursor = conn.cursor()
	cursor.execute("SELECT P.user_id, count(*), U.fname, U.lname FROM Pictures P, Users U WHERE U.user_id = P.user_id GROUP BY P.user_id ORDER BY count(*) DESC LIMIT 10")
	pictureScores = cursor.fetchall()
	cursor = conn.cursor()
	cursor.execute("SELECT C.user_id, count(*), U.fname, U.lname FROM Comments C, Users U WHERE U.user_id = C.user_id GROUP BY C.user_id ORDER BY count(*) DESC LIMIT 10")
	commentScores = cursor.fetchall()
	scoreDict = {}
	for p in pictureScores:
		if p[0] not in scoreDict:
			scoreDict[p[0]] = [0, p[2], p[3]]
		scoreDict[p[0]][0] += p[1]
	for c in commentScores:
		if c[0] not in scoreDict:
			scoreDict[c[0]] = [0, c[2], c[3]]
		scoreDict[c[0]][0] += c[1]
	scoreDict = dict(sorted(scoreDict.items(), key = itemgetter(1), reverse=True))
	return [(k, v[0], v[1], v[2]) for k, v in scoreDict.items()]
	
def getMostPopularTags():
	cursor = conn.cursor()
	cursor.execute("SELECT tname, count(*) FROM Tagged GROUP BY tname ORDER BY count(*) DESC LIMIT 3")
	return cursor.fetchall()


@app.route('/profile')
@flask_login.login_required
def protected():
	print(getMostContributedUser())
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('hello.html', fname=getUserFirstName(uid), lname=getUserLastName(uid), dob=getUserDateOfBirth(uid), \
			hometown=getUserHometown(uid), email=flask_login.current_user.id, message="Here's your profile", \
			albums=getAlbumNames(uid), friends=getUsersFriends(uid),
			uid=uid, ownUser="True")

@app.route('/profile/<arg0>/')
def view_profile(arg0):
	print(arg0)
	return render_template('hello.html', fname=getUserFirstName(arg0), lname=getUserLastName(arg0), dob=getUserDateOfBirth(arg0), \
			hometown=getUserHometown(arg0), email=getUserEmailFromUid(arg0)[0], \
			albums=getAlbumNames(arg0), friends=getUsersFriends(arg0))

def getAlbumNameFromAid(aid):
	cursor = conn.cursor()
	cursor.execute("SELECT aname FROM Albums WHERE album_id = '{0}'".format(aid))
	return cursor.fetchall()

@app.route('/profile/<arg0>/<arg1>/')
def view_album(arg0, arg1):
	if current_user.is_authenticated:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('hello.html', fname=getUserFirstName(uid), lname=getUserLastName(uid), dob=getUserDateOfBirth(uid), \
				hometown=getUserHometown(uid), email=flask_login.current_user.id, \
				aname=getAlbumNameFromAid(arg1)[0][0], photos=getUsersPhotosFromAlbum(arg1), base64=base64)
	else:
		return render_template('hello.html', fname="Visitor", \
				aname=getAlbumNameFromAid(arg1)[0][0], photos=getUsersPhotosFromAlbum(arg1), \
				base64=base64)

def getSpecificPhoto(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE picture_id = '{0}'".format(pid))
	return cursor.fetchone()

def getUserFullNameWithPid(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT U.fname, U.lname FROM Users U, Pictures P WHERE P.picture_id = '{0}' AND P.user_id = U.user_id".format(pid))
	return cursor.fetchone()

# def getUserFullNameWithCid(cid):
# 	cursor = conn.cursor()
# 	cursor.execute("SELECT U.fname, U.lname FROM Users U, Comments C WHERE C.comment_id = '{0}' AND C.user_id = U.user_id".format(cid))
# 	return cursor.fetchone()

def getPhotosComments(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT C.ctext, C.cdate, U.fname, U.lname FROM Comments C, Users U WHERE C.picture_id = '{0}' AND C.user_id = U.user_id".format(pid))
	return cursor.fetchall()

def getNumLikesPhoto(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(*) as count FROM Likes WHERE picture_id = '{0}'".format(pid))
	return cursor.fetchall()

def isPhotoLiked(uid, pid):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(*) as count FROM Likes WHERE picture_id = '{0}' AND user_id = '{1}'".format(pid, uid))
	return cursor.fetchall()

def getPhotosTags(pid):
	cursor = conn.cursor()
	cursor.execute(f"SELECT tname FROM Tagged WHERE picture_id = '{pid}'")
	return cursor.fetchall()

#arg2 = pid #arg1 = aid
@app.route('/profile/<arg0>/<arg1>/<arg2>', methods=['GET', 'POST'])
def view_photo(arg0, arg1, arg2):
	fullname = getUserFullNameWithPid(arg2)
	fname = fullname[0]
	lname = fullname[1]
	name = fname + " " + lname
	tags = getPhotosTags(arg2)
	comments = getPhotosComments(arg2)
	likes = getNumLikesPhoto(arg2)
	print(tags)
	if current_user.is_authenticated:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		if isPhotoLiked(uid, arg2)[0][0] == 1:
			likeOrUnlike = 'Unlike'
		else:
			likeOrUnlike = 'Like'

		if request.method == 'GET':
			return render_template('viewPhoto.html', user=name, photo=getSpecificPhoto(arg2),\
				comments=comments, likes=likes[0][0], tags=tags, likeOrUnlike=likeOrUnlike, base64=base64)
		else:
			if 'commentButton' in request.form and request.form['commentButton'] == 'Upload':
				ctext = request.form.get('comment')
				cursor = conn.cursor()
				cursor.execute('''INSERT INTO Comments (ctext, user_id, picture_id) VALUES (%s, %s, %s)''', (ctext, uid, arg2))
				conn.commit()
				comments = getPhotosComments(arg2)
				return render_template('viewPhoto.html', user=name, photo=getSpecificPhoto(arg2), \
					action=f'/profile/{arg0}/{arg1}/{arg2}', tags=tags, comments=comments, likes=likes[0][0], likeOrUnlike=likeOrUnlike, base64=base64)
			
			elif request.form['likeOrUnlike'] == 'Like':
				cursor = conn.cursor()
				cursor.execute('''INSERT INTO Likes (user_id, picture_id) VALUES (%s, %s)''', (uid, arg2))
				conn.commit()
				likes = getNumLikesPhoto(arg2)
				return render_template('viewPhoto.html', user=name, photo=getSpecificPhoto(arg2), \
					action=f'/profile/{arg0}/{arg1}/{arg2}', tags=tags, comments=comments, likes=likes[0][0], likeOrUnlike='Unlike', base64=base64)
			
			elif request.form['likeOrUnlike'] == 'Unlike':
				cursor = conn.cursor()
				cursor.execute('''DELETE FROM Likes WHERE user_id = '{0}' AND picture_id = '{1}' '''.format(uid, arg2))
				conn.commit()
				likes = getNumLikesPhoto(arg2)
				return render_template('viewPhoto.html', user=name, photo=getSpecificPhoto(arg2), \
					action=f'/profile/{arg0}/{arg1}/{arg2}', tags=tags, comments=comments, likes=likes[0][0], likeOrUnlike='Like', base64=base64)
	else:
		if request.method == 'GET':
			return render_template('viewPhoto.html', user=name, photo=getSpecificPhoto(arg2),\
				comments=comments, tags=tags, likes=likes[0][0], visitor="True", base64=base64)	

def isPhotoLiked(uid, pid):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(*) FROM Likes WHERE picture_id = '{0}' AND user_id = '{1}'".format(pid, uid))
	return cursor.fetchall()

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def getAlbumIdFromAlbumName(aname, uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id FROM Albums WHERE user_id = '{0}' AND aname = '{1}'".format(uid, aname))
	return cursor.fetchone()[0]

def getAlbumNames(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT aname, album_id FROM Albums WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()

def parseTagList(tl):
	lowercase = tl.lower()
	taglist = lowercase.split()
	return taglist
	

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		album_name = request.form.get('album_name')
		tagList = parseTagList(request.form.get('tags'))
		photo_data =imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption, album_id) VALUES (%s, %s, %s, %s)''', (photo_data, uid, caption, getAlbumIdFromAlbumName(album_name, uid)))
		for t in tagList:
			cursor.execute(f"INSERT IGNORE INTO Tags (tname) VALUES ('{t}')")
			#how to get image id from inserted picture?
			cursor.execute("SELECT MAX(picture_id) FROM Pictures")
			picture_id = cursor.fetchone()
			print(picture_id)
			cursor.execute(f"INSERT IGNORE INTO Tagged (picture_id, tname) VALUES ({picture_id[0]}, '{t}')")
			conn.commit()

		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		albumNameList = getAlbumNames(uid)
		print(albumNameList)
		return render_template('upload.html', anames=albumNameList)
#end photo uploading code

def findUsersWithEmail(email):
	cursor = conn.cursor()
	cursor.execute(f"SELECT fname, lname, user_id FROM Users WHERE email = '{email}'")
	return cursor.fetchall()

def addFriend(uid1, uid2):
	cursor = conn.cursor()
	cursor.execute(f"INSERT INTO Friendship (UID1, UID2) VALUES ({uid1}, {uid2})")
	cursor.execute(f"INSERT INTO Friendship (UID1, UID2) VALUES ({uid2}, {uid1})")
	conn.commit()

@app.route('/addFriends', methods=['GET', 'POST'])
@flask_login.login_required
def search_friends():
	if request.method == 'POST':
		if 'searchButton' in request.form and request.form['searchButton'] == 'Search':
			searchUid = request.form.get('uSearch')
			searchResult = findUsersWithEmail(searchUid)
			print(searchResult)
			return render_template('addFriends.html', searchResult=searchResult)
	else:
		return render_template('addFriends.html')
	
@app.route('/addFriends/<arg1>/', methods=['GET', 'POST'])
@flask_login.login_required
def add_friends(arg1):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		try:
			addFriend(uid, arg1)
		except:
			return render_template('addFriends.html', message="Invalid user")
		return render_template('addFriends.html', message="Friend added!")
	else:
		return render_template('addFriends.html')

def isAlbumUnique(aname, user_id):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT A.aname FROM Albums A, Users U WHERE A.aname = '{0}' AND U.user_id = '{1}'".format(aname, user_id)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

@app.route('/createAlbum', methods=['GET', 'POST'])
@flask_login.login_required
def createAlbum():
	if request.method == 'POST':
		try:
			uid = getUserIdFromEmail(flask_login.current_user.id)
			albumname=request.form.get('albumname')
		except:
			print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
			return flask.redirect(flask.url_for('createAlbum'))
		cursor = conn.cursor()
		test =  isAlbumUnique(albumname, uid)
		if test:
			cursor.execute('''INSERT INTO Albums (aname, user_id) VALUES (%s, %s)''', (albumname, uid))
			conn.commit()
			return render_template('createAlbum.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid), base64=base64)
		#The method is GET so we return a  HTML form to upload the a photo.
		else:
			return render_template('createAlbum.html')
	else:
		return render_template('createAlbum.html')

def getUsersPhotosFromTag(tname):
	cursor = conn.cursor()
	cursor.execute("SELECT P.imgdata, P.picture_id, P.caption, P.user_id, P.album_id FROM Pictures P, Tagged T WHERE T.tname = '{0}' AND T.picture_id = P.picture_id".format(tname))
	return cursor.fetchall()

@app.route('/viewTag/<arg0>/')
def viewPhotosWithTag(arg0):
	return render_template('viewTag.html', tag=arg0, photos=getUsersPhotosFromTag(arg0), base64=base64)


@app.route('/searchTag', methods=['GET', 'POST'])
@flask_login.login_required
def search_friends():
	if request.method == 'POST':
		return render_template('viewTag.html')
	else:
		return render_template('searchTag.html')

#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('homepage.html', message='Welecome to Photoshare', leaderboard=getMostContributedUser(), \
			popularTags=getMostPopularTags())


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
