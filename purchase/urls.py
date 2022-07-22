from django.urls import path,include
from purchase import  views

urlpatterns = [


    path("inquiry/create/",views.inquiry_create),

    path("inquiry/<slug:did>/create/",views.inquiry_createByid),
    path("create/qui/",views.create_qui),
    path("delete/",views.purchase_delete),


    path('quote/evaluate/',views.quote_evaluate),
    path("quote/evaluateByID/",views.quote_evaluateByID),


    path('list/',views.purchase_list),
    path('create/',views.purchase_create),
    path('createByQuote/',views.purchase_createByQuote),
    path('documents/',views.purchase_documents),
]
