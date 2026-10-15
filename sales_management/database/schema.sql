CREATE DATABASE IF NOT EXISTS sales_management_db;
USE sales_management_db;

-- 1. BRANCH TABLE
CREATE TABLE BRANCH (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    location VARCHAR(150) NOT NULL,
    phone VARCHAR(20)
);

-- 2. EMPLOYEE TABLE
CREATE TABLE EMPLOYEE (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    branch_id INT,
    hire_date DATE,
    FOREIGN KEY (branch_id) REFERENCES BRANCH(branch_id)
);

-- 3. USER TABLE
CREATE TABLE USER (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    employee_id INT,
    status VARCHAR(20) DEFAULT 'Active',
    FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id)
);

-- 4. CATEGORY TABLE
CREATE TABLE CATEGORY (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    description TEXT
);

-- 5. PRODUCT TABLE
CREATE TABLE PRODUCT (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    product_name VARCHAR(150) NOT NULL,
    barcode VARCHAR(50) UNIQUE,
    cost_price DECIMAL(10, 2) NOT NULL,
    selling_price DECIMAL(10, 2) NOT NULL,
    reorder_level INT DEFAULT 10,
    FOREIGN KEY (category_id) REFERENCES CATEGORY(category_id)
);

-- 6. SUPPLIER TABLE
CREATE TABLE SUPPLIER (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT
);

-- 7. CUSTOMER TABLE
CREATE TABLE CUSTOMER (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT
);

-- 8. PURCHASE TABLE
CREATE TABLE PURCHASE (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    branch_id INT NOT NULL,
    employee_id INT NOT NULL,
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(12, 2) NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES SUPPLIER(supplier_id),
    FOREIGN KEY (branch_id) REFERENCES BRANCH(branch_id),
    FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id)
);

-- 9. PURCHASE_ITEM TABLE
CREATE TABLE PURCHASE_ITEM (
    purchase_item_id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_cost DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(12, 2) NOT NULL,
    FOREIGN KEY (purchase_id) REFERENCES PURCHASE(purchase_id),
    FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id)
);

-- 10. INVENTORY TABLE
CREATE TABLE INVENTORY (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity_on_hand INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES BRANCH(branch_id),
    FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id)
);

-- 11. SALE TABLE
CREATE TABLE SALE (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    branch_id INT NOT NULL,
    employee_id INT NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(12, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id),
    FOREIGN KEY (branch_id) REFERENCES BRANCH(branch_id),
    FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id)
);

-- 12. SALE_ITEM TABLE
CREATE TABLE SALE_ITEM (
    sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(12, 2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES SALE(sale_id),
    FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id)
);

-- 13. PAYMENT TABLE
CREATE TABLE PAYMENT (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reference VARCHAR(100),
    FOREIGN KEY (sale_id) REFERENCES SALE(sale_id)
);

-- 14. EXPENSE TABLE
CREATE TABLE EXPENSE (
    expense_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT NOT NULL,
    employee_id INT NOT NULL,
    expense_type VARCHAR(100) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    expense_date DATE NOT NULL,
    description TEXT,
    FOREIGN KEY (branch_id) REFERENCES BRANCH(branch_id),
    FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id)
);