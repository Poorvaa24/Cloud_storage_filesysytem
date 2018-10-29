from flask import Flask, jsonify, request, json, render_template, make_response, redirect, flash
from flask_mysqldb import MySQL
from datetime import datetime
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from werkzeug.utils import secure_filename
import boto3
import os

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'MYSQL_DB_HOST_NAME'
app.config['MYSQL_USER'] = 'MYSQL_USER'
app.config['MYSQL_PASSWORD'] = 'MYSQL_PASSWORD'
app.config['MYSQL_DB'] = 'MYSQL_DB'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['JWT_SECRET_KEY'] = 'JWT_SECRET_KEY'


mysql = MySQL(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

CORS(app)

session = boto3.Session(aws_access_key_id='AWS_ACCESS_KEY_ID', aws_secret_access_key='AWS_SECRET_ACCESS_KEY', region_name='us-west-1')
bucketName = 'BUCKET_NAME'
cf_url = 'CLOUDFRONT_DOMAIN'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/users/register', methods=['POST'])
def register():
	first_name = request.get_json()['first_name']
	last_name = request.get_json()['last_name']
	email = request.get_json()['email']
	
	bPresent = IsUserAlreadyPresent(email)
	print 'User Present = ',bPresent;
	
	if bPresent == True:
		print 'user already exist';
		return jsonify({'message': 'User Already Exists', 'success': 'false'})
	else:
		password = bcrypt.generate_password_hash(request.get_json()['password']).decode('utf-8')
		created = datetime.today()
		role = 'user'
		
		InsertUserToDB(first_name, last_name, email, password, created, role)
		if role == 'user':
			createS3UserFolder(email)
		
		result = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': password,
        'created': created
		}
		return jsonify({'result': result, 'message': 'Registration Successful', 'success': 'true'})

@app.route('/users/login', methods=['POST'])
def login():
	cur = mysql.connection.cursor()
	email = request.get_json()['email']
	password = request.get_json()['password']
	result = ""
	row_count = cur.execute("SELECT * FROM users where email = '" + str(email) + "'")
	print '*****************************************';
	print '******Row Count  = ',row_count;
	print '*****************************************';
	
	if row_count == 0:
		return jsonify({'message': 'Invalid username and password', 'success':'false'})
		
	rv = cur.fetchone()
	if bcrypt.check_password_hash(rv['password'], password):
		access_token = create_access_token(
            identity={
                'first_name': rv['first_name'],
                'last_name': rv['last_name'],
                'email': rv['email'],
				'role': rv['role']
            })
		#result = access_token;
		result = jsonify({'token': access_token, 'role':rv['role'], 'message':'Login Successful','success':'true'})
	else:
		result = jsonify({'message': 'Invalid username and password', 'success':'false'})
	return result

@app.route('/users', methods=['GET'])
def getUsers():
	userList = ListofUsers()
	return jsonify({'users': userList})
	
@app.route('/users/<email>', methods = ['DELETE'])
def removeUser(email):
	print email;
	DeleteUserFromDB(email)
	DeleteFilesofUserFromDB(email)
	DeleteFolderAndFiles(email)
	return json.dumps({'status': 'success', 'message': 'User deleted'})

@app.route('/files', methods = ['GET'])
def getFiles():
	fileList = []
	if 'email' in request.args:
		email = request.args.get('email')
		print 'email is '+ email
		#fileList = ListofFilesInFolderFromS3(email)
		fileList = ListofFileInFolderFromDB(email)
		
	else:
		#fileList = ListofAllFilesFromS3()
		fileList = ListofAllFilesFromDB()
		
	return json.dumps({'status' : 'success', 'files': fileList })
	
@app.route('/files', methods = ['POST'])
def addFile():
	if 'file' not in request.files:
		print 'No file part'
		flash('No file part')
		return redirect(request.url)
		
	file = request.files['file'];
	if file.filename == '':
		print 'no selected file'
		flash('No selected file')
		return redirect(request.url)
		
	if file:
		filename = secure_filename(file.filename)
		srcFileName = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		file.save(srcFileName)	
		
		print filename;
		print srcFileName;
		
		email = request.form['email'];
		description = request.form['description']
		size = os.path.getsize(srcFileName);
				
		print 'size of file = ' + str(size);
		
		bPresent  = IsFileAlreadyPresent(filename, email)
		print 'File present = ',bPresent;
		
		destFileName = email + '/' + filename
		UploadFileToS3(srcFileName, destFileName)
		os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		
		if bPresent == False:	
			InsertFileToDB(filename, email, description, str(size))
			return json.dumps({'status' : 'success', 'message': 'file added'})
		else:
			UpdateFileInDB(filename, email, description, str(size))
			return json.dumps({'status' : 'success', 'message': 'file alredy Exist'})
		
		

