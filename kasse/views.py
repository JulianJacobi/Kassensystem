from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from . import forms
from . import models
from django.contrib.auth import models as auth_models
import json
from datetime import timedelta
from django.conf import settings
import netifaces
from kasse.lib import worker_com
import debinterface


@login_required
def kasse_view(request):
    menus = models.Menu.objects.all()
    tablesets = models.TableSet.objects.all()
    return render(request, 'kasse.html', context={'title': 'Kasse',
                                                  'menus': menus,
                                                  'tablesets': tablesets})


@login_required
def menu_view(request, menu_id):
    try:
        menu = models.Menu.objects.get(id=menu_id)
        return render(request, 'menu.html', context={'title': 'Kasse {}'.format(menu.name),
                                                     'menu': menu,
                                                     'gpio_available': settings.GPIO_AVAILABLE})
    except models.Menu.DoesNotExist:
        return redirect('kasse:kasse')


@login_required
def tableset_view(request, table_set_id):
    try:
        tableset = models.TableSet.objects.get(id=table_set_id)
        return render(request, 'tableset.html', context={'title': 'Tischanordnung {}'.format(tableset.name),
                                                         'tableset': tableset})
    except models.TableSet.DoesNotExist:
        return redirect('kasse:kasse')


@login_required
def table_menu_view(request, table_set_id, table_id):
    try:
        tableset = models.TableSet.objects.get(id=table_set_id)
        table = tableset.table_set.get(id=table_id)
        menu = tableset.menu

        if table.bookings != '':
            bookings = json.loads(table.bookings)
        else:
            bookings = []

        total = 0.0
        for booking in bookings:
            total += booking.get('price', 0.0)

        categories = {}
        for category in models.ProductCategory.objects.filter(products__menu=menu):
            products = category.products.filter(menu=menu)
            categories[category.name] = products
        uncategorized = menu.products.filter(category__isnull=True)

        return render(request, 'table_menu.html', context={'title': 'Tisch {}'.format(table.name),
                                                           'table': table,
                                                           'bookings': bookings,
                                                           'total': total,
                                                           'categories': categories,
                                                           'uncategorized': uncategorized,
                                                           'menu': menu})
    except models.TableSet.DoesNotExist:
        return redirect('kasse:kasse')
    except models.Table.DoesNotExist:
        return redirect('kasse:tableset', table_set_id=table_set_id)


@login_required
def add_product_to_table_view(request, table_set_id, table_id):
    try:
        tableset = models.TableSet.objects.get(id=table_set_id)
        table = tableset.table_set.get(id=table_id)
        product = models.Product.objects.get(id=request.GET.get('productId', default=None))
        if table.bookings != '':
            bookings = json.loads(table.bookings)
        else:
            bookings = []
        bookings.append({'name': product.name, 'price': float(product.price.amount)})
        table.bookings = json.dumps(bookings)
        table.save()
    except models.TableSet.DoesNotExist:
        return redirect('kasse:kasse')
    except models.Table.DoesNotExist:
        return redirect('kasse:tableset', table_set_id=table_set_id)
    except models.Product.DoesNotExist:
        pass
    return redirect('kasse:table_menu', table_set_id=table_set_id, table_id=table_id)


@login_required
def remove_product_from_table_view(request, table_set_id, table_id):
    try:
        tableset = models.TableSet.objects.get(id=table_set_id)
        table = tableset.table_set.get(id=table_id)
        index = int(request.GET.get('index', default=None))
        all = int(request.GET.get('all', default=False))
        if index is not None and table.bookings != '':
            bookings = json.loads(table.bookings)
            bookings.pop(index)
            table.bookings = json.dumps(bookings)
            table.save()
        if all:
            table.bookings = ""
            table.save()
        return redirect('kasse:table_menu', table_set_id=table_set_id, table_id=table_id)
    except models.TableSet.DoesNotExist:
        return redirect('kasse:kasse')
    except models.Table.DoesNotExist:
        return redirect('kasse:tableset', table_set_id=table_set_id)


