USE sales_management_db;

-- ==========================================
-- 1. BRANCH (3 Records)
-- ==========================================
INSERT INTO BRANCH (branch_id, branch_name, location, phone) VALUES 
(1, 'Main Store', 'Kampala Road, City Center', '0771234567'),
(2, 'Ntinda Branch', 'Ntinda Complex, Kisota Rd', '0752345678'),
(3, 'Wandegeya Branch', 'Wandegeya Arcade, Bombo Rd', '0783456789');

-- ==========================================
-- 2. EMPLOYEE (5 Records)
-- ==========================================
INSERT INTO EMPLOYEE (employee_id, first_name, last_name, phone, email, branch_id, hire_date) VALUES 
(1, 'John', 'Mukasa', '0701112223', 'john.mukasa@sales.com', 1, '2024-01-15'),
(2, 'Grace', 'Namubiru', '0702223334', 'grace.namubiru@sales.com', 1, '2024-03-20'),
(3, 'Brian', 'Opio', '0703334445', 'brian.opio@sales.com', 2, '2024-06-10'),
(4, 'Diana', 'Atuhaire', '0704445556', 'diana.atuhaire@sales.com', 3, '2025-01-05'),
(5, 'Admin', 'Supervisor', '0705556667', 'admin@sales.com', 1, '2023-11-01');

-- ==========================================
-- 3. USER (3 Records)
-- ==========================================
INSERT INTO USER (user_id, username, password_hash, role, employee_id, status) VALUES 
(1, 'admin_user', 'scrypt:32768:8:1$fakehash_admin', 'Administrator', 5, 'Active'),
(2, 'manager_john', 'scrypt:32768:8:1$fakehash_manager', 'Manager', 1, 'Active'),
(3, 'cashier_grace', 'scrypt:32768:8:1$fakehash_cashier', 'Sales Employee', 2, 'Active');

-- ==========================================
-- 4. CATEGORY (5 Records)
-- ==========================================
INSERT INTO CATEGORY (category_id, category_name, description) VALUES 
(1, 'Beverages', 'Soda, energy drinks, juice, and bottled water'),
(2, 'Electronics', 'Phone chargers, cables, earbuds, and small gadgets'),
(3, 'Groceries', 'Packaged flour, sugar, cooking oil, and spices'),
(4, 'Toiletries', 'Soaps, toothpaste, tissues, and detergents'),
(5, 'Stationery', 'Exercise books, pens, and office supplies');

-- ==========================================
-- 5. PRODUCT (12 Records)
-- ==========================================
INSERT INTO PRODUCT (product_id, category_id, product_name, barcode, cost_price, selling_price, reorder_level) VALUES 
(1, 1, 'Coca Cola 500ml', 'BC001', 1500.00, 2000.00, 15),
(2, 1, 'Mineral Water 500ml', 'BC002', 800.00, 1200.00, 25),
(3, 1, 'Red Bull 250ml', 'BC003', 3500.00, 5000.00, 10),
(4, 2, 'Type-C USB Cable', 'BC004', 5000.00, 8000.00, 8),
(5, 2, 'Bluetooth Earbuds', 'BC005', 25000.00, 40000.00, 5),
(6, 2, '10W Phone Charger', 'BC006', 12000.00, 18000.00, 10),
(7, 3, 'Wheat Flour 1kg', 'BC007', 4000.00, 5500.00, 12),
(8, 3, 'Sugar 1kg', 'BC008', 4500.00, 6000.00, 12),
(9, 3, 'Cooking Oil 1L', 'BC009', 8500.00, 11000.00, 10),
(10, 4, 'Geisha Soap 200g', 'BC010', 2500.00, 3500.00, 15),
(11, 4, 'Colgate Toothpaste 100g', 'BC011', 4000.00, 5500.00, 10),
(12, 5, 'Counter Book 96 Pages', 'BC012', 3000.00, 4500.00, 20);

-- ==========================================
-- 6. SUPPLIER (4 Records)
-- ==========================================
INSERT INTO SUPPLIER (supplier_id, supplier_name, phone, email, address) VALUES 
(1, 'Century Bottling Co.', '0414111222', 'supply@century.co.ug', 'Namanve Industrial Park'),
(2, 'Gadget World Ltd', '0414333444', 'sales@gadgetworld.ug', 'Kikuubo Lane, Kampala'),
(3, 'Uganda Grain Millers', '0414555666', 'orders@ugandagrain.com', 'Jinja Road'),
(4, 'Global Consumer Goods', '0414777888', 'info@globalcg.ug', 'Industrial Area');

