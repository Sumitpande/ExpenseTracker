from django.contrib import admin
from .models import *
# Register your models here.
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'cost','account','category','date','message','bookmark','user')
    list_editable = ('cost','account','category','message','bookmark','user')


class ExpenseAdmin(admin.ModelAdmin):
    
    list_display = ('id','cost','account','category','date','message','bookmark','user')
    list_editable = ('cost','account','category','message','bookmark','user')

class TransferAdmin(admin.ModelAdmin):
    
    list_display = ('id','cost','From','to','date','message','bookmark','user')
    list_editable = ('cost','From','to','message','bookmark','user')

class MemoAdmin(admin.ModelAdmin):
    
    list_display = ('id','title','content','date','user')
    list_editable = ('title','content','date','user')

admin.site.register(Income,IncomeAdmin)
admin.site.register(Transfer,TransferAdmin)
admin.site.register(Expense,ExpenseAdmin)
admin.site.register(Memo,MemoAdmin)