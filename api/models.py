from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Customer(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=33, null=True)

    def __str__(self):
        return self.name


class Record(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255, null=True)
    amount = models.FloatField(null=True,blank=True,default=0.0)
    sku = models.CharField(max_length=100)
    qty = models.IntegerField(default=1)
    is_replacement = models.BooleanField(default=False)
    remarks = models.TextField(default="",null=True,blank=True)
    sale_date = models.DateTimeField(default=now)
    created_on = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    order_id = models.CharField(max_length=20, default="1111111")
    class Meta:
        ordering = ('-sale_date','-created_on')

    def __str__(self):
        return self.product_name
    
class Product(models.Model):
    sku = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


CATEGORY_CHOICES =(
    ("wire", "Wire Cable"),
    ("board", "Distribution Board"),
    ("china_light", "China Light"),
)
class Stock(models.Model):
    name = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    home = models.IntegerField(default=0)
    shop = models.IntegerField(default=0)
    category = models.CharField(max_length=100, choices = CATEGORY_CHOICES ,default="wire")

    def __str__(self) -> str:
        return self.name

    