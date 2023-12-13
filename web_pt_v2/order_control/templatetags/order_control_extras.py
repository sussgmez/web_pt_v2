from django import template

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
def short_address(value):
    return value[:100] + '...'


