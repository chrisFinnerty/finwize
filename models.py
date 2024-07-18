from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect the app to our database."""
    with app.app_context():
        db.app = app
        db.init_app(app)
        db.create_all()

# ------------------- Helper Functions -------------------

def current_month():
    return datetime.now().month

def current_year():
    return datetime.now().year

# ------------------- Models/Tables -------------------

class User(db.Model):
    """User to access the budget app."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))

    @classmethod
    def signup(cls, email, password):
        """Class method to call in app.py to signup a user to access the budgeting app.
            Hashes the password and stores to database."""
        
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)

        return user
    
    @classmethod
    def authenticate(cls, email, password):
        """Find user with email and password.
            Searches for the user whose password hash matches the password. Returns that user object.
            If it does not find matching user or password is false, returns False. """
        
        user = cls.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class Account(db.Model):
    """Accounts like bank balance, credit card balance, etc."""

    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)
    account_name = db.Column(db.String(255), nullable=False, unique=True)
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('user_id', 'account_name', name='uq_user_account_name'),)

class Transaction(db.Model):
    """Transactions to allow users to enter transactions in their categories/subcategories in their monthly budget."""

    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255))
    tran_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default = datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate = datetime.now(timezone.utc))

class Category(db.Model):
    """Categories for each user to see in their monthly budgets."""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default = datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate = datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='uq_user_category_name'),)

class Subcategory(db.Model):
    """Subcategories for each budget category. This app will be subcategory based, so this table is crucial for rollup of data."""

    __tablename__ = 'subcategories'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default = datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate = datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('category_id', 'name', name='uq_category_subcategory_name'),)

class MonthlyBudget(db.Model):
    """The Monthly Budget will have it's own id for each subcategory in categories for a user.
        This will allow us to set a budgeted amount and spent amount for each subcategory, then transaction in that sub."""
    
    __tablename__ = 'monthlybudgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False, default=current_month)
    year = db.Column(db.Integer, nullable=False, default=current_year)
    budgeted_amount = db.Column(db.Numeric(10, 2), nullable=False)
    spent_amount = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))

class MonthlySummary(db.Model):
    """Summary data for the current month that the user is viewing/editing."""

    __tablename__ = 'monthlysummaries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False, default=current_month)
    year = db.Column(db.Integer, nullable=False, default=current_year)
    total_spent = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))

class YearlySummary(db.Model):
    """Summary data for the current year that the user is viewing/editing."""

    __tablename__ = 'yearlysummaries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False, default=current_year)
    total_spent = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))


