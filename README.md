# Pure Mustard Oil E-commerce

A Flask-based e-commerce application for selling organic mustard oil products.

## Features

- **Customer Features:**
  - Browse products
  - Add to cart
  - Guest checkout
  - Order tracking
  - Payment screenshot upload

- **Admin Features:**
  - Product management (add, edit, hide/show)
  - Order management
  - Payment verification
  - Contact message management

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd e-commerce
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create `.env` file:
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URL=mysql://username:password@localhost/database_name
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

5. **Database Setup**
   ```bash
   python -c "from app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

6. **Run Application**
   ```bash
   python run.py
   ```

## Project Structure

```
e-commerce/
├── app/
│   ├── static/
│   │   ├── uploads/          # Product images & payment screenshots
│   │   ├── home.css         # Main stylesheet
│   │   ├── home.js          # JavaScript
│   │   └── logo.png         # Logo
│   ├── templates/           # HTML templates
│   ├── __init__.py         # App factory
│   ├── models.py           # Database models
│   ├── admin_routes.py     # Admin routes
│   ├── customer_routes.py  # Customer routes
│   └── extensions.py       # Flask extensions
├── config.py               # Configuration
├── requirements.txt        # Dependencies
├── run.py                 # Application entry point
└── .env                   # Environment variables
```

## Usage

- **Customer Access:** Visit `/` for the main store
- **Admin Access:** Visit `/admin` for admin panel
- **Track Orders:** Use the "Track Order" button in navigation

## Technologies

- Flask 3.1.0
- SQLAlchemy (MySQL)
- Flask-Mail
- Bootstrap 5
- Font Awesome