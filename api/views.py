import random
import string
import csv
from django.shortcuts import get_object_or_404
from rest_framework import views, filters
from django.http import HttpResponse, JsonResponse
from api.common.constant import WAREHOUSE_CHOICES
from api.common.util import DateUtil, OrderUtil
from api.models import Brand, Category, Customer, ItemModel, Payment, ProductLogHistory, PurchaseOrder,Record, SaleOrder, SaleReturnOrder,Stock,Product, ProductLog, StockHistory, Subcategory, Type, Vendor
from rest_framework import  viewsets
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
from api import serializers
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.db.models import Sum,F,Q
import time
import json
from django.db.models.functions import Lower

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Category.objects.filter(active=True)
    serializer_class = serializers.CategorySerializer


class SubcategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Subcategory.objects.filter(active=True)
    serializer_class = serializers.SubcategorySerializer
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)


class BrandViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Brand.objects.filter(active=True)
    serializer_class = serializers.BrandSerializer


class ItemModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = ItemModel.objects.filter(active=True)
    serializer_class = serializers.ItemModelSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Customer.objects.all().order_by(Lower("name"))
    serializer_class = serializers.CustomerSerializer
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)


class VendorViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Vendor.objects.all().order_by(Lower("name"))
    serializer_class = serializers.VendorSerializer
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)


def _updatestock(id,type:str,qty:int):
    try:
        stock = Stock.objects.get(product__id = id,warehouse="shop")
        if stock:
            if type == "sale":
                stock.qty = stock.qty - qty
            elif type == "purchase":
                stock.qty = stock.qty + qty
            elif type == "sale_return":
                stock.qty = stock.qty + qty
            stock.save()
    except ObjectDoesNotExist as e:
        try:
            prod = Product.objects.get(pk=id)
            stock_obj = Stock.objects.create(product = prod, warehouse="shop")
            if type == "sale":
                stock_obj.qty = stock_obj.qty - qty
            elif type == "purchase":
                stock_obj.qty = stock_obj.qty + qty
            elif type == "sale_return":
                stock_obj.qty = stock_obj.qty + qty
            stock_obj.save()
        except:
            pass

def checkstock(request):
    if request.method == "GET":
        pid = request.GET.get('pid')
        wh = request.GET.get('warehouse')
        try:
            stock = Stock.objects.get(product__id = pid,warehouse=wh)
            return JsonResponse(data={"qty":stock.qty}, safe=False)
        except ObjectDoesNotExist as e:
            return JsonResponse(data={"error":"item not found in stock!"}, safe=False)



class PurchaseOrderViewSet(viewsets.ModelViewSet):
    def list(self, request):
        if request.method == "GET":
            queryset = Record.objects.prefetch_related("purchase").exclude(purchase__isnull=True).values("id","product__name",
            "product__sku","purchase__entry_user__username","purchase__vendor__name",
            "purchase__vendor__contact","purchase__invoice_amount","purchase__invoice_date",
            "purchase__invoice_id","purchase__created_on","amount","discount","qty",
            "remarks").order_by("-purchase__purchase_date")
            from_date = request.GET.get('from', None)
            to_date = request.GET.get('to', None)
            te = " 23:59:59"
            ts = " 00:00:00"
            if from_date is not None:
                queryset = queryset.filter(purchase__invoice_date__range=[from_date + ts, to_date + te])
            return JsonResponse(data=list(queryset), safe=False)
        
    def create(self, request):
        vendor = None
        invoice_id = request.data.get("invoice_id", None)
        user = User.objects.get(pk=request.data["entry_user"])
        if "vendor" in request.data:
            new_data = request.data.pop('vendor')
            vendor, create = Vendor.objects.get_or_create(name=new_data["name"])
            if not invoice_id:
                invoice_id = datetime.now().strftime("%d%m%y%H/")+new_data["name"]
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        po_obj,created = PurchaseOrder.objects.get_or_create(entry_user=user,
                                                           invoice_amount=request.data["invoice_amount"],
                                                           invoice_date=request.data["invoice_date"],
                                                           order_recieved_date=request.data["order_recieved_date"] +" "+current_time,
                                                           invoice_id=invoice_id,vendor=vendor)
        if created:
            for rec in request.data["items"]:
                prod = Product.objects.get(pk=rec["item_id"])
                Record.objects.create(purchase=po_obj,product=prod,amount=rec["amount"],discount=rec["discount"],
                                      qty=rec["qty"],remarks=rec["remarks"])
                _updatestock(rec["item_id"],"purchase",rec["qty"])
                ProductLog.objects.create(product=prod,module="Purchase",from_wh="",
                                          to_wh="shop",qty=rec["qty"],entry_user=user)
            Payment.objects.create(vendor = vendor,amount=request.data["invoice_amount"],type="stock_in",user=user)
            return Response({"invoice_id":invoice_id}, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk):
        po = Record.objects.filter(id=pk).values('purchase')
        if po:
            record_count = Record.objects.filter(purchase__id=po[0]["purchase"]).count()
            if record_count > 1:
                Record.objects.get(id=pk).delete()
            else:
                Record.objects.get(id=pk).delete()
                PurchaseOrder.objects.get(id=po[0]["purchase"]).delete()
                
        return Response(data="Deleted", status=status.HTTP_204_NO_CONTENT)



