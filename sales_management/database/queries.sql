-- =====================================================================
-- RISMS - queries.sql   (run AFTER schema.sql and seed_data.sql)
-- Section A: the 9 queries required by the proposal
-- Section B: INSERT / UPDATE / DELETE (wrapped in a transaction, then rolled back
--            so the sample data is left unchanged)
-- Section C: extra JOIN, aggregate and management reports
-- Section D: constraint / trigger demonstrations (each should FAIL)
-- =====================================================================
USE sales_management_db;

-- =====================================================================
-- A. REQUIRED QUERIES
-- =====================================================================

-- Q1: Products at or below their reorder level
SELECT p.product_name, b.branch_name, i.quantity_on_hand, p.reorder_level
  FROM INVENTORY i
  JOIN PRODUCT p ON i.product_id = p.product_id
  JOIN BRANCH  b ON i.branch_id  = b.branch_id
 WHERE i.quantity_on_hand <= p.reorder_level
 ORDER BY b.branch_name, p.product_name;

-- Q2: Total sales for a selected period (change the dates as needed)
SELECT IFNULL(SUM(total_amount), 0) AS total_sales, COUNT(sale_id) AS total_transactions
  FROM SALE
 WHERE sale_date BETWEEN '2026-03-01 00:00:00' AND '2026-03-31 23:59:59';

--     Q2 variations: per day, per week, per month
SELECT * FROM V_DAILY_SALES ORDER BY sale_day;
SELECT YEARWEEK(sale_date, 1) AS year_week, SUM(total_amount) AS total_sales
  FROM SALE GROUP BY YEARWEEK(sale_date, 1) ORDER BY year_week;
SELECT DATE_FORMAT(sale_date, '%Y-%m') AS month, SUM(total_amount) AS total_sales
  FROM SALE GROUP BY DATE_FORMAT(sale_date, '%Y-%m');

-- Q3: Products supplied by a particular supplier (supplier_id = 1)
--     Connected through PURCHASE and PURCHASE_ITEM
SELECT DISTINCT p.product_name, c.category_name, sup.supplier_name
  FROM PURCHASE_ITEM pi
  JOIN PURCHASE pur ON pi.purchase_id = pur.purchase_id
  JOIN PRODUCT  p   ON pi.product_id  = p.product_id
  JOIN CATEGORY c   ON p.category_id  = c.category_id
  JOIN SUPPLIER sup ON pur.supplier_id = sup.supplier_id
 WHERE sup.supplier_id = 1;

-- Q4: Sales made by each employee (employees with no sales show 0, not NULL)
SELECT e.employee_id, CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
       COUNT(s.sale_id) AS total_sales_made,
       IFNULL(SUM(s.total_amount), 0) AS total_revenue
  FROM EMPLOYEE e
  LEFT JOIN SALE s ON e.employee_id = s.employee_id
 GROUP BY e.employee_id, employee_name
 ORDER BY total_revenue DESC;

-- Q5: Total value of inventory at a branch (branch_id = 1)
SELECT b.branch_name,
       SUM(i.quantity_on_hand * p.cost_price)    AS total_inventory_cost_value,
       SUM(i.quantity_on_hand * p.selling_price) AS total_inventory_retail_value
  FROM INVENTORY i
  JOIN PRODUCT p ON i.product_id = p.product_id
  JOIN BRANCH  b ON i.branch_id  = b.branch_id
 WHERE i.branch_id = 1
 GROUP BY b.branch_name;

-- Q6: Best-selling products
SELECT p.product_name, SUM(si.quantity) AS total_quantity_sold, SUM(si.subtotal) AS total_revenue
  FROM SALE_ITEM si
  JOIN PRODUCT p ON si.product_id = p.product_id
 GROUP BY p.product_id, p.product_name
 ORDER BY total_quantity_sold DESC
 LIMIT 5;

-- Q7: Purchase history for a supplier (supplier_id = 1)
SELECT pur.purchase_id, sup.supplier_name, b.branch_name, pur.purchase_date, pur.total_amount
  FROM PURCHASE pur
  JOIN SUPPLIER sup ON pur.supplier_id = sup.supplier_id
  JOIN BRANCH   b   ON pur.branch_id   = b.branch_id
 WHERE sup.supplier_id = 1
 ORDER BY pur.purchase_date;

-- Q8: A customer's sales history (customer_id = 1)
SELECT s.sale_id, c.customer_name, s.sale_date, s.total_amount, b.branch_name
  FROM SALE s
  JOIN CUSTOMER c ON s.customer_id = c.customer_id
  JOIN BRANCH   b ON s.branch_id   = b.branch_id
 WHERE c.customer_id = 1
 ORDER BY s.sale_date;

-- Q9: Total expenses for a selected period
SELECT expense_type, SUM(amount) AS total_expense_amount
  FROM EXPENSE
 WHERE expense_date BETWEEN '2026-02-01' AND '2026-03-31'
 GROUP BY expense_type
 ORDER BY total_expense_amount DESC;

-- =====================================================================
-- B. INSERT / UPDATE / DELETE  (rolled back at the end)
-- =====================================================================
START TRANSACTION;

-- INSERT a product, then restock it (the trigger updates INVENTORY and the purchase total)
INSERT INTO PRODUCT (category_id, product_name, barcode, cost_price, selling_price, reorder_level)
VALUES (1, 'Orange Juice 1L', 'BC013', 3500.00, 5000.00, 12);
SET @new_product = LAST_INSERT_ID();

INSERT INTO PURCHASE (supplier_id, branch_id, employee_id) VALUES (1, 1, 6);
SET @new_purchase = LAST_INSERT_ID();
INSERT INTO PURCHASE_ITEM (purchase_id, product_id, quantity, unit_cost)
VALUES (@new_purchase, @new_product, 40, 3500.00);

