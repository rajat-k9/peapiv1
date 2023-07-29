from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from api import models

# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'email', 'is_staff']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id', 'name']


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subcategory
        fields = ['id', 'name']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Brand
        fields = ['id', 'name']


class ItemModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ItemModel
        fields = ['id', 'name']


class CustomerSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Customer
        fields = ["id","name","contact","balance"]

    def get_balance(self, obj):
        queryset = models.Payment.objects.filter(customer=obj).values_list("amount","type")
        bal = 0.0
        for i in queryset:
            if i[1] == "expense":
                bal = bal + float(i[0])
            else:
                bal = bal - float(i[0])
        return bal


class VendorSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Vendor
        fields = ["id","name","contact","balance"]

    def get_balance(self, obj):
        queryset = models.Payment.objects.filter(vendor=obj).values_list("amount","type")
        bal = 0.0
        for i in queryset:
            if i[1] == "expense":
                bal = bal + float(i[0])
            else:
                bal = bal - float(i[0])
        return bal


class SaleOrderSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(read_only=True)
    created_on = serializers.ReadOnlyField()
    customer = CustomerSerializer(required=False)
    product_name = serializers.CharField(source='product.name',read_only=True)
    itemcode = serializers.CharField(source='product.sku',read_only=True)

    class Meta:
        model = models.SaleOrder
        fields = ["id","entry_user","user_name","sale_date","product_name",
                  "created_on","order_id","total_amount","customer","itemcode"]

    
    def get_user_name(self, obj):
       return obj.entry_user.username
    

class SaleReturnSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(read_only=True)
    created_on = serializers.ReadOnlyField()
    customer = CustomerSerializer(required=False)
    product_name = serializers.CharField(source='product.name',read_only=True)
    itemcode = serializers.CharField(source='product.sku',read_only=True)

    class Meta:
        model = models.SaleReturnOrder
        fields = ["id","entry_user","user_name","order_type","return_date","product_name",
                  "created_on","order_id","total_amount","customer","itemcode"]

    
    def get_user_name(self, obj):
       return obj.entry_user.username


class RecordSerializer(serializers.ModelSerializer):
    sale_order = SaleOrderSerializer(required=False)
    # purchase_order = Purc
    item_id = serializers.CharField(source='product.id')
    
    class Meta:
        model = models.Record
        fields = ["id","amount","discount","qty",
        "is_replacement","remarks","sale_order","item_id"]

    # def create(self, validated_data):
    #     print(isinstance(validated_data, list))
    #     if "customer" in validated_data:
    #         new_data = validated_data.pop('customer')
    #         customer, created = Customer.objects.get_or_create(**new_data)
    #         return Record.objects.create(**validated_data, customer=customer)
    #     else:
    #         return Record.objects.create(**validated_data, customer=None)



class ProductLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.CharField(source='product.name')
    class Meta:
        model = models.ProductLog
        fields = ("id","entry_user","created_on","user_name", "product","from_wh","to_wh",
                  "module", "qty","product_name")

    def get_user_name(self, obj):
       return obj.entry_user.username
    
class StockSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(source='product.id') 
    product_name = serializers.CharField(source='product.name')
    class Meta:
        model = models.Stock
        fields = ("id","product_category","product_id","product_name","warehouse","qty")
    
    # def create(self, validated_data):
    #     prod_id = self.context['request'].data.get("product_id",None)
    #     prod = Product.objects.get(pk=prod_id)
    #     instance = Stock.objects.create(product = prod, **validated_data)
    #     return instance

    # def update(self, instance, validated_data):
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.home = validated_data.get('home', instance.home)
    #     instance.shop = validated_data.get('shop', instance.shop)
    #     instance.category = validated_data.get('category', instance.category)
    #     instance.save()
    #     return instance
    

class LoginSerializer(serializers.Serializer):
    """
    This serializer defines two fields for authentication:
      * username
      * password.
    It will try to authenticate the user with when validated.
    """
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        # This will be used when the DRF browsable API is enabled
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        # Take username and password from request
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Try to authenticate the user using Django auth framework.
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                # If we don't have a regular user, raise a ValidationError
                msg = 'Access denied: wrong username or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        # We have a valid user, put it in the serializer's validated_data.
        # It will be used in the view.
        attrs['user'] = user
        return attrs

class ProductSerializer(serializers.ModelSerializer):
    type_name = serializers.SerializerMethodField()
    model_name = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    subcategory_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Product
        fields = ['id', 'name','type_name','model_name','brand_name','subcategory_name','category_name']

    def get_type_name(self, obj):
        return obj.type.name
    
    def get_model_name(self, obj):
        return obj.type.item_model.name
    
    def get_brand_name(self, obj):
        return obj.type.item_model.brand.name
    
    def get_subcategory_name(self, obj):
        return obj.type.item_model.brand.subcategory.name
    
    def get_category_name(self, obj):
        return obj.type.item_model.brand.subcategory.category.name


class PaymentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(read_only=True)
    vendor_name = serializers.SerializerMethodField(read_only=True)
    vendor_id = serializers.SerializerMethodField(read_only=True)
    vendor_contact = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Payment
        fields = ['id','user_name',"user_id","name","mobile", 'amount', 'type', 
                  'created_on', 'due_date', 'remarks', 'due_date_history', 'vendor_name',
                    'vendor_id', 'vendor_contact']

    def get_user_name(self, obj):
       return obj.user.username
    
    def get_vendor_name(self, obj):
        return obj.vendor.name if obj.vendor is not None else ""
    
    def get_vendor_id(self, obj):
        return obj.vendor.id if obj.vendor is not None else ""
    
    def get_vendor_contact(self, obj):
        return obj.vendor.contact if obj.vendor is not None else ""
    