class SaleOrderViewSet(viewsets.ModelViewSet):

    def list(self, request):
        if request.method == 'GET':
            queryset = Record.objects.prefetch_related("sale").exclude(sale__isnull=True).values("id","product__name",
            "product__sku","sale__entry_user__username","sale__customer__name","sale__customer__contact",
            "sale__total_amount","sale__sale_date","sale__order_id","sale__created_on","amount",
            "discount","qty","remarks").order_by("-sale__sale_date")
            from_date = request.GET.get('from', None)
            to_date = request.GET.get('to', None)
            te = " 23:59:59"
            ts = " 00:00:00"
            if from_date is not None:
                queryset = queryset.filter(sale__sale_date__range=[from_date + ts, to_date + te])
            return JsonResponse(data=list(queryset), safe=False)
        
    def destroy(self, request, pk):
        sales = Record.objects.filter(id=pk).values('sale')
        if sales:
            record_count = Record.objects.filter(sale__id=sales[0]["sale"]).count()
            if record_count > 1:
                Record.objects.get(id=pk).delete()
            else:
                Record.objects.get(id=pk).delete()
                SaleOrder.objects.get(id=sales[0]["sale"]).delete()
                
        return Response(data="Deleted", status=status.HTTP_204_NO_CONTENT)



    def create(self, request):
        order_util =  OrderUtil()
        orderid = order_util._generate_order_id("sale")
        customer = None
        user = User.objects.get(pk=request.data["entry_user"])
        if "customer_id" in request.data:
            new_data = request.data.pop("customer_id")
            customer = Customer.objects.get(pk=new_data)
        elif "customer" in request.data:
            new_data = request.data.pop('customer')
            customer, create = Customer.objects.get_or_create(name=new_data["name"],contact=new_data["contact"])
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        sale_obj,created = SaleOrder.objects.get_or_create(entry_user=user,
                                                           total_amount=request.data["total_amount"],
                                                           sale_date=request.data["sale_date"] +" "+current_time,order_id=orderid,
                                                           customer=customer)
        if created:
            for rec in request.data["items"]:
                prod = Product.objects.get(pk=rec["item_id"])
                Record.objects.create(sale=sale_obj,product=prod,amount=rec["amount"],discount=rec["discount"],
                                      qty=rec["qty"],remarks=rec["remarks"])
                _updatestock(rec["item_id"],"sale",rec["qty"])
                ProductLog.objects.create(product=prod,module="Sale",from_wh="shop",
                                          to_wh="",qty=rec["qty"],entry_user=user)
            return Response({"order_id":orderid}, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class SaleReturnViewSet(viewsets.ModelViewSet):
    def list(self, request):
        if request.method == 'GET':
            queryset = Record.objects.prefetch_related("salereturn").exclude(salereturn__isnull=True).values("id","product__name",
            "product__sku","salereturn__entry_user__username","salereturn__customer__name",
            "salereturn__customer__contact","salereturn__total_amount","salereturn__return_date",
            "salereturn__order_id","salereturn__created_on","amount","discount","qty","remarks").order_by("-salereturn__return_date")
            from_date = request.GET.get('from', None)
            to_date = request.GET.get('to', None)
            te = " 23:59:59"
            ts = " 00:00:00"
            if from_date is not None:
                queryset = queryset.filter(salereturn__return_date__range=[from_date + ts, to_date + te])
            return JsonResponse(data=list(queryset), safe=False)
        
    def destroy(self, request, pk):
        sales = Record.objects.filter(id=pk).values('salereturn')
        if sales:
            record_count = Record.objects.filter(sale__id=sales[0]["salereturn"]).count()
            if record_count > 1:
                Record.objects.get(id=pk).delete()
            else:
                Record.objects.get(id=pk).delete()
                SaleReturnOrder.objects.get(id=sales[0]["salereturn"]).delete()
                
        return Response(data="Deleted", status=status.HTTP_204_NO_CONTENT)



    def create(self, request):
        orderid = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=5))
        # customer = None
        user = User.objects.get(pk=request.data["entry_user"])
        # if "customer" in request.data:
        #     new_data = request.data.pop('customer')
        #     customer, create = Customer.objects.get_or_create(name=new_data["name"],contact=new_data["contact"])
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        sale_obj,created = SaleReturnOrder.objects.get_or_create(entry_user=user,
                                                           total_amount=request.data["total_amount"],
                                                           return_date=request.data["return_date"] +" "+current_time,order_id=orderid)
                                                        #    customer=customer)
        if created:
            for rec in request.data["items"]:
                prod = Product.objects.get(pk=rec["item_id"])
                Record.objects.create(salereturn=sale_obj,product=prod,amount=rec["amount"],discount=rec["discount"],
                                      qty=rec["qty"],remarks=rec["remarks"])
                _updatestock(rec["item_id"],"sale_return",rec["qty"])
                ProductLog.objects.create(product=prod,module="SaleReturn",from_wh="",
                                          to_wh="shop",qty=rec["qty"],entry_user=user)
            return Response({"order_id":orderid}, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = serializers.RecordSerializer

    def list(self, request):
        if request.method == 'GET':
            queryset = Record.objects.all()
            from_date = request.GET.get('from', None)
            to_date = request.GET.get('to', None)
            if from_date is not None:
                queryset = self.queryset.filter(sale_date__range=[from_date, to_date])
            serializer_class = serializers.RecordSerializer(queryset, many=True)
            return Response(serializer_class.data)


    def create(self, request):
        orderid = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=7))
        if "customer" in request.data[0]:
            new_data = request.data[0].pop('customer')
            customer, created = Customer.objects.get_or_create(name=new_data["name"],contact=new_data["contact"])
            for rec in request.data:
                serializer = serializers.RecordSerializer(data=rec)
                if serializer.is_valid():
                    serializer.validated_data['order_id'] = orderid
                    serializer.validated_data['customer'] = customer 
                    serializer.save()
                    _updatestock(rec["sku"])
            return Response({"order_id":orderid}, status=status.HTTP_201_CREATED)
        else:
            for rec in request.data:
                serializer = serializers.RecordSerializer(data=rec)
                if serializer.is_valid():
                    serializer.validated_data['order_id'] = orderid
                    serializer.save()
                    _updatestock(rec["sku"])
            return Response({"order_id":orderid}, status=status.HTTP_201_CREATED)


