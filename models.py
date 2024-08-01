from datetime import datetime, timezone

from flask import g
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
    created_at = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.Date, onupdate=datetime.now(timezone.utc))

    @classmethod
    def signup(cls, email, password):
        """Class method to call in app.py to signup a user to access the budgeting app.
            Hashes the password and stores to database."""
        
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(email=email,password=hashed_pwd)

        db.session.add(user)
        db.session.commit()

        # Create a mapping of categories to user categories
        category_to_user_category = {}
        categories = Category.query.all()
        for cat in categories:
            user_category = UserCategory(user_id=user.id, category_id=cat.id, name=cat.name, active=True)
            db.session.add(user_category)
            db.session.commit() # commit each user_category to get its id

            category_to_user_category[cat.id] = user_category.id

        # Create user subcategories    
        subcategories = Subcategory.query.all()
        for subcat in subcategories:
            user_category_id = category_to_user_category[subcat.category_id]
            user_subcategory = UserSubcategory(user_id=user.id, subcategory_id=subcat.id, user_category_id=user_category_id, name=subcat.name, active=True)
            db.session.add(user_subcategory)

        db.session.commit()
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
    created_at = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.Date, onupdate=datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('user_id', 'account_name', name='uq_user_account_name'),)

class Category(db.Model):
    """Categories for each user to see in their monthly budgets.
    Maybe create a flag to set category + sub to active/inactive, then load dashboard with info.
    
    Removed user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) so that categories are now global/not tied to user."""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    active = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.Date, onupdate=datetime.now(timezone.utc))

class Subcategory(db.Model):
    """Subcategories for each budget category."""

    __tablename__ = 'subcategories'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='cascade'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.Date, onupdate=datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('category_id', 'name', name='uq_category_subcategory_name'),)

class UserCategory(db.Model):
    """User-specific categories. Will give users the ability to create/update/delete the categories in their user instance."""

    __tablename__ = 'usercategories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='cascade'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.Date, onupdate=datetime.now(timezone.utc))

    def get_total_budgeted(self, month, year):
        """Helper func to calculate total budgeted amounts."""
        return db.session.query(db.func.sum(MonthlyBudget.budgeted_amount)).\
            join(UserSubcategory, UserSubcategory.id == MonthlyBudget.user_subcategory_id).\
            filter(UserSubcategory.user_category_id == self.id,
                   MonthlyBudget.month == month,
                   MonthlyBudget.year == year).scalar() or 0

    def get_total_actual(self, month, year):
        return db.session.query(db.func.sum(Transaction.amount)).\
        join(UserSubcategory, UserSubcategory.id == Transaction.user_subcategory_id).\
        filter(UserSubcategory.user_category_id == self.id,
            db.extract('month', Transaction.tran_date) == month,
            db.extract('year', Transaction.tran_date) == year,
            Transaction.user_id == self.user_id).scalar() or 0

class UserSubcategory(db.Model):
    """User-specific subcategories. Gives users ability to create/update/delete subcategories in user instance."""

    __tablename__ = 'usersubcategories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.id', ondelete='cascade'), nullable=True) # reference to global subcategories
    user_category_id = db.Column(db.Integer, db.ForeignKey('usercategories.id', ondelete='cascade'), nullable=True) # reference to user-specific categories
    name = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.Date, onupdate=datetime.now(timezone.utc))

    def get_total_budgeted(self, month, year):
        """Helper func to calculate total budgeted amounts."""
        return db.session.query(db.func.sum(MonthlyBudget.budgeted_amount)).\
            filter(MonthlyBudget.user_subcategory_id == self.id,
                   MonthlyBudget.month == month,
                   MonthlyBudget.year == year).scalar() or 0

    def get_total_actual(self, month, year):
        return db.session.query(db.func.sum(Transaction.amount)).\
        join(UserSubcategory, UserSubcategory.id == Transaction.user_subcategory_id).\
        filter(Transaction.user_subcategory_id == self.id,
            db.extract('month', Transaction.tran_date) == month,
            db.extract('year', Transaction.tran_date) == year,
            Transaction.user_id == self.user_id).scalar() or 0
    
class Transaction(db.Model):
    """Transactions to allow users to enter transactions in their categories/subcategories in their monthly budget.
        Need this table for transaction detail. Will need to do some joins to get the data onto the Dashboard, per month."""

    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id', ondelete='cascade'), nullable=True)
    user_category_id = db.Column(db.Integer, db.ForeignKey('usercategories.id', ondelete='cascade'), nullable=False)
    user_subcategory_id = db.Column(db.Integer, db.ForeignKey('usersubcategories.id', ondelete='cascade'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255))
    tran_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.Date, onupdate=datetime.now(timezone.utc))

    # Relationships
    user_category = db.relationship('UserCategory', backref='transactions')
    user_subcategory = db.relationship('UserSubcategory', backref='transactions')

class MonthlyBudget(db.Model):
    """The Monthly Budget will have its own id for each subcategory in categories for a user.
        This will allow us to set a budgeted amount and spent amount for each subcategory, then transaction in that sub."""
    
    __tablename__ = 'monthlybudgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)
    user_category_id = db.Column(db.Integer, db.ForeignKey('usercategories.id', ondelete='cascade'), nullable=False)
    user_subcategory_id = db.Column(db.Integer, db.ForeignKey('usersubcategories.id', ondelete='cascade'), nullable=False)
    month = db.Column(db.Integer, nullable=False, default=current_month)
    year = db.Column(db.Integer, nullable=False, default=current_year)
    budgeted_amount = db.Column(db.Numeric(10, 2), nullable=False)
    spent_amount = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.Date, onupdate=datetime.now(timezone.utc))

    @classmethod
    def get_monthly_budget(cls, user_id, month, year):
        """Retrieve the monthly budget for a user for a specific month/year."""
        return cls.query.filter_by(user_id=user_id, month=month, year=year).all()

    @classmethod
    def get_total_budgeted(cls, user_id, month, year):
        """Calcs total budgeted amount for a user for a specific month/year."""
        total = db.session.query(db.func.sum(cls.budgeted_amount)).\
            filter(cls.user_id == user_id,
                   cls.month == month,
                   cls.year == year).scalar()
        return total or 0
    
    @classmethod
    def get_total_actual(cls, user_id, month, year):
        """Calc total actual amount spent by a user for a specific month/year."""
        total = db.session.query(db.func.sum(cls.Transaction.amount)).\
        join(UserSubcategory, UserSubcategory.id == Transaction.user_subcategory_id).\
        join(UserCategory, UserCategory.id == UserSubcategory.user_category_id).\
        filter(UserCategory.user_id == user_id,
               db.extract('month', Transaction.tran_date) == month,
               db.extract('year', Transaction.tran_date) == year).scalar()
        return total or 0