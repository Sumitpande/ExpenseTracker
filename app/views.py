import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render,get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, date, timedelta
from itertools import chain
from django.db.models import Sum,Count
from . models import *
from .forms import *
import calendar
from django.utils import timezone


from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import ListView

from django.utils.decorators import method_decorator
from django.db.models.functions import TruncMonth,TruncDay

# def index(request):
#     form=MyForm()
#     data = Expense.objects.annotate(day=TruncDay('date')).values('day').annotate(c=Count('id')).order_by() 
    
#     return render(request,"app/daily.html",{
#         'form':form,
#         'data':data,
        
#     })

class IncomeCreate(CreateView):
    model = Income
    fields = ['cost','account','category','message']
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    success_url = reverse_lazy('income-list')

class IncomeUpdate(UpdateView):
    model = Income
    fields = ['cost','account','category','message']
    success_url = reverse_lazy('income-list')

class IncomeDelete(DeleteView):
    model = Income
    success_url = reverse_lazy('income-list')


class IncomeList(ListView):
    queryset = Income.objects.order_by('-date')
    context_object_name = 'income_list'
    template_name = 'app/list.html'

    # @method_decorator(login_required)
    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)

        return queryset

class ExpenseList(ListView):
    queryset = Expense.objects.order_by('-date')
    context_object_name = 'expense_list'
    template_name = 'app/expense.html'

    # @method_decorator(login_required)
    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        
        return queryset
    
class TransferList(ListView):
    queryset = Transfer.objects.order_by('-date')
    context_object_name = 'transfer_list'
    template_name = 'app/transfer.html'

    # @method_decorator(login_required)
    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        
        return queryset


class ExpenseCreate(CreateView):
    
    model = Expense
    fields = ['cost','account','category','message']
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    success_url = reverse_lazy('expense-list')

class ExpenseUpdate(UpdateView):
    model = Expense

    fields = ['cost','account','category','message']
    success_url = reverse_lazy('expense-list')

class ExpenseDelete(DeleteView):
    model = Expense
    success_url = reverse_lazy('expense-list')

class TransferCreate(CreateView):
    model = Transfer
    fields = ['cost','to','From','message']
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    success_url = reverse_lazy('transfer-list')

class TransferUpdate(UpdateView):
    model = Transfer

    fields = ['cost','to','From','message']
    success_url = reverse_lazy('transfer-list')

class TransferDelete(DeleteView):
    model = Transfer
    success_url = reverse_lazy('transfer-list')





@csrf_exempt
def memoCreate(request):
    if request.method == "GET":
        memos = Memo.objects.filter(user=request.user)
        return JsonResponse([memo.serialize(memo.id) for memo in memos],safe=False)

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    
    data = json.loads(request.body)
    

    # Get contents of memo
    title = data.get("title", "")
    content = data.get("content", "")

    memo = Memo(
        user=request.user,
        title=title,
        content=content,
        date=datetime.now()
    )
    memo.save()
    print(f'id:{memo.id}')
    

    return JsonResponse(memo.serialize(memo.id))


# @csrf_exempt
def memo(request):
    memos  = Memo.objects.filter(user=request.user)
    print(memos)

    return render(request,"app/memo.html",{
        'memos':memos
    })


@csrf_exempt
def memoUpdate(request,id):
    try:
        memo = Memo.objects.get(user=request.user,id=id)
    except Memo.DoesNotExist:
        return JsonResponse({"error": "Memo not found."}, status=404)

    # Return email contents
    
    # Update whether email is read or should be archived
    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("title") is not None:
            memo.title = data["title"]
        if data.get("content") is not None:
            memo.content = data["content"]
        memo.save()
        return JsonResponse({
            "message": "memo updated."
        }, status=400)


    # memo must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


@csrf_exempt
def delMemo(request,id):
    memo = Memo.objects.get(id=id)
    memo.delete()

    memos = Memo.objects.filter(user=request.user)
    print(memos)
    c = [m.serialize(m.id) for m in memos]
    print(c)

    return JsonResponse(c,safe=False)

def bookmark(request):
        
    i  = Income.objects.filter(user=request.user).filter(bookmark=True).order_by('-date')
    e  = Expense.objects.filter(user=request.user).filter(bookmark=True).order_by('-date')
    t  = Transfer.objects.filter(user=request.user).filter(bookmark=True).order_by('-date')
    ii  = Income.objects.filter(user=request.user).order_by('-date')
    ee  = Expense.objects.filter(user=request.user).order_by('-date')
    tt  = Transfer.objects.filter(user=request.user).order_by('-date')
    
    return render(request,"app/bookmark.html",{
        'income':ii,
        'expense':ee,
        'transfer':tt,
        'trans':chain(i,e,t)
        
    })


