from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

from api.common.constant import CATEGORY_CHOICES, ORDER_TYPES, PAYMENT_MODE_CHOICES, PAYMENT_TYPE_CHOICES, WAREHOUSE_CHOICES


class Customer(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=33, null=True)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=33, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    active = models.BooleanField(default=True)


class Subcategory(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


class Brand(models.Model):
    name = models.CharField(max_length=150)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


class ItemModel(models.Model):
    name = models.CharField(max_length=150)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


class Type(models.Model):
    name = models.CharField(max_length=150)
    item_model = models.ForeignKey(ItemModel, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)



class Product(models.Model):
    sku = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    # image = models.ImageField(null=True,blank=True,upload_to="static")
    description = models.TextField(null=True,blank=True)
    HSN = models.IntegerField(null=True,blank=True)
    type = models.ForeignKey(Type, on_delete=models.CASCADE, null=True, blank=True)
    list_price = models.FloatField(null=True,blank=True)
    price_with_gst = models.FloatField(null=True,blank=True)
    selling_price = models.FloatField(null=True,blank=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name
    

class SaleOrder(models.Model):
    entry_user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE)
    total_amount = models.FloatField(default=0.0)
    sale_date = models.DateTimeField(default=now)
    order_id = models.CharField(max_length=15, default="1111111")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-sale_date','-created_on')

    def __str__(self):
        return self.order_id


class SaleReturnOrder(models.Model):
    entry_user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE)
    total_amount = models.FloatField(default=0.0)
    return_date = models.DateTimeField(default=now)
    order_id = models.CharField(max_length=7, default="11111")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-return_date','-created_on')

    def __str__(self):
        return self.order_id
    

class PurchaseOrder(models.Model):
    entry_user = models.ForeignKey(User, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.CASCADE)
    invoice_amount = models.FloatField(default=0.0)
    invoice_date = models.DateTimeField(default=now)
    order_recieved_date = models.DateTimeField(null=True, blank=True, default=now)
    invoice_id = models.CharField(max_length=100, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-invoice_date','-created_on')

    def __str__(self):
        return self.invoice_id
    

class PurchaseReturnOrder(models.Model):
    entry_user = models.ForeignKey(User, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.CASCADE)
    invoice_amount = models.FloatField(default=0.0)
    invoice_date = models.DateTimeField(default=now)
    order_return_date = models.DateTimeField(null=True, blank=True, default=now)
    invoice_id = models.CharField(max_length=100, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-invoice_date','-created_on')

    def __str__(self):
        return self.invoice_id


class Record(models.Model):
    purchase = models.ForeignKey(PurchaseOrder,on_delete=models.CASCADE,null=True,blank=True)
    sale = models.ForeignKey(SaleOrder,on_delete=models.CASCADE,null=True,blank=True)
    salereturn = models.ForeignKey(SaleReturnOrder,on_delete=models.CASCADE,null=True,blank=True)
    purchasereturn = models.ForeignKey(PurchaseReturnOrder,on_delete=models.CASCADE,null=True,blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True,blank=True)
    # product_name = models.CharField(max_length=255, null=True)
    amount = models.FloatField(null=True,blank=True,default=0.0)
    discount = models.FloatField(null=True,blank=True,default=0.0)
    qty = models.IntegerField(default=0)
    is_replacement = models.BooleanField(verbose_name="Replacement/Return", default=False)
    remarks = models.TextField(default="",null=True,blank=True)
    # created_on = models.DateTimeField(auto_now_add=True)
    # customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    
    class Meta:
        ordering = ('product',)

    def __str__(self):
        return str(self.product)
    

class Stock(models.Model):
    # name = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    warehouse = models.CharField(max_length=100, default="home", choices=WAREHOUSE_CHOICES)
    qty = models.IntegerField(default=0)
    # category = models.CharField(max_length=100, choices = CATEGORY_CHOICES ,default="wire")

    def __str__(self) -> str:
        return self.product.name
    

class ProductLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    module = models.CharField(max_length=30)
    from_wh = models.CharField(max_length=100, choices=WAREHOUSE_CHOICES, null=True, blank=True)
    to_wh = models.CharField(max_length=100, choices=WAREHOUSE_CHOICES, null=True, blank=True)
    qty = models.IntegerField(default=0)
    entry_user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.product.name
    

class Payment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    mobile = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    type = models.CharField(max_length=50, choices = PAYMENT_TYPE_CHOICES ,default="income")
    mode = models.CharField(max_length=50, choices = PAYMENT_MODE_CHOICES ,default="cash")
    remarks = models.TextField(default="",null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    due_date = models.DateTimeField(blank=True, null=True)
    due_date_history = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return str(self.amount)

    