@app.route('/files', methods = ['PUT'])
def updateFile():
	print 'Updating  File '
	body_data = request.get_json()
	filename = body_data.get('filename')
	description = body_data.get('description')
	email = body_data.get('email')
	size = body_data.get('size')
	print filename;
	print description;
	print email;
	print size;
	UpdateFileInDB(filename, email, description, size)
	return json.dumps({'status': 'success', 'message': 'file updated'})

@app.route('/files', methods = ['DELETE'])
def removeFile():
	email = ''
	filename = ''	
	if 'email' in request.args:
		email = request.args.get('email')
		
	if 'filename' in request.args:
		filename = request.args.get('filename')
	
	print 'email is ' + email
	print 'Delete file name is '+ filename
	
	fullFilePath = email + '/' + filename
	DeleteFileFromS3(fullFilePath)
	DeleteFileFromDB(filename, email)
	return json.dumps({'status': 'success', 'message': 'file deleted'})
	
def createS3UserFolder(folderName):
	print 'creating S3 folder for user ' + folderName
	s3 = session.client('s3')
	s3.put_object(ACL='public-read-write', Bucket=bucketName, Key= folderName + '/')
	
def ListofFilesInFolderFromS3(folderName):
	folderName = folderName + '/'
	print 'list of files in folder ' + folderName
	s3 = session.client('s3')
	keys = s3.list_objects_v2(Bucket=bucketName, Prefix=folderName, StartAfter=folderName)		
	fileList = []	
	if 'Contents' in keys:		
		for key in keys['Contents']:
			name = key['Key'].split('/')[1]
			date = key['LastModified']
			size = key['Size']
			#url = '{}/{}/{}'.format(s3.meta.endpoint_url, bucketName, key['Key'])
			url = '{}/{}'.format(cf_url, key['Key'])
			newFile= {
			'name': name,
			'date': date,
			'size': size,
			'url': url
			}
			fileList.append(newFile)
	return fileList;

def ListofAllFilesFromS3():
	print 'List of All files in Bucket'
	s3 = session.client('s3')
	keys = s3.list_objects(Bucket=bucketName)	
	fileList = []
	if 'Contents' in keys:		
		for key in keys['Contents']:
			name = key['Key']
			date = key['LastModified']
			size = key['Size']
			#url = '{}/{}/{}'.format(s3.meta.endpoint_url, bucketName, name)
			url = '{}/{}'.format(cf_url, name)
			newFile= {
			'name': name,
			'date': date,
			'size': size,
			'url': url
			}
			fileList.append(newFile)
	return fileList

def DeleteFileFromS3(filename):
	print 'Deleting file ' + filename
	s3 = session.client('s3')
	s3.delete_object(Bucket= bucketName, Key= filename)

