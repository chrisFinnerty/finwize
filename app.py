import os

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, session, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Account, Transaction, Category, Subcategory, MonthlyBudget, MonthlySummary, YearlySummary
from forms import SignupLoginForm

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
   
    # IMPORTANT!!!
    # ------------------------------------------------------------------------------------
    # Remove connect_db() when deploying to Render!!!
    connect_db(app)
    # Update: ran python3 server.py, and it was able to properly connect to Supabase db with connect_db() commented out.
    # Update: Was ble to also run python3 app.py, and the app was launched on local server. 
    # Question: will anything inputted there be connected to supabase or local db?
    # ------------------------------------------------------------------------------------

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

    
    # Homepage route
    @app.route('/')
    def homepage():
        if g.user:
            return render_template('home.html')
        else:
            return render_template('anon-home.html')

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
                return redirect('/')
            
            flash('Invalid credentials', 'danger')
        
        return render_template('/users/login.html', form=form)

    @app.route('/logout')
    def logout():
        do_logout()
        flash('Successfully logged out.', 'success')
        return redirect('/login')
    
    return app


if __name__ == '__main__':
    app = create_app('finwize_db', testing=True)
    app.run(debug=True)