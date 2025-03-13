# databaseHandler.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from database import db, Outlet, Ingredient

class DatabaseHandler:
    def __init__(self, app):
        db.init_app(app)
        with app.app_context():
            if self.check_database_connection():
                db.create_all()
            else:
                raise Exception("Database connection failed")
            
    def check_database_connection(self):
        try:
            db.session.execute(text('SELECT 1'))
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
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