@login_required
def book_table_view(request, table_set_id, table_id):
    try:
        tableset = models.TableSet.objects.get(id=table_set_id)
        table = tableset.table_set.get(id=table_id)
        account_entry = models.AccountEntry(type='sale',
                                            comment='billing:{}'.format(table.bookings),
                                            amount=table.total(),
                                            user=request.user)
        account_entry.save()
        table.bookings = ''
        table.save()
        return redirect('kasse:tableset', table_set_id=table_set_id)
    except models.TableSet.DoesNotExist:
        return redirect('kasse:kasse')
    except models.Table.DoesNotExist:
        return redirect('kasse:tableset', table_set_id=table_set_id)


@login_required
def settings_view(request):
    menus = models.Menu.objects.all()
    table_sets = models.TableSet.objects.all()
    return render(request, 'settings/checkout_list.html', context={'title': 'Einstellungen',
                                                                   'menus': menus,
                                                                   'table_sets': table_sets})


@login_required
def add_menu_view(request):
    if request.method == 'POST':
        form = forms.MenuForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kasse:settings')
    else:
        form = forms.MenuForm()

    return render(request, 'settings/menu_form.html', context={'title': 'Menu erstellen',
                                                               'form': form})


@login_required
def add_table_set_view(request):
    if request.method == 'POST':
        form = forms.TableSetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kasse:settings')
    else:
        form = forms.TableSetForm()

    return render(request, 'settings/table_set_form.html', context={'title': 'Tischanordnung erstellen',
                                                                    'form': form})


@login_required
def product_list_view(request):
    products = models.Product.objects.all()
    product_categories = models.ProductCategory.objects.all()
    return render(request, 'settings/product_list.html', context={'title': 'Produkte',
                                                                  'products': products,
                                                                  'product_categories': product_categories})


@login_required
def add_product_view(request):
    if request.method == 'POST':
        form = forms.ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kasse:product_list')
    else:
        form = forms.ProductForm()

    return render(request, 'settings/product_form.html', context={'title': 'Produkt erstellen',
                                                                  'form': form})


@login_required
def edit_product_view(request, product_id):
    try:
        product = models.Product.objects.get(id=product_id)
        if request.method == 'POST':
            form = forms.ProductForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
                return redirect('kasse:product_list')
        else:
            form = forms.ProductForm(instance=product)
        return render(request, 'settings/product_form.html', context={'title': 'Produkt bearbeiten',
                                                                      'form': form})
    except models.Product.DoesNotExist:
        return redirect('kasse:product_list')


@login_required
def remove_product(request, product_id):
    try:
        if request.method == 'POST':
            product = models.Product.objects.get(id=product_id)
            product.delete()
    except models.Product.DoesNotExist:
        pass
    return redirect('kasse:product_list')


@login_required
def add_product_category_view(request):
    if request.method == 'POST':
        form = forms.ProductCategoryForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('kasse:product_list')
    else:
        form = forms.ProductCategoryForm()
    return render(request, 'settings/product_category_form.html', context={'title': 'Produktkategorie erstellen',
                                                                           'form': form})


@login_required
def edit_product_category_view(request, product_category_id):
    try:
        product_category = models.ProductCategory.objects.get(id=product_category_id)
        if request.method == 'POST':
            form = forms.ProductCategoryForm(instance=product_category, data=request.POST)
            if form.is_valid():
                form.save()
                return redirect('kasse:product_list')
        else:
            form = forms.ProductCategoryForm(instance=product_category)
        return render(request, 'settings/product_category_form.html', context={'title': 'Produktkategorie bearbeiten',
                                                                               'form': form,
                                                                               'edit': True})
    except models.ProductCategory.DoesNotExist:
        redirect('kasse:product_list')


@login_required
def delete_product_category_view(request, product_category_id):
    try:
        product_category = models.ProductCategory.objects.get(id=product_category_id)
        if request.method == 'POST':
            product_category.delete()
    except models.ProductCategory.DoesNotExist:
        pass
    return redirect('kasse:product_list')