class StockViewSet(viewsets.ModelViewSet):
    def list(self, request):
        if request.method == 'GET':
            stock_prod_id = Stock.objects.order_by().values_list('product__id').distinct()
            queryset = Stock.objects.select_related("product").annotate(product_category=F(
                "product__type__item_model__brand__subcategory__category"),product_subcategory=F(
                "product__type__item_model__brand__subcategory"),product_brand=F(
                "product__type__item_model__brand"),product_model=F("product__type__item_model")).values("product__id"
                ,"product_category","product_subcategory","product_brand","product_model","product__name","qty",
                "warehouse","product__selling_price").order_by("product__name")
            category = request.GET.get('category', None)
            # subcategory = request.GET.get('subcategory', None)
            # brand = request.GET.get('brand', None)
            # item_model = request.GET.get('model', None)
            # filter = None
            if category:
                # filter = Q(product_category=category)
                queryset = queryset.filter(product_category=category)
            # if subcategory:
            #     filter = filter & Q(product_subcategory=subcategory)
            # if brand:
            #     filter = filter & Q(product_brand=brand)
            # if item_model:
            #     filter = filter & Q(product_model=item_model)
            # queryset = queryset.filter(filter)
            stock_prod_id = queryset.values_list('product__id').distinct()
            result = []
            if queryset:
                for id in stock_prod_id:
                    data = [v for v in list(queryset) if v["product__id"] == id[0]]
                    obj = {"product_id":data[0]["product__id"],"product_name":data[0]["product__name"],
                        "product_category":data[0]["product_category"],"selling_price":data[0]["product__selling_price"]}
                    c = 0
                    for i in data:
                        if i["warehouse"] == "home":
                            obj["home"] = i["qty"] if i["qty"] else 0
                            c = c+ int(obj["home"])
                        elif i["warehouse"] == "shop":
                            obj["shop"] = i["qty"] if i["qty"] else 0
                            c = c+ int(obj["shop"])
                        elif i["warehouse"] == "po_godown":
                            obj["po_godown"] = i["qty"] if i["qty"] else 0
                            c = c+ int(obj["po_godown"])
                        elif i["warehouse"] == "colony":
                            obj["colony"] = i["qty"] if i["qty"] else 0
                            c = c+ int(obj["colony"])
                        elif i["warehouse"] == "hameerpur":
                            obj["hameerpur"] = i["qty"] if i["qty"] else 0
                            c = c+ int(obj["hameerpur"])
                    obj["total"] = c

                    result.append(obj)
            return JsonResponse(data=result, safe=False)
        
    def retrieve(self, request, pk=None):
        stock_obj = Stock.objects.get(product__id=pk,warehouse="shop")
        obj = {"product_id":stock_obj.product_id,"shop":stock_obj.qty}
        
        return  JsonResponse(data=obj, safe=False)
        