-- ==========================================
-- 7. CUSTOMER (5 Records)
-- ==========================================
INSERT INTO CUSTOMER (customer_id, customer_name, phone, email, address) VALUES 
(1, 'Alice Namugenyi', '0779998881', 'alice@gmail.com', 'Ntinda'),
(2, 'David Kigozi', '0779998882', 'david.k@yahoo.com', 'Bukoto'),
(3, 'Sarah Akello', '0779998883', 'sakello@outlook.com', 'Muyenga'),
(4, 'Moses Ssempijja', '0779998884', 'moses.s@gmail.com', 'Kisaasi'),
(5, 'Walk-in Customer', '0000000000', 'N/A', 'Local');

-- ==========================================
-- 8. INVENTORY (Data across branches)
-- ==========================================
INSERT INTO INVENTORY (inventory_id, branch_id, product_id, quantity_on_hand) VALUES 
(1, 1, 1, 10),  -- Low stock trigger test (< 15)
(2, 1, 2, 30),
(3, 1, 4, 6),   -- Low stock trigger test (< 8)
(4, 1, 7, 15),
(5, 2, 1, 25),
(6, 2, 3, 4),   -- Low stock trigger test (< 10)
(7, 2, 5, 12),
(8, 3, 2, 20),
(9, 3, 10, 8),  -- Low stock trigger test (< 15)
(10, 3, 12, 18);

-- ==========================================
-- 9. PURCHASE & PURCHASE_ITEM (Sample Orders)
-- ==========================================
INSERT INTO PURCHASE (purchase_id, supplier_id, branch_id, employee_id, purchase_date, total_amount) VALUES 
(1, 1, 1, 1, '2026-02-01 10:00:00', 150000.00),
(2, 2, 1, 1, '2026-02-05 11:30:00', 350000.00);

INSERT INTO PURCHASE_ITEM (purchase_item_id, purchase_id, product_id, quantity, unit_cost, subtotal) VALUES 
(1, 1, 1, 50, 1500.00, 75000.00),
(2, 1, 2, 75, 800.00, 60000.00),
(3, 2, 4, 20, 5000.00, 100000.00),
(4, 2, 5, 10, 25000.00, 250000.00);

-- ==========================================
-- 10. SALE & SALE_ITEM (Sample Transactions)
-- ==========================================
INSERT INTO SALE (sale_id, customer_id, branch_id, employee_id, sale_date, total_amount) VALUES 
(1, 1, 1, 2, '2026-03-01 14:20:00', 10000.00),
(2, 2, 1, 2, '2026-03-02 15:10:00', 48000.00),
(3, 3, 2, 3, '2026-03-03 09:45:00', 11000.00);

INSERT INTO SALE_ITEM (sale_item_id, sale_id, product_id, quantity, unit_price, subtotal) VALUES 
(1, 1, 1, 2, 2000.00, 4000.00),
(2, 1, 2, 5, 1200.00, 6000.00),
(3, 2, 5, 1, 40000.00, 40000.00),
(4, 2, 1, 4, 2000.00, 8000.00),
(5, 3, 9, 1, 11000.00, 11000.00);

-- ==========================================
-- 11. PAYMENT (3 Records)
-- ==========================================
INSERT INTO PAYMENT (payment_id, sale_id, payment_method, amount, payment_date, reference) VALUES 
(1, 1, 'Cash', 10000.00, '2026-03-01 14:21:00', 'CASH-001'),
(2, 2, 'Mobile Money', 48000.00, '2026-03-02 15:12:00', 'MM-TXN-98211'),
(3, 3, 'Cash', 11000.00, '2026-03-03 09:46:00', 'CASH-002');

-- ==========================================
-- 12. EXPENSE (3 Records)
-- ==========================================
INSERT INTO EXPENSE (expense_id, branch_id, employee_id, expense_type, amount, expense_date, description) VALUES 
(1, 1, 1, 'Utility', 120000.00, '2026-02-28', 'Monthly Electricity Bill for Main Store'),
(2, 2, 3, 'Transport', 45000.00, '2026-03-01', 'Restocking fuel delivery cost'),
(3, 1, 1, 'Maintenance', 80000.00, '2026-03-02', 'Repaired cash register printer');