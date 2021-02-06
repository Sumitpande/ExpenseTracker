from . import views
from app.views import *
from django.urls import path
from django.urls import include, re_path
from django.contrib.auth.decorators import login_required, permission_required
urlpatterns = [
    path('daily/', views.trans_daily, name='trans_daily'),
    path('weekly/', views.trans_weekly, name='trans_weekly'),
    path('monthly/', views.trans_monthly, name='trans_monthly'),

    path('', login_required(IncomeList.as_view()), name='income-list'),
    path('expense/', login_required(ExpenseList.as_view()), name='expense-list'),
    path('transfer/', login_required(TransferList.as_view()), name='transfer-list'),

    path('income/add/', IncomeCreate.as_view(), name='income-add'),
    path('income/<int:pk>/', IncomeUpdate.as_view(), name='income-update'),
    path('income/<int:pk>/delete/', IncomeDelete.as_view(), name='income-delete'),

    path('expense/add/', ExpenseCreate.as_view(), name='expense-add'),
    path('expense/<int:pk>/', ExpenseUpdate.as_view(), name='expense-update'),
    path('expense/<int:pk>/delete/', ExpenseDelete.as_view(), name='expense-delete'),

    path('transfer/add/', TransferCreate.as_view(), name='transfer-add'),
    path('transfer/<int:pk>/', TransferUpdate.as_view(), name='transfer-update'),
    path('transfer/<int:pk>/delete/', TransferDelete.as_view(), name='transfer-delete'),


    path('bookmark/',views.bookmark,name='bookmark'),
    path('bookmarki/<int:id>',views.bookmarki,name='bookmarki'),
    path('bookmarke/<int:id>',views.bookmarke,name='bookmarke'),
    path('bookmarkt/<int:id>',views.bookmarkt,name='bookmarkt'),


    path("statistics/",views.stats, name="stats"),

    #Memo
    path("memo",login_required(views.memo) , name="memo"),
    path("memos",views.memoCreate , name="memoCreate"),
    path("memo/<int:id>",views.memoUpdate , name="memoUpdate"),
    path('memo/delete/<int:id>',views.delMemo,name="delMemo")


]