def move_stock_to_history(request):
    products = Stock.objects.all()
    for prod in products:
        product = Product.objects.get(pk=prod.product_id)
        StockHistory.objects.create(product=product,warehouse=prod.warehouse,qty=prod.qty)
    return HttpResponse(content="ok")

class StockHistoryViewSet(viewsets.ModelViewSet):
    queryset = StockHistory.objects.all()
    serializer_class = serializers.StockHistorySerializer

    def list(self, request):
        if request.method == 'GET':
            stock_prod_id = StockHistory.objects.order_by().values_list('product__id').distinct()
            queryset = StockHistory.objects.select_related("product").annotate(product_category=F(
                "product__type__item_model__brand__subcategory__category"),product_subcategory=F(
                "product__type__item_model__brand__subcategory"),product_brand=F(
                "product__type__item_model__brand"),product_model=F("product__type__item_model")).values("product__id"
                ,"product_category","product_subcategory","product_brand","product_model","product__name","qty",
                "warehouse","product__selling_price","created_on").order_by("product__name")
            category = request.GET.get('category', None)
            if category:
                # filter = Q(product_category=category)
                queryset = queryset.filter(product_category=category)
            stock_prod_id = queryset.values_list('product__id').distinct()
            result = []
            if queryset:
                for id in stock_prod_id:
                    data = [v for v in list(queryset) if v["product__id"] == id[0]]
                    obj = {"product_id":data[0]["product__id"],"product_name":data[0]["product__name"],
                        "product_category":data[0]["product_category"],"selling_price":data[0]["product__selling_price"],
                        "created_on":data[0]["created_on"]}
                    for i in data:
                        c = 0
                        if i["warehouse"] == "home":
                            obj["home"] = i["qty"] if i["qty"] else 0
                            c = c+ int(obj["home"])
                        elif i["warehouse"] == "shop":
                            obj["shop"] = i["qty"] if i["qty"] else 0
                            c = c+ int(obj["shop"])
                        elif i["warehouse"] == "po_godown":
                            obj["po_godown"] = i["qty"] if i["qty"] else 0
                            c = c+ int(obj["po_godown"])
                        elif i["warehouse"] == "colony":
                            obj["colony"] = i["qty"] if i["qty"] else 0
                            c = c+ int(obj["colony"])
                        elif i["warehouse"] == "hameerpur":
                            obj["hameerpur"] = i["qty"] if i["qty"] else 0
                            c = c+ int(obj["hameerpur"])
                        obj["total"] = c

                    result.append(obj)
            return JsonResponse(data=result, safe=False)

