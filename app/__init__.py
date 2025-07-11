
from flask import Flask
from .models import db
from .admin_routes import admin_bp
from .customer_routes import customer_bp
from .extensions import mail  # ✅ Import from extensions

def init_mail(app):
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'hafizmuhammadshah11@gmail.com'
    app.config['MAIL_PASSWORD'] = 'dujz upaw ucpp rbgo'  # App-specific password
    app.config['MAIL_DEFAULT_SENDER'] = 'hafizmuhammadshah11@gmail.com'
    mail.init_app(app)

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:muhammad%40555@localhost/mustard_oil'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    app.config['SECRET_KEY'] = 'your_secret_key'

    db.init_app(app)
    init_mail(app)

    app.register_blueprint(admin_bp)
    app.register_blueprint(customer_bp)

    return app
