from django.shortcuts import render
import random
from datetime import datetime
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from supply import models
# Create your views here.

import json
""" 表单数据验证+报错信息 """
def form_item_check(context,type="nan"):
    if context.strip()=="":
        if type[:2] == "id":
            return "请设置" + type[2:]
        return "必填字段，内容不能为空"
    need={"int":"整数","int+":"正整数","float":"数字","float+":"正数"}
    if not type=="nan" and not type[:2]=="id":
        ctx=context
        if context[0]=="-":
            ctx=context[1:]
        if ctx.count(".")>1 or not ctx[0].isdigit() or not ctx.replace(".","").isdigit():
            return "输入错误,请输入"+need[type]
        if type[-1]=="+" and float(context)<=0:
            return "输入错误,请输入"+need[type]
    return True

def form_check(toCheck,types):
    #设置表单数据校验
    errors=[] #校验结果
    returnStatus=True #是否通过所有校验
    for idx,(cck,typ) in enumerate(zip(toCheck,types)):
        result=form_item_check(cck,typ)
        errors.append(result)
        if not result==True:
            returnStatus=False
    res_dict = {"status": returnStatus, "error": errors}
    return res_dict

def check_message(request):
    return JsonResponse({"status": True,"newMessage":False,"ans":"没有新消息！"})

def all_message():
    me,them='e0003','e0002'
    who = models.Yuangong.objects.filter(id=them).first().username
    tos=models.Xiaoxi.objects.filter(fromId=them,toId=me).all()
    froms=models.Xiaoxi.objects.filter(fromId=me,toId=them).all()
    message_flow=[]
    for i in froms:
        message_flow.append({"isThem":True,"time":i.time.strftime("%m月%d日 %H:%M:%S"),"text":i.context,"compare":int(i.time.strftime("%Y%m%d%H%M%S%f"))})
    for i in tos:
        message_flow.append({"isThem":False,"time":i.time.strftime("%m月%d日 %H:%M:%S"),"text":i.context,"compare":int(i.time.strftime("%Y%m%d%H%M%S%f"))})
    message_flow=sorted(message_flow,key=lambda a: a["compare"])
    flow1 = {"who": "部门经理", "flow": message_flow}
    return [flow1,flow1]

def add_message(line):
    html_class="me"
    icon=""
    if line["isThem"]:
        html_class="them"
        icon='<div class="chat-bubble-img-container"><img src="http://via.placeholder.com/38x38" alt=""></div>'
    html_template=' <div class="chat-bubble {}">{}<div class="chat-bubble-text-container"><span class="chat-bubble-text">{}</span></div></div>'
    html=html_template.format(html_class,icon,line["text"])
    return html

def group_by_time(f):
    flow=f["flow"]
    start=int(flow[0]["compare"])
    interval=200000
    group=0
    groups={0:[]}
    for i in flow:
        if int(i["compare"])-start>=interval:
            start=i["compare"]
            group+=1
            groups[group]=[]
        groups[group].append(i)
    return groups

def add_group(group):
    time_template='<div class="chat-start-date">{}</div>'
    time=time_template.format(group[0]["time"])
    for line in group:
        time+=add_message(line)
    return time

def set_message_detail(request):
    #flow=request.POST.get("flow")
    flow=all_message()[0]
    groups=group_by_time(flow)
    out=""
    for g in groups.values():
        out+=add_group(g)
    return JsonResponse({"status":True,"message":out})



# 登录功能
def login(request):
    if request.method=="GET":
        return render(request,'login.html')
    username=request.POST.get("username")
    password=request.POST.get("password")
    ins=models.Yuangong.objects.filter(username=username).first()
    err=["",""]
    if not str(username).strip():
        err[0]="用户名不能为空"
    if not str(password).strip():
        err[1]="密码不能为空"
    if err[0] or err[1]:
        return JsonResponse({"status":False,"errors":err})
    if not err[0] and not err[1] and not ins:
        err[0]="用户名不存在"
        return JsonResponse({"status":False,"errors":err})
    if password!=ins.password:
        err[0]="密码错误"
        return JsonResponse({"status":False,"errors":err})

    # 记录登录信息
    request.session["info"]={"name":ins.username,"id":ins.id,"issuper":ins.issuper
        ,"office":ins.office,"business":ins.businessid.name}
    # request.session["messageFlow"] = all_message()
    return JsonResponse({"status":True})

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
    return render(request,'supply_list.html',{"queryset":qu,"yuangong":yuan,"title":"供应商列表"})
