from django.contrib.auth.models import User
from api.models import Customer,Record,Stock
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
        fields = ["name","contact"]


class RecordSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(read_only=True)
    created_on = serializers.ReadOnlyField()
    customer = CustomerSerializer(required=False)
    
    class Meta:
        model = Record
        fields = ["id","user_id","user_name","product_name","amount","sku","qty",
        "is_replacement","remarks","sale_date","created_on","customer","order_id"]

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

    
class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ["id","name","home","shop","category"]
    
    def create(self, validated_data):
        return Stock.objects.create(**validated_data)

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
    