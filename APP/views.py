from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth
from datetime import date, datetime, timedelta
from .models import *
from django.db.models.functions import ExtractQuarter

import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
import random

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
    profit_this_month = Sale.objects.filter(sale_date__range=(start_date_this_month, end_date_this_month))
    total_profit_int = 0
    for sale in profit_this_month:
        total_profit_int += sale.inventory.Inventory_unit_price * sale.sale_volume
    total_profit = format(int(total_profit_int), ",d")
    total_customers = CustomerProgress.objects.filter(sale__in = sales_this_month).values('customer').annotate(total=Count('customer')).count()
    
    
    # 獲取上個月 
    sales_last_month = Sale.objects.filter(sale_date__range=(start_date_last_month, end_date_last_month))
    sales_last_month_cnt = sales_last_month.count()
    profit_last_month = Sale.objects.filter(sale_date__range=(start_date_last_month, end_date_last_month))
    total_profit_last_month_int = 0
    for sale in profit_last_month:
        total_profit_last_month_int += sale.inventory.Inventory_unit_price * sale.sale_volume
    total_profit_last_month = format(int(total_profit_last_month_int), ",d")
    customers_last_month = CustomerProgress.objects.filter(sale__in = sales_last_month).values('customer').annotate(total=Count('customer')).count()
    
    # 計算變化量
    sales_increase = total_sales_cnt - sales_last_month_cnt
    sales_increase_percentage = int((sales_increase / sales_last_month_cnt) * 100) if sales_last_month_cnt != 0 else 0
    profit_increase = total_profit_int - total_profit_last_month_int
    profit_increase_percentage = int((profit_increase / total_profit_last_month_int) * 100) if total_profit_last_month_int != 0 else 0
    customer_increase = total_customers - customers_last_month
    customers_increase_percentage = int((customer_increase / customers_last_month) * 100) if customers_last_month != 0 else 0
    
    # 字體改變
    sales_increase_percentage_str = "increase" if sales_increase_percentage >= 0 else "decrease"
    sales_precentage_color = "text-success small pt-1 fw-bold" if sales_increase_percentage >= 0 else "text-danger small pt-1 fw-bold"
    profit_increase_percentage_str = "increase" if profit_increase_percentage >= 0 else "decrease"
    profit_precentage_color = "text-success small pt-1 fw-bold" if sales_increase_percentage >= 0 else "text-danger small pt-1 fw-bold"
    customers_increase_percentage_str = "increase" if customers_increase_percentage >= 0 else "decrease"
    customers_precentage_color = "text-success small pt-1 fw-bold" if customers_increase_percentage >= 0 else "text-danger small pt-1 fw-bold"
    
    sales_by_month = Sale.objects.filter(sale_date__year=current_year)
    monthly_customers = CustomerProgress.objects.annotate(month=ExtractMonth('sale__sale_date')).values('month').annotate(total_customers=Count('customer', distinct=True)).order_by('month')
    months_range = range(1, 13)
    
    sales_dict = {}
    profit_dict = {}
    customer_dict = {}
    
    for month in months_range:
        sales_dict[month] = 0
        profit_dict[month] = 0
        customer_dict[month] = 0
    
    for month in months_range:
        sales_count = 0
        profit_count = 0
        customer_count = 0
        for sale in sales_by_month:
            if sale.sale_date.month == month:
                sales_count = profit.sale_volume
                sales_dict[month] += sales_count
        
        for profit in sales_by_month:
            if profit.sale_date.month == month:
                profit_count = profit.inventory.Inventory_unit_price * profit.sale_volume
                profit_dict[month] += profit_count
        # print(f"Month {month}: {profit_count}")
        
        for customer in monthly_customers:
            if customer['month'] == month:
                customer_count = customer['total_customers']
        customer_dict[month] += customer_count
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
            sales = Sale.objects.filter(sale_id = id)
            for sale in sales:
                profit_total += sale.inventory.Inventory_unit_price * sale.sale_volume
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
        sale_list_month = Sale.objects.filter(branch = branch.branch_id, sale_date__range=(start_date_this_month, end_date_this_month))
        total_sale_month = 0
        for sale in sale_list_month:
            total_sale_month += sale.inventory.Inventory_unit_price * sale.sale_volume
        branche_dict[branch.branch_name] = total_sale_month
        
        sale_list_year = Sale.objects.filter(branch = branch.branch_id)
        total_sale_year = 0
        for sale in sale_list_year:
            if sale.sale_date.year == today.year:
                total_sale_year += sale.inventory.Inventory_unit_price * sale.sale_volume
        branche_dict_year[branch.branch_name] = total_sale_year
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
    print(branch_list_year)
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
            )
            for i in range(4):
                sales_amount = 0
                for entry in sales_by_quarter:
                    if entry.quarter == i + 1:
                        sales_amount = entry.inventory.Inventory_unit_price * entry.sale_volume
                        break
                loacl_total[i] += sales_amount
                q_table[i][idx + 1] += sales_amount
        q_list_2.append({'local': local_list[idx], 'value': loacl_total})
    for i in range(4):
        q_list.append({"q":i + 1, "value": q_table[i]})
    return render(request, 'season_rank.html', locals())

