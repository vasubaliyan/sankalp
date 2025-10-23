from django import template
from django.contrib.auth.models import Group
register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
     group = Group.objects.get(name=group_name)
     return True if group in user.groups.all() else False
 
# from django import template
# from django.contrib.auth.models import Group
# from datetime import datetime

# register = template.Library()

# @register.simple_tag(takes_context=True)
# def dynamic_group_name(context):
#     # Construct the group name based on the current date, or any other logic
#     return datetime.now().strftime("Active-%Y-%m")

# @register.filter(name='has_group')
# def has_group(user, group_name):
#     try:
#         return Group.objects.get(name=group_name) in user.groups.all()
#     except Group.DoesNotExist:
#         return False
