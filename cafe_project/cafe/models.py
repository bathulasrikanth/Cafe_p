from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone

class TableReservation(models.Model):
    Table_choices = [
        ('1', 'Table 1'),
        ('2', 'Table 2'),
        ('3', 'Table 3'),
        ('4', 'Table 4'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    date = models.DateField()
    time = models.TimeField()
    table_number = models.CharField(max_length=10, choices=Table_choices)
    reserved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - Table {self.table_number}"

    def is_expired(self):
        """Check if the reservation is expired (older than 1 hour)."""
        expiration_time = self.reserved_at + timedelta(hours=1)
        return timezone.now() > expiration_time




class Product(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField(max_length=300 , default="NiceDrink")
    image=models.ImageField(upload_to='image/')
    price=models.IntegerField()
    available=models.BooleanField()
    
    def __str__(self):
        return self.title


class CoolDrinks(models.Model):
    title=models.CharField(max_length=200)
    image=models.ImageField(upload_to='image/')
    price=models.IntegerField()
    available=models.BooleanField()

    def __str__(self):
        return self.title

class Shakes(models.Model):
    title=models.CharField(max_length=100) 
    image=models.ImageField(upload_to='image/')
    price=models.IntegerField()   
    description=models.TextField(default="Drink The Shake")
    available=models.BooleanField()
    
    def __str__(self):
        return self.title

 
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    cool_drink = models.ForeignKey(CoolDrinks, null=True, blank=True, on_delete=models.CASCADE)
    Shakess=models.ForeignKey(Shakes,null=True,blank=True,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        if self.product:
            return self.product.price * self.quantity
        elif self.cool_drink:
            return self.cool_drink.price * self.quantity
        elif self.Shakess:
            return self.Shakess.price*self.quantity

        return 0 
    

