from django.urls import path,include
from .views import *
from excel import views


urlpatterns = [


    path('excel_upload', TestDjangoExcelUpload.as_view(), name='excel_upload'),
    path('excel_download', TestDjangoExcelDownload.as_view(), name='excel_download'),

    path('excel_download_account', TestDjangoExcelDownload_ac.as_view()),

    path('new_excel',views.new_excel)
]