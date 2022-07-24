from django.shortcuts import render,HttpResponse

# Create your views here.
from supply import models
from django.http import JsonResponse

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
    issuper = o['issuper']
    if isactive=="是":
        isa = 1
    else:
        isa = 0
    if issuper == "是":
        isp = 1
    else:
        isp = 0

    print(o["businessid_id"])
    gs = models.Gongsi.objects.get(myid=o["businessid_id"])
    print(gs)
    models.Yuangong.objects.create(office=o['office'],username=o['username'],password=o['password']
                                        ,id=sid,isactive=isa,issuper=isp,businessid=gs)
    # print(request.POST)
    return JsonResponse({"status":True})
# 编辑用户时返回用户原始数据
def ac_detail(request):
    id=request.GET.get("uid")
    ac=models.Yuangong.objects.filter(id=id).values("office",'password','username',"isactive","issuper","businessid_id").first()
    if not ac:
        return JsonResponse({"status":False,"error":"数据不存在"})
    return JsonResponse({"account":ac,"status":True})

# 保存编辑用户的最新数据
def ac_edit(request):
    id=request.GET.get("uid")
    o=request.POST
    isactive = o['isactive']
    issuper = o['issuper']

    print(isactive)
    models.Yuangong.objects.filter(id=id).update(office=o['office'],username=o['username'],password=o['password']
                                                 ,isactive=isactive,issuper=issuper,businessid=o['businessid_id'])

    return JsonResponse({"status":True})

# # 删除供应商
# def ac_delete(request):
#     id=request.GET.get("uid")
#     '''
#     s=models.Wuliao.objects.filter(supplyid_id=id).first()
#     # 先判断是否有关联关系，如果有则不能删除，目前没有
#     if s:
#         return JsonResponse({"status":False})
#     '''
#     models.Wuliao.objects.filter(id=id).delete()
#     return JsonResponse({"status":True})