
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import random
from .models import db, Product, ContactMessage, Customer , CartItem , Order , OrderItem 
from .extensions import mail
from flask_mail import Message
from app.token import generate_reset_token, verify_reset_token

customer_bp = Blueprint('customer_bp', __name__)

# -------------------- Home / Products ----------------------






@customer_bp.route('/', endpoint='home')
def index():
    products = Product.query.all()
    customer_id = session.get('customer_id')

    orders = []
    if customer_id:
        orders = Order.query.filter_by(customer_id=customer_id).all()

    return render_template('index.html', products=products, orders=orders)





# @customer_bp.route('/products')
# def customer_products():
#     products = Product.query.all()
#     return render_template('customer_products.html', products=products)



@customer_bp.route('/products')
def customer_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    pagination = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=6)
    products = pagination.items

    return render_template('customer_products.html', products=products, pagination=pagination, search=search)



# -------------------- Contact Form -------------------------

@customer_bp.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        flash('All fields are required.', 'danger')
        return redirect(url_for('customer_bp.home') + '#contact')

    new_message = ContactMessage(name=name, email=email, message=message)
    db.session.add(new_message)
    db.session.commit()

    try:
        # Message to Admin
        msg_to_you = Message(
            subject='New Contact Message from Website',
            sender='hafizmuhammadshah11@gmail.com',
            recipients=['hafizmuhammadshah11@gmail.com'],
            reply_to=email
        )
        msg_to_you.body = f"""
        New message from:

        Name: {name}
        Email: {email}
        Message: {message}
        """
        mail.send(msg_to_you)

        # Thank You to Customer
        thank_you = Message(
            subject='Thank You for Contacting Us!',
            sender='hafizmuhammadshah11@gmail.com',
            recipients=[email]
        )
        thank_you.body = f"""
        Dear {name},

        Thank you for reaching out! We've received your message.

        Message: {message}

        Regards,
        Pure Mustard Oil Team
        """
        mail.send(thank_you)

        flash('Your message has been sent successfully!', 'success')

    except Exception as e:
        flash('Failed to send email. Please try again later.', 'danger')
        print(str(e))

    return redirect(url_for('customer_bp.home') + '#contact')

# -------------------- Signup / Verify Email ----------------------

@customer_bp.route('/customer_signup', methods=['GET', 'POST'])
def customer_signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        address = request.form.get('address')
        cnic = request.form.get('cnic')

        # Uniqueness checks
        if Customer.query.filter_by(Email=email).first():
            flash("Email already exists.", "danger")
            return render_template('customer_signup.html')

        if Customer.query.filter_by(Phone=phone).first():
            flash("Phone already exists.", "danger")
            return render_template('customer_signup.html')

        if Customer.query.filter_by(Cnic=cnic).first():
            flash("CNIC already exists.", "danger")
            return render_template('customer_signup.html')

        verification_code = str(random.randint(100000, 999999))
        session['temp_customer'] = {
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'phone': phone,
            'address': address,
            'cnic': cnic,
            'code': verification_code
        }

        try:
            msg = Message("Email Verification Code", recipients=[email])
            msg.body = f"Your verification code is: {verification_code}"
            mail.send(msg)

            flash("Verification code sent to your email.", "info")
            return redirect(url_for('customer_bp.verify_email'))
        except Exception as e:
            flash(f"Failed to send email: {str(e)}", "danger")

    return render_template('customer_signup.html')


@customer_bp.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    if request.method == 'POST':
        entered_code = request.form.get('code')
        temp = session.get('temp_customer')

        if not temp:
            flash("Session expired. Please sign up again.", "danger")
            return redirect(url_for('customer_bp.customer_signup'))

        if entered_code == temp['code']:
            try:
                new_customer = Customer(
                    Name=temp['name'],
                    Email=temp['email'],
                    Password=temp['password'],
                    Phone=temp['phone'],
                    Address=temp['address'],
                    Cnic=temp['cnic']
                )
                db.session.add(new_customer)
                db.session.commit()
                session.pop('temp_customer')

                flash("Email verified! You can now log in.", "success")
                return redirect(url_for('customer_bp.customer_login'))
            except Exception as e:
                db.session.rollback()
                flash(f"Error creating account: {str(e)}", "danger")
                return redirect(url_for('customer_bp.customer_signup'))
        else:
            flash("Invalid code. Please try again.", "danger")

    return render_template('verify_email.html')


