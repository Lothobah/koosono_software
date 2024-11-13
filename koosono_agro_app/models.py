from django.urls import reverse
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.utils import timezone
class CustomUser(AbstractUser):
    user_type_data = ((1, "admin"),(2, "Staff"))
    user_type = models.CharField(
        default=1, choices=user_type_data, max_length=10)


class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    cost_price = models.DecimalField(max_digits=30, decimal_places=2)
    selling_price = models.DecimalField(max_digits=30, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='purchases', null=True, blank=True)
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='sales', null=True, blank=True)
    quantity = models.PositiveIntegerField()
    sale_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    @property
    def profit(self):
        if self.product:
            unit_profit = self.product.selling_price - self.product.cost_price
            return unit_profit * self.quantity
        return 0