# 添加供应商
def supply_add(request):
    n=10000000
    if models.Gongyingshang.objects.first():
        n=models.Gongyingshang.objects.all().order_by('-id').first().id[1:]
    sid="s"+str(int(n)+1)#编号递增，这样计算避免删除后出现错误
    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    o=request.POST
    id=request.session["info"]['id']
    toCheck=[o['name'],o['address']]
    types=['nan','nan']
    res=form_check(toCheck,types)
    if res['status']:
        models.Gongyingshang.objects.create(name=o['name'],address=o['address'],createtime=time
                                            ,id=sid,updatetime=time,createnumberid_id=id,updatenumberid_id=id)
    return JsonResponse(res)

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
    toCheck=[s['name'],s['address']]
    types=['nan','nan']
    res=form_check(toCheck,types)
    if res:
        models.Gongyingshang.objects.filter(id=id).update(name=s['name'],
                                                      address=s['address'],updatetime=time,updatenumberid_id=uid)

    return JsonResponse(res)

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
        ,"title":"物料供应关系"
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
    toCheck = [sid, mid]
    types = ['id供应商编号', 'id物料编号']
    res = form_check(toCheck, types)
    res["isexist"]=False
    print(res)
    if res['status']:
        models.Gongyingguanxi.objects.create(createtime=time,updatetime=time,
                                             createid_id=id,updateid_id=id,
                                             supplyid_id=sid,materialid_id=mid)
    return JsonResponse(res)

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
    toCheck = [sid, mid]
    types = ['id供应商编号', 'id物料编号']
    res = form_check(toCheck, types)
    res["isexist"]=False
    if res["status"]:
        i.update(supplyid_id=sid,materialid_id=mid,updatetime=time,updateid_id=uid)
    return JsonResponse(res)




def quote_list(request):
    """进行报价"""
    q=models.Baojiadan.objects.filter(isdelete=0)

    return render(request, 'quote_list.html', {"queryset":q, "title": "报价单管理"})


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
    toCheck=[quote]
    types=["float+"]
    res=form_check(toCheck,types)
    if res['status']:
        models.Baojiadan.objects.filter(inquiryid_id=inid).update(quote=quote,
                                                                  quoteid=qid,
                                                                  createtime=time,
                                                                  createuserid_id=id,
                                                                  isreceived=0)
    return JsonResponse(res)


def quote_detail(request):
    """修改报价单时返回相应数据"""
    id=request.GET.get("uid")
    quote=models.Baojiadan.objects.filter(quoteid=id).first().quote
    return JsonResponse({"status":True,"quote":quote})


def quote_edit(request):
    """根据报价单号修改报价"""
    quid=request.GET.get("quid")
    quote=request.POST.get("quote")
    toCheck=[quote]
    types=["float+"]
    res=form_check(toCheck,types)
    if res['status']:
        models.Baojiadan.objects.filter(quoteid=quid).update(quote=quote)
    return JsonResponse(json.dumps(res,ensure_ascii=False),safe=False)


# 展示物料列表
def mm_list(request):
    qu=models.Wuliao.objects.all()
    yu=models.Yuangong.objects.all()
    id=[]
    n=[]
    for i in yu:
        id.append(i.id)
        n.append(i.username)
    yuan=dict(zip(id,n))
    return render(request,'create_material.html',{"queryset":qu,"yuangong":yuan,"title":"物料列表"})
# 添加供应商
def mm_add(request):
    n=1000
    if models.Wuliao.objects.first():
        n=models.Wuliao.objects.all().order_by('-id').first().id[1:]
    sid="m"+str(int(n)+1)#编号递增，这样计算避免删除后出现错误
    #time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    o=request.POST
    id=request.session["info"]['id']
    models.Wuliao.objects.create(type=o['type'],salegroup=o['salegroup'],saleway=o['saleway']
                                        ,id=sid,calcutype=o['calcutype'],desc=o['desc'])
    print(request.POST)
    return JsonResponse({"status":True})
# 编辑供应商时返回供应商原始数据
def mm_detail(request):
    sid=request.GET.get("uid")
    su=models.Wuliao.objects.filter(id=sid).values("type",'salegroup','saleway',"calcutype","desc").first()
    if not su:
        return JsonResponse({"status":False,"error":"数据不存在"})
    return JsonResponse({"supply":su,"status":True})

# 保存编辑供应商的最新数据
def mm_edit(request):
    id=request.GET.get("uid")
    uid=request.session["info"]['id']
    # 用户ID
    o=request.POST
    #time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    models.Wuliao.objects.filter(id=id).update(type=o['type'],salegroup=o['salegroup'],saleway=o['saleway']
                                        ,calcutype=o['calcutype'],desc=o['desc'])

    return JsonResponse({"status":True})

# 删除供应商
def mm_delete(request):
    id=request.GET.get("uid")
    '''
    s=models.Wuliao.objects.filter(supplyid_id=id).first()
    # 先判断是否有关联关系，如果有则不能删除，目前没有
    if s:
        return JsonResponse({"status":False})
    '''
    models.Wuliao.objects.filter(id=id).delete()
    return JsonResponse({"status":True})