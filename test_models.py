from unittest import TestCase, main
from datetime import date
from app import create_app
from models import db, User, Account, Category, Subcategory, Transaction, UserCategory, UserSubcategory, MonthlyBudget

class ModelTestCase(TestCase):
    def setUp(self):
        self.app = create_app('finwize_db_test', testing=True)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///finwize_db_test'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

            self.user = User(email='uniqueuser@test.com', password='password')
            db.session.add(self.user)
            db.session.commit()

            self.account = Account(user_id = self.user.id, account_name='Test Account', balance=500)
            db.session.add(self.account)
            db.session.commit()

            self.category = Category(name='Test Category', active=True)
            db.session.add(self.category)
            db.session.commit()

            self.subcategory = Subcategory(category_id=self.category.id, name='Test Subcategory', active=True)
            db.session.add(self.subcategory)
            db.session.commit()

            self.user_category = UserCategory(user_id=self.user.id, category_id=self.category.id, name='Test UserCategory')
            db.session.add(self.user_category)
            db.session.commit()

            self.user_subcategory = UserSubcategory(user_id=self.user.id, subcategory_id=self.subcategory.id, user_category_id=self.user_category.id, name='Test UserSubcategory')
            db.session.add(self.user_subcategory)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
            
    def test_user_model(self):
        with self.app.app_context():
            user = User(email='testuser2@test.com', password='password')
            db.session.add(user)
            db.session.commit()

            self.assertEqual(len(User.query.all()), 2)

    def test_account_model(self):
        with self.app.app_context():

            user = db.session.merge(self.user)

            account = Account(user_id = user.id, account_name='Savings', balance=1000)
            db.session.add(account)
            db.session.commit()

            self.assertEqual(len(Account.query.all()), 2)
            self.assertEqual(Account.query.filter_by(balance=1000).count(), 1)

    def test_transaction_model(self):
        with self.app.app_context():
            user = db.session.merge(self.user)
            account = db.session.merge(self.account)
            user_category = db.session.merge(self.user_category)
            user_subcategory = db.session.merge(self.user_subcategory)

            transaction = Transaction(
                user_id=user.id, 
                account_id=account.id, 
                user_category_id=user_category.id, 
                user_subcategory_id=user_subcategory.id,
                amount=100,
                description='Groceries',
                tran_date=date.today())
            
            db.session.add(transaction)
            db.session.commit()

            self.assertEqual(len(Transaction.query.all()), 1)


    def test_monthly_budget(self):
        with self.app.app_context():

            user = db.session.merge(self.user)
            user_category = db.session.merge(self.user_category)
            user_subcategory = db.session.merge(self.user_subcategory)

            monthly_budget = MonthlyBudget(
                user_id=user.id, 
                user_category_id=user_category.id, 
                user_subcategory_id=user_subcategory.id, 
                budgeted_amount=1000, 
                spent_amount=500)
            
            db.session.add(monthly_budget)
            db.session.commit()

            self.assertEqual(len(MonthlyBudget.query.all()), 1)



if __name__ == '__main__':
    main()