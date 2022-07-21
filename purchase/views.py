from django.shortcuts import render
import random
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from supply import models



def inquiry_create(request):
    """创建询价单页面"""
    q={}
    did=request.GET.get("did","")
    fid=request.GET.get("fid","")
    mid=request.GET.get("mid","")
    if did:
        q['demandid__contains']=did
    if fid:
        q['facid__id__contains']=fid
    if mid:
        q['maid__id__contains']=mid

    queryset=models.Caigouxuqiu.objects.filter(**q).all()
    result={
        "queryset":queryset,
        "did":did,
        "fid":fid,
        "mid":mid
    }
    return render(request, 'inquiry_create.html', result)

def inquiry_createByid(request,did):
    """创建引用请购单的询价单"""
    queryset=models.Gongyingguanxi.objects.filter().all()
    demand=models.Caigouxuqiu.objects.filter(demandid=did).first()
    print(demand)
    result={
        "queryset":queryset,
        "demand":demand
    }
    return render(request, 'inquiry_createByid.html', result)

@csrf_exempt
def create_qui(request):
    did=request.GET.get("did")
    date=request.POST.get("date")
    sid=request.POST.get("sid")
    d=models.Caigouxuqiu.objects.filter(demandid=did).first()
    n=10000000
    if models.Xunjiadan.objects.all().first():
        n=models.Xunjiadan.objects.all().order_by('-inquiryid').first().inquiryid[2:]
    inid="in"+str(int(n)+1)#编号递增，这样计算避免删除后出现错误
    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id=request.session["info"]['id']
    user=models.Yuangong.objects.filter(id=id).first()
    models.Xunjiadan.objects.create(inquiryid=inid,tcount=d.tcount,validitytime=date,
                                    createtime=time,bussid_id=user.businessid_id,createuserid_id=id,
                                    demandid_id=did,maid_id=d.maid_id,supplyid_id=sid
                                    )
    # 将请购单的状态修改为2
    models.Caigouxuqiu.objects.filter(demandid=did).update(status=2)


    #需要同时生成报价单,暂时将报价单号等于询价单号，供应商完报价之后，真正形成报价单
    models.Baojiadan.objects.create(inquiryid_id=inid,tcount=d.tcount,validitytime=date,
                                    bussid_id=user.businessid_id,maid_id=d.maid_id,
                                    supplyid_id=sid,quoteid=inid)
    return JsonResponse({"status":True,"inid":inid})


def quote_list(request):
    """进行报价"""
    q=models.Baojiadan.objects.all()

    return render(request, 'quote_list.html', {"queryset":q})


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


def quote_evaluate(request):

    q=models.Baojiadan.objects.all()
    result={
        "queryset":q
    }
    return render(request, 'quote_evaluate.html', result)


def quote_evaluateByID(request):
    """评估报价单"""
    quid=request.GET.get("quid")
    isrece=request.POST.get("isreceived")
    isall=request.POST.get("isall")
    if isall=="1":
        did=models.Baojiadan.objects.filter(quoteid=quid).first().inquiryid.demandid_id
        c=models.Baojiadan.objects.filter(inquiryid__demandid_id=did).update(isreceived=2)
        #查询出同一个请购单下的其他所有报价单，并且将其拒绝

    #将本个报价单状态进行修改
    models.Baojiadan.objects.filter(quoteid=quid).update(isreceived=isrece)
    return JsonResponse({"status":True})


def purchase_list(request):

    q=models.Caigoudan.objects.all()
    result={
        "queryset":q
    }
    print(q)
    return render(request, 'purchase_list.html', result)


def purchase_create(request):

    q=models.Baojiadan.objects.all()
    result={
        "queryset":q
    }
    return render(request, "purchase_create.html", result)


def purchase_createByQuote(request):
    """根据报价单创建采购订单"""
    quid=request.GET.get("quid")
    deadline=request.POST.get("deadline")
    # 修改报价单的状态
    quote=models.Baojiadan.objects.filter(quoteid=quid)
    quote.update(isreceived=3)
    # 创建采购订单
    n=10000000
    if models.Caigoudan.objects.all().first():
        n=models.Caigoudan.objects.all().order_by('-purchaseid').first().purchaseid[2:]
    puid="pu"+str(int(n)+1)#编号递增，这样计算避免删除后出现错误
    createtime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id=request.session["info"]['id']
    tcount=quote.first().tcount
    fid=quote.first().inquiryid.demandid.facid_id
    mid=quote.first().maid_id
    sid=quote.first().supplyid_id
    price=quote.first().quote
    models.Caigoudan.objects.create(purchaseid=puid,price=price,tcount=tcount,
                                    createtime=createtime,deadline=deadline,
                                    iscomplete=0,createuserid_id=id,facid_id=fid,
                                    maid_id=mid,quoteid_id=quid,supplyid_id=sid)
    # 更新该工厂的在途库存
    w=models.Gongchangkucun.objects.filter(facid_id=fid,maid_id=mid).order_by("-updatetime").first()
    if  w:
        models.Gongchangkucun.objects.create(facid_id=fid,maid_id=mid,inventorytemp=w.inventorytemp
                                             ,inventoryonroad=tcount+w.inventoryonroad,
                                             inventoryfreeze=w.inventoryfreeze,inventoryunrest=w.inventoryunrest
                                             ,updatetime=createtime)
    else:
        models.Gongchangkucun.objects.create(facid_id=fid,maid_id=mid,inventorytemp=0
                                             ,inventoryonroad=tcount,
                                             inventoryfreeze=0,inventoryunrest=0
                                             ,updatetime=createtime)

    #需要同时生成暂存单，当进行暂存处理时真正生成暂存单
    models.Zanshoudan.objects.create(temid=puid,tcount=tcount,maid_id=mid,
                                     purchaseid_id=puid,qualitycheckinfo=-1,
                                     quantitycheckinfo=-1)
    return JsonResponse({"status":True,"pid":puid})


