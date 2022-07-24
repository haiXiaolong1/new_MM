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
    #time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    o=request.POST
    id=request.session["info"]['id']
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

    print(o["myid"])
    gs = models.Gongsi.objects.get(myid=o["myid"])
    print(gs)
    models.Yuangong.objects.create(office=o['office'],username=o['username'],password=o['password']
                                        ,id=sid,isactive=isa,issuper=isp,businessid=gs)
    print(request.POST)
    return JsonResponse({"status":True})
# 编辑供应商时返回供应商原始数据
def ac_detail(request):
    sid=request.GET.get("uid")
    su=models.Wuliao.objects.filter(id=sid).values("type",'salegroup','saleway',"calcutype","desc").first()
    if not su:
        return JsonResponse({"status":False,"error":"数据不存在"})
    return JsonResponse({"supply":su,"status":True})

# 保存编辑供应商的最新数据
def ac_edit(request):
    id=request.GET.get("uid")
    uid=request.session["info"]['id']
    # 用户ID
    o=request.POST
    #time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    models.Wuliao.objects.filter(id=id).update(type=o['type'],salegroup=o['salegroup'],saleway=o['saleway']
                                        ,calcutype=o['calcutype'],desc=o['desc'])

    return JsonResponse({"status":True})

# 删除供应商
def ac_delete(request):
    id=request.GET.get("uid")
    '''
    s=models.Wuliao.objects.filter(supplyid_id=id).first()
    # 先判断是否有关联关系，如果有则不能删除，目前没有
    if s:
        return JsonResponse({"status":False})
    '''
    models.Wuliao.objects.filter(id=id).delete()
    return JsonResponse({"status":True})

def ac_check_message(request):
    return JsonResponse({"status": True,"newMessage":False,"ans":"没有新消息！"})