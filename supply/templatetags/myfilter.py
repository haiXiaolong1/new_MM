from django import template
register = template.Library()

@register.filter(name="front_add")
def front_add(arg,val):
    return str(val)+str(arg)

@register.filter(name="table_status")
def front_add(arg):
    return "table_status_{}".format(arg)