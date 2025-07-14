from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)




class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())




class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())








# --- Customer Model ---
class Customer(db.Model):
    __tablename__ = 'customer'
    CustomerID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Phone = db.Column(db.String(20))
    Address = db.Column(db.Text)
    Cnic = db.Column(db.String(15))


# --- CartItem Model ---
class CartItem(db.Model):
    __tablename__ = 'cart_item'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.CustomerID'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    product = db.relationship('Product')
    customer = db.relationship('Customer')


# --- Order Model ---
class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.CustomerID'))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    customer = db.relationship('Customer')
    order_items = db.relationship('OrderItem', backref='order', lazy=True)


# --- OrderItem Model ---
class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # price at time of order

    product = db.relationship('Product')













