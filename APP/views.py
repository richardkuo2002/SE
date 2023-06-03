from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth
from datetime import date, datetime, timedelta
from .models import *
from django.db.models.functions import ExtractQuarter

# Create your views here.

def index(request):
    # 獲取當前日期
    today = date.today()
    current_year = datetime.now().year
    
    # 獲取本月的第一天和最後一天
    today = datetime.today().date()
    start_date_this_month = today.replace(day=1)
    end_date_this_month = start_date_this_month.replace(day=1, month=start_date_this_month.month + 1)

    start_date_last_month = (start_date_this_month - timedelta(days=1)).replace(day=1)
    end_date_last_month = start_date_this_month - timedelta(days=1)

    # 獲取本月的銷售量
    sales_this_month = Sale.objects.filter(sale_date__range=(start_date_this_month, end_date_this_month))
    total_sales_cnt = sales_this_month.count()
    profit_this_month = Sale.objects.filter(sale_date__range=(start_date_last_month, end_date_last_month)).aggregate(total = Sum('sale_amount'))
    total_profit = format(int(profit_this_month["total"]), ",d")
    total_customers = CustomerProgress.objects.filter(sale__in = sales_this_month).values('customer').annotate(total=Count('customer')).count()
    
    
    # 獲取上個月 
    sales_last_month = Sale.objects.filter(sale_date__range=(start_date_last_month, end_date_last_month))
    sales_last_month_cnt = sales_this_month.count()
    profit_last_month = Sale.objects.filter(sale_date__range=(start_date_last_month, end_date_last_month)).aggregate(total = Sum('sale_amount'))
    total_profit_last_month = int(profit_last_month["total"]) if profit_last_month["total"] != None else 0
    customers_last_month = CustomerProgress.objects.filter(sale__in = sales_last_month).values('customer').annotate(total=Count('customer')).count()
    
    # 計算變化量
    sales_increase = total_sales_cnt - sales_last_month_cnt
    sales_increase_percentage = int((sales_increase / sales_last_month_cnt) * 100) if sales_last_month_cnt != 0 else 0
    profit_increase = profit_this_month["total"] - total_profit_last_month
    profit_increase_percentage = int((profit_increase / total_profit_last_month) * 100) if total_profit_last_month != 0 else 0
    customer_increase = total_customers - customers_last_month
    customers_increase_percentage = int((customer_increase / customers_last_month) * 100) if customers_last_month != 0 else 0
    
    # 字體改變
    sales_increase_percentage_str = "increase" if sales_increase_percentage >= 0 else "decrease"
    sales_precentage_color = "text-success small pt-1 fw-bold" if sales_increase_percentage >= 0 else "text-danger small pt-1 fw-bold"
    profit_increase_percentage_str = "increase" if profit_increase_percentage >= 0 else "decrease"
    profit_precentage_color = "text-success small pt-1 fw-bold" if sales_increase_percentage >= 0 else "text-danger small pt-1 fw-bold"
    customers_increase_percentage_str = "increase" if customers_increase_percentage >= 0 else "decrease"
    customers_precentage_color = "text-success small pt-1 fw-bold" if customers_increase_percentage >= 0 else "text-danger small pt-1 fw-bold"
    
    sales_by_month = Sale.objects.filter(sale_date__year=current_year).values_list('sale_date__month').annotate(count=Count('sale_id'), month=Count('sale_date__month')).order_by('sale_date__month')
    monthly_profit = Sale.objects.filter(sale_date__year=current_year).values_list('sale_date__month').annotate(count=Sum('sale_amount'), month=Count('sale_date__month')).order_by('sale_date__month')
    monthly_customers = CustomerProgress.objects.annotate(month=ExtractMonth('sale__sale_date')).values('month').annotate(total_customers=Count('customer', distinct=True)).order_by('month')
    months_range = range(1, 13)
    
    sales_dict = {}
    profit_dict = {}
    customer_dict = {}
    for month in months_range:
        sales_count = 0
        profit_count = 0
        customer_count = 0
        for sale in sales_by_month:
            if sale[0] == month:
                sales_count = sale[1]
                break
        sales_dict[month] = sales_count
        # print(f"Month {month}: {sales_count}")
        
        for profit in monthly_profit:
            if profit[0] == month:
                profit_count = profit[1]
                break
        profit_dict[month] = profit_count
        
        for customer in monthly_customers:
            if customer['month'] == month:
                customer_count = customer['total_customers']
                break
        customer_dict[month] = customer_count
    return render(request, 'index.html', locals())

