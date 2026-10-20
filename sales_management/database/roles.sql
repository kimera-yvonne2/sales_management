-- =====================================================================
-- RISMS - roles.sql  (OPTIONAL, MySQL 8.0+ only)
-- Database-level access control that mirrors the application roles.
-- Run after schema.sql:  mysql -u root -p < roles.sql
-- =====================================================================
USE sales_management_db;

CREATE ROLE IF NOT EXISTS 'risms_admin', 'risms_manager', 'risms_sales', 'risms_inventory';

-- Administrator: everything
GRANT ALL PRIVILEGES ON sales_management_db.* TO 'risms_admin';

-- Manager: read everything, record expenses
GRANT SELECT ON sales_management_db.* TO 'risms_manager';
GRANT INSERT, UPDATE ON sales_management_db.EXPENSE TO 'risms_manager';

-- Sales employee: record sales and customers (UPDATE on stock/total is done by triggers)
GRANT SELECT ON sales_management_db.PRODUCT   TO 'risms_sales';
GRANT SELECT, UPDATE ON sales_management_db.INVENTORY TO 'risms_sales';
GRANT SELECT, INSERT ON sales_management_db.CUSTOMER  TO 'risms_sales';
GRANT SELECT, INSERT, UPDATE ON sales_management_db.SALE      TO 'risms_sales';
GRANT SELECT, INSERT ON sales_management_db.SALE_ITEM TO 'risms_sales';
GRANT SELECT, INSERT ON sales_management_db.PAYMENT   TO 'risms_sales';

-- Inventory employee: record purchases and maintain stock
GRANT SELECT ON sales_management_db.PRODUCT  TO 'risms_inventory';
GRANT SELECT ON sales_management_db.SUPPLIER TO 'risms_inventory';
GRANT SELECT, INSERT, UPDATE ON sales_management_db.INVENTORY     TO 'risms_inventory';
GRANT SELECT, INSERT, UPDATE ON sales_management_db.PURCHASE      TO 'risms_inventory';
GRANT SELECT, INSERT         ON sales_management_db.PURCHASE_ITEM TO 'risms_inventory';

-- Example: create a login and give it a role
--   CREATE USER 'cashier_app'@'localhost' IDENTIFIED BY 'ChangeMe!123';
--   GRANT 'risms_sales' TO 'cashier_app'@'localhost';
--   SET DEFAULT ROLE 'risms_sales' TO 'cashier_app'@'localhost';