class ProductLogViewSet(viewsets.ModelViewSet):
    queryset = ProductLog.objects.all()
    serializer_class = serializers.ProductLogSerializer
    def list(self, request):
        if request.method == 'GET':
            # queryset = ProductLog.objects.all()
            from_date = request.GET.get('from', None)
            to_date = request.GET.get('to', None)
            if from_date is not None:
                self.queryset = self.queryset.filter(created_on__date__range=[from_date, to_date])
            serializer_class = serializers.ProductLogSerializer(self.queryset, many=True)
            return Response(serializer_class.data)
        
    def retrieve(self, request, pk=None):
        # queryset = User.objects.all()
        log = get_object_or_404(self.queryset, product__id=pk)
        if log:
            prod = Product.objects.filter(id=pk).values("name","opening_stock")[0]
            results = []
            obj = {"id":0,"entry_user":2,"created_on":None,"username":"myash","product":pk,"from_wh":"",
                   "to_wh":"","module":"Opening Stock","qty":prod["opening_stock"],"product_name":prod["name"]}
            results.append(obj)
            self.queryset = self.queryset.filter(product__id=pk)
            for objc in self.queryset:
                obj = {"id":objc["id"],"entry_user":objc["entry_user"],"created_on":objc["created_on"],"username":objc["entry_user__username"],
                       "product":pk,"from_wh":objc["from_wh"],"to_wh":objc["to_wh"],"module":"Opening Stock","qty":prod["opening_stock"],"product_name":prod["name"]}
            serializer = serializers.ProductLogSerializer(self.queryset, many=True)
            return Response(serializer.data)

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
                try:
                    cat= Category.objects.get_or_create(name=row["Category"])
                    subcat = Subcategory.objects.get_or_create(category=cat[0],name=row["SubCategory"])
                    brand = Brand.objects.get_or_create(subcategory=subcat[0],name=row["BrandName"])
                    modelname = ItemModel.objects.get_or_create(brand=brand[0],name=row["ModelName"])
                    type = Type.objects.get_or_create(item_model=modelname[0],name=row["Type"])
                    prod = None
                    try:
                        prod = Product.objects.get(sku=row["ItemCode"])
                    except ObjectDoesNotExist as e:
                        print("internaaaaaaaaaaaaaal")
                        print(e.args)
                    if row["Description"] == "Domestic Appliances - All out Machine - ":
                        print("inter")
                    if prod:
                        prod.name = row["Description"]
                        prod.type = type[0]
                        prod.hsn = None if row["HSNCode"]=="" else row["HSNCode"]
                        prod.list_price = None if row["ListPrice"] == "" else row["ListPrice"]
                        prod.price_with_gst = None if row["NetRateWithGST"] == "" else row["NetRateWithGST"]
                        prod.save()
                    else:
                        Product.objects.create(type=type[0],sku=row["ItemCode"],name=row["Description"],
                                        HSN=None if row["HSNCode"]=="" else row["HSNCode"],
                                        list_price=None if row["ListPrice"] == "" else row["ListPrice"],
                                        price_with_gst=None if row["NetRateWithGST"] == "" else row["NetRateWithGST"])
                except Exception as e:
                    print(row["Description"])
                    print(e.args)
    return HttpResponse("OK")

