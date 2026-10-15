from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection
from .models import Product
from .serializers import ProductSerializer

class ProductCreateView(APIView):
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class LowStockReportView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.product_name, i.quantity_on_hand, p.reorder_level, b.branch_name
                FROM api_inventory i
                JOIN api_product p ON i.product_id = p.product_id
                JOIN api_branch b ON i.branch_id = b.branch_id
                WHERE i.quantity_on_hand <= p.reorder_level;
            """)
            columns = [col[0] for col in cursor.description]
            results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return Response(results)