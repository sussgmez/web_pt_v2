from django import template
from datetime import datetime, timezone

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
            if element.date_assigned.date() not in dates:
                date = element.date_assigned.replace(tzinfo=timezone.utc).astimezone(tz=None)
                dates.append(date.date())
        except: pass
    return dates

@register.filter
def get_orders(value, date):
    value = value.filter(date_assigned__year=date.year, date_assigned__month=date.month, date_assigned__day=date.day)
    return value

@register.filter
def get_undefined(value):
    value = value.filter(date_assigned=None)
    return value


@register.filter
def short_address(value):
    return value[:100] + '...'


