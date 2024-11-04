from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_access_cookies
from flask_cors import CORS
from model.models import db, User, Notes
from config.config import Config
from api.summary_model import summarize_text
#TODO: currently there is an error related to your postgre db on AWS, so I decide to temporarily switch to local db
#TODO: the error is "value too long for type character varying(120)"
#refer to https://stackoverflow.com/questions/13485030/strange-postgresql-value-too-long-for-type-character-varying500
#refer to https://stackoverflow.com/questions/26980713/solve-cross-origin-resource-sharing-with-flask to solve the problem with CORS

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173", "supports_credentials": True}})
db.init_app(app)
jwt = JWTManager(app)

@app.route("/test", methods=['GET'], endpoint = "test")
@jwt_required()
def test():
    #a route for testing if the client is already authenticated or not
    return jsonify({"message": "Test route working"}), 200

#!authentication route
@app.route("/register", methods = ['POST'], endpoint = "register")
def register():
    data = request.json
    if not data:
        app.logger.error("No JSON data received")
        return jsonify({"error": "No data provided"}), 400
    if "username" not in data or "password" not in data:
        app.logger.error("Missing username or password in request")
        return jsonify({"error": "Username and password are required"}), 400
    if (User.find_by_username(data["username"])):
        return jsonify("User already existed"), 409
    try:
        User.create_user(username = data["username"], pwd = data["password"])
        app.logger.info(f"User {data['username']} registered succesfully")
        print(f"User {data['username']} registered succesfully")
        return jsonify({"message" : "Register successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error during user registration: {str(e)}")
        db.session.rollback()
        return jsonify({"error": f"Registration Failed: {str(e)}"}), 400

@app.route("/login", methods = ['POST'])
def login():
    try:
        data = request.json
        user : User = User.find_by_username(data["username"])
        input_pw = data["password"]
        if (not user.check_password(input_pw)):
            raise Exception('Invalid credentials')
        access_token = create_access_token(identity=user.id)
        response = jsonify({"message" : "Login sucessfully", "access_token" : access_token})
        return response, 200
    except Exception as e:
        return jsonify({"message" : f"Login Failed: {str(e)}"}), 401

@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    try:
        response = jsonify({"message" : "Logout succesfully"})
        return response, 200
    except Exception as e:
        return jsonify({"message" : f"Logout Failed: {str(e)}"}), 400
    
#!AI summarization route
@app.route("/summarize", methods = ["POST"], endpoint = "summarize_text_call")
@jwt_required()
def summarize_text_call():
    try:
        data = request.json
        temp = summarize_text(data['input_text'])
        print("___DEBUG___")
        res = temp[7:-4]
        print(res)
        print(type(res))
        return jsonify({'result': res}), 200
    except Exception as e:
        return jsonify({"message" : f"Summarize Failed: {str(e)}"}), 400

#!CRUD routes
#will implement further later
@app.route("/get_all", methods = ["GET"], endpoint='get_all')
@jwt_required()
def get_all():
    try:
        current_user = get_jwt_identity() #user.id
        notes = Notes.get_all(current_user)
        return jsonify([{'id' : note.id, 'title' : note.title} for note in notes] ), 200
    except Exception as e:
        return jsonify({'message' : f'Get all notes failed: {str(e)}'}), 400

@app.route("/note", methods = ["POST"], endpoint = "create_new_note")
@jwt_required()
def create_new_note():
    try:
        data = request.json
        current_user = get_jwt_identity()
        res = Notes.add_notes(data["input_title"], current_user)
        return jsonify({'message' : f'Successfully create new notes {str(res)}'}), 200
    except Exception as e:
        return jsonify({'message' : f'Create note failed: {str(e)}'}), 400
    

@app.route("/note/<int:note_id>")
@jwt_required()
def get_specific_note(note_id : int):
    try:
        res : Notes = Notes.get_specific_notes(note_id)
        return jsonify({'id' : note_id, 'title' : res.title}), 200
    except Exception as e:
        return jsonify({'message' : f'Get note failed: {str(e)}'}), 400
    
@app.route("/note", methods = ["DELETE"], endpoint = "delete_note_all")
@jwt_required()
def delete_note_all():
    try:
        Notes.delete_all(get_jwt_identity())
        return jsonify({'message' : f'Successfully delete all nodes'}), 200
    except Exception as e:
        return jsonify({'message' : f'Create note failed: {str(e)}'}), 400

# # Add an error handler for CORS issues
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#     response.headers.add('Access-Control-Allow-Credentials', 'true')
#     return response

if (__name__ == "__main__"):
    with app.app_context():
        db.create_all()
    app.run(debug=True)