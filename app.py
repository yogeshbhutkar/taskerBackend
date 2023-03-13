from flask import *
import psycopg2
from urllib.parse import urlparse
from flask_cors import CORS, cross_origin
from json import load

#Database connectivity

#Establish connection with postgres db.

result = urlparse("postgres://flask_i22d_user:XLFsNLAqUGI8CUAzUqrRAfjQ1dEojtEU@dpg-cg5csdfdvk4pls4d5e30-a.singapore-postgres.render.com/flask_i22d")
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port
conn = psycopg2.connect(database=database,
                        host=hostname,
                        user=username,
                        password=password,
                        port=port)

conn.autocommit = True

cursor = conn.cursor()


################  Tasks relation  ##########################
def createTasksRelation():
    cursor.execute("create table userTasks(id serial PRIMARY KEY, todoItem varchar(20) unique not null, completed boolean not null, created_at timestamptz NOT NULL DEFAULT now(), userID int FOREIGN KEY (userID) REFERENCES users(id))")

################  User Relation  ###########################
def createUserRelation():
    cursor.execute("create table users(id serial PRIMARY KEY, username varchar(20) unique not null, password varchar(20) not null)")


####################  Tasks Related methods  ####################


def fetchData():
    cursor.execute("select * from userTasks")
    data = []
    for item in cursor.fetchall():
        json = {"id":item[0], "item":item[1], "completed":item[2], "created_at": item[3], "user_id":item[4]}
        data.append(json)
    return {"data": data}

def insertDB(item, completed, userID):
    cursor.execute("""INSERT INTO userTasks (todoItem, completed, userID) VALUES (%s,%s,%s)""", (item, completed,userID))
    conn.commit()
    return fetchData()

def updateDB(completed, id):
    cursor.execute("""UPDATE userTasks SET completed = %s WHERE id = %s""", (completed, id))
    conn.commit()
    return fetchData()

def deleteData(id):
    cursor.execute(f'DELETE FROM userTasks WHERE ID = {id}')
    conn.commit()
    return fetchData()

################  User related methods  ##############


def fetchUserData():
    cursor.execute("select * from users")
    data = []
    for item in cursor.fetchall():
        json = {"id":item[0], "username":item[1], "password":item[2], }
        data.append(json)
    return {"data": data}

def insertUser(username, password):
    cursor.execute("""INSERT INTO users (username, password) VALUES (%s,%s)""", (username, password))
    conn.commit()
    return fetchUserData()

def updateUser(password, id):
    cursor.execute("""UPDATE users SET password = %s WHERE id = %s""", (password, id))
    conn.commit()
    return fetchUserData()


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == '__main__':
    app.run(debug=False, port=5000)

@app.route('/api/dashboard', methods=["GET", "POST", "PUT", "DELETE"])
@cross_origin()
def getAllPosts():
    if (request.method=="POST"):
        try:
            return insertDB(request.json['item'], request.json['completed'], request.json['user_id'])
        except Exception as e :
            print(e)
            return jsonify({"error":"Cannot post the data, check params, check log"})
            
    if (request.method=="PUT"):
        try:
            return updateDB(request.json['completed'], request.json['id'])
        except Exception as e :
            print(e)
            return jsonify({"error":"Cannot update the given element, check params, check logs"})
        
    if (request.method=="GET"):
        try:
            return jsonify(fetchData())
        except Exception as e :
            print(e)
            return jsonify({"error":"cannot get elements, check server, check logs"})

    if (request.method=="DELETE"):
        try:
            return deleteData(request.json['id'])
        except Exception as e :
            print(e)
            return jsonify({"error":"Cannot delete the given element, check params, check logs"})

@app.route('/api/dashboard/users', methods=["GET", "POST", "PUT"])
@cross_origin()
def getAllUsers():
    try:
        if (request.method=="POST"):
            return insertUser(request.json['username'], request.json['password'])
    except Exception as e :
            print(e)
            return jsonify({"error":"Cannot post the given element, check params, check logs"})

    if (request.method=="PUT"):
        try:
            return updateUser(request.json['password'], request.json['id'])
        except Exception as e :
            print(e)
            return jsonify({"error":"Cannot update the given element, check params, check logs"})

    if (request.method=="GET"):
        try:
            return jsonify(fetchUserData())
        except Exception as e :
            print(e)
            return jsonify({"error":"Cannot get the data, check server, check logs"})