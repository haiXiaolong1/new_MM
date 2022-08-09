"""newMM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path,include
from supply import views
from django.views.generic.base import RedirectView

##静态url所需配置
from django.urls import re_path as url
from django.views import static
from django.conf import settings

urlpatterns = [
    path('supply/',include('supply.urls')),
    path('login/',views.login),
    path('logout/', views.logout),
    path('forgot', views.forgot),
    path('purchase/',include('purchase.urls')),
    path('inventory/',include('inventory.urls')),
    path('account/',include('account.urls')),
    path('excel/',include('excel.urls')),
    path('initial/',views.initial),
    path('guide/',views.guide),
    # path(r'^favicon\.ico$',RedirectView.as_view(url=r'static/images/favicon.ico')),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
    # url(r'^static/(?P<path>.*)$', static.serve,
    #   {'document_root': settings.STATIC_ROOT}, name='static'),
]
