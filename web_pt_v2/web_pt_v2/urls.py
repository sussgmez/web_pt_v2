from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.urls import include
from order_control.views import CustomerListView, load_excel, CustomerCreateView, CustomerUpdateView, OrderUpdateView, InstallationUpdateView, order_create, order_delete, customer_delete, order_complete, order_activated, export_customers, Schedule, PreScheduleView, Preconfig

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
    path('customer/order/activated/<int:pk>', login_required(order_activated), name='order-activated'),
    path('customer/export', login_required(export_customers), name='export-customers'),
    path('load_excel/', login_required(load_excel), name='load-excel'),
    path('customer_exist/<int:pk>', login_required(load_excel), name='load-excel'),
    path('schedule/', login_required(Schedule.as_view()), name='schedule'),
    path('schedule/assign', login_required(PreScheduleView.as_view()), name='pre-schedule'),
    path('preconfig/', login_required(Preconfig.as_view()), name='preconfig'),   
]
