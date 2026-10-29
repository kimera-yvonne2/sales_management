-- =====================================================================
-- RISMS - seed_extra.sql   (OPTIONAL: 100 additional sample rows)
-- Run AFTER schema.sql and seed_data.sql:
--     mysql -u root -p < database/seed_extra.sql
-- Do NOT run it twice (the fixed IDs would clash). To start over, re-run
-- schema.sql, seed_data.sql, then this file.
--
-- Row count added:  EMPLOYEE 2 | USER 2 | CUSTOMER 5 | SUPPLIER 2 | PRODUCT 6
--                   PURCHASE 6 | PURCHASE_ITEM 20 | SALE 12 | SALE_ITEM 27
--                   PAYMENT 12 | EXPENSE 6                     = 100
--
-- Stock and totals come from the triggers, as in seed_data.sql.
-- New demo logins:  cashier_ruth (ruth123) - Ntinda Branch
--                   cashier_samuel (samuel123) - Wandegeya Branch
-- =====================================================================
USE sales_management_db;

-- EMPLOYEE (2) + USER (2)
INSERT INTO EMPLOYEE (employee_id, first_name, last_name, phone, email, branch_id, hire_date) VALUES
(7, 'Ruth',   'Nakato', '0707778889', 'ruth.nakato@sales.com',   2, '2025-06-01'),
(8, 'Samuel', 'Okello', '0708889990', 'samuel.okello@sales.com', 3, '2025-07-15');

INSERT INTO USER (user_id, username, password_hash, role, employee_id, status) VALUES
(7, 'cashier_ruth',   SHA2('ruth123',   256), 'Sales Employee', 7, 'Active'),
(8, 'cashier_samuel', SHA2('samuel123', 256), 'Sales Employee', 8, 'Active');

-- CUSTOMER (5)
INSERT INTO CUSTOMER (customer_id, customer_name, phone, email, address) VALUES
(6,  'Kampala Girls School', '0779998885', 'bursar@kgs.ug',      'Kampala'),
(7,  'Esther Nabirye',       '0779998886', 'esther.n@gmail.com', 'Kololo'),
(8,  'Patrick Mugisha',      '0779998887', NULL,                 'Ntinda'),
(9,  'Joan Auma',            '0779998888', 'joan.auma@yahoo.com','Wandegeya'),
(10, 'Hope Supermarket',     '0779998889', 'orders@hope.ug',     'Nakawa');

-- SUPPLIER (2)
INSERT INTO SUPPLIER (supplier_id, supplier_name, phone, email, address) VALUES
(5, 'Pan Africa Wholesalers', '0414999000', 'sales@panafrica.ug', 'Nakasero Market'),
(6, 'Fresh Foods Uganda',     '0414999111', 'info@freshfoods.ug', 'Bugolobi');

-- PRODUCT (6)
INSERT INTO PRODUCT (product_id, category_id, product_name, barcode, cost_price, selling_price, reorder_level) VALUES
(13, 2, 'Flash Drive 32GB',        'BC013', 18000.00, 28000.00,  6),
(14, 1, 'Orange Juice 1L',         'BC014',  3500.00,  5000.00, 12),
(15, 4, 'Laundry Detergent 1kg',   'BC015',  6500.00,  9000.00, 10),
(16, 5, 'Black Pens (Box of 50)',  'BC016',  9000.00, 14000.00,  5),
(17, 3, 'Maize Flour 2kg',         'BC017',  5500.00,  7500.00, 12),
(18, 4, 'Hand Wash 500ml',         'BC018',  3000.00,  4500.00, 10);

-- PURCHASE (6) + PURCHASE_ITEM (20): triggers add stock and totals
INSERT INTO PURCHASE (purchase_id, supplier_id, branch_id, employee_id, purchase_date) VALUES
(8,  1, 1, 6, '2026-04-02 10:00:00'),
(9,  2, 1, 6, '2026-04-05 11:00:00'),
(10, 3, 1, 6, '2026-04-08 09:30:00'),
(11, 4, 2, 3, '2026-04-10 14:00:00'),
(12, 5, 1, 6, '2026-04-11 10:45:00'),
(13, 6, 3, 4, '2026-04-12 13:15:00');

INSERT INTO PURCHASE_ITEM (purchase_id, product_id, quantity, unit_cost) VALUES
(8,  1, 60, 1500.00),  (8,  2, 50,  800.00),   (8,  3, 30,  3500.00),
(9,  4, 25, 5000.00),  (9,  6, 10, 12000.00),  (9, 13, 30, 18000.00),
(10, 7, 30, 4000.00),  (10, 8, 20,  4500.00),  (10, 17, 40, 5500.00),
(11, 10, 30, 2500.00), (11, 15, 20, 6500.00),  (11, 18, 25, 3000.00),
(12, 14, 40, 3500.00), (12, 15, 25, 6500.00),  (12, 16, 12, 9000.00),  (12, 18, 30, 3000.00),
(13, 1, 30, 1500.00),  (13, 3, 15, 3500.00),   (13, 7, 25, 4000.00),   (13, 13, 10, 18000.00);

