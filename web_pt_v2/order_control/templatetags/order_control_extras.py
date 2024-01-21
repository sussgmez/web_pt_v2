from django import template
from datetime import timezone

register = template.Library()

@register.filter
def last_order(value):
    try: return value.order_by('-date_created')[0]
    except: pass

@register.filter
def order_by_date_created(value):
    return value.order_by('-date_created')

@register.filter
def not_completed(value):
    return value.filter(completed=False).filter(closed=False).order_by('date_assigned')

@register.filter
def previous(value, i):
    try: 
        return value[i - 1]
    except:
        return None

@register.filter
def get_dates(list):
    dates = []
    for element in list:
        try:
            date = element.date_assigned.replace(tzinfo=timezone.utc).astimezone(tz=None).date() 
            if date not in dates:
                dates.append(date)
        except: pass
    return dates

@register.filter
def get_dates_preconfig(list):
    dates = []
    for element in list:
        try:
            date = element.instance.order.date_assigned.replace(tzinfo=timezone.utc).astimezone(tz=None).date() 
            if date not in dates:
                dates.append(date)
        except: pass
    return dates

@register.filter
def get_orders(value, date):
    value = value.filter(date_assigned__year=date.year, date_assigned__month=date.month, date_assigned__day=date.day)
    return value

@register.filter
def filter_date(list, date):
    aux_list = []
    for installation_form in list:
        order_date = installation_form.instance.order.date_assigned.replace(tzinfo=timezone.utc).astimezone(tz=None).date() 
        if order_date.day == date.day and order_date.month == date.month and order_date.year == date.year:
            aux_list.append(installation_form)
    return aux_list


@register.filter
def get_undefined(value):
    value = value.filter(date_assigned=None)
    return value


@register.filter
def short_address(value):
    return value[:100] + '...'


@register.filter
def get_order_form(list, technician=None):
    final_list = []

    if technician==None: final_list = [f for f in list if f.instance.technician == None]
    else:
        for form in list:
            try:
                if (form.instance.technician.pk == technician):
                    final_list.append(form)
            except: pass

    return final_list
