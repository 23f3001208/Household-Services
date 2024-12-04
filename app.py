from flask import Flask
from backend.models import db
from backend.models import User

app=None

def setup_app():
    app=Flask(__name__)
    app.secret_key="MY_SECRET_KEY"
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///household_services.sqlite3"
    db.init_app(app) 
    app.app_context().push()
    db.create_all()

    admin = User.query.filter_by(role="admin").first()

    if not admin:
        admin = User(
            username='admin@household.com',
            password='admin123',
            full_name='Admin',
            address='Admin Location',
            pincode=123456,
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
    app.debug=True

setup_app()

from backend.controllers import *

if __name__=="__main__":
    app.run()