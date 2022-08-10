from django.contrib import admin
from supply.models import Gongsi,Wuliao,Securityquestion,\
    Yuangong,Xiaoxi,Gongchang,Gongyingshang,Gongyingguanxi,\
    Gongchangkucun,Caigouxuqiu,Xunjiadan,Baojiadan,\
    Caigoudan,Zanshoudan,Rukudan,Fapiao
# Register your models here.

admin.site.register(Gongsi)
admin.site.register(Wuliao)
admin.site.register(Securityquestion)
admin.site.register(Xiaoxi)
admin.site.register(Yuangong)
admin.site.register(Gongchang)
admin.site.register(Gongyingshang)
admin.site.register(Gongyingguanxi)
admin.site.register(Gongchangkucun)
admin.site.register(Caigouxuqiu)
admin.site.register(Xunjiadan)
admin.site.register(Baojiadan)
admin.site.register(Caigoudan)
admin.site.register(Zanshoudan)
admin.site.register(Rukudan)
admin.site.register(Fapiao)


admin.AdminSite.site_header = 'new MM'
admin.AdminSite.site_title = 'new MM'