from django import template

register = template.Library()


# @register.filter(name='addclass')
# def addclass(field, myclass):
#     return field.as_widget(attrs={"class": myclass})


from django.forms import BoundField

@register.filter(name='addclass')
def addclass(field, myclass):
    if isinstance(field, BoundField):
        return field.as_widget(attrs={"class": myclass})
    else:
        # Handle the case where field is not a BoundField, or raise an error
        return field


