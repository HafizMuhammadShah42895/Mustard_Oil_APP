from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import db, Product, ContactMessage, Order, OrderItem, Payment, Review
from .extensions import mail
from flask_mail import Message
import os
from werkzeug.utils import secure_filename

customer_bp = Blueprint('customer_bp', __name__)

# Add these helper functions at the top of the file
def get_product(product_id):
    """Helper function to get product by ID for templates"""
    return Product.query.get(int(product_id))

def sum_cart_total():
    """Helper function to calculate cart total for templates"""
    if 'cart' not in session:
        return 0
    
    total = 0
    for product_id, quantity in session['cart'].items():
        product = Product.query.get(int(product_id))
        if product:
            total += product.price * quantity
    return total

def cart_count():
    """Helper function to get cart item count for templates"""
    if 'cart' not in session:
        return 0
    
    return sum(session['cart'].values())

# These functions are now registered as template globals in __init__.py

# -------------------- Home / Products ----------------------

@customer_bp.route('/', endpoint='home')
def index():
    products = Product.query.filter_by(is_active=True).all()
    return render_template('index.html', products=products)

@customer_bp.route('/products')
def customer_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    query = Product.query.filter_by(is_active=True)
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

    # Email functionality disabled for Render deployment
    flash('Your message has been sent successfully!', 'success')

    return redirect(url_for('customer_bp.home') + '#contact')

# -------------------- Guest Checkout Process ----------------------

@customer_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    # Store cart items in session for guest users
    if 'cart' not in session:
        session['cart'] = {}
    
    product_id_str = str(product_id)
    if product_id_str in session['cart']:
        session['cart'][product_id_str] += 1
    else:
        session['cart'][product_id_str] = 1
    
    session.modified = True
    flash("Product added to cart.", "success")
    return redirect(url_for('customer_bp.view_cart'))

@customer_bp.route('/cart')
def view_cart():
    if 'cart' not in session or not session['cart']:
        flash("Your cart is empty.", "info")
        return render_template('cart.html', cart_items=[])
    
    cart_items = []
    total = 0
    
    for product_id, quantity in session['cart'].items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@customer_bp.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    product_id_str = str(product_id)
    if 'cart' in session and product_id_str in session['cart']:
        del session['cart'][product_id_str]
        session.modified = True
        flash("Item removed from cart.", "info")
    return redirect(url_for('customer_bp.view_cart'))

@customer_bp.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    new_qty = int(request.form.get('quantity', 1))
    product_id_str = str(product_id)
    
    if 'cart' in session and product_id_str in session['cart']:
        if new_qty < 1:
            del session['cart'][product_id_str]
        else:
            session['cart'][product_id_str] = new_qty
        session.modified = True
        flash("Cart updated.", "success")
    
    return redirect(url_for('customer_bp.view_cart'))

@customer_bp.route('/clear_cart', methods=['POST'])
def clear_cart():
    if 'cart' in session:
        session.pop('cart')
        flash("Your cart has been cleared.", "info")
    return redirect(url_for('customer_bp.view_cart'))

