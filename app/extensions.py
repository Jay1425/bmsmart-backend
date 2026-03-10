"""
Flask extensions initialization.
Extensions are initialized here and then attached to the app in the factory.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Initialize extensions
db = SQLAlchemy()
cors = CORS()
jwt = JWTManager()
