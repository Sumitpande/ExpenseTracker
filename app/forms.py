from django import forms  
from .models import *  
   
   

class MyForm(forms.Form):
    month_choices = (
        ('1','Jan'),
        ('2','Feb'),
        ('3','Mar'),
        ('4','Apr'),
        ('5','May'),
        ('6','Jun'),
        ('7','July'),
        ('8','Aug'),
        ('9','Sept'),
        ('10','Oct'),
        ('11','Nov'),
        ('12','Dec'),
    )
    month = forms.ChoiceField(choices=month_choices)
    year = forms.IntegerField()
