from django.urls import path,include
from account import  views

urlpatterns = [
    path('ac/list/',views.ac_list),
    path('ac/add/',views.ac_add),
    path('ac/edit/',views.ac_edit),
    path('ac/delete/', views.ac_delete),
    path('ac/detail/',views.ac_detail),
    path('ac/password/',views.ac_password),
    path('ac/send/',views.ac_send),
    path('ac/login/',views.ac_login),
    path('account_excel/',views.ac_excel),
]