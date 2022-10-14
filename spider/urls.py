from django.urls import path, include
from spider import views

urlpatterns = [
    path('weather/',views.get_weather),
    path('fiction/',views.get_fiction),
    path('fiction/chapters',views.get_chapters),
    path('fiction/chapter',views.get_chapter),
    path('picture/',views.get_picture),
    path('picture/bigImage',views.get_bigImage),
    path('picture/more',views.get_more),
    path('picturesearch/',views.get_picturesearch),
    path('picturesearch/bigPicture',views.get_bigPicture),
    path('audio/',views.get_audioList),
    path('audio/audio',views.get_audio)

]
