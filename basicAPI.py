import os
from flask import Flask, request, jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

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



#######################Step 4 : Setting_up Decorator to enforce use of token provided by LOGIN(step3) Route###############
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        #token always needs to be passed as header             ## <==>

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try: 
            #token + SECRET_KEY = __original__ data['public_id']             ## <==>

            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        # current_user is than needs to be passed all ROUTeS that req token access                                                  ## <==>
        return f(current_user, *args, **kwargs)

    return decorated


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
@token_required 
def get_one_user(current_user,public_id):

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

    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user.admin = True
    db.session.commit()

    return jsonify({'message' : 'The user has been promoted!'})



# public_id used & passed in funct.
@app.route('/user/<public_id>', methods=['DELETE'])       
@token_required                  
def delete_user(current_user,public_id):

    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message' : 'The user has been deleted!'})

##################TODO####################
@app.route('/todo',methods=["GET"])
@token_required
def get_all_todos(current_user):
    todos = Todo.query.filter_by(user_id=current_user.id).all()

    output = []

    for todo in todos:
        todo_data = {}
        todo_data['id'] = todo.id
        todo_data['text'] = todo.text
        todo_data['complete'] = todo.complete
        output.append(todo_data)

    return jsonify({'todos' : output})


@app.route('/todo/<todo_id>',methods=["GET"])
@token_required
def get_one_todo(current_user,todo_id):

    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({'message' : 'No todo found!'})

    todo_data = {}
    todo_data['id'] = todo.id
    todo_data['text'] = todo.text
    todo_data['complete'] = todo.complete

    return jsonify(todo_data)    


@app.route('/todo', methods=['POST'])
@token_required
def create_todo(current_user):
    data = request.get_json()

    new_todo = Todo(text=data['text'], complete=False, user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({'message' : "Todo created!"})

@app.route('/todo/<todo_id>',methods=["PUT"])
@token_required
def complete_todo(current_user,todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({'message' : 'No todo found!'})

    todo.complete = True
    db.session.commit()

    return jsonify({'message' : 'Todo item has been completed!'})
@app.route('/todo/<todo_id>', methods=["DELETE"])
@token_required
def delete_todo(current_user,todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({'message' : 'No todo found!'})

    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message' : 'Todo item deleted!'})


#################### 3rd step SETTING UP AUTHORIZATION using http basic authentcation ##################
#### this will return a TOKEN which is used for every subsequent API request###################



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
    '''check_password_hash is default py function to check it against salted pass'''
    if check_password_hash(user.password, auth.password):
        #token is combination of users public_id +SECRET_KEY __ 30  min token token expiration time
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')})


    ''' auth.pass didn't match, user not present'''
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})


if __name__ == '__main__':
    app.run(debug=True)