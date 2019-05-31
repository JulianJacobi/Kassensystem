from django.db import models
from djmoney.models.fields import MoneyField
import json

# Create your models here.


class Product(models.Model):
    name = models.CharField('Name', max_length=50)
    price = MoneyField('Preis', decimal_places=2, max_digits=20, default_currency='EUR')


class Menu(models.Model):
    name = models.CharField('Name', max_length=50)
    products = models.ManyToManyField(Product, through='MenuItem')

    def sort_products(self):
        return self.products.order_by('menuitem__sort')

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sort = models.IntegerField()
    color = models.CharField(max_length=50, default='default')


class AccountEntry(models.Model):
    types = (
        ('sale', 'Verkauf'),
        ('output', 'Entnahme'),
        ('input', 'Einzahlung')
    )
    type = models.CharField('Typ', choices=types, max_length=20)
    comment = models.TextField('Kommentar')
    amount = MoneyField('Betrag', max_digits=20, decimal_places=2, default_currency='EUR')
    timestamp = models.DateTimeField(auto_now=True)
    user = models.CharField('Benutzer', max_length=200, default='')


class Event(models.Model):
    name = models.CharField('Name', max_length=300)
    start = models.DateTimeField('Start')
    end = models.DateTimeField('Ende')


class TableSet(models.Model):
    name = models.CharField('Name', max_length=300)
    menu = models.ForeignKey(Menu, on_delete=models.PROTECT, verbose_name='Menü')


class Table(models.Model):
    name = models.CharField('Name', max_length=300)
    table_set = models.ForeignKey(TableSet, on_delete=models.CASCADE)
    pos_x = models.FloatField()
    pos_y = models.FloatField()
    size_x = models.FloatField()
    size_y = models.FloatField()
    bookings = models.TextField(blank=True)

    def total(self):
        total = 0.0
        if self.bookings != "":
            bookings = json.loads(self.bookings)
            for booking in bookings:
                total += booking.get('price', 0.0)
        return total