@login_required
def menu_edit_view(request, menu_id):
    try:
        menu = models.Menu.objects.get(id=menu_id)
        return render(request, 'settings/menu_settings.html', context={'title': 'Menü "{}"'.format(menu.name),
                                                                       'menu': menu,
                                                                       'all_products': models.Product.objects.all()})
    except models.Menu.DoesNotExist:
        return redirect('kassse:settings')


@login_required
def table_set_edit_view(request, table_set_id):
    try:
        table_set = models.TableSet.objects.get(id=table_set_id)
        return render(request, 'settings/table_set_settings.html', context={
            'title': 'Tischanordnung "{}"'.format(table_set.name),
            'table_set': table_set,
        })

    except models.TableSet.DoesNotExist:
        return redirect('kasse:settings')


@login_required
def table_set_data_edit_view(request, table_set_id):
    try:
        table_set = models.TableSet.objects.get(id=table_set_id)
        if request.method == 'POST':
            form = forms.TableSetForm(instance=table_set, data=request.POST)
            if form.is_valid():
                form.save(commit=True)
                return redirect(reverse('kasse:edit_table_set', kwargs={'table_set_id': table_set.id}))
        else:
            form = forms.TableSetForm(instance=table_set)
        return render(request, 'settings/table_set_form.html', context={'title': 'Tischanordnung bearbeiten',
                                                                        'form': form})
    except models.TableSet.DoesNotExist:
        return redirect('kasse:settings')


@login_required
def menu_delete_view(request, menu_id):
    try:
        if request.method == 'POST':
            menu = models.Menu.objects.get(id=menu_id)
            menu.delete()
    except models.Menu.DoesNotExist:
        pass
    return redirect('kasse:settings')


@login_required
def table_set_delete_view(request, table_set_id):
    try:
        if request.method == 'POST':
            table_set = models.TableSet.objects.get(id=table_set_id)
            table_set.delete()
    except models.TableSet.DoesNotExist:
        pass
    return redirect('kasse:settings')


@login_required
def users_view(request):
    users = auth_models.User.objects.all()
    return render(request, 'settings/users.html', context={'title': 'Benutzer', 'users': users})


@login_required
def add_user_view(request):
    if request.method == 'POST':
        form = forms.UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kasse:users')
    else:
        form = forms.UserCreationForm()
    return render(request, 'settings/create_user_form.html', context={'title': 'Benutzer erstellen', 'form': form})


@login_required
def set_password_view(request, user_id):
    try:
        user = auth_models.User.objects.get(id=user_id)
        if request.method == 'POST':
            form = forms.SetPasswordForm(data=request.POST, user=user)
            if form.is_valid():
                form.save()
                return redirect('kasse:users')
        else:
            form = forms.SetPasswordForm(user=user)
        return render(request, 'settings/set_password.html', context={'title': 'Passwort setzen',
                                                                      'edituser': user,
                                                                      'form': form})
    except auth_models.User.DoesNotExist:
        return redirect('kasse:users')


@login_required
def remove_user_view(request, user_id):
    if request.method == 'POST':
        try:
            user = auth_models.User.objects.get(id=user_id)
            user.delete()
        except auth_models.User.DoesNotExist:
            pass
    return redirect('kasse:users')


@login_required
def events_view(request):
    events = models.Event.objects.all().order_by('start')
    return render(request, 'settings/events.html', context={'title': 'Events', 'events': events})


@login_required
def create_event_view(request):
    if request.method == 'POST':
        form = forms.EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kasse:events')
    else:
        form = forms.EventForm()
    return render(request, 'settings/event_form.html', context={'title': 'Event erstellen', 'form': form})


