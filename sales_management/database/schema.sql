-- =====================================================================
-- RISMS - Retail Inventory and Sales Management System
-- schema.sql : database, tables, constraints, triggers, procedure, views
-- DBMS       : MySQL 8.0
-- Run order  : schema.sql -> seed_data.sql -> queries.sql (-> roles.sql optional)
-- WARNING    : drops and recreates the database every time it is run.
-- =====================================================================

DROP DATABASE IF EXISTS sales_management_db;
CREATE DATABASE sales_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sales_management_db;

-- ---------------------------------------------------------------------
-- 1. TABLES
-- ---------------------------------------------------------------------

-- 1. BRANCH (strong entity)
CREATE TABLE BRANCH (
    branch_id    INT AUTO_INCREMENT PRIMARY KEY,
    branch_name  VARCHAR(100) NOT NULL UNIQUE,
    location     VARCHAR(150) NOT NULL,
    phone        VARCHAR(20)
) ENGINE=InnoDB;

-- 2. EMPLOYEE (strong). branch_id is NULL only for system-level administrators.
CREATE TABLE EMPLOYEE (
    employee_id  INT AUTO_INCREMENT PRIMARY KEY,
    first_name   VARCHAR(50)  NOT NULL,
    last_name    VARCHAR(50)  NOT NULL,
    phone        VARCHAR(20),
    email        VARCHAR(100) UNIQUE,
    branch_id    INT NULL,
    hire_date    DATE NOT NULL,
    CONSTRAINT fk_employee_branch FOREIGN KEY (branch_id)
        REFERENCES BRANCH(branch_id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 3. USER (strong) - one login per employee (1:1)
CREATE TABLE USER (
    user_id        INT AUTO_INCREMENT PRIMARY KEY,
    username       VARCHAR(50) NOT NULL UNIQUE,
    password_hash  CHAR(64)    NOT NULL,            -- SHA-256 hex digest, never plain text
    role           ENUM('Administrator','Manager','Sales Employee','Inventory Employee') NOT NULL,
    employee_id    INT NOT NULL UNIQUE,
    status         ENUM('Active','Inactive') NOT NULL DEFAULT 'Active',
    CONSTRAINT fk_user_employee FOREIGN KEY (employee_id)
        REFERENCES EMPLOYEE(employee_id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 4. CATEGORY (strong)
CREATE TABLE CATEGORY (
    category_id    INT AUTO_INCREMENT PRIMARY KEY,
    category_name  VARCHAR(100) NOT NULL UNIQUE,
    description    TEXT
) ENGINE=InnoDB;

-- 5. PRODUCT (strong)
CREATE TABLE PRODUCT (
    product_id     INT AUTO_INCREMENT PRIMARY KEY,
    category_id    INT NOT NULL,
    product_name   VARCHAR(150) NOT NULL,
    barcode        VARCHAR(50) UNIQUE,
    cost_price     DECIMAL(10,2) NOT NULL,
    selling_price  DECIMAL(10,2) NOT NULL,
    reorder_level  INT NOT NULL DEFAULT 10,
    CONSTRAINT fk_product_category FOREIGN KEY (category_id)
        REFERENCES CATEGORY(category_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_product_prices  CHECK (cost_price >= 0 AND selling_price >= cost_price),
    CONSTRAINT chk_product_reorder CHECK (reorder_level >= 0),
    INDEX idx_product_name (product_name)
) ENGINE=InnoDB;

-- 6. SUPPLIER (strong)
CREATE TABLE SUPPLIER (
    supplier_id    INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name  VARCHAR(150) NOT NULL,
    phone          VARCHAR(20),
    email          VARCHAR(100),
    address        TEXT
) ENGINE=InnoDB;

-- 7. CUSTOMER (strong)
CREATE TABLE CUSTOMER (
    customer_id    INT AUTO_INCREMENT PRIMARY KEY,
    customer_name  VARCHAR(100) NOT NULL,
    phone          VARCHAR(20),
    email          VARCHAR(100),
    address        TEXT
) ENGINE=InnoDB;

-- 8. PURCHASE (strong). total_amount is maintained by trigger.
CREATE TABLE PURCHASE (
    purchase_id    INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id    INT NOT NULL,
    branch_id      INT NOT NULL,
    employee_id    INT NOT NULL,
    purchase_date  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount   DECIMAL(12,2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_purchase_supplier FOREIGN KEY (supplier_id) REFERENCES SUPPLIER(supplier_id),
    CONSTRAINT fk_purchase_branch   FOREIGN KEY (branch_id)   REFERENCES BRANCH(branch_id),
    CONSTRAINT fk_purchase_employee FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id),
    CONSTRAINT chk_purchase_total   CHECK (total_amount >= 0)
) ENGINE=InnoDB;

-- 9. PURCHASE_ITEM (weak / associative: Purchase <-> Product)
CREATE TABLE PURCHASE_ITEM (
    purchase_item_id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id      INT NOT NULL,
    product_id       INT NOT NULL,
    quantity         INT NOT NULL,
    unit_cost        DECIMAL(10,2) NOT NULL,
    subtotal         DECIMAL(12,2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_pi_purchase FOREIGN KEY (purchase_id) REFERENCES PURCHASE(purchase_id) ON DELETE CASCADE,
    CONSTRAINT fk_pi_product  FOREIGN KEY (product_id)  REFERENCES PRODUCT(product_id),
    CONSTRAINT chk_pi_qty  CHECK (quantity > 0),
    CONSTRAINT chk_pi_cost CHECK (unit_cost >= 0),
    UNIQUE KEY uq_purchase_product (purchase_id, product_id)
) ENGINE=InnoDB;

-- 10. INVENTORY (weak: depends on Branch + Product)
CREATE TABLE INVENTORY (
    inventory_id      INT AUTO_INCREMENT PRIMARY KEY,
    branch_id         INT NOT NULL,
    product_id        INT NOT NULL,
    quantity_on_hand  INT NOT NULL DEFAULT 0,
    last_updated      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_inv_branch  FOREIGN KEY (branch_id)  REFERENCES BRANCH(branch_id),
    CONSTRAINT fk_inv_product FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id),
    CONSTRAINT chk_inv_qty    CHECK (quantity_on_hand >= 0),      -- stock never below zero
    UNIQUE KEY uq_branch_product (branch_id, product_id)
) ENGINE=InnoDB;

-- 11. SALE (strong). customer_id NULL = walk-in. total_amount maintained by trigger.
CREATE TABLE SALE (
    sale_id       INT AUTO_INCREMENT PRIMARY KEY,
    customer_id   INT NULL,
    branch_id     INT NOT NULL,
    employee_id   INT NOT NULL,
    sale_date     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount  DECIMAL(12,2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_sale_customer FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id),
    CONSTRAINT fk_sale_branch   FOREIGN KEY (branch_id)   REFERENCES BRANCH(branch_id),
    CONSTRAINT fk_sale_employee FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id),
    CONSTRAINT chk_sale_total   CHECK (total_amount >= 0),
    INDEX idx_sale_date (sale_date)
) ENGINE=InnoDB;

-- 12. SALE_ITEM (weak / associative: Sale <-> Product)
CREATE TABLE SALE_ITEM (
    sale_item_id  INT AUTO_INCREMENT PRIMARY KEY,
    sale_id       INT NOT NULL,
    product_id    INT NOT NULL,
    quantity      INT NOT NULL,
    unit_price    DECIMAL(10,2) NOT NULL,
    subtotal      DECIMAL(12,2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_si_sale    FOREIGN KEY (sale_id)    REFERENCES SALE(sale_id) ON DELETE CASCADE,
    CONSTRAINT fk_si_product FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id),
    CONSTRAINT chk_si_qty    CHECK (quantity > 0),
    CONSTRAINT chk_si_price  CHECK (unit_price >= 0),
    UNIQUE KEY uq_sale_product (sale_id, product_id)
) ENGINE=InnoDB;

-- 13. PAYMENT (weak: depends on Sale). A sale may have several payments.
CREATE TABLE PAYMENT (
    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    sale_id         INT NOT NULL,
    payment_method  ENUM('Cash','Mobile Money','Card','Bank Transfer') NOT NULL,
    amount          DECIMAL(12,2) NOT NULL,
    payment_date    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reference       VARCHAR(100),
    CONSTRAINT fk_pay_sale FOREIGN KEY (sale_id) REFERENCES SALE(sale_id) ON DELETE CASCADE,
    CONSTRAINT chk_pay_amount CHECK (amount > 0)
) ENGINE=InnoDB;

-- 14. EXPENSE (strong)
CREATE TABLE EXPENSE (
    expense_id    INT AUTO_INCREMENT PRIMARY KEY,
    branch_id     INT NOT NULL,
    employee_id   INT NOT NULL,
    expense_type  VARCHAR(100) NOT NULL,
    amount        DECIMAL(12,2) NOT NULL,
    expense_date  DATE NOT NULL,
    description   TEXT,
    CONSTRAINT fk_exp_branch   FOREIGN KEY (branch_id)   REFERENCES BRANCH(branch_id),
    CONSTRAINT fk_exp_employee FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id),
    CONSTRAINT chk_exp_amount  CHECK (amount > 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 2. TRIGGERS  (validation + automatic stock / total maintenance)
-- ---------------------------------------------------------------------
DELIMITER $$

-- PURCHASES: compute subtotal, add stock, refresh purchase total
CREATE TRIGGER trg_purchase_item_bi BEFORE INSERT ON PURCHASE_ITEM
FOR EACH ROW
BEGIN
    SET NEW.subtotal = NEW.quantity * NEW.unit_cost;
END$$

CREATE TRIGGER trg_purchase_item_ai AFTER INSERT ON PURCHASE_ITEM
FOR EACH ROW
BEGIN
    DECLARE v_branch INT;
    SELECT branch_id INTO v_branch FROM PURCHASE WHERE purchase_id = NEW.purchase_id;

    INSERT INTO INVENTORY (branch_id, product_id, quantity_on_hand)
    VALUES (v_branch, NEW.product_id, NEW.quantity)
    ON DUPLICATE KEY UPDATE quantity_on_hand = quantity_on_hand + NEW.quantity;

    UPDATE PURCHASE
       SET total_amount = (SELECT SUM(subtotal) FROM PURCHASE_ITEM WHERE purchase_id = NEW.purchase_id)
     WHERE purchase_id = NEW.purchase_id;
END$$

-- SALES: validate stock, compute subtotal, deduct stock, refresh sale total
CREATE TRIGGER trg_sale_item_bi BEFORE INSERT ON SALE_ITEM
FOR EACH ROW
BEGIN
    DECLARE v_branch INT;
    DECLARE v_stock  INT;
    SELECT branch_id INTO v_branch FROM SALE WHERE sale_id = NEW.sale_id;
    SELECT quantity_on_hand INTO v_stock FROM INVENTORY
     WHERE branch_id = v_branch AND product_id = NEW.product_id;

    IF v_stock IS NULL OR v_stock < NEW.quantity THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Insufficient stock for this product at this branch';
    END IF;
    SET NEW.subtotal = NEW.quantity * NEW.unit_price;
END$$

CREATE TRIGGER trg_sale_item_ai AFTER INSERT ON SALE_ITEM
FOR EACH ROW
BEGIN
    DECLARE v_branch INT;
    SELECT branch_id INTO v_branch FROM SALE WHERE sale_id = NEW.sale_id;

    UPDATE INVENTORY
       SET quantity_on_hand = quantity_on_hand - NEW.quantity
     WHERE branch_id = v_branch AND product_id = NEW.product_id;

    UPDATE SALE
       SET total_amount = (SELECT SUM(subtotal) FROM SALE_ITEM WHERE sale_id = NEW.sale_id)
     WHERE sale_id = NEW.sale_id;
END$$

-- Removing a sale line returns the stock and corrects the sale total
CREATE TRIGGER trg_sale_item_ad AFTER DELETE ON SALE_ITEM
FOR EACH ROW
BEGIN
    DECLARE v_branch INT;
    SELECT branch_id INTO v_branch FROM SALE WHERE sale_id = OLD.sale_id;
    IF v_branch IS NOT NULL THEN
        UPDATE INVENTORY
           SET quantity_on_hand = quantity_on_hand + OLD.quantity
         WHERE branch_id = v_branch AND product_id = OLD.product_id;
        UPDATE SALE
           SET total_amount = IFNULL((SELECT SUM(subtotal) FROM SALE_ITEM WHERE sale_id = OLD.sale_id), 0)
         WHERE sale_id = OLD.sale_id;
    END IF;
END$$

-- PAYMENTS: a sale cannot be overpaid
CREATE TRIGGER trg_payment_bi BEFORE INSERT ON PAYMENT
FOR EACH ROW
BEGIN
    DECLARE v_total DECIMAL(12,2);
    DECLARE v_paid  DECIMAL(12,2);
    SELECT total_amount INTO v_total FROM SALE WHERE sale_id = NEW.sale_id;
    SELECT IFNULL(SUM(amount), 0) INTO v_paid FROM PAYMENT WHERE sale_id = NEW.sale_id;
    IF v_paid + NEW.amount > v_total THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Payment exceeds the outstanding balance of the sale';
    END IF;
END$$

-- USERS: only hashed passwords may be stored
CREATE TRIGGER trg_user_bi BEFORE INSERT ON USER
FOR EACH ROW
BEGIN
    IF NEW.password_hash NOT REGEXP '^[0-9a-f]{64}$' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'password_hash must be a SHA-256 hex digest';
    END IF;
END$$

-- ---------------------------------------------------------------------
-- 3. STORED PROCEDURE: authentication
--    Returns one row only if the username/password match an ACTIVE account.
-- ---------------------------------------------------------------------
CREATE PROCEDURE SP_LOGIN(IN p_username VARCHAR(50), IN p_password VARCHAR(100))
BEGIN
    SELECT u.user_id, u.username, u.role,
           e.employee_id, e.branch_id,
           CONCAT(e.first_name, ' ', e.last_name) AS full_name
      FROM USER u
      JOIN EMPLOYEE e ON e.employee_id = u.employee_id
     WHERE u.username = p_username
       AND u.password_hash = SHA2(p_password, 256)
       AND u.status = 'Active';
END$$

DELIMITER ;

-- ---------------------------------------------------------------------
-- 4. VIEWS (used by the reports)
-- ---------------------------------------------------------------------
CREATE VIEW V_LOW_STOCK AS
SELECT b.branch_name, p.product_id, p.product_name, i.quantity_on_hand, p.reorder_level
  FROM INVENTORY i
  JOIN PRODUCT p ON p.product_id = i.product_id
  JOIN BRANCH  b ON b.branch_id  = i.branch_id
 WHERE i.quantity_on_hand <= p.reorder_level;

CREATE VIEW V_INVENTORY_VALUE AS
SELECT b.branch_name,
       SUM(i.quantity_on_hand)                 AS total_units,
       SUM(i.quantity_on_hand * p.cost_price)  AS cost_value,
       SUM(i.quantity_on_hand * p.selling_price) AS retail_value
  FROM INVENTORY i
  JOIN PRODUCT p ON p.product_id = i.product_id
  JOIN BRANCH  b ON b.branch_id  = i.branch_id
 GROUP BY b.branch_name;

CREATE VIEW V_DAILY_SALES AS
SELECT DATE(sale_date) AS sale_day, COUNT(*) AS num_sales, SUM(total_amount) AS total_sales
  FROM SALE
 GROUP BY DATE(sale_date);

CREATE VIEW V_SALES_BY_EMPLOYEE AS
SELECT e.employee_id, CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
       COUNT(s.sale_id) AS num_sales, IFNULL(SUM(s.total_amount), 0) AS total_sales
  FROM EMPLOYEE e
  LEFT JOIN SALE s ON s.employee_id = e.employee_id
 GROUP BY e.employee_id, e.first_name, e.last_name;

CREATE VIEW V_BEST_SELLERS AS
SELECT p.product_id, p.product_name, SUM(si.quantity) AS units_sold, SUM(si.subtotal) AS revenue
  FROM SALE_ITEM si
  JOIN PRODUCT p ON p.product_id = si.product_id
 GROUP BY p.product_id, p.product_name;

CREATE VIEW V_SALE_BALANCE AS
SELECT s.sale_id, s.customer_id, s.sale_date, s.total_amount,
       IFNULL(SUM(pay.amount), 0)                  AS paid,
       s.total_amount - IFNULL(SUM(pay.amount), 0) AS balance
  FROM SALE s
  LEFT JOIN PAYMENT pay ON pay.sale_id = s.sale_id
 GROUP BY s.sale_id, s.customer_id, s.sale_date, s.total_amount;