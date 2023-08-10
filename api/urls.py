from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'customers', views.CustomerViewSet)
router.register(r'vendors', views.VendorViewSet)
router.register(r'saleorders', views.SaleOrderViewSet, basename='saleorders')
router.register(r'salereturns', views.SaleReturnViewSet, basename='salereturns')
router.register(r'purchaseorders', views.PurchaseOrderViewSet, basename='purchaseorders')
router.register(r'stocks', views.StockViewSet, basename='stocks')
router.register(r'productlog', views.ProductLogViewSet, basename='productlog')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'category', views.CategoryViewSet, basename='category')
router.register(r'subcategory', views.SubcategoryViewSet, basename='subcategory')
router.register(r'brand', views.BrandViewSet, basename='brand')
router.register(r'model', views.ItemModelViewSet, basename='model')
router.register(r'productloghistory', views.ProductLogHistoryViewSet, basename='productloghistory')


urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('uploadproduct/', views.UploadProduct, name="product"),
    path('ledger/', views.GetLedger, name="ledger"),
    path('login/', views.LoginView.as_view()),
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard_income_expense, name='dashboard'),
    path('printorder/', views.printorder, name='order'),
    path('movestock/', views.move_stock, name="stockmove"),
    path('movetohistory/', views.move_stock_to_history, name="stockmovehistory"),
    path('checkstock/', views.checkstock, name="checkstock")
]