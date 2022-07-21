from django.shortcuts import render
import random
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from supply import models


# 查看库存
def inventory_display(request):
    a=models.Gongchangkucun.objects.values('facid_id','maid_id').distinct()
    q=[]
    for i in a:
        q.append(
            models.Gongchangkucun.objects.filter(facid_id=i['facid_id']
                                                 ,maid_id=i['maid_id']).order_by('-updatetime').first()
        )
        #查询展示每个工厂物料对应的最新的库存信息
    # print(q[0].updatetime)
    return render(request, 'inventory_display.html', {"queryset":q})


def inventory_detail(request,uid):#路径传参要写进函数参数中
    m=models.Gongchangkucun.objects.filter(id=uid).first()
    nowdata=[]
    nowdata.append(m.inventoryonroad)
    nowdata.append(m.inventorytemp)
    nowdata.append(m.inventoryunrest)
    nowdata.append(m.inventoryfreeze)
    fid=m.facid
    mid=m.maid
    qu=models.Gongchangkucun.objects.filter(facid_id=fid,maid_id=mid).order_by("-updatetime")[:6]

    q=qu[::-1]
    datelist=[]
    l1=[]
    l2=[]
    l3=[]
    l4=[]
    for i in q:
        datelist.append(str(i.updatetime.strftime("%Y-%m-%d %H:%M:%S")))
        l1.append(i.inventoryonroad)
        l2.append(i.inventorytemp)
        l3.append(i.inventoryunrest)
        l4.append(i.inventoryfreeze)
    result={
        "history":q,"now":m,"nowdata":nowdata,
        "datelist":datelist,
        "l1":l1,
        "l2":l2,
        "l3":l3,
        "l4":l4

    }
    print(result)
    return render(request, 'inventory_detail.html', result)

# 采购需求列表
def inventory_demand(request):
    """采购需求管理（请购单）"""
    material=models.Wuliao.objects.filter().all()
    factory=models.Gongchang.objects.filter().all()
    caigou=models.Caigouxuqiu.objects.filter().all()
    result={
        "material":material,
        "factory":factory,
        "caigou":caigou
    }
    return render(request, 'inventory_demand.html', result)
# 添加采购需求
def demand_add(request):
    """添加采购需求"""
    n=10000000
    if models.Caigouxuqiu.objects.all().first():
        n=models.Caigouxuqiu.objects.all().order_by('-demandid').first().demandid[2:]
    did="de"+str(int(n)+1)#编号递增，这样计算避免删除后出现错误
    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    r=request.POST
    id=request.session["info"]['id']
    models.Caigouxuqiu.objects.create(demandid=did,price=r["price"],tcount=r['tcount']
                                      ,status=0,createtime=time,createuserid_id=id,
                                      facid_id=r['facid_id'],maid_id=r['maid_id'])
    return JsonResponse({"status":True})

@csrf_exempt
def demand_verify(request):
    """审核采购需求"""
    did=request.POST.get("did")
    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id=request.session["info"]['id']
    models.Caigouxuqiu.objects.filter(demandid=did).update(verifytime=time,
                                                           verifyuserid_id=id,status=1)
    return JsonResponse({"status":True})

# 进行暂存检查
def inventory_temp(request):

    """暂存检查"""
    # 首先查到所有待暂存的采购订单

    q=models.Zanshoudan.objects.all()

    return render(request,'temp_list.html',{"queryset":q})

def ischeck(request,pid):
    """判断是否检查完成"""
    z=models.Zanshoudan.objects.filter(purchaseid_id=pid)
    flag=False
    # 质检量检均完成后，才算完成
    if z.first().quantitycheckinfo!=-1 and z.first().qualitycheckinfo!=-1:
        n=10000000
        createtime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if models.Zanshoudan.objects.all().first():
            n=models.Zanshoudan.objects.all().order_by('-temid').first().temid[2:]
        zid="te"+str(int(n)+1)#编号递增，这样计算避免删除后出现错误
        z.update(temid=zid,isreceived=0,createtime=createtime)
        #更新库存信息
        fid=z.first().purchaseid.facid_id
        mid=z.first().maid_id
        tcount=z.first().tcount
        w=models.Gongchangkucun.objects.filter(facid_id=fid,maid_id=mid).order_by("-updatetime").first()
        if w:
            models.Gongchangkucun.objects.create(facid_id=fid,maid_id=mid,inventorytemp=tcount+w.inventorytemp
                                                 ,inventoryonroad=w.inventoryonroad-tcount,
                                                 inventoryfreeze=w.inventoryfreeze,inventoryunrest=w.inventoryunrest
                                                 ,updatetime=createtime)
        else:
            models.Gongchangkucun.objects.create(facid_id=fid,maid_id=mid,inventorytemp=tcount
                                                 ,inventoryonroad=0,
                                                 inventoryfreeze=0,inventoryunrest=0
                                                 ,updatetime=createtime)
        # 暂时生成入库单,单号等于暂存单号
        id=request.session["info"]['id']
        models.Rukudan.objects.create(id=zid,purcount=tcount,createusersid_id=id,facid_id=fid,
                                      maid_id=mid,temid_id=zid)
        flag=True
    return flag