def bookmarki(request,id):

    i = Income.objects.get(id=id)
    if i.bookmark == True:
        i.bookmark = False
        i.save()
    else:
        i.bookmark = True
        i.save()

    
   

    return HttpResponseRedirect(reverse('income-list'))


def bookmarkt(request,id):
    i = Transfer.objects.get(id=id)
    if i.bookmark == True:
        i.bookmark = False
        i.save()
    else:
        i.bookmark = True
        i.save()

    return HttpResponseRedirect(reverse('transfer-list'))

def bookmarke(request,id):
    i = Expense.objects.get(id=id)
    if i.bookmark == True:
        i.bookmark = False
        i.save()
    else:
        i.bookmark = True
        i.save()

    return HttpResponseRedirect(reverse('expense-list'))


def trans_weekly(request):
    day = int(datetime.now().strftime("%d")) 
    month = int(datetime.now().strftime("%m"))
    year = int(datetime.now().strftime("%Y"))
    if request.method == 'POST':
        month=int(request.POST['month'])
        year=int(request.POST['year'])
        

    if month is not int(datetime.now().strftime("%m")):
        day= 31

    if checkYear(year):
        day = 29
    else:
        day = 28
    
    # end_date - timedelta(days=7)
    end_date =  date(year,month,day)
    start_date =  date(year,month,day)
    
    d = []
    # e = Expense.objects.filter(user=request.user).filter(date__range=(start_date,end_date)).order_by('-date')
    # i = Income.objects.filter(user=request.user).filter(date__range=(start_date,end_date)).order_by('-date')
    t = Transfer.objects.filter(user=request.user).filter(date__range=(start_date,end_date)).order_by('-date')
    
    ecost = []
    icost = []
    while day>7:
        end_date =  date(year,month,day)
        start_date =  date(year,month,day-7)
        e = Expense.objects.filter(user=request.user).filter(date__range=(start_date,end_date)).order_by('-date')
        i = Income.objects.filter(user=request.user).filter(date__range=(start_date,end_date)).order_by('-date')
        
        d.append([day,day-7,e.aggregate(Sum('cost')),i.aggregate(Sum('cost'))])
        day = day-7
    
    if day <= 7:
        end_date =  date(year,month,day)
        start_date =  date(year,month,1)
        e = Expense.objects.filter(user=request.user).filter(date__range=(start_date,end_date)).order_by('-date')
        i = Income.objects.filter(user=request.user).filter(date__range=(start_date,end_date)).order_by('-date')
        
        print(e.aggregate(Sum('cost')))
        print(i.aggregate(Sum('cost')))
        d.append([day,1,e.aggregate(Sum('cost')),i.aggregate(Sum('cost'))])

    
    

    return render(request, "app/weekly.html",{
        'form':MyForm(),
        'trans':chain(e,i),
        'date':datetime.now(),
        'time':date(year,month,day),
        'months':[(1,'January'),
                  (2,'February'),
                  (3,'March'),
                  (4,'April'),
                  (5,'May'),
                  (6,'June'),
                  (7,'July'),
                  (8,'August'),
                  (9,'September'),
                  (10,'October'),
                  (11,'November'),
                  (12,'December'),],
        'days':d,
        'expense':e,
        'income':i,
        'transfer':t,
        'expense_total':e.aggregate(Sum('cost')),
        'income_total':i.aggregate(Sum('cost')),
        'msg':'weekly'
    })




def trans_monthly(request):

    day = int(datetime.now().strftime("%d"))
    month = int(datetime.now().strftime("%m"))
    year = int(datetime.now().strftime("%Y"))
    if request.method == 'POST':
        month=int(request.POST['month'])
        year=int(request.POST['year'])
        



    e = Expense.objects.filter(user=request.user).filter(date__year=year).order_by('-date')
    i = Income.objects.filter(user=request.user).filter(date__year=year).order_by('-date')
    
    ecost = e.aggregate(Sum('cost'))
    icost = i.aggregate(Sum('cost'))

    print(ecost,icost)

    months = [(1,'January'),
                  (2,'February'),
                  (3,'March'),
                  (4,'April'),
                  (5,'May'),
                  (6,'June'),
                  (7,'July'),
                  (8,'August'),
                  (9,'September'),
                  (10,'October'),
                  (11,'November'),
                  (12,'December'),]
    l = []
    for m in months:
        month = m[0]
        e = Expense.objects.filter(user=request.user).filter(date__year=year).filter(date__month=month).order_by('-date')
        i = Income.objects.filter(user=request.user).filter(date__year=year).filter(date__month=month).order_by('-date')
        t = Transfer.objects.filter(user=request.user).filter(date__year=year).filter(date__month=month).order_by('-date')
        l.append([m[1],e.aggregate(Sum('cost')),i.aggregate(Sum('cost'))])

    return render(request, "app/monthly.html",{
        'form':MyForm(),
        'trans':chain(e,i,t),
        'list':l,
        'date':datetime.now(),
        'year':year,
        'expense':e,
        'income':i,
        'transfer':t,
        'expense_total':ecost,
        'income_total':icost,
        'msg':'monthly'
    })


