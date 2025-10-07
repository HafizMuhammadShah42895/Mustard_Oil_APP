
import os
from flask import Flask
from dotenv import load_dotenv
from .models import db
from .admin_routes import admin_bp
from .customer_routes import customer_bp, sum_cart_total, get_product, cart_count
from .extensions import mail  # ✅ Import from extensions

# Load .env file
load_dotenv()

def init_mail(app):
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    mail.init_app(app)

def create_app():
    app = Flask(__name__)
    
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    db.init_app(app)
    init_mail(app)

    # Register template global functions
    app.add_template_global(sum_cart_total, 'sum_cart_total')
    app.add_template_global(get_product, 'get_product')
    app.add_template_global(cart_count, 'cart_count')

    app.register_blueprint(admin_bp)
    app.register_blueprint(customer_bp)

    return app
