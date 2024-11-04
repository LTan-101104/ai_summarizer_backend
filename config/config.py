import os
import datetime
from dotenv import load_dotenv

#load environment variable
load_dotenv()

#configure the app object before running it
# TODO: config and connect to your host postgreSQL database

class Config:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///summarizer_app.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL_AWS')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_COOKIE_SECURE = True 
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1) #expire after 1 hour
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    DEBUG = True