# -------------------- Login / Logout ----------------------

@customer_bp.route('/login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        customer = Customer.query.filter_by(Email=email).first()
        if customer and check_password_hash(customer.Password, password):
            session['customer_id'] = customer.CustomerID
            session['customer_name'] = customer.Name 
            flash("Login successful!", "success")
            return redirect(url_for('customer_bp.home'))
        else:
            flash("Invalid credentials.", "danger")

    return render_template('customer_login.html')


@customer_bp.route('/logout')
def customer_logout():
    session.pop('customer_id', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('customer_bp.customer_login'))


# -------------------- Forgot / Reset Password ----------------------

@customer_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        customer = Customer.query.filter_by(Email=email).first()

        if customer:
            token = generate_reset_token(email)
            reset_link = url_for('customer_bp.reset_password', token=token, _external=True)

            msg = Message('Password Reset Link', recipients=[email])
            msg.body = f'Click to reset your password: {reset_link}'
            mail.send(msg)

            flash('Reset link sent to your email.', 'success')
        else:
            flash('Email not found.', 'danger')

    return render_template('forgot_password.html')


@customer_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('customer_bp.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(request.url)

        if len(password) < 8 or not any(char in "!@#$%^&*()" for char in password):
            flash('Password must be at least 8 characters and include one special character.', 'danger')
            return redirect(request.url)

        customer = Customer.query.filter_by(Email=email).first()
        if customer:
            customer.Password = generate_password_hash(password)
            db.session.commit()
            flash('Password updated. Please log in.', 'success')
            return redirect(url_for('customer_bp.customer_login'))

    return render_template('reset_password.html')






















@customer_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'customer_id' not in session:
        flash("Please login to add items to cart.", "warning")
        return redirect(url_for('customer_bp.customer_login'))

    customer_id = session['customer_id']
    existing_item = CartItem.query.filter_by(customer_id=customer_id, product_id=product_id).first()

    if existing_item:
        existing_item.quantity += 1  # increase quantity
    else:
        new_item = CartItem(customer_id=customer_id, product_id=product_id, quantity=1)
        db.session.add(new_item)

    db.session.commit()
    flash("Product added to cart.", "success")
    return redirect(url_for('customer_bp.view_cart'))






@customer_bp.route('/cart')
def view_cart():
    if 'customer_id' not in session:
        flash("Please login to view your cart.", "warning")
        return redirect(url_for('customer_bp.customer_login'))

    customer_id = session['customer_id']
    cart_items = CartItem.query.filter_by(customer_id=customer_id).all()
    return render_template('cart.html', cart_items=cart_items)








@customer_bp.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Item removed from cart.", "info")
    return redirect(url_for('customer_bp.view_cart'))








@customer_bp.route('/update_cart/<int:item_id>', methods=['POST'])
def update_cart(item_id):
    new_qty = int(request.form.get('quantity'))
    item = CartItem.query.get_or_404(item_id)

    if new_qty < 1:
        db.session.delete(item)  # delete if quantity is zero or negative
    else:
        item.quantity = new_qty

    db.session.commit()
    flash("Cart updated.", "success")
    return redirect(url_for('customer_bp.view_cart'))




@customer_bp.route('/clear_cart', methods=['POST'])
def clear_cart():
    if 'customer_id' not in session:
        flash("Please login to clear your cart.", "warning")
        return redirect(url_for('customer_bp.customer_login'))

    customer_id = session['customer_id']
    CartItem.query.filter_by(customer_id=customer_id).delete()
    db.session.commit()
    flash("Your cart has been cleared.", "info")
    return redirect(url_for('customer_bp.view_cart'))












@customer_bp.route('/place_order/<int:item_id>', methods=['GET', 'POST'])
def place_order(item_id):
    if 'customer_id' not in session:
        flash("Please login to place an order.", "warning")
        return redirect(url_for('customer_bp.customer_login'))

    cart_item = CartItem.query.get_or_404(item_id)
    product = Product.query.get_or_404(cart_item.product_id)
    customer = Customer.query.get_or_404(cart_item.customer_id)

    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        email = request.form.get('email')
        address = request.form.get('address')

        if quantity < 1:
            flash("Quantity must be at least 1.", "danger")
            return redirect(request.url)

        # Update customer details
        customer.Email = email
        customer.Address = address

        # Calculate total price
        total_price = product.price * quantity

        # Create order
        order = Order(
            customer_id=customer.CustomerID,
            name=customer.Name,
            email=email,
            address=address,
            phone=customer.Phone,
            total_price=total_price
        )
        db.session.add(order)
        db.session.flush()  # get order.id before commit

        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            price=product.price
        )
        db.session.add(order_item)

        # Remove item from cart
        db.session.delete(cart_item)
        db.session.commit()

        try:
            # Email to Admin
            msg_admin = Message(
                subject='New Order Received',
                sender='hafizmuhammadshah11@gmail.com',
                recipients=['hafizmuhammadshah11@gmail.com']
            )
            msg_admin.body = f"""
            A new order has been placed:

            Customer: {customer.Name}
            Email: {email}
            Address: {address}

            Product: {product.name}
            Quantity: {quantity}
            Price per item: Rs. {product.price}
            Total: Rs. {total_price}
            """
            mail.send(msg_admin)

            # Email to Customer
            msg_cust = Message(
                subject='Your Order Confirmation',
                sender='hafizmuhammadshah11@gmail.com',
                recipients=[email]
            )
            msg_cust.body = f"""
            Dear {customer.Name},

            Thank you for your order!

            Product: {product.name}
            Quantity: {quantity}
            Price per item: Rs. {product.price}
            Total: Rs. {total_price}

            We will deliver your order to:
            {address}

            Regards,
            Pure Mustard Oil Team
            """
            mail.send(msg_cust)

        except Exception as e:
            flash("Order placed, but failed to send email.", "warning")
            print(str(e))
        else:
            flash("Order placed successfully and email sent.", "success")

        return redirect(url_for('customer_bp.my_orders'))

    return render_template('place_order.html', cart_item=cart_item, product=product, customer=customer)









@customer_bp.route('/my_orders')
def my_orders():
    if 'customer_id' not in session:
        flash("Please login to view your orders.", "warning")
        return redirect(url_for('customer_bp.customer_login'))

    customer_id = session['customer_id']
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.id.desc()).all()
    return render_template('my_orders.html', orders=orders)

















