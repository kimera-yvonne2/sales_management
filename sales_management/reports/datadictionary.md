Data Dictionary

1. USER
Field

Data Type

Size

Constraints

Description

user_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the user account

username

VARCHAR

50

NOT NULL, UNIQUE

Login username

password_hash

VARCHAR

255

NOT NULL

Hashed password

role

ENUM

—

NOT NULL ('Administrator','Manager','Cashier','Store Employee')

Access level of the user

employee_id

INT

—

FK → EMPLOYEE(employee_id)

Links the login account to an employee

status

ENUM

—

DEFAULT 'Active' ('Active','Inactive')

Account status

Field

Data Type

Size

Constraints

Description

employee_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the employee

first_name

VARCHAR

50

NOT NULL

Employee's first name

last_name

VARCHAR

50

NOT NULL

Employee's last name

phone

VARCHAR

15

UNIQUE

Contact phone number

email

VARCHAR

100

UNIQUE

Contact email address

branch_id

INT

—

FK → BRANCH(branch_id)

Branch the employee is assigned to

hire_date

DATE

—

NOT NULL

Date employee was hired

Field

Data Type

Size

Constraints

Description

branch_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the branch

branch_name

VARCHAR

100

NOT NULL

Name of the retail branch

location

VARCHAR

150

NOT NULL

Physical address/location

phone

VARCHAR

15

—

Branch contact number

2. EMPLOYEE

Field

Data Type

Size

Constraints

Description

employee_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the employee

first_name

VARCHAR

50

NOT NULL

Employee's first name

last_name

VARCHAR

50

NOT NULL

Employee's last name

phone

VARCHAR

15

UNIQUE

Contact phone number

email

VARCHAR

100

UNIQUE

Contact email address

branch_id

INT

—

FK → BRANCH(branch_id)

Branch the employee is assigned to

hire_date

DATE

—

NOT NULL

Date employee was hired

3. BRANCH

Field

Data Type

Size

Constraints

Description

branch_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the branch

branch_name

VARCHAR

100

NOT NULL

Name of the retail branch

location

VARCHAR

150

NOT NULL

Physical address/location

phone

VARCHAR

15

—

Branch contact number

4. CATEGORY

Field

Data Type

Size

Constraints

Description

category_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for a product category

category_name

VARCHAR

50

NOT NULL, UNIQUE

Name of the category

description

VARCHAR

255

—

Brief description of the category

5. PRODUCT

Field

Data Type

Size

Constraints

Description

product_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the product

category_id

INT

—

FK → CATEGORY(category_id), NOT NULL

Category the product belongs to

product_name

VARCHAR

100

NOT NULL

Name of the product

barcode

VARCHAR

50

UNIQUE

Product barcode

cost_price

DECIMAL

10,2

NOT NULL, CHECK ≥ 0

Cost price to the business

selling_price

DECIMAL

10,2

NOT NULL, CHECK ≥ 0

Price charged to customers

reorder_level

INT

—

DEFAULT 0

Minimum stock quantity before restocking

Field

Data Type

Size

Constraints

Description

supplier_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the supplier

supplier_name

VARCHAR

100

NOT NULL

Name of the supplying business/individual

phone

VARCHAR

15

—

Supplier contact number

email

VARCHAR

100

—

Supplier email address

address

VARCHAR

150

—

Supplier physical address

6. SUPPLIER

Field

Data Type

Size

Constraints

Description

customer_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the customer

customer_name

VARCHAR

100

NOT NULL

Customer's name

phone

VARCHAR

15

—

Customer contact number

email

VARCHAR

100

—

Customer email address

address

VARCHAR

150

—

Customer address

7. CUSTOMER

Field

Data Type

Size

Constraints

Description

purchase_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the purchase

supplier_id

INT

—

FK → SUPPLIER(supplier_id), NOT NULL

Supplier who provided the items

branch_id

INT

—

FK → BRANCH(branch_id), NOT NULL

Branch where the purchase was made

employee_id

INT

—

FK → EMPLOYEE(employee_id), NOT NULL

