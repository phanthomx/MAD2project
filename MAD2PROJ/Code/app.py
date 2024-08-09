from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from cloudinary import config as cloudinary_config
from models import db
from influencer import influencer as influencer_blueprint
from sponcer import sponcer as sponcer_blueprint
from admin import admin as admin_blueprint
from worker import celery_init_app
from celery.schedules import crontab,schedule
from tasks import send_daily_email,generate_monthly_report
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.secret_key = "hello"

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'athenamcgonagall7@gmail.com'
    app.config['MAIL_PASSWORD'] = 'hkvw dsmi bwxb uyjl'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

    cloudinary_config(
        cloud_name='ddfzdi2py',
        api_key='986259854125851',
        api_secret='28xQ1ArAeUMSOurgBLBirOz_nR8'
    )

    db.init_app(app)
    mail.init_app(app)

    app.register_blueprint(influencer_blueprint, url_prefix="/influencer")
    app.register_blueprint(sponcer_blueprint, url_prefix="/sponcer")
    app.register_blueprint(admin_blueprint, url_prefix="/admin")

    @app.route("/")
    def home():
        return render_template("landingpage.html")

    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print("Error creating database tables:", e)


    return app

app = create_app()
celery_app = celery_init_app(app)

@celery_app.on_after_configure.connect
def send_email(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=22, minute=8, day_of_month="1-31/2"),  # Every 2 days
        send_daily_email.s(),
    )
@celery_app.on_after_configure.connect
def send_monthly_report(sender, **kwargs):
        sender.add_periodic_task(
        schedule(30),
        # crontab(hour=22, minute=8, day_of_month="1-31/2"), 
        generate_monthly_report.s(),
        )
    


if __name__ == "__main__":
    app.run(debug=True)
