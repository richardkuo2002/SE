from django.db import models

# Create your models here.
from django.db import models

"""
1. 分店(Branch): 代表按摩椅企業的分店。
    分店編號(Branch ID)
    分店名稱(Branch Name)
    分店地址(Branch Address)
"""
class Branch(models.Model):
    branch_id = models.IntegerField(primary_key=True)
    branch_name = models.CharField(max_length=100)
    branch_address = models.CharField(max_length=100)

"""
2. 銷售(Sale): 代表按摩椅的銷售記錄。
    銷售編號(Sale ID)
    銷售日期(Sale Date)
    銷售金額(Sale Amount)
    分店編號(Branch ID)[外鍵，關聯至分店實體]
"""
class Sale(models.Model):
    sale_id = models.IntegerField(primary_key=True)
    sale_date = models.DateField()
    sale_amount = models.DecimalField(max_digits=10, decimal_places=2)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

"""
3. 毛利(Profit): 代表按摩椅銷售的毛利情況。
    毛利編號(Profit ID)
    毛利金額(Profit Amount)
    銷售編號(Sale ID)[外鍵，關聯至銷售實體]
"""
class Profit(models.Model):
    profit_id = models.IntegerField(primary_key=True)
    profit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE)

"""
4. 業務員(Salesperson): 代表按摩椅企業的業務員。
    業務員編號(Salesperson ID)
    業務員姓名(Salesperson Name)
"""
class Salesperson(models.Model):
    salesperson_id = models.IntegerField(primary_key=True)
    salesperson_name = models.CharField(max_length=100)

"""
5. 客人(Customer): 代表按摩椅企業的客人。
    客人編號(Customer ID)
    客人姓名(Customer Name)
"""
class Customer(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    customer_name = models.CharField(max_length=100)

"""
6. 客戶進度(Customer Progress): 代表客戶在銷售過程中的進度。
    進度編號(Progress ID)
    客人編號(Customer ID)[外鍵，關聯至客人實體]
    銷售編號(Sale ID)[外鍵，關聯至銷售實體]
    業務員編號(Salesperson ID)[外鍵，關聯至業務員實體]
    進度狀態(Progress Status)
"""
class CustomerProgress(models.Model):
    progress_id = models.IntegerField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    salesperson = models.ForeignKey(Salesperson, on_delete=models.CASCADE)
    progress_status = models.CharField(max_length=100)
