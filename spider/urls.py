from django.urls import path, include
from spider import views

urlpatterns = [
    path('weather/',views.get_weather),
    path('fiction/',views.get_fiction),
    path('fiction/chapters',views.get_chapters),
    path('fiction/chapter',views.get_chapter)

]
