from django.urls import path, include
from spider import views

urlpatterns = [
    path('weather/',views.get_weather),
    path('get1data/', views.get_1_data),
    path('get7data/',views.get_7_data)

]