def quality_check(request):
    """质检"""

    puid=request.GET.get("puid")
    q=request.POST.get("check")
    info=request.POST.get("moreinfo")
    z=models.Zanshoudan.objects.filter(purchaseid_id=puid)
    if z.first().moreinfo:
        info=info+z.first().moreinfo
    z.update(qualitycheckinfo=q,moreinfo=info)

    ischeck(request,puid)

    return JsonResponse({"status":True})


def quantity_check(request):
    """量检"""
    puid=request.GET.get("puid")
    q=request.POST.get("check")
    info=request.POST.get("moreinfo")
    z=models.Zanshoudan.objects.filter(purchaseid_id=puid)
    if z.first().moreinfo:
        info=info+z.first().moreinfo
    z.update(quantitycheckinfo=q,moreinfo=info)
    ischeck(request,puid)
    return JsonResponse({"status":True})

# 展示入库单
def inventory_receive(request):
    """入库管理"""
    q=models.Rukudan.objects.all()

    return render(request, 'inventory_receive.html', {"queryset":q})

# 添加入库
def receive_add(request):
    """添加入库"""
    tid=request.GET.get("tid")
    t=models.Rukudan.objects.filter(temid_id=tid)
    fid=t.first().facid_id
    mid=t.first().maid_id
    pid=t.first().temid.purchaseid_id
    receivecount=request.POST.get("receivecount")
    pcount=t.first().purcount
    moreinfo=request.POST.get("moreinfo")
    id=request.session["info"]['id']
    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 生成入库单
    n=10000000
    if models.Rukudan.objects.all().first():
        n=models.Rukudan.objects.all().order_by('-id').first().id[2:]
    wid="wa"+str(int(n)+1)#编号递增，这样计算避免删除后出现错误
    t.update(id=wid,createtime=time,receivecount=receivecount,
             moreinfo=moreinfo,createusersid_id=id)

    # 库存状态更新
    w=models.Gongchangkucun.objects.filter(facid_id=fid,maid_id=mid).order_by("-updatetime").first()
    if w:
        models.Gongchangkucun.objects.create(facid_id=fid,maid_id=mid,inventorytemp=w.inventorytemp-pcount
                                             ,inventoryonroad=w.inventoryonroad,
                                             inventoryfreeze=w.inventoryfreeze,
                                             inventoryunrest=w.inventoryunrest+float(receivecount)
                                             ,updatetime=time)
    else:
        models.Gongchangkucun.objects.create(facid_id=fid,maid_id=mid,inventorytemp=0
                                             ,inventoryonroad=0,
                                             inventoryfreeze=0,inventoryunrest=receivecount
                                             ,updatetime=time)

    # 暂存单，采购单收货状态更新

    models.Zanshoudan.objects.filter(temid=tid).update(isreceived=1)
    models.Caigoudan.objects.filter(purchaseid=pid).update(iscomplete=1)



    return JsonResponse({"status":True})


# 展示发票
def inventory_invoice(request):
    q=models.Fapiao.objects.all()

    return render(request, 'inventory_invoice.html', {"queryset":q})

# 添加发票
def invoice_add(request):
    tid=request.GET.get("tid")
    t=models.Rukudan.objects.filter(temid_id=tid)
    pid=t.first().temid.purchaseid_id
    sid=t.first().temid.purchaseid.supplyid_id
    print(sid)
    fee=request.POST.get("receivecount")
    pcount=t.first().purcount
    price=t.first().temid.purchaseid.price
    id=request.session["info"]['id']
    bid=t.first().temid.purchaseid.quoteid.bussid
    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    totalcount=pcount
    money=float(totalcount)*float(price)
    totalmoney=money+float(fee)
    moreinfo=request.POST.get("moreinfo")

    n=10000000
    if models.Fapiao.objects.all().first():
        n=models.Fapiao.objects.all().order_by('-invoiceid').first().invoiceid[2:]
    ivid="iv"+str(int(n)+1)#编号递增，
    models.Fapiao.objects.create(invoiceid=ivid,totalmoney=totalmoney,totalcount=totalcount
                                 ,fee=fee,createtime=time,  supplyid_id=sid,
                                 createuserid_id=id,purchaseid_id=pid,money=money,moreinfo=moreinfo
                                 )
    #更新暂收单状态
    models.Zanshoudan.objects.filter(temid=tid).update(isreceived=2)
    return JsonResponse({"status":True,"id":ivid})


def invoice_display(request,ivid):
    """展示发票详情"""
    invoice=models.Fapiao.objects.filter(invoiceid=ivid).first()
    return render(request,'invoice_display.html',{"invoice":invoice})