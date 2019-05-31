from django.forms.models import ModelForm
from django import forms
from .models import *
from django.contrib.auth import forms as auth_forms


class BootstrapForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})


class MenuForm(BootstrapForm):

    class Meta:
        model = Menu
        fields = ['name']


class TableSetForm(BootstrapForm):

    class Meta:
        model = TableSet
        fields = ['name', 'menu']


class ProductForm(BootstrapForm):

    class Meta:
        model = Product
        fields = ['name', 'price']


class EventForm(BootstrapForm):

    class Meta:
        model = Event
        exclude = {}


class UserCreationForm(auth_forms.UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})


class SetPasswordForm(auth_forms.SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})


class IpEditForm(forms.Form):
    ip = forms.CharField(label='IP', widget=forms.TextInput(attrs={'class': 'form-control'}))
    subnet = forms.CharField(label='Subnetzmaske', widget=forms.TextInput(attrs={'class': 'form-control'}))


class TimeEditForm(forms.Form):
    time = forms.DateTimeField(label='Zeit', widget=forms.TextInput(attrs={'class': 'form-control'}))

