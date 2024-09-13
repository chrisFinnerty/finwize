import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, session, flash, g, url_for, jsonify
from datetime import datetime, date, timedelta
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Account, Transaction, Category, Subcategory, UserCategory, UserSubcategory, MonthlyBudget
from forms import SignupLoginForm, AccountEntryForm, CategoryEntryForm, TransactionForm
from dateutil.relativedelta import relativedelta


CURR_USER_KEY = 'curr_user'
load_dotenv()

def create_app(db_name, testing=False):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URI', f'postgresql:///{db_name}'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'its_a_secret')

    if testing:
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_ECHO'] = True

    toolbar = DebugToolbarExtension()
   
    # IMPORTANT!
    # ------------------------------------------------------------------------------------
    # Remove connect_db() when deploying to Render!
    # connect_db(app)
    # ------------------------------------------------------------------------------------

    # Helper Functions
    # Login / Logout Helper Functions
    @app.before_request
    def add_user_to_g():
        """Adds the user that logs in successfully to the global variable."""

        if CURR_USER_KEY in session:
            g.user = User.query.get(session[CURR_USER_KEY])

        else:
            g.user = None

    def do_login(user):
        """Logs user in using session[CURR_USER_KEY] set equal to user's id."""

        session[CURR_USER_KEY] = user.id

    def do_logout():
        """Handles logging out the user from the app in the /logout route."""

        if CURR_USER_KEY in session:
            del session[CURR_USER_KEY]

    
    # Homepage/Dashboard route
    @app.route('/', methods=['GET', 'POST'])
    def homepage():
        if g.user:
            form = TransactionForm()
            form.account.choices = [(a.id, a.account_name) for a in Account.query.filter_by(user_id=g.user.id).all()]
            form.category.choices = [(c.id, c.name) for c in UserCategory.query.filter_by(user_id=g.user.id, active=True).all()]
            form.subcategory.choices = [(sc.id, sc.name) for sc in UserSubcategory.query.filter_by(user_id=g.user.id, active=True).all()]

            user_categories = UserCategory.query.filter_by(user_id=g.user.id, active=True).all()
            user_subcategories = UserSubcategory.query.filter_by(user_id=g.user.id, active=True).all()

            # Determine the current or selected month and year
            current_month = datetime.now().month
            current_year = datetime.now().year
            selected_month = request.args.get('month', current_month, type=int)
            selected_year = request.args.get('year', current_year, type=int)

            # Format the month and year
            selected_date = datetime(selected_year, selected_month, 1)
            formatted_date = selected_date.strftime('%B %Y')
            short_formatted_date = selected_date.strftime('%b %Y')

            # Ensure a MonthlyBudget exists for each UserSubcategory
            for subcategory in user_subcategories:
                monthly_budget = MonthlyBudget.query.filter_by(
                    user_id=g.user.id,
                    user_category_id=subcategory.user_category_id,
                    user_subcategory_id=subcategory.id,
                    month=selected_month,
                    year=selected_year
                ).first()

                if not monthly_budget:
                    monthly_budget = MonthlyBudget(
                        user_id=g.user.id,
                        user_category_id=subcategory.user_category_id,
                        user_subcategory_id=subcategory.id,
                        month=selected_month,
                        year=selected_year,
                        budgeted_amount=0.00,  # Default budget amount, can be modified later
                        spent_amount=0.00
                    )
                    db.session.add(monthly_budget)
                    db.session.commit()

            # Fetch the created or existing MonthlyBudgets for display
            monthly_budgets = MonthlyBudget.query.filter_by(
                user_id=g.user.id,
                month=selected_month,
                year=selected_year
            ).all()

            # Sum of Budget + Actual for the month the user is viewing
            total_budgeted = sum(u_cat.get_total_budgeted(selected_month, selected_year)
                                 for u_cat in user_categories)
            total_actual = sum(u_cat.get_total_actual(selected_month, selected_year)
                                 for u_cat in user_categories)
            difference = total_budgeted - total_actual

            # Balance of Accounts (always "as of last updated date")
            accounts = Account.query.filter_by(user_id=g.user.id).all()
            sum_of_accounts = sum(account.balance for account in accounts)

            latest_account_date = db.session.query(func.greatest(func.max(Account.created_at), func.max(Account.updated_at)))\
            .filter(Account.user_id == g.user.id).scalar()

            if latest_account_date:
                latest_account_date_str = latest_account_date.strftime('%b %d, %Y')
            else:
                latest_account_date_str = 'No accounts found'


            return render_template('users/dashboard.html', form=form,
                                user_categories=user_categories,
                                user_subcategories=user_subcategories,
                                monthly_budgets=monthly_budgets,
                                total_budgeted=total_budgeted,
                                total_actual=total_actual,
                                difference=difference,
                                accounts=accounts,
                                sum_of_accounts=sum_of_accounts,
                                latest_account_date_str=latest_account_date_str,
                                selected_month=selected_month,
                                selected_year=selected_year,
                                formatted_date=formatted_date,
                                short_formatted_date=short_formatted_date)
        else:
            return render_template('anon-home.html')
        
    @app.route('/user/<int:user_id>/budgeted_amount', methods=['POST'])
    def update_budgeted_amount(user_id):
        """Updates the budgeted amount by subcategory for the month/year the user is editing."""

        if not g.user or g.user.id != user_id:
            flash('Access unauthorized.', 'danger')
            return redirect(url_for('homepage'))
        
        user_subcategory_id = request.form.get('user_subcategory_id')
        month = request.form.get('month', type=int)
        year = request.form.get('year', type=int)
        new_budgeted_amount = request.form.get('budgeted_amount', type=float)

        monthly_budget = MonthlyBudget.query.filter_by(user_id=user_id, user_subcategory_id=user_subcategory_id, month=month, year=year).first()

        if monthly_budget:
            monthly_budget.budgeted_amount = new_budgeted_amount
            db.session.commit()
            return redirect(url_for('homepage'))
        else:
            return jsonify({'error': 'Budget entry not found'}), 404
        
    @app.route('/user/<int:user_id>/profile')
    def show_profile(user_id):
        """Allow a user to view their profile.
        Future func: to allow users to edit their email/password and/or reset their password."""

        if not g.user:
            flash('Access unauthorized.', 'danger')
            return url_for(redirect('homepage'))
        
        return render_template('/users/userprofile.html')


    # Signup/Login Routes
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        form = SignupLoginForm()

        if form.validate_on_submit():
            try:
                user = User.signup(
                    email = form.email.data,
                    password = form.password.data
                )
                db.session.commit()

            except IntegrityError as e:
                db.session.rollback()
                if 'unique constraint' in str(e.orig):
                    flash('An account with that email already exists.', 'danger')
                else:
                    flash('An error occurred. Please try again.')
                return render_template('/users/signup.html', form=form)
            
            do_login(user)

            return redirect('/')
        
        else:
            return render_template('/users/signup.html', form=form)
        
    @app.route('/login', methods=['GET', 'POST'])
    def login():

        form = SignupLoginForm()

        if form.validate_on_submit():
            user = User.authenticate(form.email.data, form.password.data)

            if user:
                do_login(user)
                flash(f'Welcome back to FinWize!', 'success')
                return redirect(url_for('homepage'))
            
            flash('Invalid credentials', 'danger')
        
        return render_template('/users/login.html', form=form)

    @app.route('/logout')
    def logout():
        do_logout()
        flash('Successfully logged out.', 'success')
        return redirect('/login')
    
    # Setup routes
    # Accounts
    @app.route('/user/<int:user_id>/accounts', methods=['GET', 'POST'])
    def show_accounts(user_id):
        """Display accounts tied to the user_id that is logged in."""

        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")
        
        form = AccountEntryForm()

        accounts = Account.query.filter_by(user_id=user_id).all()

        if form.validate_on_submit():
            account_name = form.account_name.data
            balance = form.balance.data

            new_account = Account(user_id=user_id, account_name=account_name, balance=balance)

            db.session.add(new_account)
            db.session.commit()

            return redirect(f'/user/{user_id}/accounts')
        
        return render_template('/setup/accounts.html', user_id=user_id, form=form, accounts=accounts)
    
    @app.route('/user/<int:user_id>/accounts/<int:account_id>/update', methods=['GET','POST'])
    def update_account(user_id, account_id):
        """Allows a user to make an update to their account's balance."""
        if not g.user or g.user.id != user_id:
            flash("Access unauthorized.", 'danger')
            return redirect(url_for('homepage'))
        
        account = Account.query.filter_by(user_id=user_id, id=account_id).first()
        
        form = AccountEntryForm(obj=account)

        if form.validate_on_submit():
            account.account_name = form.account_name.data
            account.balance = form.balance.data

            db.session.commit()
            flash('Account updated successfully!', 'success')
            return redirect(url_for('show_accounts', user_id=user_id))
        
        return render_template('/setup/update_account.html', form=form, account=account)

            
    # Cateogires/Subcategories
    @app.route('/user/<int:user_id>/categories', methods=['GET', 'POST'])
    def categories_subcategories(user_id):
        """Route to create/edit categories + subcategories."""

        if not g.user:
            flash('Access denied.', 'danger')
            return redirect(url_for('homepage'))
        
        cat_form = CategoryEntryForm()
        
        # Active user categories/subcategories
        user_categories = UserCategory.query.filter_by(user_id=g.user.id, active=True).all()
        user_subcategories = UserSubcategory.query.filter_by(user_id=g.user.id, active=True).all()

        return render_template('/setup/categories.html', cat_form=cat_form, user_categories=user_categories, user_subcategories=user_subcategories)

    # Transactions
    @app.route('/user/<int:user_id>/transactions')
    def show_transactions(user_id):
        transactions = Transaction.query.filter_by(user_id=user_id).all()

        return render_template('transactions/transactions.html', user_id=user_id, transactions=transactions)
    
    @app.route('/add-transaction', methods=['GET', 'POST'])
    def add_transaction():
        form = TransactionForm()
        form.account.choices = [(a.id, a.account_name) for a in Account.query.filter_by(user_id=g.user.id).all()]
        form.category.choices = [(c.id, c.name) for c in UserCategory.query.filter_by(user_id=g.user.id, active=True).all()]
        form.subcategory.choices = [(sc.id, sc.name) for sc in UserSubcategory.query.filter_by(user_id=g.user.id, active=True).all()]

        if form.validate_on_submit():
            try:
                transaction = Transaction(
                    user_id=g.user.id,
                    account_id=form.account.data,
                    user_category_id=form.category.data,
                    user_subcategory_id=form.subcategory.data,
                    amount=form.amount.data,
                    description=form.description.data,
                    tran_date=form.tran_date.data
                )
                db.session.add(transaction)
                db.session.commit()
                flash('Transaction added successfully!', 'success')
                return redirect(url_for('homepage'))
            except Exception as e:
                flash(f"Error adding transaction: {e}", 'error')
                return redirect(url_for('homepage'))

        return redirect(url_for('homepage'))
    
    @app.route('/user/<int:user_id>/transactions/<int:tran_id>', methods=['GET', 'POST'])
    def update_transaction(user_id, tran_id):
        """Allow a user to update their transaction in the transactions view."""
        if not g.user or g.user.id != user_id:
            flash('Access unauthorized.', 'danger')
            return redirect(url_for('homepage'))
        
        transaction = Transaction.query.filter_by(user_id=user_id, id=tran_id).first()
        
        form = TransactionForm(obj=transaction)

        form.account.choices = [(a.id, a.account_name) for a in Account.query.filter_by(user_id=user_id).all()]
        form.category.choices = [(c.id, c.name) for c in UserCategory.query.filter_by(user_id=user_id).all()]
        form.subcategory.choices = [(u_sub.id, u_sub.name ) for u_sub in UserSubcategory.query.filter_by(user_id=user_id).all()]

        if form.validate_on_submit():
            transaction.account_id = form.account.data
            transaction.user_category_id = form.category.data
            transaction.user_subcategory_id = form.subcategory.data
            transaction.amount = form.amount.data
            transaction.description = form.description.data
            transaction.tran_date = form.tran_date.data
            db.session.commit()
            flash('Transaction updated successfully!', 'success')
            return redirect(url_for('show_transactions', user_id=user_id))
        
        return render_template('/transactions/update_transaction.html', user_id=user_id, form=form, transaction=transaction)

    
    
    # Monthly Budget Data - API
    @app.route('/api/get-monthly-data', methods=['GET'])
    def get_monthly_data():
        """Fetches the budget data for the given month/year."""
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)

        if not (month and year):
            return jsonify({'error': 'Invalid month or year'}), 400

        user_id = g.user.id

        # Get all active User Categories
        user_categories = UserCategory.query.filter_by(user_id=user_id, active=True).all()
        response_data = []

        for u_cat in user_categories:
            category_data = {
                'category_name': u_cat.name,
                'total_budgeted': u_cat.get_total_budgeted(month, year),
                'total_actual': u_cat.get_total_actual(month, year),
                'subcategories': []
            }
            
            # Get all active User Subcategories
            user_subcategories = UserSubcategory.query.filter_by(user_category_id=u_cat.id, active=True).all()
            for u_sub in user_subcategories:
                subcategory_data = {
                    'subcategory_name': u_sub.name,
                    'total_actual': u_sub.get_total_actual(month, year)
                }
                category_data['subcategories'].append(subcategory_data)

            response_data.append(category_data)

        return jsonify(response_data)


    return app


if __name__ == '__main__':
    app = create_app('finwize_db', testing=True)
    app.run(debug=True)