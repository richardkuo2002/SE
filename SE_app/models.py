from django.db import models

# Create your models here.
from django.db import models

class Branch(models.Model):
    branch_id = models.IntegerField(primary_key=True)
    branch_name = models.CharField(max_length=100)
    branch_address = models.CharField(max_length=100)

class Sale(models.Model):
    sale_id = models.IntegerField(primary_key=True)
    sale_date = models.DateField()
    sale_amount = models.DecimalField(max_digits=10, decimal_places=2)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

class Profit(models.Model):
    profit_id = models.IntegerField(primary_key=True)
    profit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE)

class Salesperson(models.Model):
    salesperson_id = models.IntegerField(primary_key=True)
    salesperson_name = models.CharField(max_length=100)

class Customer(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    customer_name = models.CharField(max_length=100)

class CustomerProgress(models.Model):
    progress_id = models.IntegerField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    salesperson = models.ForeignKey(Salesperson, on_delete=models.CASCADE)
    progress_status = models.CharField(max_length=100)
