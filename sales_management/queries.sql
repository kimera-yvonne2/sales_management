-- Query 1: Total Sales Revenue per Branch
SELECT b.branch_name, COUNT(s.sale_id) AS total_transactions, SUM(s.total_amount) AS total_revenue
FROM sale s
JOIN branch b ON s.branch_id = b.branch_id
GROUP BY b.branch_id, b.branch_name;

-- Query 2: Purchase History by Supplier
SELECT pur.purchase_id, s.supplier_name, pur.purchase_date, pur.total_amount, b.branch_name
FROM purchase pur
JOIN supplier s ON pur.supplier_id = s.supplier_id
JOIN branch b ON pur.branch_id = b.branch_id
WHERE s.supplier_id = 1;

-- Query 3: Low Stock Alert
SELECT p.product_name, i.quantity_on_hand, p.reorder_level, b.branch_name
FROM inventory i
JOIN product p ON i.product_id = p.product_id
JOIN branch b ON i.branch_id = b.branch_id
WHERE i.quantity_on_hand <= p.reorder_level;