class LoginView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = serializers.LoginSerializer(data=self.request.data,
            context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        data = {"userid":User.objects.get(username=user).pk}
        return Response(data, status=status.HTTP_202_ACCEPTED)
    
def GetLedger(request):
    if request.method == 'GET':
        vid = request.GET.get('vid')
        if vid:
            results = []
            vendor = Vendor.objects.filter(id=vid).values("opening_balance","name","contact")[0]
            payment_data = Payment.objects.filter(vendor__id=vid).order_by('created_on','type','amount').values('created_on','type','amount','remarks')
            obj = {"type":"","remarks":"opening balance","amount":vendor["opening_balance"],"created_on":None}
            results.append(obj)
            for payment in payment_data:
                obj = {"type":payment["type"],"remarks":payment["remarks"],"amount":payment["amount"],"created_on":payment["created_on"]}
                results.append(obj)
            vendor_obj = {"name":vendor["name"],"contact":vendor["contact"]}
            ledger = {"vendor":vendor_obj,"data":results}
            return JsonResponse(data=ledger, safe=False)
        
def printorder(request):
    if request.method == "GET":
        oid = request.GET.get('oid')
        if oid:
            return JsonResponse(data=list(Record.objects.filter(sale=SaleOrder.objects.filter(order_id=oid)[0]).values("product__name","qty","amount")), safe=False)

class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)
    queryset = Product.objects.select_related('type','type__item_model','type__item_model__brand','type__item_model__brand__subcategory','type__item_model__brand__subcategory__category')
    serializer_class = serializers.ProductSerializer
    

class PaymentViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Payment.objects.select_related('user','vendor')
    serializer_class = serializers.PaymentSerializer

    def list(self, request):
        from_date = request.GET.get('from', None)
        to_date = request.GET.get('to', None)
        te = " 23:59:59"
        ts = " 00:00:00"
        self.queryset = Payment.objects.select_related('user','vendor')
        for i in self.queryset:
            print(str(i))
        if from_date is not None:
            self.queryset = self.queryset.filter(created_on__range=[from_date + ts, to_date + te])
        serializer = serializers.PaymentSerializer(self.queryset, many=True)
        return JsonResponse(data=serializer.data, safe=False)

    def create(self, request):
        user = User.objects.get(pk=request.data["user_id"])
        if request.data.get('vid',None):
            serializer = serializers.PaymentSerializer(data=request.data)
            if serializer.is_valid():
                    vendor = Vendor.objects.get(pk=request.data['vid'])
                    serializer.validated_data['vendor'] = vendor
                    serializer.validated_data['user'] = user
                    serializer.save()
        elif request.data.get('cid',None):
            serializer = serializers.PaymentSerializer(data=request.data)
            if serializer.is_valid():
                customer = Customer.objects.get(pk=request.data['cid'])
                serializer.validated_data['customer'] = customer
                serializer.validated_data['user'] = user
                serializer.save()
        else:
            serializer = serializers.PaymentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data['user'] = user
                serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

def dashboard_income_expense(request):
    final = {}
    result = []
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    util = DateUtil()
    util.numberOfDays(currentYear,currentMonth)
    payments = Payment.objects.filter(created_on__year=currentYear, created_on__month=currentMonth, type="expense").values('created_on__date').annotate(amt=Sum('amount'))
    sales = Record.objects.filter(sale__sale_date__year=currentYear, sale__sale_date__month=currentMonth).values('sale__sale_date__date').annotate(amt=Sum('amount'))
    if sales.count() > payments.count():
        for item in sales:
            payment = payments.filter(created_on__date=item['sale__sale_date__date'])
            if payment:
                result.append({"date":item['sale__sale_date__date'].strftime("%Y-%m-%d"),"expense":'{0:.2f}'.format(float(payment[0]["amt"])),"income":'{0:.2f}'.format(float(item['amt']))})
            else:
                result.append({"date":item['sale__sale_date__date'].strftime("%Y-%m-%d"),"expense":'{0:.2f}'.format(float("0")),"income":'{0:.2f}'.format(float(item['amt']))})
    elif sales.count() < payments.count():
        for item in payments:
            sale = sales.filter(sale__sale_date__date=item['created_on__date'])
            if sale:
                result.append({"date":item['created_on__date'].strftime("%Y-%m-%d"),"expense":'{0:.2f}'.format(float(item["amt"])),"income":'{0:.2f}'.format(float(sale[0]['amt']))})
            else:
                result.append({"date":item['created_on__date'].strftime("%Y-%m-%d"),"expense":'{0:.2f}'.format(float(item["amt"])),"income":'{0:.2f}'.format(float("0"))})
    else:
        for item in payments:
            sale = sales.filter(sale__sale_date__date=item['created_on__date'])
            if sale:
                result.append({"date":item['created_on__date'].strftime("%Y-%m-%d"),"expense":'{0:.2f}'.format(float(item["amt"])),"income":'{0:.2f}'.format(float(sale[0]['amt']))})
            else:
                result.append({"date":item['created_on__date'].strftime("%Y-%m-%d"),"expense":'{0:.2f}'.format(float(item["amt"])),"income":'{0:.2f}'.format(float("0"))})
        for item in sales:
            payment = payments.filter(created_on__date=item['sale__sale_date__date'])
            if payment:
                result.append({"date":item['sale__sale_date__date'].strftime("%Y-%m-%d"),"expense":'{0:.2f}'.format(float(payment[0]["amt"])),"income":'{0:.2f}'.format(float(item['amt']))})
            else:
                result.append({"date":item['sale__sale_date__date'].strftime("%Y-%m-%d"),"expense":'{0:.2f}'.format(float("0")),"income":'{0:.2f}'.format(float(item['amt']))})
    sales_in_month = Record.objects.filter(sale__sale_date__year=currentYear, sale__sale_date__month=currentMonth).values("product__type__item_model__brand__subcategory__category__name").annotate(amt=Sum('amount'))
    sale_records = []
    for item in sales_in_month:
        record = {"category":item["product__type__item_model__brand__subcategory__category__name"],"amount":'{0:.2f}'.format(float(item["amt"]))}
        sale_records.append(record)
    final = {"records":result,"sales":sale_records}
    print(final)
    return JsonResponse(data=final, safe=False)

