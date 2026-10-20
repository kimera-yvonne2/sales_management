-- =====================================================================
-- RISMS - seed_data.sql   (run AFTER schema.sql)
-- Stock levels and sale/purchase totals are produced by the triggers,
-- so inventory always reconciles with purchases and sales.
--
-- Demo logins (password in brackets):
--   admin_user (admin123)      Administrator
--   manager_john (manager123)  Manager
--   cashier_grace (cashier123) Sales Employee   - Main Store
--   cashier_brian (brian123)   Sales Employee   - Ntinda Branch
--   store_peter (store123)     Inventory Employee - Main Store
--   cashier_diana (diana123)   Sales Employee   - INACTIVE (login is rejected)
-- =====================================================================
USE sales_management_db;

-- 1. BRANCH (3)
INSERT INTO BRANCH (branch_id, branch_name, location, phone) VALUES
(1, 'Main Store',       'Kampala Road, City Center',  '0771234567'),
(2, 'Ntinda Branch',    'Ntinda Complex, Kisota Rd',  '0752345678'),
(3, 'Wandegeya Branch', 'Wandegeya Arcade, Bombo Rd', '0783456789');

-- 2. EMPLOYEE (6)  - the system administrator has no branch (NULL)
INSERT INTO EMPLOYEE (employee_id, first_name, last_name, phone, email, branch_id, hire_date) VALUES
(1, 'John',  'Mukasa',   '0701112223', 'john.mukasa@sales.com',     1,    '2024-01-15'),
(2, 'Grace', 'Namubiru', '0702223334', 'grace.namubiru@sales.com',  1,    '2024-03-20'),
(3, 'Brian', 'Opio',     '0703334445', 'brian.opio@sales.com',      2,    '2024-06-10'),
(4, 'Diana', 'Atuhaire', '0704445556', 'diana.atuhaire@sales.com',  3,    '2025-01-05'),
(5, 'Admin', 'Supervisor','0705556667','admin@sales.com',           NULL, '2023-11-01'),
(6, 'Peter', 'Ssali',    '0706667778', 'peter.ssali@sales.com',     1,    '2025-02-10');

-- 3. USER (6)  - passwords are stored as SHA-256 hashes
INSERT INTO USER (user_id, username, password_hash, role, employee_id, status) VALUES
(1, 'admin_user',    SHA2('admin123',   256), 'Administrator',      5, 'Active'),
(2, 'manager_john',  SHA2('manager123', 256), 'Manager',            1, 'Active'),
(3, 'cashier_grace', SHA2('cashier123', 256), 'Sales Employee',     2, 'Active'),
(4, 'cashier_brian', SHA2('brian123',   256), 'Sales Employee',     3, 'Active'),
(5, 'store_peter',   SHA2('store123',   256), 'Inventory Employee', 6, 'Active'),
(6, 'cashier_diana', SHA2('diana123',   256), 'Sales Employee',     4, 'Inactive');

-- 4. CATEGORY (5)
INSERT INTO CATEGORY (category_id, category_name, description) VALUES
(1, 'Beverages',   'Soda, energy drinks, juice, and bottled water'),
(2, 'Electronics', 'Phone chargers, cables, earbuds, and small gadgets'),
(3, 'Groceries',   'Packaged flour, sugar, cooking oil, and spices'),
(4, 'Toiletries',  'Soaps, toothpaste, tissues, and detergents'),
(5, 'Stationery',  'Exercise books, pens, and office supplies');

-- 5. PRODUCT (12)
INSERT INTO PRODUCT (product_id, category_id, product_name, barcode, cost_price, selling_price, reorder_level) VALUES
(1,  1, 'Coca Cola 500ml',          'BC001', 1500.00,  2000.00, 15),
(2,  1, 'Mineral Water 500ml',      'BC002',  800.00,  1200.00, 25),
(3,  1, 'Red Bull 250ml',           'BC003', 3500.00,  5000.00, 10),
(4,  2, 'Type-C USB Cable',         'BC004', 5000.00,  8000.00,  8),
(5,  2, 'Bluetooth Earbuds',        'BC005',25000.00, 40000.00,  5),
(6,  2, '10W Phone Charger',        'BC006',12000.00, 18000.00, 10),
(7,  3, 'Wheat Flour 1kg',          'BC007', 4000.00,  5500.00, 12),
(8,  3, 'Sugar 1kg',                'BC008', 4500.00,  6000.00, 12),
(9,  3, 'Cooking Oil 1L',           'BC009', 8500.00, 11000.00, 10),
(10, 4, 'Geisha Soap 200g',         'BC010', 2500.00,  3500.00, 15),
(11, 4, 'Colgate Toothpaste 100g',  'BC011', 4000.00,  5500.00, 10),
(12, 5, 'Counter Book 96 Pages',    'BC012', 3000.00,  4500.00, 20);

-- 6. SUPPLIER (4)
INSERT INTO SUPPLIER (supplier_id, supplier_name, phone, email, address) VALUES
(1, 'Century Bottling Co.',   '0414111222', 'supply@century.co.ug',   'Namanve Industrial Park'),
(2, 'Gadget World Ltd',       '0414333444', 'sales@gadgetworld.ug',   'Kikuubo Lane, Kampala'),
(3, 'Uganda Grain Millers',   '0414555666', 'orders@ugandagrain.com', 'Jinja Road'),
(4, 'Global Consumer Goods',  '0414777888', 'info@globalcg.ug',       'Industrial Area');