@login_required
def edit_event_view(request, event_id):
    try:
        event = models.Event.objects.get(id=event_id)
        if request.method == 'POST':
            form = forms.EventForm(request.POST, instance=event)
            if form.is_valid():
                form.save()
                return redirect('kasse:events')
        else:
            form = forms.EventForm( instance=event)
        return render(request, 'settings/event_form.html', context={'title': 'Event beareiten', 'form': form})
    except models.Event.DoesNotExist:
        return redirect('kasse:events')


@login_required
def delete_event_view(request, event_id):
    if request.method == 'POST':
        try:
            event = models.Event.objects.get(id=event_id)
            event.delete()
        except models.Event.DoesNotExist:
            pass
    return redirect('kasse:events')


@login_required
def event_view(request, event_id):
    try:
        event = models.Event.objects.get(id=event_id)
        entries = models.AccountEntry.objects\
            .filter(timestamp__range=(event.start, event.end)).order_by('timestamp')
        complete_sum = 0.0
        for entry in entries:
            complete_sum += entry.amount
        return render(request, 'settings/event.html', context={'title': event.name,
                                                               'event': event,
                                                               'entries': entries,
                                                               'complete_sum': complete_sum})
    except models.Event.DoesNotExist:
        return redirect('kasse:events')


@login_required
def event_stats_view(request, event_id):
    try:
        event = models.Event.objects.get(id=event_id)
        account_entries = models.AccountEntry.objects\
            .filter(timestamp__range=(event.start, event.end)).order_by('timestamp')
        sale_entries = []
        for entry in account_entries:

            if entry.type == 'sale':
                products = []
                if entry.comment[:8] == 'billing:':
                    billing_object = json.loads(entry.comment[8:])
                    for product in billing_object:
                        products.append(product['name'])
                sale_entries.append({
                    'timestamp': entry.timestamp,
                    'products': products
                })
        products_count = {}
        overall_products = 0
        for entry in sale_entries:
            for product in entry['products']:
                if product in products_count:
                    products_count[product] += 1
                else:
                    products_count[product] = 1
                overall_products += 1
        amount_time = []
        current_time = event.start
        while current_time < event.end:
            delta_entries = models.AccountEntry.objects.filter(timestamp__range=(current_time,
                                                                                 current_time+timedelta(minutes=5)))
            amount = 0
            for entry in delta_entries:
                if entry.type == 'sale':
                    amount += abs(float(entry.amount))
            amount_time.append({
                'timestamp': current_time.timestamp(),
                'amount': amount,
            })

            current_time = current_time + timedelta(minutes=3)

        return render(request, 'settings/stats.html', context={'title': 'Event Statistiken',
                                                               'event': event,
                                                               'products_count': products_count,
                                                               'overall_products': overall_products,
                                                               'amount_time': amount_time})
    except models.Event.DoesNotExist:
        return redirect('kasse:events')


@login_required()
def general_settings_view(request):
    context = {'title': 'Einstellungen', 'errors': [], 'ip_form': forms.IpEditForm(), 'time_form': forms.TimeEditForm()}

    if request.method == 'POST':
        if 'type' in request.POST and request.POST['type'] == 'network':
            form = forms.IpEditForm(request.POST)
            if form.is_valid():
                worker_com.set_interface(ip=form.cleaned_data['ip'], netmask=form.cleaned_data['subnet'])
        if 'type' in request.POST and request.POST['type'] == 'time':
            form = forms.TimeEditForm(request.POST)
            if form.is_valid():
                worker_com.set_time(form.cleaned_data['time'])
        if 'type' in request.POST and request.POST['type'] == 'deactivate_network':
            worker_com.deactivate_interface()
        return redirect('kasse:general_settings')

    if settings.ETHERNET_PORT is not None:
        interfaces = debinterface.Interfaces()
        adapter = interfaces.getAdapter(settings.ETHERNET_PORT)
        if adapter is not None:
            context['ip_address'] = adapter.get_attr('address')
            context['subnet'] = adapter.get_attr('netmask')
        else:
            context['eth_deactivated'] = True

    return render(request, 'settings/general_settings.html', context=context)
