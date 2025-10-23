# forms.py
from django import forms
from .models import Project1Record, Project2Record

class Project1RecordForm(forms.ModelForm):
    class Meta:
        model = Project1Record
        fields = '__all__'   # ya phir tu apne required fields specify kar sakta hai


class Project2RecordForm(forms.ModelForm):
    class Meta:
        model = Project2Record
        fields = '__all__'
