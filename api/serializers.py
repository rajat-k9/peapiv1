from django.contrib.auth.models import User
from api.models import Customer,Record,Stock
from rest_framework import serializers

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
    class Meta:
        model = Record
        fields = ["user_id","user_name","product_name","amount","sku","qty",
        "is_replacement","remarks","sale_date","created_on"]

    def get_user_name(self, obj):
       return obj.user_id.username

    
class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ["id","name","home","shop"]
    
    def create(self, validated_data):
        return Stock.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.home = validated_data.get('home', instance.home)
        instance.shop = validated_data.get('shop', instance.shop)
        instance.save()
        return instance