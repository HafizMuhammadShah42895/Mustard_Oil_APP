from app import create_app
from app.models import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Only runs once to create tables
    app.run(debug=True)
