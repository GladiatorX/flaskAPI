import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


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
    return ''

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
    return ''


# public_id used & passed in funct.
@app.route('/user/<public_id>', methods=['DELETE'])                         
def delete_user(current_user, public_id):
    return ''



if __name__ == '__main__':
    app.run(debug=True)