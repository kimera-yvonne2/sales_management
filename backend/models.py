# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Branch(models.Model):
    branch_id = models.AutoField(primary_key=True)
    branch_name = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'branch'


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(unique=True, max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'category'


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customer'


class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(unique=True, max_length=15, blank=True, null=True)
    email = models.CharField(unique=True, max_length=100, blank=True, null=True)
    branch = models.ForeignKey(Branch, models.DO_NOTHING)
    hire_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'employee'


class Expense(models.Model):
    expense_id = models.AutoField(primary_key=True)
    branch = models.ForeignKey(Branch, models.DO_NOTHING)
    employee = models.ForeignKey(Employee, models.DO_NOTHING, blank=True, null=True)
    expense_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField()
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'expense'


class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    branch = models.ForeignKey(Branch, models.DO_NOTHING)
    product = models.ForeignKey('Product', models.DO_NOTHING)
    quantity_on_hand = models.IntegerField()
    last_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'inventory'
        unique_together = (('branch', 'product'),)


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    sale = models.ForeignKey('Sale', models.DO_NOTHING)
    payment_method = models.CharField(max_length=13)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(blank=True, null=True)
    reference = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment'


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, models.DO_NOTHING)
    product_name = models.CharField(max_length=100)
    barcode = models.CharField(unique=True, max_length=50, blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product'


class Purchase(models.Model):
    purchase_id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey('Supplier', models.DO_NOTHING)
    branch = models.ForeignKey(Branch, models.DO_NOTHING)
    employee = models.ForeignKey(Employee, models.DO_NOTHING)
    purchase_date = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'purchase'


class PurchaseItem(models.Model):
    purchase_item_id = models.AutoField(primary_key=True)
    purchase = models.ForeignKey(Purchase, models.DB_CASCADE)
    product = models.ForeignKey(Product, models.DO_NOTHING)
    quantity = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'purchase_item'


class Sale(models.Model):
    sale_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, models.DO_NOTHING, blank=True, null=True)
    branch = models.ForeignKey(Branch, models.DO_NOTHING)
    employee = models.ForeignKey(Employee, models.DO_NOTHING)
    sale_date = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'sale'


class SaleItem(models.Model):
    sale_item_id = models.AutoField(primary_key=True)
    sale = models.ForeignKey(Sale, models.DB_CASCADE)
    product = models.ForeignKey(Product, models.DO_NOTHING)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'sale_item'


class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'supplier'


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=14)
    employee = models.ForeignKey(Employee, models.DO_NOTHING, blank=True, null=True)
    status = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'
