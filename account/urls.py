from django.urls import path,include
from account import  views

urlpatterns = [
    path('list/',views.account_list),
    #path('create/',views.account_create),
]