Employee who processed the purchase

purchase_date

DATETIME

—

NOT NULL DEFAULT CURRENT_TIMESTAMP

Date and time of the purchase

total_amount

DECIMAL

12,2

NOT NULL, CHECK ≥ 0

Total amount of the purchase

8. PURCHASE

Field

Data Type

Size

Constraints

Description

purchase_item_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the purchase item

purchase_id

INT

—

FK → PURCHASE(purchase_id), ON DELETE CASCADE

Link to the parent purchase

product_id

INT

—

FK → PRODUCT(product_id), NOT NULL

Product purchased

quantity

INT

—

NOT NULL

Quantity of the product purchased

unit_cost

DECIMAL

10,2

NOT NULL, CHECK ≥ 0

Cost per unit at the time of purchase

subtotal

DECIMAL

12,2

NOT NULL

Quantity × unit cost

9. PURCHASE_ITEM

Field

Data Type

Size

Constraints

Description

inventory_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the inventory record

branch_id

INT

—

FK → BRANCH(branch_id), NOT NULL

Branch where the product is stocked

product_id

INT

—

FK → PRODUCT(product_id), NOT NULL

Product in inventory

quantity_on_hand

INT

—

NOT NULL DEFAULT 0

Current stock quantity at the branch

last_updated

TIMESTAMP

—

NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

Last time the inventory record was updated

Field

Data Type

Size

Constraints

Description

UNIQUE KEY uq_branch_product (branch_id, product_id)

10. INVENTORY

Field

Data Type

Size

Constraints

Description

sale_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the sale

customer_id

INT

—

FK → CUSTOMER(customer_id)

Customer who made the purchase (NULL = walk-in)

branch_id

INT

—

FK → BRANCH(branch_id), NOT NULL

Branch where the sale occurred

employee_id

INT

—

FK → EMPLOYEE(employee_id), NOT NULL

Employee who processed the sale

sale_date

DATETIME

—

NOT NULL DEFAULT CURRENT_TIMESTAMP

Date and time of the sale

total_amount

DECIMAL

12,2

NOT NULL, CHECK ≥ 0

Total amount of the sale

11. SALE

Field

Data Type

Size

Constraints

Description

sale_item_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the sale item

sale_id

INT

—

FK → SALE(sale_id), ON DELETE CASCADE

Link to the parent sale

product_id

INT

—

FK → PRODUCT(product_id), NOT NULL

Product sold

quantity

INT

—

NOT NULL

Quantity of the product sold

unit_price

DECIMAL

10,2

NOT NULL, CHECK ≥ 0

Price per unit at the time of sale

subtotal

DECIMAL

12,2

NOT NULL

Quantity × unit price

12. SALE_ITEM

Field

Data Type

Size

Constraints

Description

payment_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the payment

sale_id

INT

—

FK → SALE(sale_id), ON DELETE CASCADE

Link to the parent sale

payment_method

ENUM

—

NOT NULL ('Cash','Mobile Money','Card','Bank Transfer')

Method of payment

amount

DECIMAL

12,2

NOT NULL, CHECK > 0

Payment amount

payment_date

DATETIME

—

NOT NULL DEFAULT CURRENT_TIMESTAMP

Date and time of the payment

reference

VARCHAR

100

—

Payment reference or transaction ID

13. PAYMENT

Field

Data Type

Size

Constraints

Description

expense_id

INT

—

PK, AUTO_INCREMENT

Unique identifier for the expense

branch_id

INT

—

FK → BRANCH(branch_id), NOT NULL

Branch where the expense occurred

employee_id

INT

—

FK → EMPLOYEE(employee_id), NOT NULL

Employee who incurred the expense

expense_type

VARCHAR

100

NOT NULL

Type of expense (e.g., Rent, Utilities, Salaries)

amount

DECIMAL

12,2

NOT NULL, CHECK > 0

Expense amount

expense_date

DATE

—

NOT NULL

Date the expense was incurred

description

TEXT

—

Optional description of the expense

14. EXPENSE