def DeleteFolderAndFiles(folderName):
	print 'delete all files in folder From S3'
	s3 = session.client('s3')
	folderName = folderName + '/'
	objects_to_delete = s3.list_objects(Bucket=bucketName, Prefix = folderName)
	if 'Contents' in objects_to_delete:
		delete_keys = {'Objects' : []}
		delete_keys['Objects'] = [{'Key' : k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]
		print delete_keys['Objects']
		s3.delete_objects(Bucket=bucketName, Delete=delete_keys)


def UploadFileToS3(srcFile, destFile):
	print 'uploading file ';
	print 'src ' + srcFile;
	print 'destination ' + destFile; 
	
	s3 = session.client('s3')
	s3.upload_file(srcFile, bucketName, destFile, ExtraArgs={'ACL': 'public-read'})

def InsertFileToDB(filename, email, description, size):
	print 'Insert File entry in files db'
	cur = mysql.connection.cursor()	
	created = datetime.today();
	modified = created;
	cur.execute(
        "INSERT INTO files (filename, created, modified, description, size, email) VALUES ('"
        + str(filename) + "','" + str(created) + "','" + str(modified) +
        "','" + str(description) + "','" + str(size) + "','" + str(email) + "')")
	mysql.connection.commit()	
	
def DeleteFileFromDB(filename, email):
	print 'Delete File entry in files db'
	cur = mysql.connection.cursor()			
	cur.execute("DELETE FROM files where filename = '" + str(filename) + "' AND email = '" + str(email) + "'")
		
	mysql.connection.commit()	

def ListofFileInFolderFromDB(email):
	print 'List of file in folder from DB'
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM files where email = '" + str(email) + "'")
	data = cur.fetchall();
	s3 = session.client('s3')
	fileListDB = []
	for row in data:
		newFile = {
		'email': row['email'],
		'filename': row['filename'],
		'created': row['created'],
		'modified': row['modified'],
		'size': row['size'],
		'description': row['description'],
		#'url': '{}/{}/{}/{}'.format(s3.meta.endpoint_url, bucketName, email, row['filename'])
		'url': '{}/{}/{}'.format(cf_url, email, row['filename'])
		}
		fileListDB.append(newFile);
	print fileListDB
	return fileListDB

def ListofAllFilesFromDB():
	print 'List of All files from DB'
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM files")
	data = cur.fetchall();
	s3 = session.client('s3')
	fileListDB = []
	for row in data:
		newFile = {
		'email': row['email'],
		'filename': row['filename'],
		'created': row['created'],
		'modified': row['modified'],
		'size': row['size'],
		'description': row['description'],
		#'url': '{}/{}/{}/{}'.format(s3.meta.endpoint_url, bucketName, row['email'], row['filename'])
		'url': '{}/{}/{}'.format(cf_url, row['email'], row['filename'])
		}
		fileListDB.append(newFile);
	print fileListDB
	return fileListDB

def UpdateFileInDB(filename, email, description, size):
	print 'Update File description in DB'
	modified = datetime.today();
	cur = mysql.connection.cursor()			
	cur.execute("UPDATE files SET description = '" + str(description) + "', modified = '" + str(modified) + "', size = '" + str(size) + "' where filename = '" + str(filename) + "' AND email = '" + str(email) + "'")
		
	mysql.connection.commit()	

def IsFileAlreadyPresent(filename, email):
	print 'Check File Already Exist For this User'
	cur = mysql.connection.cursor()	
	cur.execute("SELECT COUNT(*) AS COUNT FROM files where email = '" + str(email) + "' AND filename = '" + str(filename) + "'" )
	row = cur.fetchone()
	row_count = int(row['COUNT'])
	print row_count;
	print '\n';
	
	if row_count > 0:
		return True;
	else:
		return False;
	
def ListofUsers():
	print 'List of users from DB'
	role = 'user';
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM users where role = '" + str(role) + "'" )
	data = cur.fetchall();
	userList = []
	for row in data:
		newUser = {
		'first_name': row['first_name'],
		'last_name': row['last_name'],
		'email': row['email'],
		'created': row['created']
		}
		userList.append(newUser);
	print userList
	return userList

def DeleteUserFromDB(email):
	print 'Delete user from Users DB'
	cur = mysql.connection.cursor()			
	cur.execute("DELETE FROM users where email = '" + str(email) + "'")		
	mysql.connection.commit()		

def DeleteFilesofUserFromDB(email):
	print 'Delete all files of this user from files DB'
	cur = mysql.connection.cursor()			
	cur.execute("DELETE FROM files where email = '" + str(email) + "'")		
	mysql.connection.commit()		

def IsUserAlreadyPresent(email):
	print 'Check User Already Registered'
	cur = mysql.connection.cursor()	
	cur.execute("SELECT COUNT(*) AS COUNT FROM users where email = '" + str(email) + "'" )
	row = cur.fetchone()
	row_count = int(row['COUNT'])
	print row_count;
	print '\n';
	
	if row_count > 0:
		return True;
	else:
		return False;

def InsertUserToDB(first_name, last_name, email, password, created, role):
	print 'Insert User into Database'
	cur = mysql.connection.cursor()
	cur.execute( "INSERT INTO users (first_name, last_name, email, password, created, role) VALUES ('" + str(first_name) + "','" + str(last_name) + "','" + str(email) +
		"','" + str(password) + "','" + str(created) + "','" + str(role) + "')")
	mysql.connection.commit()
	
if __name__ == '__main__':
    app.run(debug=True)
