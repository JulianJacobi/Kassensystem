from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from . import models
import json
from kassensystem import settings
import time


@login_required
@csrf_exempt
def update_menu_view(request, menu_id):
    try:
        menu = models.Menu.objects.get(id=menu_id)
        if request.method == 'POST':
            menu.products.clear()
            data = json.loads(request.POST['data'])
            for menu_entry in data:
                product = models.Product.objects.get(id=menu_entry['menu_id'])
                models.MenuItem.objects.create(menu=menu,
                                               product=product,
                                               color=menu_entry['color'],
                                               sort=menu_entry['sort'])
            return HttpResponse('', 200)
    except models.Menu.DoesNotExist:
        return HttpResponse('', 404)


@login_required
@csrf_exempt
def search_products(request):
    if 'q' in request.GET:
        products = models.Product.objects.filter(name__icontains=request.GET['q'])
        return_value = []
        for product in products:
            return_value.append({
                'name': product.name,
                'price': str(product.price),
                'id': product.id,
            })
        return JsonResponse(return_value, safe=False, status=200)
    return HttpResponse('', 400)


@login_required
@csrf_exempt
def open_drawer(request):
    if request.method == 'POST':
        if settings.GPIO_AVAILABLE and settings.GPIO_OPEN is not None and settings.GPIO_DETECTION is not None:
            import RPi.GPIO as gpio
            gpio.output(settings.GPIO_OPEN, gpio.HIGH)
            time.sleep(0.2)
            gpio.output(settings.GPIO_OPEN, gpio.LOW)
            while gpio.input(settings.GPIO_DETECTION) == gpio.LOW:
                time.sleep(0.5)
            return HttpResponse('OK', status=200)
        else:
            return HttpResponse('Drawer could not be opened', status=400)
    else:
        return HttpResponse('Only POST allowed', status=400)


@login_required
@csrf_exempt
def add_sale_view(request):
    if request.method == 'POST':
        if 'products' in request.POST:
            products = json.loads(request.POST['products'])
            database_products = []
            price = 0.0
            for product in products:
                database_products.append({
                    'name': product['name'],
                    'price': product['price']
                })
                price += product['price']
            account_entry = models.AccountEntry()
            account_entry.type = 'sale'
            account_entry.comment = 'billing:'+json.dumps(database_products)
            account_entry.amount = price
            account_entry.user = request.user.username
            account_entry.save()
            return HttpResponse('', status=200)
        else:
            return HttpResponse('', status=404)
    else:
        return HttpResponse('Only POST allowed', status=400)


@login_required()
def time_view(request):
    return HttpResponse(int(timezone.now().timestamp()), status=200)
