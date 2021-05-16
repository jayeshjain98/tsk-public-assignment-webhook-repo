from flask import Flask
from .extensions import mongo
from app.webhook.routes import webhook
from flask_pymongo import PyMongo



# Creating our flask app
def create_app(config_object='app.settings'):

    app = Flask(__name__)
    
    # app.config['MONGO_DBNAME'] = 'github_actions'
    # app.config['MONGO_URI'] = 'mongodb://localhost:27017/github_actions'
    app.config.from_object(config_object)
    
    # mongo = PyMongo(app)
    
    # registering all the blueprints
    mongo.init_app(app)
    
    app.register_blueprint(webhook)

    return app
