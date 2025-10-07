from flask import flash, session, render_template, redirect, url_for, request, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, Admin, Product, Order, ContactMessage, Payment, Review
import os
from werkzeug.utils import secure_filename
from .extensions import mail
from flask_mail import Message

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Input validation
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('admin_bp.admin_signup'))
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'danger')
            return redirect(url_for('admin_bp.admin_signup'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('admin_bp.admin_signup'))

        existing = Admin.query.filter_by(username=username).first()
        if existing:
            flash('Username already taken.')
            return redirect(url_for('admin_bp.admin_signup'))

        hashed_password = generate_password_hash(password)
        new_admin = Admin(username=username, password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()

        flash('Signup successful. Please log in.')
        return redirect(url_for('admin_bp.admin_login'))

    return render_template('admin_signup.html')


@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Input validation
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('admin_bp.admin_login'))

        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            flash('Login successful!')
            return redirect(url_for('admin_bp.admin_dashboard'))
        else:
            flash('Invalid username or password.')

    return render_template('admin_login.html')


@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('admin_bp.admin_login'))

    # Get counts for dashboard
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='Pending').count()
    pending_payments = Order.query.filter_by(payment_status='Pending Verification').count()
    total_products = Product.query.count()
    
    return render_template('admin_dashboard.html', 
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         pending_payments=pending_payments,
                         total_products=total_products)

@admin_bp.route('/admin')
def admin_welcome():
    return render_template('admin_welcome.html')

@admin_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    flash('Logged out successfully.')
    return redirect(url_for('admin_bp.admin_login'))

# Product Management
@admin_bp.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    if 'admin_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('admin_bp.admin_login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price_str = request.form.get('price', '')
        description = request.form.get('description', '').strip()
        image = request.files.get('image')
        
        # Input validation
        if not name or not price_str or not description:
            flash('All fields are required.', 'danger')
            return redirect(request.url)
        
        try:
            price = float(price_str)
            if price <= 0:
                flash('Price must be a positive number.', 'danger')
                return redirect(request.url)
        except ValueError:
            flash('Invalid price format.', 'danger')
            return redirect(request.url)

        if image and image.filename:
            # Validate file extension
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' in image.filename and image.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                filename = secure_filename(image.filename)
                image.save(os.path.join('app/static/uploads', filename))
            else:
                flash("Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.", "danger")
                return redirect(request.url)
        else:
            filename = "default.jpg"

        new_product = Product(name=name, price=price, description=description, image_filename=filename)
        db.session.add(new_product)
        db.session.commit()
        flash("Product added successfully!")
        return redirect(url_for('admin_bp.all_products'))

    return render_template('add_product.html')

@admin_bp.route('/admin/products')
def all_products():
    if 'admin_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('admin_bp.admin_login'))

    products = Product.query.all()
    return render_template('all_products.html', products=products)

@admin_bp.route('/admin/edit-product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if 'admin_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('admin_bp.admin_login'))

    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.description = request.form['description']
        image = request.files['image']

        if image and image.filename:
            # Validate file extension
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' in image.filename and image.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                filename = secure_filename(image.filename)
                image.save(os.path.join('app/static/uploads', filename))
                product.image_filename = filename
            else:
                flash("Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.", "danger")
                return redirect(request.url)

        db.session.commit()
        flash("Product updated successfully.")
        return redirect(url_for('admin_bp.all_products'))

    return render_template('edit_product.html', product=product)

@admin_bp.route('/admin/hide-product/<int:id>', methods=['POST'])
def hide_product(id):
    if 'admin_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('admin_bp.admin_login'))

    product = Product.query.get_or_404(id)
    product.is_active = False
    db.session.commit()
    flash("Product hidden successfully.")
    return redirect(url_for('admin_bp.all_products'))

@admin_bp.route('/admin/show-product/<int:id>', methods=['POST'])
def show_product(id):
    if 'admin_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('admin_bp.admin_login'))

    product = Product.query.get_or_404(id)
    product.is_active = True
    db.session.commit()
    flash("Product is now visible.")
    return redirect(url_for('admin_bp.all_products'))

# Order Management
@admin_bp.route('/orders')
def view_orders():
    if 'admin_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('admin_bp.admin_login'))

    payment_filter = request.args.get('payment', 'No-payment')
    
    query = Order.query
    
    if payment_filter == 'No-payment':
        query = query.filter_by(payment_status='Pending')
    elif payment_filter == 'Check Payment':
        query = query.filter_by(payment_status='Pending Verification')
    elif payment_filter == 'Verified Payment':
        query = query.filter_by(payment_status='Verified')
    elif payment_filter == 'Rejected Payment':
        query = query.filter_by(payment_status='Rejected')
    
    orders = query.order_by(Order.created_at.desc()).all()
    
    return render_template('orders.html', 
                         orders=orders, 
                         current_payment=payment_filter)

