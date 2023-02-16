from django.http import HttpResponse
from api.models import Customer,Record,Stock
from rest_framework import  viewsets
from django.contrib.auth.models import User

from api.scripts import web_script
from .serializers import UserSerializer,CustomerSerializer,RecordSerializer,StockSerializer
from rest_framework import permissions

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


def InvokeWhatsApp(request):
    permission_classes = [permissions.AllowAny]
    return HttpResponse(web_script.call_api())

    