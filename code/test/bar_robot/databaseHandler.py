# database.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy import OperationalError


#Database Configuration
DB_USERNAME = "robi"
DB_PASSWORD = "Keins123!"
DB_NAME = "barroboterdatabase"
DB_HOST = "localhost"
DB_PORT = "3306"

db = SQLAlchemy()

class DatabaseHandler:
    def __init__(self, app):
        db.init_app(app)
        with app.app_context():
            if self.check_database_connection():
                if not self.table_exists('outlets'):
                    db.create_all(bind=['outlets'])
                if not self.table_exists('ingredients'):
                    db.create_all(bind=['ingredients'])
            else:
                raise Exception("Database connection failed")
            
    def check_database_connection(self):
        try:
            db.session.execute('SELECT 1')
            return True
        except OperationalError:
            return False

    def table_exists(self, table_name):
        inspector = inspect(db.engine)
        return inspector.has_table(table_name)

    def get_all_cocktails(self):
        return db.session.query(Ingredient.cocktail_id).distinct().all()

    def get_ingredients_for_cocktail(self, cocktail_id):
        return Ingredient.query.filter_by(cocktail_id=cocktail_id).order_by(Ingredient.sequence).all()

    def get_outlet_position(self, beveragetype):
        return Outlet.query.filter_by(beveragetype=beveragetype).first()
    
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
