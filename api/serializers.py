from django.contrib.auth.models import User
from api.models import Customer, Payment, Product,Record,Stock, Vendor
from rest_framework import serializers
from django.contrib.auth import authenticate

# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'email', 'is_staff']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id","name","contact"]


class VendorSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Vendor
        fields = ["id","name","contact","balance"]

    def get_balance(self, obj):
        queryset = Payment.objects.filter(vendor=obj).values_list("amount","type")
        bal = 0.0
        for i in queryset:
            if i[1] == "expense":
                bal = bal + float(i[0])
            else:
                bal = bal - float(i[0])
            print(obj.name,bal)
        return bal


class RecordSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(read_only=True)
    created_on = serializers.ReadOnlyField()
    customer = CustomerSerializer(required=False)
    itemcode = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Record
        fields = ["id","user_id","user_name","product_name","amount","sku","qty",
        "is_replacement","remarks","sale_date","created_on","customer","order_id","itemcode"]

    # def create(self, validated_data):
    #     print(isinstance(validated_data, list))
    #     if "customer" in validated_data:
    #         new_data = validated_data.pop('customer')
    #         customer, created = Customer.objects.get_or_create(**new_data)
    #         return Record.objects.create(**validated_data, customer=customer)
    #     else:
    #         return Record.objects.create(**validated_data, customer=None)

    def get_user_name(self, obj):
       return obj.user_id.username

    def get_itemcode(self, obj):
        code = ""
        try:
            code = Product.objects.get(pk=obj.sku).sku
        except Exception as e:
            print(e.args)
        return code

    
class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ("id","name","home","shop","category","product_id")
    
    def create(self, validated_data):
        prod_id = self.context['request'].data.get("product_id",None)
        prod = Product.objects.get(pk=prod_id)
        instance = Stock.objects.create(product = prod, **validated_data)
        return instance

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.home = validated_data.get('home', instance.home)
        instance.shop = validated_data.get('shop', instance.shop)
        instance.category = validated_data.get('category', instance.category)
        instance.save()
        return instance
    

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
    class Meta:
        model = Product
        fields = ['id', 'name']


class PaymentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(read_only=True)
    vendor_name = serializers.SerializerMethodField(read_only=True)
    vendor_id = serializers.SerializerMethodField(read_only=True)
    vendor_contact = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Payment
        fields = ['id', 'user_id', 'user_name', 'name', 'mobile', 'amount', 'type', 
                  'created_on', 'due_date', 'remarks', 'due_date_history', 'vendor_name',
                    'vendor_id', 'vendor_contact']

    def get_user_name(self, obj):
       return obj.user_id.username
    
    def get_vendor_name(self, obj):
        return obj.vendor.name if obj.vendor is not None else ""
    
    def get_vendor_id(self, obj):
        return obj.vendor.id if obj.vendor is not None else ""
    
    def get_vendor_contact(self, obj):
        return obj.vendor.contact if obj.vendor is not None else ""
    