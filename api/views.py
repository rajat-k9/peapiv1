from rest_framework import views
from django.http import HttpResponse
from api.models import Customer,Record,Stock
from rest_framework import  viewsets
from django.contrib.auth.models import User
from django.contrib.auth import login

from api.scripts import web_script
from .serializers import UserSerializer,CustomerSerializer,RecordSerializer,StockSerializer,LoginSerializer
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

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

class LoginView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = LoginSerializer(data=self.request.data,
            context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        data = {"userid":User.objects.get(username=user).pk}
        return Response(data, status=status.HTTP_202_ACCEPTED)

    