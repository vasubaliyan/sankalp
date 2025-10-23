from django.contrib.auth.models import Group
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from datetime import datetime

@receiver(user_logged_in)
def add_to_dynamic_group(sender, user, request, **kwargs):
    # Example: Create a group name based on the current year and month
    group_name = datetime.now().strftime("Active-%Y-%m")
    group, created = Group.objects.get_or_create(name=group_name)
    user.groups.add(group)
