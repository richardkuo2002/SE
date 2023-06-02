from django.shortcuts import render
from django.db.models import Sum, Count
from datetime import date, datetime, timedelta
from .models import *

# Create your views here.

def index(request):
    # 獲取當前日期
    today = date.today()
    
    # 獲取本月的第一天和最後一天
    today = datetime.today().date()
    start_date_this_month = today.replace(day=1)
    end_date_this_month = start_date_this_month.replace(day=1, month=start_date_this_month.month + 1)

    start_date_last_month = (start_date_this_month - timedelta(days=1)).replace(day=1)
    end_date_last_month = start_date_this_month - timedelta(days=1)

    # 獲取本月的銷售量
    sales_this_month = Sale.objects.filter(sale_date__range=(start_date_this_month, end_date_this_month))
    total_sales_cnt = sales_this_month.count()
    profit_this_month = Profit.objects.filter(sale__in = sales_this_month).aggregate(total = Sum('profit_amount'))
    total_profit = format(int(profit_this_month["total"]), ",d")
    total_customers = CustomerProgress.objects.filter(sale__in=sales_this_month).values('customer').annotate(total=Count('customer')).count()
    
    
    # 獲取上個月 
    sales_last_month = Sale.objects.filter(sale_date__range=(start_date_last_month, end_date_last_month))
    sales_last_month_cnt = sales_this_month.count()
    profit_last_month = Profit.objects.filter(sale__in = sales_last_month).aggregate(total = Sum('profit_amount'))
    total_profit_last_month = int(profit_last_month["total"]) if profit_last_month["total"] != None else 0
    customers_last_month = CustomerProgress.objects.filter(sale__in=sales_last_month).values('customer').annotate(total=Count('customer')).count()
    
    # 獲取差
    sales_increase = total_sales_cnt - sales_last_month_cnt
    sales_increase_percentage = int((sales_increase / sales_last_month_cnt) * 100) if sales_last_month_cnt != 0 else 0
    profit_increase = profit_this_month["total"] - total_profit_last_month
    profit_increase_percentage = int((profit_increase / total_profit_last_month) * 100) if total_profit_last_month != 0 else 0
    customer_increase = total_customers - customers_last_month
    customers_increase_percentage = int((customer_increase / customers_last_month) * 100) if customers_last_month != 0 else 0
    
    # 
    sales_increase_percentage_str = "increase" if sales_increase_percentage >= 0 else "decrease"
    sales_precentage_color = "text-success small pt-1 fw-bold" if sales_increase_percentage >= 0 else "text-danger small pt-1 fw-bold"
    profit_increase_percentage_str = "increase" if profit_increase_percentage >= 0 else "decrease"
    profit_precentage_color = "text-success small pt-1 fw-bold" if sales_increase_percentage >= 0 else "text-danger small pt-1 fw-bold"
    customers_increase_percentage_str = "increase" if customers_increase_percentage >= 0 else "decrease"
    customers_precentage_color = "text-success small pt-1 fw-bold" if customers_increase_percentage >= 0 else "text-danger small pt-1 fw-bold"
    
    sales_by_month = Sale.objects.values('sale_date__month').annotate(count=Count('sale_id'))

    for sale in sales_by_month:
        month = sale['sale_date__month']
        count = sale['count']
        print(f"Month {month}: {count}")


    
    return render(request, 'index.html', locals())

def business(request):
    
    return render(request, 'business.html', locals())

def customer(request):
    
    return render(request, 'customer.html', locals())