# <<<<<<< HEAD
# models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Initialize SQLAlchemy


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    like_count = db.Column(db.ARRAY(db.Integer), default=list)  # Array for user IDs who liked the product
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Foreign key to User model
    image_file = db.Column(db.String(100), nullable=False)  # Field for storing image filenames

    user = db.relationship('User', backref='products')  # Relationship to User model

    def __repr__(self):
        return f'<Product {self.name}>'
