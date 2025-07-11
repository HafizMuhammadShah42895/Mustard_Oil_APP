from flask import flash, session, render_template, redirect, url_for, request, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, Admin , Product  # ✅ Make sure db is imported from models
import os
from werkzeug.utils import secure_filename




admin_bp = Blueprint('admin_bp', __name__)




@admin_bp.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

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
        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            flash('Login successful!')
            return redirect(url_for('admin_bp.admin_dashboard'))  # ✅ Make sure this route exists
        else:
            flash('Invalid username or password.')

    return render_template('admin_login.html')




@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    # Only allow access if logged in
    if 'admin_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('admin_bp.admin_login'))

    return render_template('admin_dashboard.html')



@admin_bp.route('/admin')
def admin_welcome():
    return render_template('admin_welcome.html')



@admin_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    flash('Logged out successfully.')
    return redirect(url_for('admin_bp.admin_login'))











# Add Product
@admin_bp.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    if 'admin_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('admin_bp.admin_login'))

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        image = request.files['image']

        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join('app/static/uploads', filename))
        else:
            filename = "default.jpg"

        new_product = Product(name=name, price=price, description=description, image_filename=filename)
        db.session.add(new_product)
        db.session.commit()
        flash("Product added successfully!")
        return redirect(url_for('admin_bp.all_products'))

    return render_template('add_product.html')


# View All Products
@admin_bp.route('/admin/products')
def all_products():
    if 'admin_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('admin_bp.admin_login'))

    products = Product.query.all()
    return render_template('all_products.html', products=products)


# Update Product
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

        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join('app/static/uploads', filename))
            product.image_filename = filename

        db.session.commit()
        flash("Product updated successfully.")
        return redirect(url_for('admin_bp.all_products'))

    return render_template('edit_product.html', product=product)


# Delete Product
@admin_bp.route('/admin/delete-product/<int:id>', methods=['POST'])
def delete_product(id):
    if 'admin_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('admin_bp.admin_login'))

    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully.")
    return redirect(url_for('admin_bp.all_products'))