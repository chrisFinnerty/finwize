"""Seed database with sample data from CSV Files."""
import os 

from dotenv import load_dotenv
from csv import DictReader
from sqlalchemy import text
from app import db, create_app
from models import db, connect_db, Category, Subcategory

load_dotenv()
app = create_app('finwize_db')
connect_db(app)

def str_to_bool(val):
    if val.lower() in ('true'):
        return True
    elif val.lower() in ('false'):
        return False
    raise ValueError(f'Not a boolean value: {val}')

def convert_row(row):
    row['active'] = str_to_bool(row['active'])
    return row

with app.app_context():
    
    db.drop_all()
    db.create_all()

    with open('generator/categories.csv') as categories_file:
        categories_reader = DictReader(categories_file)
        category_data = [convert_row(row) for row in categories_reader]
        db.session.bulk_insert_mappings(Category, category_data)

    with open('generator/subcategories.csv') as subcategories_file:
        subcategories_reader = DictReader(subcategories_file)
        subcategory_data = [convert_row(row) for row in subcategories_reader]
        db.session.bulk_insert_mappings(Subcategory, subcategory_data)

    db.session.commit()
