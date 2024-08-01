## FinWize (Personal Budgeting app)
### Overview
FinWize is a simplified approach to budgeting. The app allows users to focus on adjusting their budgets by month, category, subcategory on the fly as the months change.
They can also add transactions that occured in a time period (past or present) to provide a better picture on Budgeted Amounts vs Actual Dollars Spent.

### Tech Stack
#### Front End
- HTMl
- CSS
- Javascript
- Bootstrap
- Jinja
- WTForms
  
#### Back End
- Python/Flask
- Flask-SQLAlchemy
- Flask-Bcrypt
- Postgresql

### Live
The app is deployed on Render: (insert Render link)

### Project Breakdown
#### Database Models
- User: user that can signup/login to their account to access their budget instance.
- Account: Accounts like bank balance, credit card balance, etc
- Category: For new accounts to have access to preset categories out of the box.
- Subcategory: For new accounts to have access to preset subcategories out of the box.
- UserCategory: User-specific categories.
- UserSubcategory: User-specific subcategories.
- Transaction: allows users to enter transactions in categories/subcategories in monthly budget view.
- MonthlyBudget: the budget instance that the user can see month by month with budgeted amounts, spent amounts, month/year.
  
#### Functionality Features
- User Authentication/Authorization: Signup and login functionality.
- Monthly Budget views: Define budgeted amounts, actual spent amounts, and transactions by month/year by category by subcategory. Each category/subcategory shows the rolled up totals for budgeted and actuals. Budgeted Amounts can be updated on the fly, and are specific to that month view you are in.
- Add Transactions: users can add transactions on their dashboard with a pop out modal. Can fill in the required fields, and it will post to the Transactions list. Transcations can be accessed by clicking "Transactions" on the sidebar, which gives users the ability to edit any transaction they've posted.
- Add Accounts: users can add bank accounts + balances here (ideally this would not be manual entry and rely on an API - but out of scope for this).
- Add Categories: users can add categories/subcategories that are unique to their login.

