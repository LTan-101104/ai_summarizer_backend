from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
db = SQLAlchemy()

#parent model
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique = True, nullable = False)
    password = db.Column(db.String(255), nullable = False) #hashed password
    notes = db.relationship('Notes', backref = 'user', lazy = True, uselist = True) # set useList meaning that this is a 1-to-many relationship

    @classmethod
    def find_by_username(cls, username : str):
        return cls.query.filter_by(username = username).first() #return 404 if not found username
    
    @classmethod
    def create_user(cls, username: str, pwd: str):
        newUser = cls(username = username, password = generate_password_hash(pwd))
        db.session.add(newUser)
        db.session.commit()
        return newUser

    def check_password(self, password: str):
        return check_password_hash(self.password, password)
    

#notes model, record usage history of users
class Notes(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(500), nullable = False) #title of the converstaion with AI
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    @classmethod
    #whichever called this will need to pass the user_id of the current user who is adding
    #TODO: try to also add the current datetime in this method
    #note that there might be some error giving a datetime value directly to flask sql, refer to https://stackoverflow.com/questions/47717840/format-db-datetime-values-automatically-in-flask-sqlalchemy
    def add_notes(cls, input_title, input_userid):
        todo = cls(title = input_title, user_id = input_userid)
        db.session.add(todo)
        db.session.commit()
        return todo

    @classmethod
    def get_all(cls, input_userid):
        return cls.query.filter_by(user_id = input_userid).all()
    
    @classmethod
    def delete_all(cls, input_userid):
        notes_so_far = cls.query.filter_by(user_id = input_userid).all()
        for note in notes_so_far:
            db.session.delete(note)
        db.session.commit()
        print("Successfully clear the history")

    @classmethod
    def get_specific_notes(cls, input_note_id : int):
        res = cls.query.filter_by(id = input_note_id).first()
        if not res:
            raise Exception("Not Found")
        return res
    
    


