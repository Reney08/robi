# database.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Outlet(db.Model):
    __tablename__ = 'outlets'
    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    position = db.Column(db.String(100), nullable=False)
    beveragetype = db.Column(db.String(100), nullable=False)

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    beveragetype = db.Column(db.String(100), nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    cocktail_id = db.Column(db.Integer, nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
