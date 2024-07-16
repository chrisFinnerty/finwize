Table user {
  id integer [primary key]
  email varchar(255) unique
  username varchar(255) unique
  password varchar(255)
  created_at timestamp
  updated_at timestamp
}

Table account {
  id integer [primary key]
  user_id integer [foreign key]
  account_name varchar
  balance decimal(10, 2)
  created_at timestamp
  updated_at timestamp
}

Table transaction {
  id integer [primary key]
  user_id integer [foreign key]
  account_id integer [foreign key]
  category_id integer [foreign key]
  subcategory_id integer [foreign key]
  amount decimal(10, 2)
  description varchar(255)
  tran_date date
  created_at timestamp
  updated_at timestamp
}

Table category {
  id integer [primary key]
  user_id integer [foreign key]
  name varchar(255)
  created_at timestamp
  updated_at timestamp
}

Table subcategory {
  id integer [primary key]
  category_id integer [foreign key]
  name varchar(255)
  created_at timestamp
  updated_at timestamp
}

Table monthlybudget {
  id integer [primary key]
  user_id integer [foreign key]
  category_id integer [foreign key]
  subcategory_id integer [foreign key]
  month integer
  year integer
  budgeted_amount decimal(10, 2)
  spent_amount decimal(10, 2)
  created_at timestamp
  updated_at timestamp
}

Table monthlysummary {
  id integer [primary key]
  user_id integer [foreign key]
  category_id integer [foreign key]
  month integer
  year integer
  total_spent decimal(10, 2)
  created_at timestamp
  updated_at timestamp
}

Table yearlysummary {
  id integer [primary key]
  user_id integer [foreign key]
  category_id integer [foreign key]
  year integer
  total_spent decimal(10, 2)
  created_at timestamp
  updated_at timestamp
}

// Each user can have multiple accounts
Ref: user.id > account.user_id

// Each user can have multiple transactions
Ref: user.id > transaction.user_id

// Each User can have multiple categories
Ref: user.id > category.user_id

// Each category can have multiple subcats
Ref: category.id > subcategory.category_id

// Each user can have multiple monthly budgets
Ref: user.id > monthlybudget.user_id
Ref: category.id > monthlybudget.category_id
Ref: subcategory.id > monthlybudget.subcategory_id

// Each user can have multiple monthly summaries
Ref: user.id > monthlysummary.user_id
Ref: category.id > monthlysummary.category_id

// Each user can have multiple yearly summaries
Ref: user.id > yearlysummary.user_id
Ref: category.id > yearlysummary.category_id