def maolee(request):
    
    current_year = datetime.now().year
    monthly_sale = Sale.objects.filter(sale_date__year=current_year)
    months_range = range(1, 13)
    sales_dict = {}
    profit_dict = {}
    cost_dict = {}
    
    for month in months_range:
        for sale in monthly_sale:
            sales_count = 0
            if sale.sale_date.month == month:
                sales_count = sale.inventory.Inventory_unit_price * sale.sale_volume
                break
        sales_dict[month] = sales_count
        
        for cost in monthly_sale:
            cost_count = 0
            if cost.sale_date.month == month:
                cost_count = sale.inventory.Inventory_cost * sale.sale_volume
                break
        cost_dict[month] = cost_count
        
        
        for profit in monthly_sale:
            profit_count = 0
            if profit.sale_date.month == month:
                profit_count = (sale.inventory.Inventory_unit_price - sale.inventory.Inventory_cost) * sale.sale_volume
                break
        profit_dict[month] = profit_count
        
    return render(request, 'maolee.html', locals())

def manyeedo(request):
    return render(request, 'manyeedo.html', locals())

def month_up(request):
    now_month = datetime.today().date().month
    months_range = [ i + 1 for i in range(now_month)]
    sales = Sale.objects.all()
    
    monthly_sales = [0 for _ in range(now_month)]
    for sale in sales:
        for month in months_range:
            if sale.sale_date.month == month + 1:
                monthly_sales[month] += sale.inventory.Inventory_unit_price * sale.sale_volume
                break
    
    monthly_sales_2d = [ [i] for i in monthly_sales]
    months_range = [ [i + 1] for i in range(now_month)]
    x, y = np.array(months_range), np.array(monthly_sales_2d)
    regressor = make_pipeline(PolynomialFeatures(3), LinearRegression())
    w = regressor.fit(x,y)
    predict = [[i + 1] for i in range(now_month, 12)]
    result = w.predict(predict)
    return render(request, 'month_up.html', locals())

def year_up(request):
    return render(request, 'year_up.html', locals())

def yagee(request):
    all_saler = Salesperson.objects.all()
    saler_list = []
    saler_cnt = []
    months_range = range(1, 13)
    month_list = []
    
    for saler in all_saler:
        this_saler_sale = CustomerProgress.objects.filter(sale = saler.salesperson_id)
        this_year = []
        cnt = 0
        for month in months_range:
            this_month = 0
            for sale in this_saler_sale:
                if sale.sale.sale_date.month == month:
                    this_month += sale.sale.inventory.Inventory_unit_price * sale.sale.sale_volume
                    cnt += 1
            this_year.append(this_month)
        saler_list.append({'name': saler.salesperson_name, 'data': this_year})
        saler_cnt.append({'name': saler.salesperson_name, 'data': cnt})
    
    
    for month in months_range:
        month_cnt = []
        for saler in all_saler:
            cnt = 0
            this_saler_sale = CustomerProgress.objects.filter(sale = saler.salesperson_id)
            for sale in this_saler_sale:
                if sale.sale.sale_date.month == month:
                    cnt += 1
            month_cnt.append(cnt)
        month_list.append({'month': month, 'data': month_cnt})
    return render(request, 'yagee.html', locals())

def yagee_all(request):
    return render(request, 'yagee_all.html', locals())

def stock(request):
    products = Inventory.objects.all()
    months_range = range(1, 13)
    stock_list = []
    total_purchase_cost = 0
    total_stock_cost = 0
    stock_list_sale = []
    
    product_stock_list = []
    
    for product in products:
        purchases = Purchases.objects.filter(Inventory_id = product.Inventory_id)
        month_list = []
        
        sales = Sale.objects.filter(inventory = product.Inventory_id)
        month_list_sale = []
        
        product_stock = 0
        for month in months_range:
            this_month = 0
            for purchase in purchases:
                if purchase.Date.month == month:
                    this_month += purchase.Quantity
                    total_purchase_cost += purchase.Quantity * purchase.Inventory_id.Inventory_cost
                    total_stock_cost += purchase.Quantity * purchase.Inventory_id.Inventory_cost
            month_list.append(this_month)
            
            this_month_sale = 0
            for sale in sales:
                if sale.sale_date.month == month:
                    this_month_sale += sale.sale_volume
                    total_stock_cost -= sale.sale_volume * sale.inventory.Inventory_cost
            month_list_sale.append(this_month_sale)
        
            product_stock += this_month - this_month_sale
        
        rgbValue=""
        for _ in range(6):
            rgbValue += random.choice("0123456789ABCDEF")

        rgbValue = "#"+rgbValue

        
        stock_list.append({'name': product.Inventory_name, 'data': month_list, 'rgb': rgbValue})
        stock_list_sale.append({'name': product.Inventory_name, 'data': month_list_sale, 'rgb': rgbValue})
        product_stock_list.append({'name': product.Inventory_name, 'data': product_stock, 'rgb': rgbValue})
    print(product_stock_list)
    return render(request, 'stock.html', locals())

def anmoyee(request):
    public_chairs = Public_Massage_chair.objects.all()
    satisfied = 0
    buy = 0
    
    for chair in public_chairs:
        if chair.get_feedback() == '滿意':
            satisfied += 1
        progresses = CustomerProgress.objects.filter(customer = chair.customer)
        for progress in progresses:
            if progress.get_customer_level() == '購買完成':
                buy += 1
    satisfied_rate = satisfied 
    unsatisfied_rate = public_chairs.count() - satisfied_rate
    
    buy_rate = buy
    not_buy_rate = public_chairs.count() - buy_rate
    
    chair_list = []
    all_chair = Inventory.objects.all()
    for chair in all_chair:
        public_chairs = Public_Massage_chair.objects.filter(Inventory_id = chair.Inventory_id)
        if public_chairs == None:
            continue
        chair_list.append({'name': chair.Inventory_name, "count": public_chairs.count()})
    
    return render(request, 'anmoyee.html', locals())