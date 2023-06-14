from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth
from datetime import date, datetime, timedelta
from .models import *
from django.db.models.functions import ExtractQuarter

import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import make_pipeline
import random

# Create your views here.

def index(request):
    # 獲取當前日期
    today = date.today()
    
    # 計算這個月
    This_Month_Sales = SALE.objects.filter(Sale_Date__month = today.month, Sale_Date__year = today.year)
    This_Month_Sales_Count = This_Month_Sales.count()
    This_month_Revenue = 0
    This_month_Customer_Count = 0
    count = []
    for sale in This_Month_Sales:
        This_month_Revenue += sale.Selling_Price
        try:
            count.index(sale.Customer.ID)
        except:
            count.append(sale.Customer.ID)
            This_month_Customer_Count += 1
    
    # 計算上個月
    Last_Month_Sales = SALE.objects.filter(Sale_Date__month = today.month - 1, Sale_Date__year = today.year)
    Last_Month_Sales_Count = Last_Month_Sales.count()
    Last_month_Revenue = 0
    Last_month_Customer_Count = 0
    count = []
    for sale in Last_Month_Sales:
        Last_month_Revenue += sale.Selling_Price
        try:
            count.index(sale.Customer.ID)
        except:
            count.append(sale.Customer.ID)
            Last_month_Customer_Count += 1
    
    # 計算變化量
    Delta_Sales_Count = This_Month_Sales_Count - Last_Month_Sales_Count
    Delta_Sales_Count_Percentage = int((Delta_Sales_Count / Last_Month_Sales_Count) * 100) if Last_Month_Sales_Count != 0 else 0
    Delta_Revenue = This_month_Revenue - Last_month_Revenue
    Delta_Revenue_Percentage = int((Delta_Revenue / Last_month_Revenue) * 100) if Last_month_Revenue != 0 else 0
    Delta_Customer_Count = This_month_Customer_Count - Last_month_Customer_Count
    Delta_Customer_Count_Percentage = int((Delta_Customer_Count / Last_month_Customer_Count) * 100) if Last_month_Customer_Count != 0 else 0
    
    # 字體改變
    sales_increase_percentage_str = "increase" if Delta_Sales_Count_Percentage >= 0 else "decrease"
    sales_precentage_color = "text-success small pt-1 fw-bold" if Delta_Sales_Count_Percentage >= 0 else "text-danger small pt-1 fw-bold"
    profit_increase_percentage_str = "increase" if Delta_Revenue_Percentage >= 0 else "decrease"
    profit_precentage_color = "text-success small pt-1 fw-bold" if Delta_Revenue_Percentage >= 0 else "text-danger small pt-1 fw-bold"
    customers_increase_percentage_str = "increase" if Delta_Customer_Count_Percentage >= 0 else "decrease"
    customers_precentage_color = "text-success small pt-1 fw-bold" if Delta_Customer_Count_Percentage >= 0 else "text-danger small pt-1 fw-bold"
    
    sales_by_month = SALE.objects.filter(Sale_Date__year = today.year)
    monthly_customers = SALE.objects.annotate(month=ExtractMonth('Sale_Date')).values('month').annotate(total_customers=Count('Customer', distinct=True)).order_by('month')
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
            if sale.Sale_Date.month == month:
                sales_dict[month] += 1
        
        for profit in sales_by_month:
            if profit.Sale_Date.month == month:
                profit_dict[month] += profit.Selling_Price
        # print(f"Month {month}: {profit_count}")
        
        for customer in monthly_customers:
            if customer['month'] == month:
                customer_count = customer['total_customers']
        customer_dict[month] += customer_count
    return render(request, 'index.html', locals())

# def business(request):
#     salesperson_sales = SELLER.objects.all()
#     saleperson_dict = {}
#     for sp in salesperson_sales:
#         salesperson_id = sp.salesperson_id
#         sale_ids = CustomerProgress.objects.filter(salesperson_id=salesperson_id).values_list('sale', flat=True)
#         salesperson = Salesperson.objects.get(pk=salesperson_id)
#         profit_total = 0
#         for id in sale_ids:
#             sales = Sale.objects.filter(sale_id = id)
#             for sale in sales:
#                 profit_total += sale.inventory.Inventory_unit_price * sale.sale_volume
#         saleperson_dict[salesperson.salesperson_name] = profit_total
#         saleperson_dict = dict(sorted(saleperson_dict.items(), key=lambda x: x[1]))
#     salesperson_list = []
#     for idx, (name, profit) in enumerate(reversed(saleperson_dict.items())):
#         salesperson_list.append({'id': idx + 1, 'name': name, 'profit': profit})
    
#     return render(request, 'business.html', locals())

