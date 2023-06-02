from django.contrib import admin
from .models import Branch, Sale, Profit, Salesperson, Customer, CustomerProgress

# Register your models here.

admin.site.register(Branch)
admin.site.register(Sale)
admin.site.register(Profit)
admin.site.register(Salesperson)
admin.site.register(Customer)
admin.site.register(CustomerProgress)