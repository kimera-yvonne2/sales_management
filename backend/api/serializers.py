from rest_framework import serializers
from .models import (
    Branch, Employee, User, Category, Product, Supplier, 
    Customer, Purchase, PurchaseItem, Inventory, Sale, SaleItem, Payment, Expense
)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)

    class Meta:
        model = Inventory
        fields = '__all__'

class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = '__all__'

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = '__all__'

# Add other model serializers as needed for your application modules