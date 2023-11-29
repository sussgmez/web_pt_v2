from django import forms
from .models import Customer, Order, Installation


class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['contract_number', 'category', 'customer_name', 'address', 'phone_1', 'phone_2', 'email', 'plan', 'customer_type', 'date_assigned', 'assigned_to', 'seller', 'comment']
        widgets = {
            "contract_number": forms.TextInput(attrs={'hidden':True}),
            "address": forms.Textarea(attrs={'rows':'4'}),
            "comment": forms.Textarea(attrs={'rows':'3'}),
            "date_assigned": forms.DateInput(format='%Y-%m-%d', attrs={'type':'date'}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['contract_number', 'category', 'customer_name', 'address', 'phone_1', 'phone_2', 'email', 'plan', 'customer_type', 'date_assigned', 'assigned_to', 'seller', 'comment']
        widgets = {
            "address": forms.Textarea(attrs={'rows':'4'}),
            "comment": forms.Textarea(attrs={'rows':'3'}),
            "date_assigned": forms.DateInput(format='%Y-%m-%d', attrs={'type':'date'}),
        }

class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['technician', 'date_assigned', 'extra_order_comment', 'closed', 'completed']
        widgets = {
            'date_assigned':forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type':'datetime-local'}),
            'extra_order_comment': forms.Textarea(attrs={'rows':'2'})
        }

class InstallationUpdateForm(forms.ModelForm):
    class Meta:
        model = Installation
        fields = ["zone", "olt", "pon", "card", "box", "port", "box_power", "house_power", "onu_serial", "router_serial", "drop_serial", "drop_used", "hook_used", "fast_conn_used", "extra_comment"]