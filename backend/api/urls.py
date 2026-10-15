from django.urls import path
from .views import ProductCreateView, LowStockReportView

urlpatterns = [
    path('api/products/', ProductCreateView.as_view(), name='product-create'),
    path('api/reports/low-stock/', LowStockReportView.as_view(), name='low-stock-report'),
]