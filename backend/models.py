#Database Models

from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(150), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'admin', 'customer'

class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    service_name= db.Column(db.String(150), nullable=False)
    experience=db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(150), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False) # 'Approved', 'Rejected', 'In Progress'

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=True)
    base_price = db.Column(db.Float, nullable=False)
    
class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=True)
    date_requested = db.Column(db.DateTime, nullable=False, default=db.func.current_date())
    date_completed = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=False)  # 'Requested', 'Rejected', 'Closed', 'Accepted'
    service = db.relationship('Service', backref='service_requests', lazy=True)  # One-to-Many with Service
    customer = db.relationship('User', backref='service_requests', lazy=True)     # One-to-Many with User (Customer)
    professional = db.relationship('Professional', backref='service_requests', lazy=True)  # One-to-Many with Professional

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(300), nullable=True)
    service = db.relationship('Service', backref='reviews', lazy=True)  # One-to-Many with Service
    customer = db.relationship('User', backref='reviews', lazy=True)    # One-to-Many with User (Customer)
    professional = db.relationship('Professional', backref='reviews', lazy=True)  # One-to-Many with Professional