def checkYear(year): 
    if (year % 4) == 0: 
        if (year % 100) == 0: 
            if (year % 400) == 0: 
                return True
            else: 
                return False
        else: 
             return True
    else: 
        return False

def trans_daily(request):
    
    month = int(datetime.now().strftime("%m"))
    year = int(datetime.now().strftime("%Y"))
    if request.method == 'POST':
        month=int(request.POST['month'])
        year=int(request.POST['year'])
        


    
    
    day = int(datetime.now().strftime("%d")) 
    m1 = [1,3,5,7,8,10,12]
    m2 = [4,6,9,11]
    if checkYear(year):
        day = 29
    else:
        day = 28
    if month is int(datetime.now().strftime("%m")):
        pass
    else:
        
        day = calendar.monthrange(year,month)[-1]
    
    # start_date = date(year,month,day)
    # end_date = start_date 

    x1,x2,x3,x4,x5,x6 = ([] for i in range(6))
    x7,x8,x9,x10,x11,x12=([] for i in range(6))
    x13,x14,x15,x16,x17,x18 = ([] for i in range(6))
    x19,x20,x21,x22,x23,x24 = ([] for i in range(6))
    x25,x26,x27,x28,x29,x30,x31 = ([] for i in range(7))
    d= []
    # print(day)
    while(day>0):

        total_e = Expense.objects.filter(user=request.user).filter(date__year=year).filter(date__month=month).filter(date__day=day).order_by('-date').aggregate(Sum('cost'))
        total_i = Income.objects.filter(user=request.user).filter(date__year=year).filter(date__month=month).filter(date__day=day).order_by('-date').aggregate(Sum('cost'))


        e = Expense.objects.filter(user=request.user).filter(date__year=year).filter(date__month=month).filter(date__day=day).order_by('-date')
        
        i = Income.objects.filter(user=request.user).filter(date__year=year).filter(date__month=month).filter(date__day=day).order_by('-date')
        t = Transfer.objects.filter(user=request.user).filter(date__year=year).filter(date__month=month).filter(date__day=day).order_by('-date')
        
        if day == 1 :
                
            x1.append(total_e)
            x1.append(total_i)
            x1.append(str(day))
            x1.append(str(year))
            x1.append(str(month))
            x1.append(str(date(year,month,day).strftime("%A")))
            x1.append(str(bool(e or t or i)))
            x1.append(chain(e,i,t))
        
        if day == 2:
        
            x2.append(total_e)
            x2.append(total_i)
            x2.append(str(day))
            x2.append(str(year))
            x2.append(str(month))
            x2.append(str(date(year,month,day).strftime("%A")))
            x2.append(str(bool(e or t or i)))
            x2.append(chain(e,i,t))
        if day == 3 :
        
            x3.append(total_e)
            x3.append(total_i)
            x3.append(str(day))
            x3.append(str(year))
            x3.append(str(month))
            x3.append(str(date(year,month,day).strftime("%A")))
            x3.append(str(bool(e or t or i)))
            x3.append(chain(e,i,t))
        if day == 4 :
        
            x4.append(total_e)
            x4.append(total_i)
            x4.append(str(day))
            x4.append(str(year))
            x4.append(str(month))
            x4.append(str(date(year,month,day).strftime("%A")))
            x4.append(str(bool(e or t or i)))
            x4.append(chain(e,i,t))
        if day == 5:
        
            x5.append(total_e)
            x5.append(total_i)
            x5.append(str(day))
            x5.append(str(year))
            x5.append(str(month))
            x5.append(str(date(year,month,day).strftime("%A")))
            x5.append(str(bool(e or t or i)))
            x5.append(chain(e,i,t))
        if day == 6:

        
            x6.append(total_e)
            x6.append(total_i)
            x6.append(str(day))
            x6.append(str(year))
            x6.append(str(month))
            x6.append(str(date(year,month,day).strftime("%A")))
            x6.append(str(bool(e or t or i)))
            x6.append(chain(e,i,t))
        if day == 7:
            
            x7.append(total_e)
            x7.append(total_i)
            x7.append(str(day))
            x7.append(str(year))
            x7.append(str(month))
            x7.append(str(date(year,month,day).strftime("%A")))
            x7.append(str(bool(e or t or i)))
            x7.append(chain(e,i,t))
        if day == 8:
            
            x8.append(total_e)
            x8.append(total_i)
            x8.append(str(day))
            x8.append(str(year))
            x8.append(str(month))
            x8.append(str(date(year,month,day).strftime("%A")))
            x8.append(str(bool(e or t or i)))
            x8.append(chain(e,i,t))
        if day == 9:
            
            x9.append(total_e)
            x9.append(total_i)
            x9.append(str(day))
            x9.append(str(year))
            x9.append(str(month))
            x9.append(str(date(year,month,day).strftime("%A")))
            x9.append(str(bool(e or t or i)))
            x9.append(chain(e,i,t))
        if day == 10:
            
            x10.append(total_e)
            x10.append(total_i)
            x10.append(str(day))
            x10.append(str(year))
            x10.append(str(month))
            x10.append(str(date(year,month,day).strftime("%A")))
            x10.append(str(bool(e or t or i)))
            x10.append(chain(e,i,t))
        if day == 11:
            
            x11.append(total_e)
            x11.append(total_i)
            x11.append(str(day))
            x11.append(str(year))
            x11.append(str(month))
            x11.append(str(date(year,month,day).strftime("%A")))
            x11.append(str(bool(e or t or i)))
            x11.append(chain(e,i,t))
        if day == 12:
            
            x12.append(total_e)
            x12.append(total_i)
            x12.append(str(day))
            x12.append(str(year))
            x12.append(str(month))
            x12.append(str(date(year,month,day).strftime("%A")))
            x12.append(str(bool(e or t or i)))
            x12.append(chain(e,i,t))
        if day == 13:
            
            x13.append(total_e)
            x13.append(total_i)
            x13.append(str(day))
            x13.append(str(year))
            x13.append(str(month))
            x13.append(str(date(year,month,day).strftime("%A")))
            x13.append(str(bool(e or t or i)))
            x13.append(chain(e,i,t))
        if day == 14:
            
            x14.append(total_e)
            x14.append(total_i)
            x14.append(str(day))
            x14.append(str(year))
            x14.append(str(month))
            x14.append(str(date(year,month,day).strftime("%A")))
            x14.append(str(bool(e or t or i)))
            x14.append(chain(e,i,t))
        if day == 15 :
            
            x15.append(total_e)
            x15.append(total_i)
            x15.append(str(day))
            x15.append(str(year))
            x15.append(str(month))
            x15.append(str(date(year,month,day).strftime("%A")))
            x15.append(str(bool(e or t or i)))
            x15.append(chain(e,i,t))
        if day == 16:
            
            x16.append(total_e)
            x16.append(total_i)
            x16.append(str(day))
            x16.append(str(year))
            x16.append(str(month))
            x16.append(str(date(year,month,day).strftime("%A")))
            x16.append(str(bool(e or t or i)))
            x16.append(chain(e,i,t))
        if day == 17:
            
            x17.append(total_e)
            x17.append(total_i)
            x17.append(str(day))
            x17.append(str(year))
            x17.append(str(month))
            x17.append(str(date(year,month,day).strftime("%A")))
            x17.append(str(bool(e or t or i)))
            x17.append(chain(e,i,t))
        if day == 18:
            
            x18.append(total_e)
            x18.append(total_i)
            x18.append(str(day))
            x18.append(str(year))
            x18.append(str(month))
            x18.append(str(date(year,month,day).strftime("%A")))
            x18.append(str(bool(e or t or i)))
            x18.append(chain(e,i,t))
        if day == 19:
            
            x19.append(total_e)
            x19.append(total_i)
            x19.append(str(day))
            x19.append(str(year))
            x19.append(str(month))
            x19.append(str(date(year,month,day).strftime("%A")))
            x19.append(str(bool(e or t or i)))
            x19.append(chain(e,i,t))
        if day == 20:
            
            x20.append(total_e)
            x20.append(total_i)
            x20.append(str(day))
            x20.append(str(year))
            x20.append(str(month))
            x20.append(str(date(year,month,day).strftime("%A")))
            x20.append(str(bool(e or t or i)))
            x20.append(chain(e,i,t))
        if day == 21:
            
            x21.append(total_e)
            x21.append(total_i)
            x21.append(str(day))
            x21.append(str(year))
            x21.append(str(month))
            x21.append(str(date(year,month,day).strftime("%A")))
            x21.append(str(bool(e or t or i)))
            x21.append(chain(e,i,t))
        if day == 22:
            
            x22.append(total_e)
            x22.append(total_i)
            x22.append(str(day))
            x22.append(str(year))
            x22.append(str(month))
            x22.append(str(date(year,month,day).strftime("%A")))
            x22.append(str(bool(e or t or i)))
            x22.append(chain(e,i,t))
        if day == 23:
            
            x23.append(total_e)
            x23.append(total_i)
            x23.append(str(day))
            x23.append(str(year))
            x23.append(str(month))
            x23.append(str(date(year,month,day).strftime("%A")))
            x23.append(str(bool(e or t or i)))
            x23.append(chain(e,i,t))
        if day == 24:
            
            x24.append(total_e)
            x24.append(total_i)
            x24.append(str(day))
            x24.append(str(year))
            x24.append(str(month))
            x24.append(str(date(year,month,day).strftime("%A")))
            x24.append(str(bool(e or t or i)))
            x24.append(chain(e,i,t))
        if day == 25:
            
            x25.append(total_e)
            x25.append(total_i)
            x25.append(str(day))
            x25.append(str(year))
            x25.append(str(month))
            x25.append(str(date(year,month,day).strftime("%A")))
            x25.append(str(bool(e or t or i)))
            x25.append(chain(e,i,t))
        if day == 26:
            
            x26.append(total_e)
            x26.append(total_i)
            x26.append(str(day))
            x26.append(str(year))
            x26.append(str(month))
            x26.append(str(date(year,month,day).strftime("%A")))
            x26.append(str(bool(e or t or i)))
            x26.append(chain(e,i,t))
        if day == 27:
            
            x27.append(total_e)
            x27.append(total_i)
            x27.append(str(day))
            x27.append(str(year))
            x27.append(str(month))
            x27.append(str(date(year,month,day).strftime("%A")))
            x27.append(str(bool(e or t or i)))
            x27.append(chain(e,i,t))
        if day == 28:
            
            x28.append(total_e)
            x28.append(total_i)
            x28.append(str(day))
            x28.append(str(year))
            x28.append(str(month))
            x28.append(str(date(year,month,day).strftime("%A")))
            x28.append(str(bool(e or t or i)))
            x28.append(chain(e,i,t))

        if checkYear(year):
            if day == 29:
                
                x29.append(total_e)
                x29.append(total_i)
                x29.append(str(day))
                x29.append(str(year))
                x29.append(str(month))
                x29.append(str(date(year,month,day).strftime("%A")))
                x29.append(str(bool(e or t or i)))
                x29.append(chain(e,i,t))

        if month in m1:
            
            if day == 29:
                
                x29.append(total_e)
                x29.append(total_i)
                x29.append(str(day))
                x29.append(str(year))
                x29.append(str(month))
                x29.append(str(date(year,month,day).strftime("%A")))
                x29.append(str(bool(e or t or i)))
                x29.append(chain(e,i,t))
            if day == 30:
                
                x30.append(total_e)
                x30.append(total_i)
                x30.append(str(day))
                x30.append(str(year))
                x30.append(str(month))
                x30.append(str(date(year,month,day).strftime("%A")))
                x30.append(str(bool(e or t or i)))
                x30.append(chain(e,i,t))
            if day == 31 :
                
                x31.append(total_e)
                x31.append(total_i)
                x31.append(str(day))
                x31.append(str(year))
                x31.append(str(month))
                x31.append(str(date(year,month,day).strftime("%A")))
                x31.append(str(bool(e or t or i)))
                x31.append(chain(e,i,t))

        if month in m2:
            
            
            if day == 29:
                
                x29.append(total_e)
                x29.append(total_i)
                x29.append(str(day))
                x29.append(str(year))
                x29.append(str(month))
                x29.append(str(date(year,month,day).strftime("%A")))
                x29.append(str(bool(e or t or i)))
                x29.append(chain(e,i,t))
            if day == 30:
                
                x30.append(total_e)
                x30.append(total_i)
                x30.append(str(day))
                x30.append(str(year))
                x30.append(str(month))
                x30.append(str(date(year,month,day).strftime("%A")))
                x30.append(str(bool(e or t or i)))
                x30.append(chain(e,i,t))
        
        

        
        d.append(day)
        day = day -1
    d= list(dict.fromkeys(d))
    ee = Expense.objects.filter(user=request.user).order_by('-date')
    ii = Income.objects.filter(user=request.user).order_by('-date')
    tt = Transfer.objects.filter(user=request.user).order_by('-date')
    
    
    return render(request, "app/daily.html",{
        'form':MyForm(),
        'day':d,
        'months':[(1,'January'),
                  (2,'February'),
                  (3,'March'),
                  (4,'April'),
                  (5,'May'),
                  (6,'June'),
                  (7,'July'),
                  (8,'August'),
                  (9,'September'),
                  (10,'October'),
                  (11,'November'),
                  (12,'December'),],
        'date' : date(year,month,2),
        'x1':x1,'x2':x2,'x3':x3,'x4':x4,'x5':x5,'x6':x6,'x7':x7,'x8':x8,'x9':x9,'x10':x10,'x11':x11,'x12':x12,'x13':x13,'x14':x14,'x15':x15,'x16':x16,'x17':x17,'x18':x18,'x19':x19,'x20':x20,'x21':x21,'x22':x22,'x23':x23,'x24':x24,'x25':x25,'x26':x26,'x27':x27,'x28':x28,'x29':x29,'x30':x30,'x31':x31,
        'expense':ee,
        'income':ii,
        'transfer':tt,
        'expense_total':ee.aggregate(Sum('cost')),
        'income_total':ii.aggregate(Sum('cost')),
        'msg':'daily'
    })


