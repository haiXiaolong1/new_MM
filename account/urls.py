from django.urls import path,include
from account import  views

urlpatterns = [
    path('ac/list/',views.ac_list),
    path('ac/add/',views.ac_add),
    path('ac/edit/',views.ac_edit),
    path('ac/delete/', views.ac_delete),
    path('checkMessage', views.ac_check_message),
]