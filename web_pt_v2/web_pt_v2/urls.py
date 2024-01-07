from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.urls import include
from order_control.views import CustomerListView, load_excel, CustomerCreateView, CustomerUpdateView, OrderUpdateView, InstallationUpdateView, TechnicianListView, order_create, order_delete, customer_delete, order_complete, export_customers, Schedule

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("django.contrib.auth.urls")),
    path('', login_required(CustomerListView.as_view()), name='customer-list'),
    path('customer/<int:pk>', login_required(CustomerUpdateView.as_view()), name='customer-update'),
    path('customer/add', login_required(CustomerCreateView.as_view()), name='customer-create'),
    path('customer/delete/<int:pk>', login_required(customer_delete), name='customer-delete'),
    path('customer/order/<int:pk>', login_required(OrderUpdateView.as_view()), name='order-update'),
    path('customer/oder/create/<int:pk>', login_required(order_create), name='order-create'),
    path('customer/order/delete/<int:pk>', login_required(order_delete), name='order-delete'),
    path('customer/installation/<int:pk>', login_required(InstallationUpdateView.as_view()), name='installation-update'),
    path('customer/order/complete/<int:pk>', login_required(order_complete), name='order-complete'),
    path('customer/export', login_required(export_customers), name='export-customers'),
    path('technicians/', login_required(TechnicianListView.as_view()), name='technician-list'),
    path('load_excel/', login_required(load_excel), name='load-excel'),
    path('customer_exist/<int:pk>', login_required(load_excel), name='load-excel'),
    path('schedule/', login_required(Schedule.as_view()), name='schedule'),
    
]
