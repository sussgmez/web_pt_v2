from django.http import HttpResponse
import pandas, math
from io import BytesIO
from datetime import datetime
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView, CreateView, TemplateView
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from .models import Customer, Order, Installation, Technician
from .forms import CustomerUpdateForm, OrderUpdateForm, InstallationUpdateForm, CustomerForm, OrderScheduleForm, InstallationPreconfigForm


class CustomerListView(ListView):
    model = Customer
    template_name = "customer_list.html"
    paginate_by = 50
    ordering = "-date_created"

    def get_queryset(self):
        s_text = ""
        try: s_text = self.request.GET['search-text']
        except: pass

        status = ""
        try: status = self.request.GET['status']
        except: pass

        sort_by = "-date_created"
        try: sort_by = self.request.GET['sort-by']
        except: pass

        min_date_get = ""
        try: 
            min_date_get = self.request.GET['min-date']
        except: pass
        
        max_date_get = ""
        try: 
            max_date_get = self.request.GET['max-date']
        except: pass

        technician = ""
        try: 
            if self.request.user.is_superuser:
                technician = self.request.GET['technician']
            else:
                technician = self.request.user.technician.code
        except: pass

        customers = Customer.objects.filter(pk__contains=s_text) | Customer.objects.filter(address__contains=s_text) | Customer.objects.filter(customer_name__contains=s_text)


        if technician != "":
            for customer in customers:
                try: 
                    last_order = customer.orders.all().order_by('-date_created')[0]
                    if last_order.technician.code != technician or (last_order.closed and not self.request.user.is_superuser): 
                        customers = customers.exclude(contract_number=customer.contract_number)
                    

                except: customers = customers.exclude(contract_number=customer.contract_number)

        if min_date_get != "" or max_date_get != "":
            for customer in customers:
                try:last_order = customer.orders.all().order_by('-date_created')[0]
                except: continue

                if last_order.date_assigned == None:
                    customers = customers.exclude(contract_number=customer.contract_number)
                    continue
                
                try: min_date = datetime.strptime(min_date_get + ' +0000', '%Y-%m-%d %z')
                except: min_date = datetime.strptime('1999-01-01 +0000', '%Y-%m-%d %z')

                try: max_date = datetime.strptime(max_date_get + ' +0000', '%Y-%m-%d %z')
                except: max_date = datetime.strptime('2050-01-01 +0000', '%Y-%m-%d %z')

                date_assigned = datetime(last_order.date_assigned.year, last_order.date_assigned.month, last_order.date_assigned.day, tzinfo=last_order.date_assigned.tzinfo)

                if min_date > date_assigned or date_assigned > max_date:
                    customers = customers.exclude(contract_number=customer.contract_number)

        if status == 'status_to_assign':
            for customer in customers:
                try: 
                    last_order = customer.orders.all().order_by('-date_created')[0]
                    if last_order.completed==True or last_order.technician!=None:
                        customers = customers.exclude(contract_number=customer.contract_number)
                except: continue

        elif status == 'status_assigned':
            for customer in customers:
                try:
                    last_order = customer.orders.all().order_by('-date_created')[0]
                    if last_order.completed==True or last_order.technician==None or last_order.closed==True:
                        customers = customers.exclude(contract_number=customer.contract_number)
                except:
                    customers = customers.exclude(contract_number=customer.contract_number)
        
        elif status == 'status_completed':
            for customer in customers:
                try: 
                    last_order = customer.orders.all().order_by('-date_created')[0]
                    if last_order.completed!=True:
                        customers = customers.exclude(contract_number=customer.contract_number)
                except: 
                    customers = customers.exclude(contract_number=customer.contract_number)

        elif status == 'status_closed':
            for customer in customers:
                try: 
                    last_order = customer.orders.all().order_by('-date_created')[0]
                    if last_order.closed!=True:
                        customers = customers.exclude(contract_number=customer.contract_number)
                except: customers = customers.exclude(contract_number=customer.contract_number)

        elif status == 'status_activated':
            for customer in customers:
                try: 
                    last_order = customer.orders.all().order_by('-date_created')[0]
                    if last_order.activated!=True:
                        customers = customers.exclude(contract_number=customer.contract_number)
                except: 
                    customers = customers.exclude(contract_number=customer.contract_number)


        return customers.order_by(sort_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['technicians'] = Technician.objects.all()
            try: 
                context["selected_technician"] = self.request.GET['technician']
            except: pass
        else: 
            context['technicians'] = Technician.objects.filter(code=self.request.user.technician.code)

        try: 
            context["search_text"] = self.request.GET['search-text']
        except: pass

        try: 
            status = self.request.GET['status']
            context["status"] = status
            if status == 'none': context['status_opt_1'] = 'selected'
            elif status == 'status_completed': context['status_opt_2'] = 'selected'
            elif status == 'status_assigned': context['status_opt_3'] = 'selected'
            elif status == 'status_to_assign': context['status_opt_4'] = 'selected'
            elif status == 'status_closed': context['status_opt_5'] = 'selected'
            elif status == 'status_activated': context['status_opt_6'] = 'selected'
        except: pass

        context["sort_by"] = '-date_created'
        try: 
            sort_by = self.request.GET['sort-by']
            if sort_by == '-date_created': context['sort_opt_1'] = 'selected'
            elif sort_by == 'date_created': context['sort_opt_2'] = 'selected'
            elif sort_by == '-date_assigned': context['sort_opt_3'] = 'selected'
            elif sort_by == 'date_assigned': context['sort_opt_4'] = 'selected'
            elif sort_by == '-pk': context['sort_opt_5'] = 'selected'
            context["sort_by"] = sort_by
        except: pass

        try: 
            context["min_date"] = self.request.GET['min-date']
        except: pass
        try: 
            context["max_date"] = self.request.GET['max-date']
        except: pass

        return context


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'order_control/customer_create.html'

    def get_success_url(self):
        messages.success(self.request, f'Cliente {self.object.contract_number} creado con éxito')
        return reverse('customer-list')


class CustomerUpdateView(UpdateView):
    model = Customer
    template_name = "order_control/customer_update.html"
    form_class = CustomerUpdateForm

    def get_success_url(self):
        messages.success(self.request, f'Cliente {self.object.contract_number} modificado con éxito')
        return reverse('customer-update', kwargs={'pk':self.object.contract_number})


class OrderUpdateView(UpdateView):
    model = Order
    template_name = "order_control/order_update.html"
    form_class = OrderUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer_form"] = CustomerUpdateForm(instance=context['object'].customer)
        context["installation_form"] = InstallationUpdateForm(instance=context['object'].installation)
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Cambios guardados con éxito')
        if self.object.closed:
            return reverse('customer-update', kwargs={'pk':self.object.customer.contract_number})
        return reverse('order-update', kwargs={'pk':self.object.pk})
    

class InstallationUpdateView(UpdateView):
    model = Installation
    template_name = "order_control/installation_update.html"
    form_class = InstallationUpdateForm
    
    def get_success_url(self):
        messages.success(self.request, "Cambios guardados con éxito")
        return reverse('order-update', kwargs={'pk':self.object.order.pk})


class TechnicianListView(ListView):
    model = Technician
    template_name = "order_control/technician_list.html"


class Schedule(TemplateView):
    template_name = "order_control/schedule.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_superuser:
            context["technicians"] = Technician.objects.all()
        else: 
            context["technicians"] = Technician.objects.filter(pk=self.request.user.technician.id)
        
        return context
    

class PreScheduleView(TemplateView):
    template_name = "order_control/pre_schedule.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        customers = Customer.objects.filter(order=None)
        for customer in customers:
            Order.objects.create(customer_id=customer.contract_number)
        orders = Order.objects.filter(completed=False).filter(closed=False).order_by('technician')

        context["technicians"] = Technician.objects.all()

        context['form_list'] = []

        for order in orders:
            context['form_list'].append(OrderScheduleForm(instance=order))

        return context
    
    def post(self, *args, **kwargs):
        id_list = self.request.POST.getlist('id')
        technician_list = self.request.POST.getlist('technician')
        date_assigned_list = self.request.POST.getlist('date_assigned')
        customer_confirmation_list = self.request.POST.getlist('customer_confirmation')

        for i in range(0, len(id_list)):
            order = Order.objects.get(id=id_list[i])

            try: order.technician = Technician.objects.get(id=technician_list[i])
            except: order.technician = None

            order.customer_confirmation = customer_confirmation_list[i]

            if date_assigned_list[i] == "": order.date_assigned = None
            else: 
                
                order.date_assigned = date_assigned_list[i]

            order.save()
        
        messages.success(self.request, 'Cambios guardados con éxito.')

        return redirect('pre-schedule')


class Preconfig(TemplateView):
    template_name = "order_control/preconfig.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        installations = Installation.objects.filter(order__completed=False).filter(order__closed=False).exclude(order__date_assigned=None).order_by('order__date_assigned')
        
        context['form_list'] = []
        for installation in installations:
            context['form_list'].append(InstallationPreconfigForm(instance=installation))

        return context
    
    def post(self, *args, **kwargs):
        id_list = self.request.POST.getlist('id')
        zone_list = self.request.POST.getlist('zone')
        onu_serial_list = self.request.POST.getlist('onu_serial')

        for i in range(0, len(id_list)):
            installation = Installation.objects.get(id=id_list[i])
            if zone_list[i] != "":
                installation.zone = zone_list[i]
            installation.onu_serial = onu_serial_list[i]
            installation.save()
        
        messages.success(self.request, 'Cambios guardados con éxito.')

        return redirect('preconfig')


def order_complete(request, pk):
    order = Order.objects.get(pk=pk)
    order.completed = True
    order.activated = True
    order.save()
    return redirect('order-update', pk=order.pk)

def order_activated(request, pk):
    order = Order.objects.get(pk=pk)
    order.activated = True
    order.save()
    return redirect('order-update', pk=order.pk)

def export_customers(request):
    s_text = ""
    try: s_text = request.GET['search-text']
    except: pass

    status = ""
    try: status = request.GET['status']
    except: pass

    min_date_get = ""
    try: 
        min_date_get = request.GET['min-date']
    except: pass
    
    max_date_get = ""
    try: 
        max_date_get = request.GET['max-date']
    except: pass

    technician = ""
    try: 
        if request.user.is_superuser:
            technician = request.GET['technician']
        else:
            technician = request.user.technician.code
    except: pass

    customers = Customer.objects.filter(pk__contains=s_text) | Customer.objects.filter(address__contains=s_text) | Customer.objects.filter(customer_name__contains=s_text)

    if technician != "":
        for customer in customers:
            try: 
                last_order = customer.orders.all().order_by('-date_created')[0]
                if last_order.technician.code != technician or (last_order.closed and not request.user.is_superuser): 
                    customers = customers.exclude(contract_number=customer.contract_number)
            except: customers = customers.exclude(contract_number=customer.contract_number)

    if min_date_get != "" or max_date_get != "":
        for customer in customers:
            try:last_order = customer.orders.all().order_by('-date_created')[0]
            except: continue

            if last_order.date_assigned == None:
                customers = customers.exclude(contract_number=customer.contract_number)
                continue
            
            try: min_date = datetime.strptime(min_date_get + ' +0000', '%Y-%m-%d %z')
            except: min_date = datetime.strptime('1999-01-01 +0000', '%Y-%m-%d %z')

            try: max_date = datetime.strptime(max_date_get + ' +0000', '%Y-%m-%d %z')
            except: max_date = datetime.strptime('2050-01-01 +0000', '%Y-%m-%d %z')

            date_assigned = datetime(last_order.date_assigned.year, last_order.date_assigned.month, last_order.date_assigned.day, tzinfo=last_order.date_assigned.tzinfo)

            if min_date > date_assigned or date_assigned > max_date:
                customers = customers.exclude(contract_number=customer.contract_number)

    if status == 'status_to_assign':
        for customer in customers:
            try: 
                last_order = customer.orders.all().order_by('-date_created')[0]
                if last_order.completed==True or last_order.technician!=None:
                    customers = customers.exclude(contract_number=customer.contract_number)
            except: continue

    elif status == 'status_assigned':
        for customer in customers:
            try:
                last_order = customer.orders.all().order_by('-date_created')[0]
                if last_order.completed==True or last_order.technician==None or last_order.closed==True:
                    customers = customers.exclude(contract_number=customer.contract_number)
            except:
                customers = customers.exclude(contract_number=customer.contract_number)
    
    elif status == 'status_completed':
        for customer in customers:
            try: 
                last_order = customer.orders.all().order_by('-date_created')[0]
                if last_order.completed!=True:
                    customers = customers.exclude(contract_number=customer.contract_number)
            except: 
                customers = customers.exclude(contract_number=customer.contract_number)

    elif status == 'status_closed':
        for customer in customers:
            try: 
                last_order = customer.orders.all().order_by('-date_created')[0]
                if last_order.closed!=True:
                    customers = customers.exclude(contract_number=customer.contract_number)
            except: customers = customers.exclude(contract_number=customer.contract_number)

    elif status == 'status_activated':
        for customer in customers:
            try: 
                last_order = customer.orders.all().order_by('-date_created')[0]
                if last_order.activated!=True:
                    customers = customers.exclude(contract_number=customer.contract_number)
            except: 
                customers = customers.exclude(contract_number=customer.contract_number)

    df = pandas.DataFrame()

    for customer in customers:
        last_order = ""
        try:
            last_order = customer.orders.all().order_by('-date_created')[0]
        except: pass

        day_name = ""
        date = ""
        try: 
            day_name = last_order.date_assigned.strftime('%A')
            date = last_order.date_assigned.strftime('%d/%m/%Y')
        except: pass

        ext_drop = ""
        drop_used = ""
        try: 
            drop_used = last_order.installation.drop_used
            if last_order.installation.drop_used > 250: 
                ext_drop = last_order.installation.drop_used
        except: pass

        hook_used = ""
        try: 
            hook_used = last_order.installation.hook_used
        except: pass

        drop_serial = ""
        try: 
            drop_serial = last_order.installation.drop_serial
        except: pass

        onu_serial = ""
        try: 
            onu_serial = last_order.installation.onu_serial
        except: pass

        router_serial = ""
        try: 
            router_serial = last_order.installation.router_serial
        except: pass

        technician = ""
        try: 
            technician = last_order.technician
        except: pass

        df_aux = pandas.DataFrame([[
            day_name,
            1,
            date,
            customer.contract_number, 
            customer.customer_name, 
            customer.address[:50],
            ext_drop,
            hook_used,
            drop_used,
            drop_serial,
            onu_serial,
            router_serial,
            technician]])  

        df = pandas.concat([df, df_aux])

    df = df.rename(columns={0:'DIA', 1:'ITEM', 2:'FECHA', 3:'CONTRATO', 4:'NOMBRE CLIENTE', 5:'DIRECCION', 6:'+ DE 250M', 7:'TENSORES', 8:'MTS DROP', 9:'SN. DROP', 10:'SERIAL ONU', 11:'SERIAL ROUTER', 12:'TÉCNICO'})

    with BytesIO() as b:
        with pandas.ExcelWriter(b) as writer:
            df.to_excel(writer, sheet_name='DATA 1', index=False)
        filename = f'{str(datetime.now().strftime("%d-%m-%Y %H%M%S"))}.xlsx'
        res = HttpResponse(
            b.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        res['Content-Disposition'] = f'attachment; filename={filename}'
        return res

@permission_required('order_control.add_order', raise_exception=True)
def order_create(request, pk):
    Order.objects.create(customer=Customer.objects.get(pk=pk))
    return redirect('customer-update', pk=pk)

@permission_required('order_control.delete_order', raise_exception=True)
def order_delete(request, pk):
    order = Order.objects.get(pk=pk)
    customer_pk = order.customer.contract_number
    if request.user.is_superuser:
        order.delete()
    return redirect('customer-update', pk=customer_pk)  

@permission_required('order_control.delete_customer', raise_exception=True)
def customer_delete(request, pk):
    if request.user.is_superuser:
        Customer.objects.get(pk=pk).delete()
    return redirect('customer-list')

def check_nan(value):
    if type(value)==float and math.isnan(value):return ""
    return value

def format_phone_number(value):
    try:
        return "0" + str(math.trunc(value))
    except: 
        pass
    return value

def load_excel(request):
    if request.user.is_superuser:
        if request.POST:
            df = pandas.read_excel(request.FILES['excel_file'])
            file_name = request.FILES['excel_file'].name
            received_date_txt = ""
            received_date = datetime.now()
            for char in file_name: 
                if char.isnumeric(): received_date_txt+=char
            try:
                received_date = datetime(day=int(received_date_txt[0:2]), month=int(received_date_txt[2:4]), year=int(received_date_txt[4:8]))
            except: pass

            message = "No se encontraron clientes para añadir."

            for id, values in df.iterrows():
                obj = ""
                created = False
                try:
                    for i in range(0,11): values.iloc[i]
                    obj, created = Customer.objects.get_or_create(contract_number=values.iloc[0])
                except: pass
                if created:
                    try:
                        obj.customer_name = values.iloc[1].title()
                        obj.phone_1 = format_phone_number(values.iloc[5])
                        obj.phone_2 = check_nan(values.iloc[6])
                        obj.address = values.iloc[7].title()
                        obj.email = check_nan(values.iloc[8])
                        obj.assigned_to = check_nan(values.iloc[10]).title()
                        obj.date_assigned = received_date
                        
                        category = "INS"
                        seller = check_nan(values.iloc[3]).title()
                        comment = ""
                        try: comment = check_nan(values.iloc[11]).capitalize()
                        except: pass

                        if seller != "":
                            if "Migracion" in seller or "Migración" in seller or "Migracion" in comment or "Migración" in comment:
                                category = "MIG"

                            if "MUDANZA" in values.iloc[3].upper():
                                category = "MUD"

                        obj.comment = comment
                        obj.seller = seller
                        obj.category = category         

                        plan = values.iloc[9].upper()
                        cod_plan = 'BR'

                        if "BASICO PLUS" in plan:
                            cod_plan = 'BP'
                        elif "BASICO" in plan:
                            cod_plan = 'BA'
                        elif "BRONCE" in plan:
                            cod_plan = 'BR'
                        elif "PLATA" in plan:
                            cod_plan = 'PL'
                        elif "ORO" in plan:
                            cod_plan = 'OR'
                        elif "EMPRENDEDOR" in plan:
                            cod_plan = 'EM'
                        elif "PRODUCTIVO PRO" in plan:
                            cod_plan = 'PP'
                        elif "PRODUCTIVO" in plan:
                            cod_plan = 'PR'
                        elif "VISIONARIO PRO" in plan:
                            cod_plan = 'VP'

                        obj.plan = cod_plan

                        obj.save()

                        if message == "No se encontraron clientes para añadir." : message = f"Se han añadido los siguientes clientes: {obj.contract_number}" 
                        else: message += f", {obj.contract_number}"
                    except:
                        obj.delete()

            messages.success(request, message)
            
    return redirect('customer-list')



        # for customer in customers:
        #     try:
        #         last_order = customer.orders.all().order_by('-date_created')[0]
        #         if last_order.completed:
        #             last_order.activated = True
        #             last_order.save()
        #     except: pass