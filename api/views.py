from django.http import HttpResponse
from api.models import Customer,Record
from rest_framework import  viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer,CustomerSerializer,RecordSerializer

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer