from django.urls import path, include

from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'customers', views.CustomerViewSet)
router.register(r'records', views.RecordViewSet, basename='records')
router.register(r'stocks', views.StockViewSet, basename='stocks')

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('invokewhatsapp/', views.InvokeWhatsApp, name="whatsapp"),
    path('login/', views.LoginView.as_view()),
    path('', views.index, name='index'),
]