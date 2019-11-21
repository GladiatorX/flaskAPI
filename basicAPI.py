import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
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
    return ''


# Getting specific user 
# public_id used & passed in funct.
@app.route('/user/<public_id>', methods=['GET'])
def get_one_user(public_id):
    return ''

# Creating a new user
@app.route('/user', methods=['POST'])
def create_user():
    return ''    


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