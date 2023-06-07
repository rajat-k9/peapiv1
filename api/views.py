import random
import string
import csv
from rest_framework import views, filters
from django.http import HttpResponse
from api.models import Customer, Payment,Record,Stock,Product, Vendor
from rest_framework import  viewsets
from django.contrib.auth.models import User
from django.contrib.auth import login

from api.scripts import web_script
from .serializers import PaymentSerializer, ProductSerializer, UserSerializer,CustomerSerializer,RecordSerializer,StockSerializer,LoginSerializer, VendorSerializer
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

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


class VendorViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Vendor.objects.all().order_by("name")
    serializer_class = VendorSerializer
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)


def _updatestock(id):
    try:
        if Stock.objects.get(product_id = id):
            stock = Stock.objects.get(product_id = id)
            stock.shop = stock.shop - 1
            stock.save()
    except:
        pass

class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer

    def list(self, request):
        if request.method == 'GET':
            queryset = Record.objects.all()
            from_date = request.GET.get('from', None)
            to_date = request.GET.get('to', None)
            if from_date is not None:
                queryset = self.queryset.filter(sale_date__range=[from_date, to_date])
            serializer_class = RecordSerializer(queryset, many=True)
            return Response(serializer_class.data)


    def create(self, request):
        orderid = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=7))
        if "customer" in request.data[0]:
            new_data = request.data[0].pop('customer')
            customer, created = Customer.objects.get_or_create(name=new_data["name"],contact=new_data["contact"])
            for rec in request.data:
                serializer = RecordSerializer(data=rec)
                if serializer.is_valid():
                    serializer.validated_data['order_id'] = orderid
                    serializer.validated_data['customer'] = customer 
                    serializer.save()
                    _updatestock(rec["sku"])
            return Response({"order_id":orderid}, status=status.HTTP_201_CREATED)
        else:
            for rec in request.data:
                serializer = RecordSerializer(data=rec)
                if serializer.is_valid():
                    serializer.validated_data['order_id'] = orderid
                    serializer.save()
                    _updatestock(rec["sku"])
            return Response({"order_id":orderid}, status=status.HTTP_201_CREATED)


class StockViewSet(viewsets.ModelViewSet):
    serializer_class = StockSerializer
    queryset = Stock.objects.all()

    def list(self, request):
        if request.method == 'GET':
            queryset = Stock.objects.all()
            category = request.GET.get('category', None)
            if category is not None:
                queryset = self.queryset.filter(category=category)
            serializer_class = StockSerializer(queryset, many=True)
            return Response(serializer_class.data)
        
       

@csrf_exempt
def UploadProduct(request):
    # permission_classes = [permissions.AllowAny]
    if request.method == 'POST':
        # FileStorage object wrapper
        file = request.FILES["myfile"]                    
        if file:
            decoded_file = file.read().decode('utf-8-sig').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                Product.objects.get_or_create(sku=row["ID"],name=row["Value"])
    return HttpResponse("OK")

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
    

class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    

class PaymentViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Payment.objects.select_related('vendor').all()
    serializer_class = PaymentSerializer

    def create(self, request):
        print(request.data)
        if request.data['vid'] != "":
            serializer = PaymentSerializer(data=request.data)
            if serializer.is_valid():
                    vendor = Vendor.objects.get(pk=request.data['vid'])
                    serializer.validated_data['vendor'] = vendor
                    serializer.save()
        elif request.data['mobile'] != "" and request.data["name"] != "":
            customer, created = Customer.objects.get_or_create(name=request.data["name"],
                                                               contact=request.data["mobile"])
            if customer:
                serializer = PaymentSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.validated_data['customer'] = customer
                    serializer.save()
            else:
                serializer = PaymentSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
        else:
            serializer = PaymentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)