@csrf_exempt
def move_stock(request):
    if request.method == "POST":
        data = json.loads(request.body)
        stock1 = None
        stock2 = None
        prod = None
        user = User.objects.get(pk=data[0]["entry_user"])
        for obj in data:
            from_wh = next((key for key, val in dict(WAREHOUSE_CHOICES).items() if val == obj["fromwarehouse"]), None)
            to_wh = next((key for key, val in dict(WAREHOUSE_CHOICES).items() if val == obj["towarehouse"]), None)
            try:
                stock1 = Stock.objects.get(product__id = obj["product_id"], warehouse=from_wh)
                if stock1:
                    stock1.qty = stock1.qty - int(obj["qty"])
                    try:
                        stock2 = Stock.objects.get(product__id = obj["product_id"], warehouse=to_wh)
                        if stock2:
                            prod = Product.objects.get(pk=obj["product_id"])
                            stock2.qty = stock2.qty + int(obj["qty"])
                            stock2.save()
                            stock1.save()
                            ProductLog.objects.create(product=prod,module="StockMove",from_wh=from_wh,
                                          to_wh=to_wh,qty=int(obj["qty"]),entry_user=user)
                    except ObjectDoesNotExist as e:
                        prod = Product.objects.get(pk=obj["product_id"])
                        stock2 = Stock.objects.create(product = prod, warehouse=to_wh, qty=int(obj["qty"]))
                        ProductLog.objects.create(product=prod,module="StockMove",from_wh=from_wh,
                                          to_wh=to_wh,qty=int(obj["qty"]),entry_user=user)
            
            except ObjectDoesNotExist as e:
                    prod = Product.objects.get(pk=obj["product_id"])
                    stock1 = Stock.objects.create(product = prod, warehouse=from_wh, qty=0)
                    try:
                        stock2 = Stock.objects.get(product__id = obj["product_id"], warehouse=to_wh)
                        if stock2:
                            stock2.qty = stock2.qty + int(obj["qty"])
                            stock2.save()
                            stock1.save()
                            ProductLog.objects.create(product=prod,module="StockMove",from_wh=from_wh,
                                          to_wh=to_wh,qty=int(obj["qty"]),entry_user=user)
                    except ObjectDoesNotExist as e:
                        prod = Product.objects.get(pk=obj["product_id"])
                        stock2 = Stock.objects.create(product = prod, warehouse=to_wh, qty=int(obj["qty"]))
                        ProductLog.objects.create(product=prod,module="StockMove",from_wh=from_wh,
                                          to_wh=to_wh,qty=int(obj["qty"]),entry_user=user)
    return JsonResponse(data={"status":"OK"}, safe=False)


class ProductLogHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = ProductLogHistory.objects.all()
    serializer_class = serializers.ProductLogHistorySerializer