def business(request):
    salesperson_sales = Salesperson.objects.all()
    saleperson_dict = {}
    for sp in salesperson_sales:
        salesperson_id = sp.salesperson_id
        sale_ids = CustomerProgress.objects.filter(salesperson_id=salesperson_id).values_list('sale', flat=True)
        salesperson = Salesperson.objects.get(pk=salesperson_id)
        profit_total = 0
        for id in sale_ids:
            tmp_profit = Sale.objects.filter(sale_id = id).aggregate(total = Sum('sale_amount'))
            profit_total += tmp_profit['total']
        saleperson_dict[salesperson.salesperson_name] = profit_total
        saleperson_dict = dict(sorted(saleperson_dict.items(), key=lambda x: x[1]))
    salesperson_list = []
    for idx, (name, profit) in enumerate(reversed(saleperson_dict.items())):
        salesperson_list.append({'id': idx + 1, 'name': name, 'profit': profit})
    
    return render(request, 'business.html', locals())

def customer(request):
    customers = Customer.objects.all()
    customers_list = []
    for customer in customers:
        try:
            salesperson_id_list = CustomerProgress.objects.filter(customer=customer.customer_id).values_list('salesperson', flat=True).distinct()
        except:
            salesperson_id_list = []
        name_list = []
        for salesperson_id in salesperson_id_list:
            salesperson_name = Salesperson.objects.filter(salesperson_id = salesperson_id).values('salesperson_name')[0]
            name_list.append(salesperson_name['salesperson_name'])
        customers_list.append({'id': customer.customer_id, 'name': customer.customer_name, 'salesperson': name_list, 'label': customer.get_customer_level()})
    
    return render(request, 'customer.html', locals())

def sale_rank(request):
    today = datetime.today().date()
    start_date_this_month = today.replace(day=1)
    end_date_this_month = start_date_this_month.replace(day=1, month=start_date_this_month.month + 1)
    start_date_this_year = today.replace(day=1)
    end_date_this_year = start_date_this_year.replace(day=1, year=start_date_this_year.year + 1)
    
    branches = Branch.objects.all()
    branche_dict = {}
    branche_dict_year = {}
    for branch in branches:
        total_profit = Sale.objects.filter(branch = branch.branch_id, sale_date__range=(start_date_this_month, end_date_this_month)).aggregate(total=Sum('sale_amount'))
        branche_dict[branch.branch_name] = total_profit['total'] if total_profit['total'] != None else 0
        total_profit = Sale.objects.filter(branch = branch.branch_id, sale_date__range=(start_date_this_year, end_date_this_year)).aggregate(total=Sum('sale_amount'))
        branche_dict_year[branch.branch_name] = total_profit['total'] if total_profit['total'] != None else 0
    branche_dict = dict(sorted(branche_dict.items(), key=lambda x: x[1]))
    branche_dict_year = dict(sorted(branche_dict_year.items(), key=lambda x: x[1]))
    
    branch_list = []
    for idx, (key, value) in enumerate(reversed(branche_dict.items())):
        if idx == 3:
            break
        branch_list.append({'name': key, 'value': value})
    
    
    branch_list_year = []
    for idx, (key, value) in enumerate(reversed(branche_dict_year.items())):
        if idx == 3:
            break
        branch_list_year.append({'name': key, 'value': value})
    return render(request, 'sale_rank.html', locals())

def season_rank(request):
    current_year = date.today().year
    local_list = ['北區', '中區', '南區']
    q_table = [[0] * 4 for _ in range(4)]
    q_list = []
    q_list_2 = [{'local': "中原店", 'value': [0, 0, 0, 0]}]
    for idx in range(3):
        branches = Branch.objects.filter(local = idx + 1)
        loacl_total = [0 for _ in range(4)]
        for branch in branches:
            # 計算每季銷售額
            sales_by_quarter = Sale.objects.filter(sale_date__year=current_year, branch = branch.branch_id).annotate(
                quarter=ExtractQuarter('sale_date')
            ).values('quarter').annotate(sales_amount=Sum('sale_amount')).order_by('quarter')

            for i in range(4):
                sales_amount = 0
                for entry in sales_by_quarter:
                    if entry['quarter'] == i + 1:
                        sales_amount = entry['sales_amount']
                        break
                loacl_total[i] += sales_amount
                q_table[i][idx + 1] += sales_amount
        q_list_2.append({'local': local_list[idx], 'value': loacl_total})
    for i in range(4):
        q_list.append({"q":i + 1, "value": q_table[i]})
    return render(request, 'season_rank.html', locals())

def maolee(request):
    
    current_year = datetime.now().year
    monthly_sale = Sale.objects.filter(sale_date__year=current_year).values_list('sale_date__month').annotate(count=Sum('sale_amount'), month=Count('sale_date__month')).order_by('sale_date__month')
    monthly_profit = Profit.objects.annotate(month=ExtractMonth('sale__sale_date')).values('month').annotate(total=Sum('profit_amount', distinct=True)).order_by('month')
    months_range = range(1, 13)
    sales_dict = {}
    profit_dict = {}
    
    for month in months_range:
        for sale in monthly_sale:
            sales_count = 0
            if sale[0] == month:
                sales_count = sale[1]
                break
        sales_dict[month] = sales_count
        
        for profit in monthly_profit:
            profit_count = 0
            if profit['month'] == month:
                profit_count = profit['total']
                break
        profit_dict[month] = profit_count
    return render(request, 'maolee.html', locals())