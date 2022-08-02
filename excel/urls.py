from django.urls import path,include
from .views import *
from excel import views


urlpatterns = [

    # ex:/assetinfo/test_django_excel_upload
    path('excel_upload', TestDjangoExcelUpload.as_view(), name='excel_upload'),

    # ex:/assetinfo/test_django_excel_download
    path('excel_download', TestDjangoExcelDownload.as_view(), name='excel_download'),
    path('new_excel',views.new_excel)
]