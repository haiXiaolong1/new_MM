from django.shortcuts import render
import random
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from supply import models
# Create your views here.

# 登录功能
def login(request):
    if request.method=="GET":
        return render(request,'login.html')
    username=request.POST.get("username")
    password=request.POST.get("password")
    ins=models.Yuangong.objects.filter(username=username).first()
    if not ins :
        return redirect('/login/')
    if password==ins.password:
        # 记录登录信息
        request.session["info"]={"name":ins.username,"id":ins.id,"issuper":ins.issuper
            ,"office":ins.office,"business":ins.businessid.name}
        return redirect('/supply/list')
#登出功能
def logout(request):

    request.session.clear()
    return redirect('/login')
# 展示供应商列表
def supply_list(request):
    qu=models.Gongyingshang.objects.all()
    yu=models.Yuangong.objects.all()
    id=[]
    n=[]
    for i in yu:
        id.append(i.id)
        n.append(i.username)
    yuan=dict(zip(id,n))
    return render(request,'supply_list.html',{"queryset":qu,"yuangong":yuan})
# 添加供应商
def supply_add(request):
    n=10000000
    if models.Gongyingshang.objects.first():
        n=models.Gongyingshang.objects.all().order_by('-id').first().id[1:]
    sid="s"+str(int(n)+1)#编号递增，这样计算避免删除后出现错误
    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    o=request.POST
    id=request.session["info"]['id']
    models.Gongyingshang.objects.create(name=o['name'],address=o['address'],createtime=time
                                        ,id=sid,updatetime=time,createnumberid_id=id,updatenumberid_id=id)
    print(request.POST)
    return JsonResponse({"status":True})
# 编辑供应商时返回供应商原始数据
def supply_detail(request):
    sid=request.GET.get("uid")
    su=models.Gongyingshang.objects.filter(id=sid).values("name","address").first()
    if not su:
        return JsonResponse({"status":False,"error":"数据不存在"})
    return JsonResponse({"supply":su,"status":True})

# 保存编辑供应商的最新数据
def supply_edit(request):
    id=request.GET.get("uid")
    uid=request.session["info"]['id']
    # 用户ID
    s=request.POST
    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    models.Gongyingshang.objects.filter(id=id).update(name=s['name'],
                                                      address=s['address'],updatetime=time,updatenumberid_id=uid)

    return JsonResponse({"status":True})

# 删除供应商
def supply_delete(request):
    id=request.GET.get("uid")
    s=models.Gongyingguanxi.objects.filter(supplyid_id=id).first()
    # 先判断是否有关联的供应关系，如果有则不能删除
    if s:
        return JsonResponse({"status":False})
    models.Gongyingshang.objects.filter(id=id).delete()
    return JsonResponse({"status":True})

# 展示供应商与材料的供应关系
def material_list(request):

    qu=models.Gongyingguanxi.objects.all()
    material=models.Wuliao.objects.all()
    supply=models.Gongyingshang.objects.all()
    result={
        "queryset":qu,
        "material":material,
        "supply":supply
    }

    return render(request,'material_list.html',result)

# 添加供应商与物料的供应关系
def material_add(request):

    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    r=request.POST
    sid=r["supplyid"]
    mid=r["materialid"]
    id=request.session["info"]['id']
    # 判断是否已经存在此供应关系，如果已存在则提示不能重复添加
    isexist=models.Gongyingguanxi.objects.filter(supplyid_id=sid,materialid_id=mid)
    if isexist:
        return JsonResponse({"status":True,"isexist":True})
    models.Gongyingguanxi.objects.create(createtime=time,updatetime=time,
                                         createid_id=id,updateid_id=id,
                                         supplyid_id=sid,materialid_id=mid)
    return JsonResponse({"status":True,"isexist":False})

# 编辑供应关系时展示原始数据
def material_detail(request):
    smid=request.GET.get("uid")
    su=models.Gongyingguanxi.objects.filter(id=smid).values("supplyid_id","materialid_id").first()
    if not su:
        return JsonResponse({"status":False,"error":"数据不存在"})
    return JsonResponse({"sm":su,"status":True})

# 保存编辑过后的供应关系
def material_edit(request):
    id=request.GET.get("uid")
    uid=request.session["info"]['id']
    # 用户ID
    s=request.POST
    mid=s["materialid"]
    sid=s["supplyid"]
    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    isexist=models.Gongyingguanxi.objects.filter(supplyid_id=sid,materialid_id=mid)
    i=models.Gongyingguanxi.objects.filter(id=id)
    # 如果未作改动依旧显示成功
    if isexist and (i.first().materialid_id!=mid or i.first().supplyid_id!=sid):
        return JsonResponse({"status":True,"isexist":True})
    i.update(supplyid_id=sid,materialid_id=mid,updatetime=time,updateid_id=uid)
    return JsonResponse({"status":True,"isexist":False})




def quote_list(request):
    """进行报价"""
    q=models.Baojiadan.objects.all()

    return render(request,'quote_list.html',{"queryset":q})


def quote_add(request):
    """报价完成"""
    inid=request.GET.get("inid")
    quote=request.POST.get("quote")
    n=10000000
    if models.Baojiadan.objects.all().first():
        n=models.Baojiadan.objects.all().order_by('-quoteid').first().quoteid[2:]
    qid="qu"+str(int(n)+1)#编号递增，这样计算避免删除后出现错误
    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id=request.session["info"]['id']
    models.Baojiadan.objects.filter(inquiryid_id=inid).update(quote=quote,
                                                              quoteid=qid,
                                                              createtime=time,
                                                              createuserid_id=id,
                                                              isreceived=0)
    return JsonResponse({"status":True})


