from django.shortcuts import render,HttpResponse

# Create your views here.
from supply import models
from  supply.views import form_check
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
def ac_list(request):
    yu=models.Yuangong.objects.all()
    gs=models.Gongsi.objects.all()
    return render(request,'account.html',{"queryset":yu,"gongsi":gs,"title":"员工列表"})
# 添加用户
def ac_add(request):
    n=10000
    if models.Yuangong.objects.first():
        n=models.Yuangong.objects.all().order_by('-id').first().id[1:]
    num = str(int(n)+1)#编号递增，这样计算避免删除后出现错误
    cal = 4 - len(num)
    sid="e"+ "0"*cal +num
    o=request.POST
    isactive = o['isactive']
    issuper = 0
    bid=o["businessid_id"]
    toCheck = [o['username'], o['password'],o['email'],bid]
    types = ['nan', 'nan','nan','nan']
    res = form_check(toCheck, types)
    if res["status"]:
        models.Yuangong.objects.create(office=o['office'],username=o['username'],password=o['password'],email=o['email']
                                        ,id=sid,isactive=isactive,issuper=issuper,businessid_id=bid)
    return JsonResponse(res)
# 编辑用户时返回用户原始数据
def ac_detail(request):
    id=request.GET.get("uid")
    ac=models.Yuangong.objects.filter(id=id).values("office",'password','username',"email","isactive","issuper","businessid_id").first()
    if not ac:
        return JsonResponse({"status":False,"error":"数据不存在"})
    return JsonResponse({"account":ac,"status":True})

# 保存编辑用户的最新数据
def ac_edit(request):
    id=request.GET.get("uid")
    o=request.POST
    isactive = o['isactive']
    issuper = 0
    bid=o["businessid_id"]
    toCheck = [o['username'], o['password'],o['email'],bid]
    types = ['nan', 'nan','nan','nan']
    res = form_check(toCheck, types)
    if res["status"]:
        models.Yuangong.objects.filter(id=id).update(office=o['office'],username=o['username'],password=o['password'],email=o['email']
                                                 ,isactive=isactive,issuper=issuper,businessid=o['businessid_id'])

    return JsonResponse(res)

# 删除用户
@csrf_exempt
def ac_delete(request):
    id=request.POST.get("uid")
    gc=models.Gongyingshang.objects.filter(createnumberid_id=id).first()
    gu=models.Gongyingshang.objects.filter(updatenumberid_id=id).first()
    cc=models.Caigouxuqiu.objects.filter(createuserid_id=id).first()
    cu=models.Caigouxuqiu.objects.filter(verifyuserid_id=id).first()
    if gc or gu or cc or cu :
        return JsonResponse({"status":False})
    print(id)
    models.Yuangong.objects.filter(id=id).delete()
    return JsonResponse({"status":True})