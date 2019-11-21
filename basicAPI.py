import os
from flask import Flask, request, jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

# This grabs our current directory
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

############################### SETTING UP DB 1st step##################################################
'''
7:30
go to terminal python
from basicAPI import db
db.create_all()
'''
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)


############################### SETTING UP ROUTE 2nd step##################################################
# Getting all user 
@app.route('/user', methods=['GET'])  
def get_all_users():
    # Get all users
    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users' : output})


# Getting specific user 
# public_id used & passed in funct.
@app.route('/user/<public_id>', methods=['GET'])
def get_one_user(public_id):

    #QUERY by public_id SPECIFIC USER only
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'user' : user_data})

# Creating a new user
@app.route('/user', methods=['POST'])
def create_user():
    # Here POSTMAN is sending username and password only
    data = request.get_json()
    
    hashed_password = generate_password_hash(data['password'], method='sha256')
    #public_id and admin is set over here
    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()


    return jsonify({'message' : 'New user created!'})


# Changing user to admin (previlage by setting boolean to true)
# public_id used & passed in funct.
@app.route('/user/<public_id>', methods=['PUT'])
def promote_user(public_id):

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user.admin = True
    db.session.commit()

    return jsonify({'message' : 'The user has been promoted!'})



# public_id used & passed in funct.
@app.route('/user/<public_id>', methods=['DELETE'])                         
def delete_user(public_id):
    
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message' : 'The user has been deleted!'})

#################### SETTING UP AUTHORIZATION using http basic authentcation ##################
#### this will return a TOKEN which is used for every subsequent API request####
@app.route('/login')
def login():
    #Getting auth info from API request
    auth = request.authorization
    '''auth or auth.uname or auth.pass didn't match'''
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
                                #Postman's basic AUTH
    user = User.query.filter_by(name=auth.username).first()

    ''' auth.uname didn't match, user not present'''
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    '''sending token on success'''
    if check_password_hash(user.password, auth.password):
        #token is combination of users public_id +SECRET_KEY __ 30  min token token expiration time
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')})


    ''' auth.pass didn't match, user not present'''
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})


if __name__ == '__main__':
    app.run(debug=True)