@admin_bp.route('/order/<int:order_id>/mark-delivery', methods=['POST'])
def mark_as_delivery(order_id):
    if 'admin_id' not in session:
        flash("Please log in as admin.")
        return redirect(url_for('admin_bp.admin_login'))

    order = Order.query.get_or_404(order_id)
    if order.status == 'Pending':
        order.status = 'Delivery'
        db.session.commit()

        # Send email notification
        try:
            msg = Message(
                subject='Your order is now out for Delivery!',
                recipients=[order.email],
                body=f"Dear {order.name},\n\nYour order #{order.id} has been dispatched for delivery.\n\nThank you for shopping with us!"
            )
            mail.send(msg)
        except Exception as e:
            print(f"Email sending failed: {e}")

        flash('Order marked as Delivery and email sent.')
    else:
        flash('Order status cannot be changed to Delivery.')

    return redirect(url_for('admin_bp.view_orders'))

@admin_bp.route('/order/<int:order_id>/mark-completed', methods=['POST'])
def mark_as_completed(order_id):
    if 'admin_id' not in session:
        flash("Please log in as admin.")
        return redirect(url_for('admin_bp.admin_login'))

    order = Order.query.get_or_404(order_id)
    if order.status == 'Delivery':
        order.status = 'Completed'
        db.session.commit()

        # Send email notification
        try:
            review_url = url_for('customer_bp.review_order', order_id=order.id, _external=True)
            msg = Message(
                subject='Your order has been Completed!',
                recipients=[order.email],
                body=f"Dear {order.name},\n\nYour order #{order.id} has been successfully delivered and marked as completed.\n\nWe would love to hear your feedback! Please leave a review:\n{review_url}\n\nWe hope to serve you again!"
            )
            mail.send(msg)
        except Exception as e:
            print(f"Email sending failed: {e}")

        flash('Order marked as Completed and email sent.')
    else:
        flash('Order status cannot be changed to Completed.')

    return redirect(url_for('admin_bp.view_orders'))

# Payment Management
@admin_bp.route('/order/<int:order_id>/verify-payment', methods=['POST'])
def verify_payment(order_id):
    if 'admin_id' not in session:
        flash("Please log in as admin.")
        return redirect(url_for('admin_bp.admin_login'))

    order = Order.query.get_or_404(order_id)
    payment = Payment.query.filter_by(order_id=order.id).first()
    
    if payment:
        payment.verified = True
        order.payment_status = 'Verified'
        db.session.commit()
        
        # Send email to customer
        try:
            msg = Message(
                subject=f'Payment Verified - Order #{order.id}',
                recipients=[order.email],
                body=f"Dear {order.name},\n\nYour payment for Order #{order.id} has been verified.\n\nWe will process your order shortly.\n\nThank you!"
            )
            mail.send(msg)
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        flash('Payment verified successfully and customer notified.')
    else:
        flash('No payment record found for this order.')

    return redirect(url_for('admin_bp.view_orders'))

@admin_bp.route('/order/<int:order_id>/reject-payment', methods=['POST'])
def reject_payment(order_id):
    if 'admin_id' not in session:
        flash("Please log in as admin.")
        return redirect(url_for('admin_bp.admin_login'))

    order = Order.query.get_or_404(order_id)
    payment = Payment.query.filter_by(order_id=order.id).first()
    
    if payment:
        order.payment_status = 'Rejected'
        db.session.commit()
        
        # Send email to customer
        try:
            msg = Message(
                subject=f'Payment Issue - Order #{order.id}',
                recipients=[order.email],
                body=f"Dear {order.name},\n\nThere was an issue with your payment for Order #{order.id}.\n\nPlease upload a new payment screenshot:\nhttp://127.0.0.1:5000/payment_instructions/{order.id}\n\nThank you!"
            )
            mail.send(msg)
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        flash('Payment rejected and customer notified.')
    else:
        flash('No payment record found for this order.')

    return redirect(url_for('admin_bp.view_orders'))

@admin_bp.route('/admin/messages')
def view_messages():
    if 'admin_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('admin_bp.admin_login'))

    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('view_messages.html', messages=messages)



@admin_bp.route('/admin/order/<int:order_id>/details')
def order_details(order_id):
    if 'admin_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('admin_bp.admin_login'))

    order = Order.query.get_or_404(order_id)
    payment = Payment.query.filter_by(order_id=order_id).first()
    review = Review.query.filter_by(order_id=order_id).first()
    return render_template('order_details.html', order=order, payment=payment, review=review)

@admin_bp.route('/admin/order/<int:order_id>/review')
def view_order_review(order_id):
    if 'admin_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('admin_bp.admin_login'))

    order = Order.query.get_or_404(order_id)
    review = Review.query.filter_by(order_id=order_id).first()
    return render_template('view_order_review.html', order=order, review=review)