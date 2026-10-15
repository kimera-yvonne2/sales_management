USE sales_management_db;

-- Q1: Display all products currently below their reorder level[cite: 5]
SELECT p.product_name, b.branch_name, i.quantity_on_hand, p.reorder_level
FROM INVENTORY i
JOIN PRODUCT p ON i.product_id = p.product_id
JOIN BRANCH b ON i.branch_id = b.branch_id
WHERE i.quantity_on_hand <= p.reorder_level;

-- Q2: Calculate total sales for a selected period[cite: 5]
SELECT SUM(total_amount) AS total_sales, COUNT(sale_id) AS total_transactions
FROM SALE
WHERE sale_date BETWEEN '2026-01-01 00:00:00' AND '2026-12-31 23:59:59';

-- Q3: List all products supplied by a particular supplier (e.g., supplier_id = 1)[cite: 5]
-- Note: Connected through PURCHASE and PURCHASE_ITEM tables
SELECT DISTINCT p.product_name, c.category_name, sup.supplier_name
FROM PURCHASE_ITEM pi
JOIN PURCHASE pur ON pi.purchase_id = pur.purchase_id
JOIN PRODUCT p ON pi.product_id = p.product_id
JOIN CATEGORY c ON p.category_id = c.category_id
JOIN SUPPLIER sup ON pur.supplier_id = sup.supplier_id
WHERE sup.supplier_id = 1;

-- Q4: Show the sales made by each employee[cite: 5]
SELECT e.employee_id, CONCAT(e.first_name, ' ', e.last_name) AS employee_name, 
       COUNT(s.sale_id) AS total_sales_made, SUM(s.total_amount) AS total_revenue
FROM EMPLOYEE e
LEFT JOIN SALE s ON e.employee_id = s.employee_id
GROUP BY e.employee_id, employee_name;

-- Q5: Calculate the total value of inventory at a branch (e.g., branch_id = 1)[cite: 5]
SELECT b.branch_name, SUM(i.quantity_on_hand * p.cost_price) AS total_inventory_cost_value,
       SUM(i.quantity_on_hand * p.selling_price) AS total_inventory_retail_value
FROM INVENTORY i
JOIN PRODUCT p ON i.product_id = p.product_id
JOIN BRANCH b ON i.branch_id = b.branch_id
WHERE i.branch_id = 1
GROUP BY b.branch_name;

-- Q6: Identify the best-selling products[cite: 5]
SELECT p.product_name, SUM(si.quantity) AS total_quantity_sold, SUM(si.subtotal) AS total_revenue
FROM SALE_ITEM si
JOIN PRODUCT p ON si.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_quantity_sold DESC
LIMIT 5;

-- Q7: Display purchase history for a supplier[cite: 5]
SELECT pur.purchase_id, sup.supplier_name, b.branch_name, pur.purchase_date, pur.total_amount
FROM PURCHASE pur
JOIN SUPPLIER sup ON pur.supplier_id = sup.supplier_id
JOIN BRANCH b ON pur.branch_id = b.branch_id
WHERE sup.supplier_id = 1;

-- Q8: Retrieve a customer's sales history (e.g., customer_id = 1)[cite: 5]
SELECT s.sale_id, c.customer_name, s.sale_date, s.total_amount, b.branch_name
FROM SALE s
JOIN CUSTOMER c ON s.customer_id = c.customer_id
JOIN BRANCH b ON s.branch_id = b.branch_id
WHERE c.customer_id = 1;

-- Q9: Calculate total expenses for a selected period[cite: 5]
SELECT expense_type, SUM(amount) AS total_expense_amount
FROM EXPENSE
WHERE expense_date BETWEEN '2026-01-01' AND '2026-12-31'
GROUP BY expense_type;