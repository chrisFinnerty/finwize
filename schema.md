Table user {
  id integer [primary key]
  email varchar(255) unique
  username varchar(255) unique
  password varchar(255)
  created_at date
  updated_at date
}

Table account {
  id integer [primary key]
  user_id integer
  account_name varchar
  balance decimal(10, 2)
  created_at date
  updated_at date
}

Table category {
  id integer [primary key]
  user_id integer
  name varchar(255)
  created_at date
  updated_at date
}

Table subcategory {
  id integer [primary key]
  category_id integer
  name varchar(255)
  created_at date
  updated_at date
}

Table usercategory {
  id integer [primary key]
  user_id integer
  category_id integer
  name varchar(255)
  active boolean
  created_at date
  updated_at date
}

Table usersubcategory {
  id integer [primary key]
  user_id integer
  subcategory_id integer
  user_category_id integer
  name varchar(255)
  active boolean
  created_at date
  updated_at date
}

Table transaction {
  id integer [primary key]
  user_id integer
  account_id integer
  user_category_id integer
  user_subcategory_id integer
  amount decimal(10, 2)
  description varchar(255)
  tran_date date
  created_at date
  updated_at date
}

Table monthlybudget {
  id integer [primary key]
  user_id integer
  user_category_id integer
  user_subcategory_id integer
  month integer
  year integer
  budgeted_amount decimal(10, 2)
  spent_amount decimal(10, 2)
  created_at date
  updated_at date
}

// Each user can have multiple accounts (bank accounts)
Ref: user.id > account.user_id

// Each user can have multiple transactions
Ref: user.id > transaction.user_id

// Each User can have multiple categories
Ref: user.id > category.user_id

// Each user can have multiple usercategories/usersubcategories
Ref: user.id > usercategory.user_id
Ref: user.id > usersubcategory.user_id

// Each category can have multiple subcats
Ref: category.id > subcategory.category_id

// Each usercategory can have multiple usersubcats
Ref: usercategory.id > usersubcategory.user_category_id
Ref: usercategory.id > transaction.user_category_id
Ref: usersubcategory.id > transaction.user_subcategory_id

// Each user can have multiple monthly budgets
Ref: user.id > monthlybudget.user_id
Ref: usercategory.id > monthlybudget.user_category_id
Ref: usersubcategory.id > monthlybudget.user_subcategory_id







