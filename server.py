from app import create_app
from models import connect_db

app = create_app('finwize_db')
connect_db(app)