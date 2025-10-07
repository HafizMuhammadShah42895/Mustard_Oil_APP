
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
    app.config['MAIL_USERNAME'] = 'hafizmuhammadshah11@gmail.com'
    app.config['MAIL_PASSWORD'] = 'dujz upaw ucpp rbgo'
    app.config['MAIL_DEFAULT_SENDER'] = 'hafizmuhammadshah11@gmail.com'
    mail.init_app(app)

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://422483_moa:muhammad%40555@mysql-hafizmuhammadshah.alwaysdata.net/hafizmuhammadshah_moa?charset=utf8mb4&connect_timeout=60&read_timeout=60&write_timeout=60'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {'connect_timeout': 60}
    }
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    app.config['SECRET_KEY'] = 'your_secret_key'

    db.init_app(app)
    init_mail(app)

    # Register template global functions
    app.add_template_global(sum_cart_total, 'sum_cart_total')
    app.add_template_global(get_product, 'get_product')
    app.add_template_global(cart_count, 'cart_count')

    app.register_blueprint(admin_bp)
    app.register_blueprint(customer_bp)

    return app