# Route to change order address
@customer_bp.route('/change_address/<int:order_id>', methods=['GET', 'POST'])
def change_order_address(order_id):
    order = Order.query.get_or_404(order_id)

    # Check if user is authorized
    if order.customer_id != session.get('customer_id'):
        flash("Unauthorized access.", "danger")
        return redirect(url_for('customer_bp.my_orders'))

    # Only allow address change for Pending orders
    if order.status.lower() != 'pending':
        flash("You can only change the address for pending orders.", "warning")
        return redirect(url_for('customer_bp.my_orders'))

    if request.method == 'POST':
        new_address = request.form.get('address')
        if not new_address:
            flash("Address cannot be empty.", "warning")
        else:
            order.address = new_address
            db.session.commit()
            flash("Delivery address updated successfully.", "success")
            return redirect(url_for('customer_bp.my_orders'))

    return render_template('change_address.html', order=order)



# from flask_mail import Message 
# from app import mail  # adjust if your mail is imported differently 

@customer_bp.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)

    if order.customer_id != session.get('customer_id'):
        flash("Unauthorized access.", "danger")
    elif order.status.lower() == 'cancelled':
        flash("Order is already cancelled.", "info")
    elif order.status.lower() != 'pending':
        flash("Only pending orders can be cancelled.", "warning")
    else:
        order.status = 'Cancelled'
        db.session.commit()
        flash("Order cancelled successfully.", "success")

        # Send email to admin
        try:
            msg = Message(
                subject=f"Order #{order.id} Cancelled",
                recipients=["hafizmuhammadshah11@gmail.com"],
                body=f"""
Dear Admin,

Order #{order.id} placed by {order.name} has been cancelled.

Details:
- Email: {order.email}
- Phone: {order.phone}
- Total: Rs. {order.total_price}
- Address: {order.address}

Regards,
Your Website
"""
            )
            mail.send(msg)
        except Exception as e:
            print(f"Email sending failed: {e}")  # Removed current_app.logger

    return redirect(url_for('customer_bp.my_orders'))



