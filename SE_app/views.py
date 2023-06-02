from django.shortcuts import render

# Create your views here.

def index_customer_business(request):
    
    return render(request, 'business.html', locals)