def customer(request):
    Customers = CUSTOMER.objects.all()
    Customers_List = []
    for Customer in Customers:
        name_list = []
        Sales = SALE.objects.filter(Customer = Customer.ID)
        for Sale in Sales:
            try:
                name_list.index(Sale.Seller.Name)
            except:
                name_list.append(Sale.Seller.Name)
        print(name_list)
        Customers_List.append({'ID': Customer.ID, 'Name': Customer.Name, 'Sellers': name_list, 'label': "普通會員"})
    
    return render(request, 'customer.html', locals())

def sale_rank(request):
    today = datetime.today()
    branches = BRANCH.objects.all()
    branche_dict = {}
    branche_dict_year = {}
    for branch in branches:
        This_Month_Sales = SALE.objects.filter(Branch = branch.ID, Sale_Date__month = today.month, Sale_Date__year = today.year)
        total_sale_month = 0
        for Sale in This_Month_Sales:
            total_sale_month += Sale.Selling_Price
        branche_dict[branch.Name] = total_sale_month
        
        This_Year_Sales = SALE.objects.filter(Branch = branch.ID, Sale_Date__year = today.year)
        total_sale_year = 0
        for Sale in This_Year_Sales:
            total_sale_year += Sale.Selling_Price
        branche_dict_year[branch.Name] = total_sale_year
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
    q_list_2 = []
    sales_by_quarter = SALE.objects.filter(Sale_Date__year=current_year, Branch_id = 1).annotate(
                quarter=ExtractQuarter('Sale_Date')
            )
    loacl_total = [0 for _ in range(4)]
    for i in range(4):
        sales_amount = 0
        for entry in sales_by_quarter:
            if entry.quarter == i + 1:
                sales_amount = entry.Selling_Price
                break
        loacl_total[i] += sales_amount
        q_table[i][0] += sales_amount
    q_list_2.append({'local': "中原店", 'value': loacl_total})
    
    for idx in range(3):
        branches = BRANCH.objects.filter(District = idx + 1)
        loacl_total = [0 for _ in range(4)]
        for branch in branches:
            # 計算每季銷售額
            sales_by_quarter = SALE.objects.filter(Sale_Date__year=current_year, Branch_id = branch.ID).annotate(
                quarter=ExtractQuarter('Sale_Date')
            )
            for i in range(4):
                sales_amount = 0
                for entry in sales_by_quarter:
                    if entry.quarter == i + 1:
                        sales_amount = entry.Selling_Price
                        break
                loacl_total[i] += sales_amount
                q_table[i][idx + 1] += sales_amount
        q_list_2.append({'local': local_list[idx], 'value': loacl_total})
    for i in range(4):
        q_list.append({"q":i , "value": q_table[i]})
    return render(request, 'season_rank.html', locals())

def maolee(request):
    current_year = datetime.now().year
    This_Year_Sales = SALE.objects.filter(Sale_Date__year=current_year)
    This_Year_Product = PRODUCT.objects.filter(Purchase_Date__year=current_year)
    months_range = range(1, 13)
    sales_dict = {}
    profit_dict = {}
    cost_dict = {}
    
    for month in months_range:
        This_Month_Sales = 0
        This_Month_Cost = 0
        This_Month_Profit = 0
        for sale in This_Year_Sales:
            if sale.Sale_Date.month == month:
                This_Month_Sales += sale.Selling_Price
                
        for Purchase in This_Year_Product:
            if Purchase.Purchase_Date.month == month:
                This_Month_Cost += Purchase.Cost
        
        This_Month_Profit += This_Month_Sales - This_Month_Cost
        sales_dict[month] = This_Month_Sales
        cost_dict[month] = This_Month_Cost
        profit_dict[month] = This_Month_Profit
        
    return render(request, 'maolee.html', locals())

def manyeedo(request):
    return render(request, 'manyeedo.html', locals())

def month_up(request):
    today = date.today()
    months_range = [ i + 1 for i in range(today.month)]
    
    monthly_sales = [0 for _ in range(today.month)]
    feature_list = []
    
    for month in months_range:
        This_Month_Sales = SALE.objects.filter(Sale_Date__month = month)
        count = []
        This_month_Customer_Count = 0
        
        for sale in This_Month_Sales:
            if sale.Sale_Date.month == month:
                monthly_sales[month - 1] += sale.Selling_Price
            
            try:
                count.index(sale.Customer.ID)
            except:
                count.append(sale.Customer.ID)
                This_month_Customer_Count += 1
        
        feature_list.append([month])
        
            
        
    monthly_sales_2d = [[i] for i in monthly_sales]
    
        
    
    x, y = np.array(feature_list), np.array(monthly_sales_2d)
    regressor = make_pipeline(PolynomialFeatures(1), LinearRegression())
    # regressor = make_pipeline(PolynomialFeatures(1), LogisticRegression())
    w = regressor.fit(x,y)
    predict = [[i + 1] for i in range(today.month, 12)]
    result = w.predict(predict)
    return render(request, 'month_up.html', locals())

def year_up(request):
    return render(request, 'year_up.html', locals())