SELECT p.product_name, i.quantity_on_hand FROM INVENTORY i
  JOIN PRODUCT p ON p.product_id = i.product_id WHERE p.product_id = @new_product;

-- UPDATE a price and deactivate a user
UPDATE PRODUCT SET selling_price = 12000.00 WHERE product_name = 'Cooking Oil 1L';
UPDATE USER    SET status = 'Inactive'      WHERE username = 'store_peter';

-- DELETE a sale line: stock is returned and the sale total corrected by the trigger
DELETE FROM SALE_ITEM WHERE sale_id = 1 AND product_id = 2;
SELECT total_amount FROM SALE WHERE sale_id = 1;

-- DELETE a record that has no dependants
DELETE FROM EXPENSE WHERE expense_id = 6;

ROLLBACK;

-- =====================================================================
-- C. EXTRA JOIN / AGGREGATE / MANAGEMENT REPORTS
-- =====================================================================

-- C1. Full detail of every sale line (6-table JOIN)
SELECT s.sale_id, s.sale_date, b.branch_name,
       CONCAT(e.first_name, ' ', e.last_name) AS cashier,
       IFNULL(c.customer_name, 'Walk-in')     AS customer,
       p.product_name, si.quantity, si.unit_price, si.subtotal
  FROM SALE s
  JOIN SALE_ITEM si ON si.sale_id = s.sale_id
  JOIN PRODUCT   p  ON p.product_id = si.product_id
  JOIN BRANCH    b  ON b.branch_id  = s.branch_id
  JOIN EMPLOYEE  e  ON e.employee_id = s.employee_id
  LEFT JOIN CUSTOMER c ON c.customer_id = s.customer_id
 ORDER BY s.sale_id, p.product_name;

-- C2. Outstanding customer balances
SELECT sb.sale_id, IFNULL(c.customer_name, 'Walk-in') AS customer,
       sb.total_amount, sb.paid, sb.balance
  FROM V_SALE_BALANCE sb
  LEFT JOIN CUSTOMER c ON c.customer_id = sb.customer_id
 WHERE sb.balance > 0;

-- C3. Gross profit per product (revenue minus cost of goods sold)
SELECT p.product_name, SUM(si.quantity) AS units_sold, SUM(si.subtotal) AS revenue,
       SUM(si.quantity * p.cost_price)                AS cost_of_goods,
       SUM(si.subtotal - si.quantity * p.cost_price)  AS gross_profit
  FROM SALE_ITEM si JOIN PRODUCT p ON p.product_id = si.product_id
 GROUP BY p.product_name
 ORDER BY gross_profit DESC;

-- C4. Revenue vs expenses per branch
SELECT b.branch_name,
       IFNULL((SELECT SUM(total_amount) FROM SALE    WHERE branch_id = b.branch_id), 0) AS revenue,
       IFNULL((SELECT SUM(amount)       FROM EXPENSE WHERE branch_id = b.branch_id), 0) AS expenses
  FROM BRANCH b;

-- C5. Takings by payment method
SELECT payment_method, COUNT(*) AS payments, SUM(amount) AS total_received
  FROM PAYMENT GROUP BY payment_method;

-- C6. Revenue by category
SELECT c.category_name, SUM(si.subtotal) AS revenue
  FROM SALE_ITEM si
  JOIN PRODUCT  p ON p.product_id  = si.product_id
  JOIN CATEGORY c ON c.category_id = p.category_id
 GROUP BY c.category_name ORDER BY revenue DESC;

-- C7. Stock of every product at every branch
SELECT b.branch_name, p.product_name, i.quantity_on_hand, p.reorder_level
  FROM INVENTORY i
  JOIN BRANCH  b ON b.branch_id  = i.branch_id
  JOIN PRODUCT p ON p.product_id = i.product_id
 ORDER BY b.branch_name, p.product_name;

-- C8. Report views
SELECT * FROM V_INVENTORY_VALUE;
SELECT * FROM V_SALES_BY_EMPLOYEE ORDER BY total_sales DESC;

-- =====================================================================
-- D. CONSTRAINT / TRIGGER DEMOS  - each statement below should FAIL.
--    Remove the leading "-- " and run one at a time.
-- =====================================================================
-- D1. Selling more than the stock available
--   INSERT INTO SALE (customer_id, branch_id, employee_id) VALUES (NULL, 1, 2);
--   INSERT INTO SALE_ITEM (sale_id, product_id, quantity, unit_price) VALUES (LAST_INSERT_ID(), 4, 9999, 8000);
-- D2. Overpaying a sale
--   INSERT INTO PAYMENT (sale_id, payment_method, amount) VALUES (1, 'Cash', 1000000);
-- D3. Selling price below cost price
--   INSERT INTO PRODUCT (category_id, product_name, cost_price, selling_price) VALUES (1, 'Bad', 500, 100);
-- D4. Storing a plain-text password
--   INSERT INTO USER (username, password_hash, role, employee_id) VALUES ('hack', 'plain', 'Manager', 4);
-- D5. Product with a category that does not exist (referential integrity)
--   INSERT INTO PRODUCT (category_id, product_name, cost_price, selling_price) VALUES (99, 'Orphan', 1, 2);
-- D6. Duplicate barcode
--   INSERT INTO PRODUCT (category_id, product_name, barcode, cost_price, selling_price) VALUES (1, 'Dup', 'BC001', 1, 2);
-- D7. Invalid role
--   UPDATE USER SET role = 'Hacker' WHERE user_id = 1;