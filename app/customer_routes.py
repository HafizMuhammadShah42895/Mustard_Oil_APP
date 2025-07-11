from flask import Blueprint, render_template , request , flash , redirect , url_for
from .models import db, Product , ContactMessage
from flask_mail import Message
from .extensions import mail 



customer_bp = Blueprint('customer_bp', __name__)


@customer_bp.route('/', endpoint='home')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)



@customer_bp.route('/products')
def customer_products():
    products = Product.query.all()
    return render_template('customer_products.html', products=products)










@customer_bp.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        flash('All fields are required.', 'danger')
        return redirect(url_for('customer_bp.home') + '#contact')

    # Save to database
    new_message = ContactMessage(name=name, email=email, message=message)
    db.session.add(new_message)
    db.session.commit()

    try:
        # 1️⃣ Send message to YOU
        msg_to_you = Message(
            subject='New Contact Message from Website',
            sender='hafizmuhammadshah11@gmail.com',  # your email
            recipients=['hafizmuhammadshah11@gmail.com'],  # your email
            reply_to=email  # this makes replying go to the user
        )
        msg_to_you.body = f"""
        You received a new message from your website:

        Name: {name}
        Email: {email}
        Message:
        {message}
        """
        mail.send(msg_to_you)

        # 2️⃣ Send thank-you email to user
        thank_you = Message(
            subject='Thank You for Contacting Us!',
            sender='hafizmuhammadshah11@gmail.com',  # your email
            recipients=[email]  # user's email
        )
        thank_you.body = f"""
        Dear {name},

        Thank you for reaching out to us! We have received your message and will get back to you shortly.

        Here is a copy of your message:
        {message}

        Best regards,
        Pure Mustard Oil Team
        """
        mail.send(thank_you)

        flash('Your message has been sent successfully!', 'success')

    except Exception as e:
        flash('Failed to send email. Please try again later.', 'danger')
        print(str(e))

    return redirect(url_for('customer_bp.home') + '#contact')