-- 7. CUSTOMER (5)
INSERT INTO CUSTOMER (customer_id, customer_name, phone, email, address) VALUES
(1, 'Alice Namugenyi',   '0779998881', 'alice@gmail.com',     'Ntinda'),
(2, 'David Kigozi',      '0779998882', 'david.k@yahoo.com',   'Bukoto'),
(3, 'Sarah Akello',      '0779998883', 'sakello@outlook.com', 'Muyenga'),
(4, 'Moses Ssempijja',   '0779998884', 'moses.s@gmail.com',   'Kisaasi'),
(5, 'Walk-in Customer',  '0000000000', NULL,                  'Local');

-- 8. PURCHASE + PURCHASE_ITEM (7 purchases, 17 lines)
--    Triggers add the stock to INVENTORY and compute each purchase total.
INSERT INTO PURCHASE (purchase_id, supplier_id, branch_id, employee_id, purchase_date) VALUES
(1, 1, 1, 6, '2026-02-01 10:00:00'),
(2, 2, 1, 6, '2026-02-05 11:30:00'),
(3, 3, 1, 6, '2026-02-08 09:15:00'),
(4, 4, 1, 6, '2026-02-10 13:40:00'),
(5, 1, 2, 3, '2026-02-12 10:20:00'),
(6, 2, 2, 3, '2026-02-13 15:00:00'),
(7, 4, 3, 4, '2026-02-15 11:10:00');

INSERT INTO PURCHASE_ITEM (purchase_id, product_id, quantity, unit_cost) VALUES
(1, 1, 50, 1500.00),  (1, 2, 75,  800.00),
(2, 4, 20, 5000.00),  (2, 5, 10, 25000.00), (2, 6, 15, 12000.00),
(3, 7, 40, 4000.00),  (3, 8, 40, 4500.00),  (3, 9, 20,  8500.00),
(4, 10, 40, 2500.00), (4, 11, 30, 4000.00), (4, 12, 50, 3000.00),
(5, 1, 40, 1500.00),  (5, 3, 12, 3500.00),  (5, 9, 10,  8500.00),
(6, 5, 15, 25000.00),
(7, 2, 30,  800.00),  (7, 10, 20, 2500.00), (7, 12, 25, 3000.00);

-- 9. SALE + SALE_ITEM (8 sales, 18 lines)
--    Triggers check stock, deduct it, and compute each sale total.
INSERT INTO SALE (sale_id, customer_id, branch_id, employee_id, sale_date) VALUES
(1, 1, 1, 2, '2026-03-01 14:20:00'),
(2, 2, 1, 2, '2026-03-02 15:10:00'),
(3, 3, 2, 3, '2026-03-03 09:45:00'),
(4, 4, 1, 2, '2026-03-05 10:30:00'),
(5, 5, 1, 2, '2026-03-08 16:05:00'),
(6, 1, 2, 3, '2026-03-10 11:50:00'),
(7, 2, 3, 4, '2026-03-12 12:40:00'),
(8, 3, 1, 2, '2026-03-15 13:30:00');

INSERT INTO SALE_ITEM (sale_id, product_id, quantity, unit_price) VALUES
(1, 1, 2, 2000.00),  (1, 2, 5, 1200.00),
(2, 5, 1, 40000.00), (2, 1, 4, 2000.00),
(3, 9, 1, 11000.00),
(4, 4, 13, 8000.00),                          -- wholesale: USB cable drops below reorder level
(5, 1, 30, 2000.00),                          -- Coca Cola at Main Store drops below reorder level
(6, 3, 8, 5000.00),  (6, 1, 5, 2000.00),      -- Red Bull at Ntinda drops below reorder level
(7, 10, 6, 3500.00), (7, 12, 4, 4500.00),     -- Geisha soap at Wandegeya drops below reorder level
(8, 7, 6, 5500.00),  (8, 8, 4, 6000.00), (8, 11, 3, 5500.00);

-- 10. PAYMENT (9 records): full payments read the computed sale total.
INSERT INTO PAYMENT (sale_id, payment_method, amount, payment_date, reference)
SELECT sale_id,
       CASE sale_id WHEN 2 THEN 'Mobile Money' WHEN 4 THEN 'Mobile Money'
                    WHEN 6 THEN 'Card'        WHEN 7 THEN 'Mobile Money' ELSE 'Cash' END,
       CASE sale_id WHEN 4 THEN 60000.00 ELSE total_amount END,     -- sale 4 is part-paid
       DATE_ADD(sale_date, INTERVAL 1 MINUTE),
       CASE sale_id WHEN 1 THEN 'CASH-001' WHEN 2 THEN 'MM-TXN-98211' WHEN 3 THEN 'CASH-002'
                    WHEN 4 THEN 'MM-TXN-98300' WHEN 5 THEN 'CASH-003' WHEN 6 THEN 'CARD-4421'
                    WHEN 7 THEN 'MM-TXN-98455' ELSE 'CASH-004' END
  FROM SALE;

-- Sale 4: the customer settles part of the balance later (split / instalment payment)
INSERT INTO PAYMENT (sale_id, payment_method, amount, payment_date, reference) VALUES
(4, 'Cash', 20000.00, '2026-03-09 09:00:00', 'CASH-005');

-- 11. EXPENSE (6)
INSERT INTO EXPENSE (expense_id, branch_id, employee_id, expense_type, amount, expense_date, description) VALUES
(1, 1, 1, 'Utility',     120000.00, '2026-02-28', 'Monthly Electricity Bill for Main Store'),
(2, 2, 3, 'Transport',    45000.00, '2026-03-01', 'Restocking fuel delivery cost'),
(3, 1, 1, 'Maintenance',  80000.00, '2026-03-02', 'Repaired cash register printer'),
(4, 3, 4, 'Rent',        600000.00, '2026-03-01', 'Wandegeya monthly rent'),
(5, 2, 3, 'Utility',      90000.00, '2026-03-04', 'Ntinda water and electricity'),
(6, 1, 1, 'Licence',     150000.00, '2026-03-06', 'Trading licence renewal');