def purchase_documents(request):
    """查看单据流"""
    # 目前暂时只支持根据采购单号，后续再改
    list=[]
    q={}
    # did=request.GET.get("did","")
    puid=request.GET.get("puid","")
    # quid=request.GET.get("quid","")
    # if did:
    #     q['demandid__contains']=did
    if puid:
        # 采购单
        p=models.Caigoudan.objects.filter(purchaseid=puid).first()
        if p:
            m={}
            date=p.createtime
            name="采购单"
            status=p.iscomplete
            id=p.purchaseid
            fid=p.facid_id
            mid=p.maid_id
            sid=p.supplyid_id
            tcount=p.tcount
            price=p.price
            m["date"]=date
            m["status"]=status
            m["id"]=id
            m["fid"]=fid
            m["tcount"]=tcount
            m["price"]=price
            m["mid"]=mid
            m['sid']=sid
            m["name"]=name
            list.append(m)
            # 请购单
            d=models.Caigouxuqiu.objects.filter(demandid=p.quoteid.inquiryid.demandid_id).first()
            m={}
            date=d.verifytime
            name="请购单"
            status=d.status-1
            id=d.demandid
            price=d.price
            m["date"]=date
            m["status"]=status
            m["id"]=id
            m["fid"]=fid
            m["tcount"]=tcount
            m["price"]=price
            m["mid"]=mid
            m['sid']=sid
            m["name"]=name
            list.append(m)
            # 询价单
            i=models.Xunjiadan.objects.filter(inquiryid=p.quoteid.inquiryid_id).first()
            m={}
            date=i.createtime
            name="询价单"
            id=i.inquiryid
            m["date"]=date
            m["id"]=id
            m["fid"]=fid
            m["tcount"]=tcount
            m["mid"]=mid
            m['bid']=i.bussid.name
            m["name"]=name
            list.append(m)
            # 报价单
            q=models.Baojiadan.objects.filter(quoteid=p.quoteid_id).first()
            m={}
            date=q.createtime
            name="报价单"
            status=q.isreceived-2
            id=q.quoteid
            quote=q.quote
            m["date"]=date
            m["status"]=status
            m["id"]=id
            m["tcount"]=tcount
            m["quote"]=quote
            m["mid"]=mid
            m['sid']=sid
            m["name"]=name
            list.append(m)
            # 暂存单
            t=models.Zanshoudan.objects.filter(purchaseid_id=puid).first()
            tid=t.temid
            m={}
            if t.purchaseid_id==tid:
                m["name"]="暂收单"
                m["id"]="暂未创建"
                list.append(m)
            else:
                name="暂收单"
                status=t.isreceived-1
                id=t.temid
                moreinfo=t.moreinfo
                date=t.createtime
                m["status"]=status
                m["date"]=date
                m["id"]=id
                m["fid"]=fid
                m["tcount"]=tcount
                m["moreinfo"]=moreinfo
                m["mid"]=mid
                m['sid']=sid
                m["name"]=name
                list.append(m)
            # 入库单
            r=models.Rukudan.objects.filter(temid_id=tid).first()
            if r.id==tid:
                m["name"]="入库单"
                m["id"]="暂未创建"
                list.append(m)
            else:
                m={}
                date=r.createtime
                name="入库单"
                id=r.id
                rcount=r.receivecount
                moreinfo=r.moreinfo
                m["date"]=date
                m["status"]=status
                m["id"]=id
                m["fid"]=fid
                m["tcount"]=tcount
                m["price"]=p.price
                m["mid"]=mid
                m['sid']=sid
                m["name"]=name
                m["rcount"]=rcount
                m["moreinfo"]=moreinfo
                list.append(m)

    # if quid:
    #     q['maid__id__contains']=quid
    result={
        "list":list,
        # "did":did,
        # "quid":quid,
        "puid":puid
    }

    return render(request, 'purchase_documents.html', result)