@customer_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('customer_bp.view_cart'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        if not all([name, email, phone, address]):
            flash("All fields are required.", "danger")
            return redirect(url_for('customer_bp.checkout'))
        
        # Calculate total
        total = 0
        order_items_data = []
        
        for product_id, quantity in session['cart'].items():
            product = Product.query.get(int(product_id))
            if product:
                item_total = product.price * quantity
                total += item_total
                order_items_data.append({
                    'product': product,
                    'quantity': quantity,
                    'price': product.price
                })
        
        # Create order
        order = Order(
            name=name,
            email=email,
            phone=phone,
            address=address,
            total_price=total
        )
        db.session.add(order)
        db.session.flush()
        
        # Create order items
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product'].id,
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # Clear cart
        session.pop('cart')
        
        # Skip email sending to prevent timeout
        # Email functionality disabled for Render deployment
        
        flash("Order placed successfully! Please complete your payment.", "success")
        return redirect(url_for('customer_bp.order_confirmation', order_id=order.id))
    
    return render_template('checkout.html')

@customer_bp.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_confirmation.html', order=order)

@customer_bp.route('/payment_instructions/<int:order_id>', methods=['GET', 'POST'])
def payment_instructions(order_id):
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'POST':
        if 'payment_screenshot' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        file = request.files['payment_screenshot']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(f"payment_{order_id}_{file.filename}")
            filepath = os.path.join('app/static/uploads', filename)
            file.save(filepath)
            
            # Update order with payment screenshot
            order.payment_screenshot = filename
            order.payment_status = 'Pending Verification'
            db.session.commit()
            
            # Create payment record
            payment = Payment(
                order_id=order.id,
                amount=order.total_price,
                screenshot_filename=filename
            )
            db.session.add(payment)
            db.session.commit()
            
            # Email functionality disabled for Render deployment
            
            flash('Payment screenshot uploaded successfully! We will verify it shortly.', 'success')
            return redirect(url_for('customer_bp.order_confirmation', order_id=order.id))
    
    return render_template('payment_instructions.html', order=order)

@customer_bp.route('/upload_payment/<int:order_id>', methods=['GET', 'POST'])
def upload_payment(order_id):
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'POST':
        if 'payment_screenshot' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        file = request.files['payment_screenshot']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(f"payment_{order_id}_{file.filename}")
            filepath = os.path.join('app/static/uploads', filename)
            file.save(filepath)
            
            # Update order with payment screenshot
            order.payment_screenshot = filename
            order.payment_status = 'Pending Verification'
            db.session.commit()
            
            # Create payment record
            payment = Payment(
                order_id=order.id,
                amount=order.total_price,
                screenshot_filename=filename
            )
            db.session.add(payment)
            db.session.commit()
            
            # Email functionality disabled for Render deployment
            
            flash('Payment screenshot uploaded successfully! We will verify it shortly.', 'success')
            return redirect(url_for('customer_bp.order_confirmation', order_id=order.id))
    
    return render_template('upload_payment.html', order=order)

@customer_bp.route('/track_order_search', methods=['POST'])
def track_order_search():
    order_id = request.form.get('order_id')
    email = request.form.get('email')
    
    if not order_id or not email:
        flash('Please provide both Order ID and Email address.', 'danger')
        return redirect(url_for('customer_bp.home'))
    
    order = Order.query.filter_by(id=order_id, email=email).first()
    
    if not order:
        flash('Order not found. Please check your Order ID and Email address.', 'danger')
        return redirect(url_for('customer_bp.home'))
    
    return redirect(url_for('customer_bp.track_order', order_id=order.id))

@customer_bp.route('/track_order/<int:order_id>')
def track_order(order_id):
    order = Order.query.get_or_404(order_id)
    review = Review.query.filter_by(order_id=order_id).first()
    return render_template('track_order.html', order=order, review=review)

@customer_bp.route('/select-address')
def select_address():
    return render_template('select_address.html')

@customer_bp.route('/review/<int:order_id>', methods=['GET', 'POST'])
def review_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.status != 'Completed':
        flash('You can only review completed orders.', 'warning')
        return redirect(url_for('customer_bp.track_order', order_id=order_id))
    
    existing_review = Review.query.filter_by(order_id=order_id).first()
    if existing_review:
        flash('You have already reviewed this order.', 'info')
        return redirect(url_for('customer_bp.track_order', order_id=order_id))
    
    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment', '').strip()
        
        if not rating or rating < 1 or rating > 5:
            flash('Please select a valid rating.', 'danger')
            return redirect(request.url)
        
        review = Review(
            order_id=order_id,
            customer_name=order.name,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()
        
        flash('Thank you for your review!', 'success')
        return redirect(url_for('customer_bp.track_order', order_id=order_id))
    
    return render_template('review_order.html', order=order)