def yagee(request):
    today = date.today()
    all_saler = SELLER.objects.all()
    saler_list = []
    saler_cnt = []
    months_range = range(1, 13)
    month_list = []
    
    for saler in all_saler:
        this_saler_sale = SALE.objects.filter(Seller = saler.ID, Sale_Date__year = today.year)
        this_year = []
        cnt = 0
        for month in months_range:
            this_month = 0
            for sale in this_saler_sale:
                if sale.Sale_Date.month == month:
                    this_month += sale.Selling_Price
                    cnt += 1
            this_year.append(this_month)
        saler_list.append({'name': saler.Name, 'data': this_year})
        saler_cnt.append({'name': saler.Name, 'data': cnt})
    
    
    for month in months_range:
        month_cnt = []
        for saler in all_saler:
            cnt = 0
            this_saler_sale = SALE.objects.filter(Seller = saler.ID, Sale_Date__year = today.year)
            for sale in this_saler_sale:
                if sale.Sale_Date.month == month:
                    cnt += 1
            month_cnt.append(cnt)
        month_list.append({'month': month, 'data': month_cnt})
    return render(request, 'yagee.html', locals())

def yagee_all(request):
    today = date.today()
    This_Year = today.year
    Last_Year = today.year - 1
    months_range = range(1, 13)
    This_Year_Sales = SALE.objects.filter(Sale_Date__year=today.year)
    Last_Year_Sales = SALE.objects.filter(Sale_Date__year=today.year - 1)
    This_Year_Sales_dict = []
    Last_Year_Sales_dict = []
    
    This_Year_Revenue = 0
    Last_Year_Revenue = 0
    for month in months_range:
        This_Month_Revenue = 0
        for sale in This_Year_Sales:
            if sale.Sale_Date.month == month:
                This_Month_Revenue += sale.Selling_Price
        This_Year_Sales_dict.append(This_Month_Revenue)
        This_Year_Revenue += This_Month_Revenue
        
        Last_Month_Revenue = 0
        for sale in Last_Year_Sales:
            if sale.Sale_Date.month == month:
                Last_Month_Revenue += sale.Selling_Price
        Last_Year_Sales_dict.append(Last_Month_Revenue)
        Last_Year_Revenue += Last_Month_Revenue
        
    return render(request, 'yagee_all.html', locals())

def stock(request):
    today = date.today()
    Products_Category =  PRODUCT_MODEL.objects.all()
    Sales = SALE.objects.all()
    months_range = range(1, 13)
    Monthly_Count = []
    Total_Purchase_Cost = 0
    Total_Stock_Cost = 0
    
    for Category in Products_Category:
        Purchase_List = []
        Sale_List = []
        for month in months_range:
            This_Month_Purchase = PRODUCT.objects.filter(Category = Category.ID, Purchase_Date__month = month, Purchase_Date__year = today.year)
            This_Month_Purchase_Count = This_Month_Purchase.count()
            Purchase_List.append(This_Month_Purchase_Count)
            for Purchase in This_Month_Purchase:
                Total_Purchase_Cost += Purchase.Cost
            
            This_Month_Sale = SALE.objects.filter(Product__Category = Category.ID, Sale_Date__month = month, Sale_Date__year = today.year)
            This_Month_Sale_Count = This_Month_Sale.count()
            Sale_List.append(This_Month_Sale_Count)
            
        
        Stocks = PRODUCT.objects.filter(Category = Category.ID, Purchase_Date__year = today.year, State = 1)
        Stock_Count = Stocks.count()
        for Stock in Stocks:
            Total_Stock_Cost += Stock.Cost
                
        rgbValue=""
        for _ in range(6):
            rgbValue += random.choice("0123456789ABCDEF")
        rgbValue = "#" + rgbValue
        
        Monthly_Count.append({"Name": Category.Name, "Purchase_Data": Purchase_List, "Sale_Data": Sale_List, "rgb": rgbValue, "Stock": Stock_Count})

    return render(request, 'stock.html', locals())

def anmoyee(request):
    Public_Chairs = PRODUCT.objects.filter(State = 3)
    Satisfied = PUBLIC_MASSAGE_CHAIR.objects.filter(Feedback = 1).count()
    Unsatisfied = PUBLIC_MASSAGE_CHAIR.objects.filter(Feedback = 2).count()
    Buy = 0
    Not_Buy = 0
    
    Chair_List = []
    
    for Chair in Public_Chairs:
        
        Experiences = PUBLIC_MASSAGE_CHAIR.objects.filter(Product = Chair.ID)
        Experience_Count = Experiences.count()
        for Experience in Experiences:
            Experience_Day = Experience.Date
            Customer = Experience.Customer
            Product = Experience.Product.Category
            if SALE.objects.filter(Customer = Customer, Sale_Date = Experience_Day, Product__Category = Product).count() > 0:
                Buy += 1
            else:
                Not_Buy += 1
        Chair_List.append({"Name": Chair.Category.Name, "Experience_Count": Experience_Count})
    
    return render(request, 'anmoyee.html', locals())