from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from cloudinary import config as cloudinary_config

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "hello"

    cloudinary_config(
        cloud_name='ddfzdi2py',
        api_key='986259854125851',
        api_secret='28xQ1ArAeUMSOurgBLBirOz_nR8'
    )

    db.init_app(app)
    mail.init_app(app)
    
    return app
