from flask import Flask
from .extensions import mongo
from app.webhook.routes import webhook


# Creating our flask app
def create_app(config_object='app.settings'):

    app = Flask(__name__)
    
    app.config.from_object(config_object)       # configuring objects from settings
    
    mongo.init_app(app)
    
    # registering all the blueprints
    app.register_blueprint(webhook)

    return app