-- SALE (12) + SALE_ITEM (27): triggers check and deduct stock, and total each sale
INSERT INTO SALE (sale_id, customer_id, branch_id, employee_id, sale_date) VALUES
(9,  6,  1, 2, '2026-04-12 10:15:00'),
(10, 7,  1, 2, '2026-04-14 11:40:00'),
(11, 8,  2, 7, '2026-04-15 09:50:00'),
(12, 9,  3, 8, '2026-04-18 15:20:00'),
(13, 5,  1, 2, '2026-04-20 12:05:00'),
(14, 10, 1, 2, '2026-04-22 16:30:00'),
(15, 9,  2, 7, '2026-04-25 10:10:00'),
(16, 1,  1, 2, '2026-05-02 13:45:00'),
(17, 2,  3, 8, '2026-05-05 11:25:00'),
(18, 4,  1, 2, '2026-05-08 09:35:00'),
(19, 3,  2, 7, '2026-05-10 14:55:00'),
(20, 6,  1, 2, '2026-05-12 15:40:00');

INSERT INTO SALE_ITEM (sale_id, product_id, quantity, unit_price) VALUES
(9,  13, 5, 28000.00), (9,  4, 4,  8000.00),
(10, 14, 6,  5000.00), (10, 15, 2,  9000.00),
(11, 10, 10, 3500.00), (11, 18, 6,  4500.00), (11, 15, 3, 9000.00),
(12, 1, 12,  2000.00), (12, 3, 5,  5000.00),  (12, 13, 2, 28000.00),
(13, 2, 24,  1200.00), (13, 17, 4, 7500.00),
(14, 16, 4, 14000.00), (14, 12, 10, 4500.00), (14, 11, 6, 5500.00),
(15, 5, 2,  40000.00), (15, 9, 3, 11000.00),
(16, 1, 40,  2000.00), (16, 6, 8, 18000.00),
(17, 7, 10,  5500.00), (17, 10, 5, 3500.00),
(18, 17, 30, 7500.00), (18, 8, 15, 6000.00),  -- Maize flour at Main Store drops below reorder level
(19, 3, 4,   5000.00), (19, 1, 10, 2000.00),  -- Red Bull at Ntinda sells out
(20, 4, 20,  8000.00), (20, 15, 10, 9000.00); -- USB cables at Main Store drop to the reorder level

-- PAYMENT (12)
--   sale 16 : split payment (cash now, mobile money for the rest)
--   sale 18 : credit sale, nothing paid yet (no payment row)
--   sales 14 and 20 : part-paid, the customer still owes a balance
INSERT INTO PAYMENT (sale_id, payment_method, amount, payment_date, reference)
SELECT sale_id,
       CASE sale_id WHEN 10 THEN 'Mobile Money' WHEN 12 THEN 'Card' WHEN 14 THEN 'Mobile Money'
                    WHEN 15 THEN 'Bank Transfer' WHEN 19 THEN 'Mobile Money' ELSE 'Cash' END,
       CASE sale_id WHEN 14 THEN ROUND(total_amount / 2, 2)
                    WHEN 20 THEN 50000.00 ELSE total_amount END,
       DATE_ADD(sale_date, INTERVAL 2 MINUTE),
       CONCAT('REF-', LPAD(sale_id, 4, '0'))
  FROM SALE
 WHERE sale_id IN (9, 10, 11, 12, 13, 14, 15, 17, 19, 20);

INSERT INTO PAYMENT (sale_id, payment_method, amount, payment_date, reference) VALUES
(16, 'Cash', 100000.00, '2026-05-02 13:50:00', 'REF-0016A');
INSERT INTO PAYMENT (sale_id, payment_method, amount, payment_date, reference)
SELECT 16, 'Mobile Money', total_amount - 100000.00, '2026-05-02 13:55:00', 'REF-0016B'
  FROM SALE WHERE sale_id = 16;

-- EXPENSE (6)
INSERT INTO EXPENSE (expense_id, branch_id, employee_id, expense_type, amount, expense_date, description) VALUES
(7,  1, 1, 'Rent',        800000.00, '2026-04-01', 'Main Store monthly rent'),
(8,  2, 3, 'Rent',        500000.00, '2026-04-01', 'Ntinda branch monthly rent'),
(9,  3, 4, 'Utility',     110000.00, '2026-04-05', 'Wandegeya electricity bill'),
(10, 1, 6, 'Transport',    70000.00, '2026-04-09', 'Supplier delivery fuel'),
(11, 2, 7, 'Maintenance',  60000.00, '2026-04-20', 'Shelf repairs at Ntinda'),
(12, 1, 1, 'Salaries',   1500000.00, '2026-04-30', 'April staff salaries, Main Store');