def stats(request):

    m=int(datetime.now().strftime("%m"))

    year = int(datetime.now().strftime("%Y"))
    if request.method == 'POST':
        m=int(request.POST['month'])

        year=int(request.POST['year'])
        
    ebar = []
    ibar = []
    x1 = []
    balance = []
    months = [(1,'January'),
                  (2,'February'),
                  (3,'March'),
                  (4,'April'),
                  (5,'May'),
                  (6,'June'),
                  (7,'July'),
                  (8,'August'),
                  (9,'September'),
                  (10,'October'),
                  (11,'November'),
                  (12,'December'),]
    for mm in months:
        x1.append(mm[1])
        month = mm[0]
        total_expense = Expense.objects.filter(user=request.user).filter(date__year=year).filter(date__month=month).aggregate(Sum('cost'))['cost__sum']
        total_income = Income.objects.filter(user=request.user).filter(date__year=year).filter(date__month=month).aggregate(Sum('cost'))['cost__sum']
        if total_expense == None:
            total_expense = 0
        if total_income == None:
            total_income = 0
        ebar.append(total_expense)
        ibar.append(total_income)
        balance.append(total_income-total_expense)
    
    total_expense = Expense.objects.filter(user=request.user).aggregate(Sum('cost'))['cost__sum']
    total_income = Income.objects.filter(user=request.user).aggregate(Sum('cost'))['cost__sum']
    labels1 = []
    data1 = []
    labels2 = []
    data2 = []
    month = m
    queryset1 = Expense.objects.filter(user=request.user).filter(date__year=year).filter(date__month=month)
    queryset2 = Income.objects.filter(user=request.user).filter(date__year=year).filter(date__month=month)
    incomecat = ['Allowance','Salary','Petty cash','Bonus','Account','Other']
    expensecat = ['Food','Social Life','Self-development','Transportation','Culture','Household','Apparel','Beauty','Health','Education','Gift','others']
    for x in expensecat :
        cat1 = queryset1.filter(category=x).aggregate(Sum('cost'))['cost__sum']
        
        if cat1 is None:
            cat1 = 0
        else:
            data1.append(cat1)
            labels1.append(x)

    for x in incomecat:
        
        cat1 = queryset2.filter(category=x).aggregate(Sum('cost'))['cost__sum']
        
        if cat1 is None:
            cat1 = 0
        else:
            data2.append(cat1)
            labels2.append(x)
            
        
        

    print(data1)
    return render(request, "app/stats.html",{
        'form':MyForm(),
        'date':date(year,month,2),
        'labels1':labels1,
        'data1':data1,
        'labels2':labels2,
        'data2':data2,
        'months':x1,
        'mm':months,
        'bar1':ebar,
        'bar2':ibar,
        'linedata':balance
        

        
    })
