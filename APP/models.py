from django.db import models

# Create your models here.

class BRANCH(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    Address = models.CharField(max_length=100)
    District = models.IntegerField(choices=(
        (1, '北區'),
        (2, '中區'),
        (3, '南區')
    ), default=1)
    
    def get_district_name(self):
        return {
            1: '北區',
            2: '中區',
            3: '南區',
        }[self.District]
    
    def __str__(self):
        return self.Name
    
    class Meta:
        verbose_name = "分店"
        verbose_name_plural = "分店"

class PRODUCT_MODEL(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    
    def __str__(self):
        return str(self.ID) + "_" + self.Name
    
    class Meta:
        verbose_name = "產品型號"
        verbose_name_plural = "產品型號"

# 產品
class PRODUCT(models.Model):
    ID = models.AutoField(primary_key=True)
    Category = models.ForeignKey(PRODUCT_MODEL, on_delete=models.CASCADE)
    Cost = models.DecimalField(max_digits=10, decimal_places=0)
    Purchase_Date = models.DateField(db_index=True)
    State = models.IntegerField(choices=(
        (1, '庫存'),
        (2, '已售出'),
        (3, '體驗椅')
    ), default=1)
    
    def get_state_name(self):
        return {
            1: '庫存',
            2: '已售出',
            3: '體驗椅',
        }[self.State]
    
    def __str__(self):
        return str(self.ID) + "_" + self.Category.Name + "_" + str(self.Purchase_Date) + "_" + self.get_state_name()
    
    class Meta:
        verbose_name = "產品"
        verbose_name_plural = "產品"

# 銷售員
class SELLER(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)

    def __str__(self):
            return str(self.ID) + "_" + self.Name
    
    class Meta:
        verbose_name = "銷售員"
        verbose_name_plural = "銷售員"

# 顧客
class CUSTOMER(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    
    def __str__(self):
            return str(self.ID) + "_" + self.Name
    
    class Meta:
        verbose_name = "顧客"
        verbose_name_plural = "顧客"

# 銷售
class SALE(models.Model):
    ID = models.AutoField(primary_key=True)
    Seller = models.ForeignKey(SELLER, on_delete=models.CASCADE)
    Customer = models.ForeignKey(CUSTOMER, on_delete=models.CASCADE)
    Product = models.ForeignKey(PRODUCT, on_delete=models.CASCADE)
    Selling_Price = models.DecimalField(max_digits=10, decimal_places=0)
    Sale_Date = models.DateField(db_index=True)
    Branch = models.ForeignKey(BRANCH, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.ID) + "_" + self.Customer.Name + "_" + str(self.Product.Category.Name) + "_" + str(self.Sale_Date)
    
    class Meta:
        verbose_name = "銷售"
        verbose_name_plural = "銷售"

# 按摩椅體驗
class PUBLIC_MASSAGE_CHAIR(models.Model):
    ID = models.AutoField(primary_key=True)
    Customer = models.ForeignKey(CUSTOMER, on_delete=models.CASCADE)
    Seller = models.ForeignKey(SELLER, on_delete=models.CASCADE)
    Date = models.DateField(db_index=True)
    Product = models.ForeignKey(PRODUCT, on_delete=models.CASCADE)
    Feedback = models.IntegerField(choices=(
        (1, '滿意'),
        (2, '不滿意')
    ), default=1)
    
    def __str__(self):
        return str(self.ID) + "_" + self.Customer.Name + "_" + self.Seller.Name + "_" + str(self.Date)
    class Meta:
        verbose_name = "按摩椅體驗"
        verbose_name_plural = "按摩椅體驗"