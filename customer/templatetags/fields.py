import datetime

from django import template

# Custom tags to apply logic in templates.

register = template.Library()


@register.filter
def get_display_attr(obj, path):
    """Receives an object and get attributes recursively. E.g.
    obj = requirement (requirement has attribute 'customer', and customer has attribute 'customer_name')
    path = 'customer.customer_name'

    1. Get 'customer' attribute:
    customer = getattr(requirement, customer)
    2. Get 'customer_name' attribute:
    customer_name = getattr(customer, customer_name)

    Finally, returns 'customer_name' value.

    """
    fields = path.split('.')
    try:
        for field in fields:
            obj = getattr(obj, field)

        # convert boolean to YES/NO string
        if isinstance(obj, bool):
            obj = 'Yes' if obj else 'No'

        # convert datetime object to string format dd/mm/yyyy
        if isinstance(obj, datetime.date):
            obj = obj.strftime('%d/%m/%Y')

        return obj if obj else '-'
    except AttributeError:
        return '-'


@register.simple_tag
def get_Item(dic, key):
    """Receives an Dic and key  and return Dic[key]
    """
    return dic[key]

@register.simple_tag
def sup(dic, key):
    """Receives an Dic and key  and return len(dic) - key
    """
    return int(key) -len(dic)

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()