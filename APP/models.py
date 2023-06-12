from django.db import models

# Create your models here.

"""
1. 分店(Branch): 代表按摩椅企業的分店。
    分店編號(Branch ID)
    分店名稱(Branch Name)
    分店地址(Branch Address)
"""
class Branch(models.Model):
    branch_id = models.AutoField(primary_key=True)
    branch_name = models.CharField(max_length=100)
    branch_address = models.CharField(max_length=100)
    local = models.IntegerField(choices=(
        (1, '北區'),
        (2, '中區'),
        (3, '南區')
    ), default=1)
    
    def get_local_name(self):
        return {
            1: '北區',
            2: '中區',
            3: '南區',
        }[self.local]
    
    def __str__(self):
        return self.branch_name
    
    class Meta:
        verbose_name = "分店"
        verbose_name_plural = "分店"

class Inventory(models.Model):
    Inventory_id = models.AutoField(primary_key=True)
    Inventory_name = models.CharField(max_length=100)
    Inventory_cost = models.DecimalField(max_digits=10, decimal_places=2)
    Inventory_unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return str(self.Inventory_id) + "_" + self.Inventory_name
    
    class Meta:
        verbose_name = "庫存"
        verbose_name_plural = "庫存"
        


"""
2. 銷售(Sale): 代表按摩椅的銷售記錄。
    銷售編號(Sale ID)
    銷售日期(Sale Date)
    銷售金額(Sale Amount)
    分店編號(Branch ID)[外鍵，關聯至分店實體]
"""
class Sale(models.Model):
    sale_id = models.AutoField(primary_key=True)
    sale_date = models.DateField(db_index=True)
    sale_volume = models.IntegerField(default=1)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, default=1)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.sale_id) + "_" + str(self.sale_date) + "_" + str(self.branch)
    
    class Meta:
        verbose_name = "銷量"
        verbose_name_plural = "銷量"

"""
4. 業務員(Salesperson): 代表按摩椅企業的業務員。
    業務員編號(Salesperson ID)
    業務員姓名(Salesperson Name)
"""
class Salesperson(models.Model):
    salesperson_id = models.AutoField(primary_key=True)
    salesperson_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.salesperson_name
    
    class Meta:
        verbose_name = "業務員"
        verbose_name_plural = "業務員"

"""
5. 顧客(Customer): 代表按摩椅企業的客人。
    顧客編號(Customer ID)
    顧客姓名(Customer Name)
    顧客等級(Customer Level)
"""
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    customer_level = models.IntegerField(choices=(
        (1, '普通會員'),
        (2, '高级會員'),
        (3, 'VIP會員')
    ), default=1)

    def get_customer_level(self):
        return {
            1: '普通會員',
            2: '高级會員',
            3: 'VIP會員'
        }[self.customer_level]
    
    def __str__(self):
        return self.customer_name
    
    class Meta:
        verbose_name = "顧客"
        verbose_name_plural = "顧客"

"""
6. 客戶進度(Customer Progress): 代表客戶在銷售過程中的進度。
    進度編號(Progress ID)
    客人編號(Customer ID)[外鍵，關聯至客人實體]
    銷售編號(Sale ID)[外鍵，關聯至銷售實體]
    業務員編號(Salesperson ID)[外鍵，關聯至業務員實體]
    進度狀態(Progress Status)
"""
class CustomerProgress(models.Model):
    progress_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, null=True)
    salesperson = models.ForeignKey(Salesperson, on_delete=models.CASCADE)
    progress_status = models.IntegerField(choices=(
        (1, '申辦會員'),
        (2, '體驗按摩椅'),
        (3, '購買完成')
    ), default=1)

    def get_customer_level(self):
        return {
            1: '申辦會員',
            2: '體驗按摩椅',
            3: '購買完成'
        }[self.progress_status]
    
    def __str__(self):
        return str(self.progress_id) + "_" + str(self.customer) + "_" + str(self.salesperson) + "_" + str(self.sale)
    
    class Meta:
        verbose_name = "客戶進度"
        verbose_name_plural = "客戶進度"

class Purchases(models.Model):
    ID = models.AutoField(primary_key=True)
    Date = models.DateField(db_index=True)
    Quantity = models.IntegerField(default=1)
    Inventory_id = models.ForeignKey(Inventory, on_delete=models.CASCADE, default=1)
    def __str__(self):
        return str(self.Date) + "_" + str(self.Inventory_id) + "_" + str(self.Quantity)
    class Meta:
        verbose_name = "進貨"
        verbose_name_plural = "進貨"
        

class Public_Massage_chair(models.Model):
    Inventory_id = models.ForeignKey(Inventory, on_delete=models.CASCADE, default=1)
    Date = models.DateField(db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    feedback = models.IntegerField(choices=(
        (1, '滿意'),
        (2, '不滿意')
    ), default=1)
    
    def get_feedback(self):
        return {
            1: '滿意',
            2: '不滿意'
        }[self.feedback]
    
    
    def __str__(self):
        return str(self.Date) + "_" + str(self.Inventory_id) + "_" + str(self.customer)
    
    class Meta:
        verbose_name = "公共按摩椅體驗"
        verbose_name_plural = "公共按摩椅體驗"