class Config:
    SECRET_KEY = 'your_secret_key'
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://422483_moa:muhammad%40555@mysql-hafizmuhammadshah.alwaysdata.net/hafizmuhammadshah_moa'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'hafizmuhammadshah11@gmail.com'
    MAIL_PASSWORD = 'dujz upaw ucpp rbgo'
    MAIL_DEFAULT_SENDER = 'hafizmuhammadshah11@gmail.com'
    
    # Upload Configuration
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Pagination
    PRODUCTS_PER_PAGE = 6