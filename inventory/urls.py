from django.urls import path, include
from inventory import views

urlpatterns = [
    path("display/", views.inventory_display),
    path("<int:uid>/detail/", views.inventory_detail),
    path("demand/<slug:did>/", views.inventory_demand),
    path("temp/", views.inventory_temp),
    path("temp/delete/", views.inventory_delete),

    path("demand/add/n/", views.demand_add),
    path("demand/verify/n/", views.demand_verify),
    path("demand/delete/n/", views.demand_delete),
    path("demand/create/",views.demand_create),

    path("quality/check/", views.quality_check),
    path("quantity/check/", views.quantity_check),
    path("receive/", views.inventory_receive),
    path("receive/add/", views.receive_add),
    path("receive/delete/", views.receive_delete),
    path("invoice/", views.inventory_invoice),
    path("invoice/add/", views.invoice_add),
    path("invoice/<slug:ivid>/display/", views.invoice_display),

]
