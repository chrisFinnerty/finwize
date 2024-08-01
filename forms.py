from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DecimalField, DateTimeField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class SignupLoginForm(FlaskForm):
    """Creates a signup form when the /signup route is accessed."""

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class AccountEntryForm(FlaskForm):
    """Allows a user to create a new account + balance."""

    account_name = StringField('Account Name', validators=[DataRequired()])
    balance = DecimalField('Balance', validators=[DataRequired()])

class CategoryEntryForm(FlaskForm):
    """Allows a user to create their own Category."""

    category_name = StringField('Category Name', validators=[DataRequired()])

class TransactionForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    tran_date = DateField('Transaction Date', validators=[DataRequired()], format='%Y-%m-%d')
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    account = SelectField('Account', coerce=int)
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    subcategory = SelectField('Subcategory', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')
