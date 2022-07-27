from django.shortcuts import render
import random
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from supply import models


# 创建询价单
def inquiry_create(request):
    """创建询价单页面"""
    q = {}
    did = request.GET.get("did", "")
    fid = request.GET.get("fid", "")
    mid = request.GET.get("mid", "")
    if did:
        q['demandid__contains'] = did
    if fid:
        q['facid__id__contains'] = fid
    if mid:
        q['maid__id__contains'] = mid
    # 根据条件进行模糊搜索，并返回结果集
    queryset = models.Caigouxuqiu.objects.filter(**q).filter(isdelete=0, status__in=[0, 1]).all()
    result = {
        "queryset": queryset,
        "did": did,
        "fid": fid,
        "mid": mid,
        "title": "询价单管理"
    }
    return render(request, 'inquiry_create.html', result)


def inquiry_createByid(request, did):
    """创建引用请购单的询价单"""
    # queryset=models.Gongyingguanxi.objects.filter().all()
    # 优化显示，这里只显示对应物料的供应商
    demand = models.Caigouxuqiu.objects.filter(demandid=did).first()
    queryset = models.Gongyingguanxi.objects.filter(materialid_id=demand.maid_id).all()
    result = {
        "queryset": queryset,
        "demand": demand
        , "title": "创建询价单"
    }
    return render(request, 'inquiry_createByid.html', result)


@csrf_exempt
def create_qui(request):
    did = request.GET.get("did")
    date = request.POST.get("date")
    if date.strip()=="":
        request.session["notify"] = [dict(id=0, tittle="错误", context="请填写询价有效期", type="error", position="top-center")]
        return JsonResponse({"status": False})
    print(date)
    if (datetime.strptime(date,'%Y-%m-%dT%H:%M') -datetime.now()).days<0:
        request.session["notify"] = [dict(id=0, tittle="错误", context="有效期不应早于当前日期！", type="error", position="top-center")]
        return JsonResponse({"status": False})
    sid = request.POST.get("sid")
    d = models.Caigouxuqiu.objects.filter(demandid=did).first()
    n = 10000000
    if models.Xunjiadan.objects.all().first():
        n = models.Xunjiadan.objects.all().order_by('-inquiryid').first().inquiryid[2:]
    inid = "in" + str(int(n) + 1)  # 编号递增，这样计算避免删除后出现错误
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id = request.session["info"]['id']
    user = models.Yuangong.objects.filter(id=id).first()
    mid=models.Caigouxuqiu.objects.filter(demandid=did).first().maid_id
    r=models.Gongyingguanxi.objects.filter(materialid_id=mid,supplyid_id=sid)
    if not r:
        request.session["notify"] = [dict(id=0, tittle="错误", context="该供应商不提供此物料",type="error", position="top-center")]
        return JsonResponse({"status": False})
    s=models.Xunjiadan.objects.filter(demandid_id=did,supplyid_id=sid,maid_id=mid)
    if s:
        request.session["notify"] = [dict(id=0, tittle="错误", context="已经向该供应商发出询价单",type="error", position="top-center")]
        return JsonResponse({"status": False})
    models.Xunjiadan.objects.create(inquiryid=inid, tcount=d.tcount, validitytime=date,
                                    createtime=time, bussid_id=user.businessid_id, createuserid_id=id,
                                    demandid_id=did, maid_id=d.maid_id, supplyid_id=sid
                                    )
    # 将请购单的状态修改为2，即已完成状态，所有的状态含义在supply的models里面找到对应实体类可以查看
    models.Caigouxuqiu.objects.filter(demandid=did).update(status=2)

    # 这里为了展示，需要同时生成报价单,暂时将报价单号等于询价单号，供应商完报价之后，真正形成报价单
    models.Baojiadan.objects.create(inquiryid_id=inid, tcount=d.tcount, validitytime=date,
                                    bussid_id=user.businessid_id, maid_id=d.maid_id,
                                    supplyid_id=sid, quoteid=inid)
    request.session["notify"] = [dict(id=0, tittle="提示", context="询价单 {} 创建成功！".format(inid), type="success", position="top-center")]
    return JsonResponse({"status": True, "inid": inid})


# 报价单列表
def quote_list(request):
    """进行报价"""
    q = models.Baojiadan.objects.all()

    return render(request, 'quote_list.html', {"queryset": q, "title": "报价单列表"})


# 新增报价单
def quote_add(request):
    """报价完成"""
    inid = request.GET.get("inid")
    quote = request.POST.get("quote")
    n = 10000000
    if models.Baojiadan.objects.all().first():
        n = models.Baojiadan.objects.all().order_by('-quoteid').first().quoteid[2:]
    qid = "qu" + str(int(n) + 1)  # 编号递增，这样计算避免删除后出现错误
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id = request.session["info"]['id']
    # 真正生成供应商的报价单
    models.Baojiadan.objects.filter(inquiryid_id=inid).update(quote=quote,
                                                              quoteid=qid,
                                                              createtime=time,
                                                              createuserid_id=id,
                                                              isreceived=0)
    return JsonResponse({"status": True})


# 评估报价单页面
def quote_evaluate(request):
    q = models.Baojiadan.objects.filter(isdelete=0).all()
    result = {
        "queryset": q
        , "title": "评估报价单"
    }
    return render(request, 'quote_evaluate.html', result)


# 评估相应的报价单
def quote_evaluateByID(request):
    """评估报价单"""
    quid = request.GET.get("quid")
    isrece = request.POST.get("isreceived")
    isall = request.POST.get("isall")
    state_dict={1: "接受",0: "待评估",2: "拒绝"}
    if isall == "1":
        did = models.Baojiadan.objects.filter(quoteid=quid).first().inquiryid.demandid_id
        c = models.Baojiadan.objects.filter(inquiryid__demandid_id=did).update(isreceived=2)
        # 查询出同一个请购单下的其他所有报价单，并且将其拒绝

    # 将本个报价单状态进行修改
    models.Baojiadan.objects.filter(quoteid=quid).update(isreceived=isrece)
    return JsonResponse({"status": True,"state":state_dict[int(isrece)]})


# 采购订单列表
def purchase_list(request):
    q = models.Caigoudan.objects.filter(isdelete=0).all()
    result = {
        "queryset": q
        , "title": "采购订单管理"
    }
    print(q)
    return render(request, 'purchase_list.html', result)


# 创建采购订单
def purchase_create(request):
    q = models.Baojiadan.objects.all()
    result = {
        "queryset": q
        , "title": "创建采购订单"
    }
    return render(request, "purchase_create.html", result)


# 根据报价单创建采购订单
def purchase_createByQuote(request):
    """根据报价单创建采购订单"""
    quid = request.GET.get("quid")
    deadline = request.POST.get("deadline")
    # 修改报价单的状态
    quote = models.Baojiadan.objects.filter(quoteid=quid)
    quote.update(isreceived=3)
    # 创建采购订单
    n = 10000000
    if models.Caigoudan.objects.all().first():
        n = models.Caigoudan.objects.all().order_by('-purchaseid').first().purchaseid[2:]
    puid = "pu" + str(int(n) + 1)  # 编号递增，这样计算避免删除后出现错误
    createtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id = request.session["info"]['id']
    tcount = quote.first().tcount
    fid = quote.first().inquiryid.demandid.facid_id
    mid = quote.first().maid_id
    sid = quote.first().supplyid_id
    price = quote.first().quote
    models.Caigoudan.objects.create(purchaseid=puid, price=price, tcount=tcount,
                                    createtime=createtime, deadline=deadline,
                                    iscomplete=0, createuserid_id=id, facid_id=fid,
                                    maid_id=mid, quoteid_id=quid, supplyid_id=sid)
    # 更新该工厂的在途库存
    w = models.Gongchangkucun.objects.filter(facid_id=fid, maid_id=mid).order_by("-updatetime").first()
    if w:
        models.Gongchangkucun.objects.create(facid_id=fid, maid_id=mid, inventorytemp=w.inventorytemp
                                             , inventoryonroad=tcount + w.inventoryonroad,
                                             inventoryfreeze=w.inventoryfreeze, inventoryunrest=w.inventoryunrest
                                             , updatetime=createtime)
    else:
        models.Gongchangkucun.objects.create(facid_id=fid, maid_id=mid, inventorytemp=0
                                             , inventoryonroad=tcount,
                                             inventoryfreeze=0, inventoryunrest=0
                                             , updatetime=createtime)

    # 为了展示需要这里需要，同时生成暂存单，当进行暂存处理时真正生成暂存单
    models.Zanshoudan.objects.create(temid=puid, tcount=tcount, maid_id=mid,
                                     purchaseid_id=puid, qualitycheckinfo=-1,
                                     quantitycheckinfo=-1)
    return JsonResponse({"status": True, "pid": puid})


def documents(list, puid):
    if puid:
        # 采购单
        p = models.Caigoudan.objects.filter(purchaseid=puid).first()
        # 有这个采购单才接着做
        if p:
            m = {}
            date = p.createtime
            name = "采购单"
            status = p.iscomplete
            id = p.purchaseid
            fid = p.facid_id
            mid = p.maid_id
            sid = p.supplyid_id
            tcount = p.tcount
            price = p.price
            m["date"] = date
            m["status"] = status
            m["id"] = id
            m["fid"] = fid
            m["tcount"] = tcount
            m["price"] = price
            m["mid"] = mid
            m['sid'] = sid
            m["name"] = name
            list.append(m)
            # 请购单
            d = models.Caigouxuqiu.objects.filter(demandid=p.quoteid.inquiryid.demandid_id).first()
            m = {}
            date = d.verifytime
            name = "请购单"
            status = d.status - 1
            id = d.demandid
            price = d.price
            m["date"] = date
            m["status"] = status
            m["id"] = id
            m["fid"] = fid
            m["tcount"] = tcount
            m["price"] = price
            m["mid"] = mid
            m['sid'] = sid
            m["name"] = name
            list.append(m)
            # 询价单
            i = models.Xunjiadan.objects.filter(inquiryid=p.quoteid.inquiryid_id).first()
            m = {}
            date = i.createtime
            name = "询价单"
            id = i.inquiryid
            m["date"] = date
            m["id"] = id
            m["fid"] = fid
            m["tcount"] = tcount
            m["mid"] = mid
            m['bid'] = i.bussid.name
            m["name"] = name
            list.append(m)
            # 报价单
            q = models.Baojiadan.objects.filter(quoteid=p.quoteid_id).first()
            m = {}
            date = q.createtime
            name = "报价单"
            status = q.isreceived - 2
            id = q.quoteid
            quote = q.quote
            m["date"] = date
            m["status"] = status
            m["id"] = id
            m["tcount"] = tcount
            m["quote"] = quote
            m["mid"] = mid
            m['sid'] = sid
            m["name"] = name
            list.append(m)
            # 暂存单
            t = models.Zanshoudan.objects.filter(purchaseid_id=puid).first()
            tid = t.temid
            m = {}
            if t.purchaseid_id == tid:
                m["name"] = "暂收单"
                m["id"] = "暂未创建"
                list.append(m)
            else:
                name = "暂收单"
                status = t.isreceived - 1
                id = t.temid
                moreinfo = t.moreinfo
                date = t.createtime
                m["status"] = status
                m["date"] = date
                m["id"] = id
                m["fid"] = fid
                m["tcount"] = tcount
                m["moreinfo"] = moreinfo
                m["mid"] = mid
                m['sid'] = sid
                m["name"] = name
                list.append(m)
            # 入库单
            r = models.Rukudan.objects.filter(temid_id=tid).first()
            if r:
                if r.id == tid:
                    m["name"] = "入库单"
                    m["id"] = "暂未创建"
                    list.append(m)
                else:
                    m = {}
                    date = r.createtime
                    name = "入库单"
                    id = r.id
                    rcount = r.receivecount
                    moreinfo = r.moreinfo
                    m["date"] = date
                    m["status"] = status
                    m["id"] = id
                    m["fid"] = fid
                    m["tcount"] = tcount
                    m["price"] = p.price
                    m["mid"] = mid
                    m['sid'] = sid
                    m["name"] = name
                    m["rcount"] = rcount
                    m["moreinfo"] = moreinfo
                    list.append(m)

                #发票
                iv=models.Fapiao.objects.filter(purchaseid_id=puid).first()
                if iv:
                    m = {}
                    date = iv.createtime
                    name = "发票"
                    id = iv.invoiceid
                    moreinfo = iv.moreinfo
                    m["date"] = date
                    m["id"] = id
                    m["tcount"] = tcount
                    m["fee"] = iv.fee
                    m["totalmoney"]=iv.totalmoney
                    m["mid"] = mid
                    m['sid'] = sid
                    m["name"] = name
                    m["moreinfo"] = moreinfo
                    list.append(m)

    return


def demand_list(list, did, quid, inid):
    # 请购单
    d = models.Caigouxuqiu.objects.filter(demandid=did).first()
    m = {}
    date = d.verifytime
    name = "请购单"
    status = d.status - 1
    id = d.demandid
    price = d.price
    fid = d.facid_id
    mid = d.maid_id
    tcount = d.tcount
    m["date"] = date
    m["status"] = status
    m["id"] = id
    m["fid"] = fid
    m["tcount"] = tcount
    m["price"] = price
    m["mid"] = mid
    m["name"] = name
    list.append(m)
    # 询价单
    i = models.Xunjiadan.objects.filter(inquiryid=inid).first()
    if i:
        m = {}
        date = i.createtime
        name = "询价单"
        id = i.inquiryid
        m["date"] = date
        m["id"] = id
        m["fid"] = fid
        m["tcount"] = tcount
        m["mid"] = mid
        m['bid'] = i.bussid.name
        m["name"] = name
        list.append(m)
    # 报价单
    q = models.Baojiadan.objects.filter(quoteid=quid).first()
    if q:
        m = {}
        date = q.createtime
        name = "报价单"
        status = q.isreceived - 2
        id = q.quoteid
        quote = q.quote
        sid = q.supplyid_id
        m["date"] = date
        m["status"] = status
        m["id"] = id
        m["tcount"] = tcount
        m["quote"] = quote
        m["mid"] = mid
        m['sid'] = sid
        m["name"] = name
        list.append(m)


def purchase_documents(request):
    """查看单据流"""
    list = []
    puid = ""
    did = ""
    inid = ""
    quid = ""
    teid = ""
    wid = ""
    nid = request.GET.get("id", "")
    tp = nid[:2]
    if tp == "pu":
        puid = nid
    if tp == "de":
        did = nid
    if tp == "in":
        inid = nid
    if tp == "qu":
        quid = nid
    if tp == "te":
        teid = nid
    if tp == "wa":
        wid = nid
    if puid:
        documents(list, puid)
    elif did:
        #     请购单
        d = models.Caigouxuqiu.objects.filter(demandid=did).first()
        if d:
            m = {}
            date = d.verifytime
            name = "请购单"
            status = d.status - 1
            id = d.demandid
            price = d.price
            fid = d.facid_id
            mid = d.maid_id
            tcount = d.tcount
            m["date"] = date
            m["status"] = status
            m["id"] = id
            m["fid"] = fid
            m["tcount"] = tcount
            m["price"] = price
            m["mid"] = mid
            m["name"] = name
            # 报价单
            qu1 = models.Baojiadan.objects.filter(inquiryid__demandid_id=did).filter(isreceived=1).first()
            qu2 = models.Baojiadan.objects.filter(inquiryid__demandid_id=did).filter(isreceived=3).first()
            if not qu1 and not qu2:
                list.append(m)
            if qu1:
                inq = models.Xunjiadan.objects.filter(demandid_id=did).filter()
                inid = inq.first().inquiryid
                quid = models.Baojiadan.objects.filter(inquiryid_id=inid).first().quoteid
                demand_list(list, did, quid, inid)
            if qu2:
                quid = models.Caigoudan.objects.filter(quoteid_id=qu2.quoteid).first().purchaseid
                list = []
                documents(list, quid)

    elif inid:
        inq = models.Xunjiadan.objects.filter(inquiryid=inid).first()
        qu = models.Baojiadan.objects.filter(inquiryid=inq).first()
        if qu:
            if qu.isreceived == 3:
                puid = models.Caigoudan.objects.filter(quoteid=qu).first().purchaseid
                documents(list, puid)
            if qu.isreceived == 1:
                inid = qu.inquiryid_id
                did = qu.inquiryid.demandid_id
                quid = qu.quoteid
                demand_list(list, did, quid, inid)
    elif quid:
        qu = models.Baojiadan.objects.filter(quoteid=quid).first()
        if qu:
            if qu.isreceived == 3:
                puid = models.Caigoudan.objects.filter(quoteid=qu).first().purchaseid
                documents(list, puid)
            if qu.isreceived == 1:
                inid = qu.inquiryid_id
                did = qu.inquiryid.demandid_id
                demand_list(list, did, quid, inid)
    elif teid:
        te = models.Zanshoudan.objects.filter(temid=teid).first()
        if te:
            puid = te.purchaseid_id
            documents(list, puid)
    elif wid:
        wa = models.Rukudan.objects.filter(id=wid).first()
        if wa:
            puid = wa.temid.purchaseid_id
            documents(list, puid)
    document_state=""
    for docu in list:
        document_state+=docu['name'][0]
        try:
            document_state+=str(docu["status"])
        except:
            document_state+="X"
    if document_state=="请1":  #区分无报价/未评估报价
        xjd=models.Xunjiadan.objects.filter(demandid=list[0]["id"]).first().inquiryid
        bjd=models.Baojiadan.objects.filter(inquiryid=xjd).first().isreceived
        print(xjd,bjd)
        if bjd==None:
            document_state+="报0"
        else:
            document_state+="报1"
    if document_state=="采0请1询X报1暂X":  #区分三种质检情况
        zsd=models.Zanshoudan.objects.filter(temid=list[0]["id"]).first()
        document_state+="质{}量{}".format(zsd.qualitycheckinfo,zsd.quantitycheckinfo)
    document_state_dict={"采1请1询X报1暂1入1发X":10,"采1请1询X报1暂0入0":8,
                         "采0请1询X报1入-1入-1":7,"采0请1询X报1暂X质1量-1":6,
                         "采0请1询X报1暂X质-1量1":6,"采0请1询X报1暂X质-1量-1":5,
                         "请1询X报-1":4,"请1报1":3,"请1报0":2,"请0":1,"请-1":-1,"":-2}
    active="background:#5893df"
    style=[""]*11
    progress=document_state_dict[document_state]
    for i in range(progress+1):
        style[i]=active
    textFirst="货物质检"
    textSecond="货物量检"
    if document_state=="采0请1询X报1暂X质-1量1":
        textFirst,textSecond=textSecond,textFirst
    progressShow=(len(list)>0)
    result = {
        "list": list,
        "id": nid,
        "title": "查看单据流",
        "progress":progress,
        "style":style,
        "textFirst":textFirst,
        "textSecond":textSecond,
        "progressShow":progressShow,
    }
    return render(request, 'purchase_documents.html', result)


# 根据id逻辑删除已完成的采购订单，已删除的采购订单不再显示
def purchase_delete(request):
    id = request.GET.get("uid")
    models.Caigoudan.objects.filter(purchaseid=id).update(isdelete=1)
    return JsonResponse({"status": True})


# 根据id逻辑删除已完成或者已拒绝的报单，已删除的报价单不再显示
def quote_delete(request):
    id = request.GET.get("uid")
    models.Baojiadan.objects.filter(quoteid=id).update(isdelete=1)
    return JsonResponse({"status": True})


def to_verify(request, did):
    # 跳转到采购需求管理页面
    return redirect('/inventory/demand/' + did + "/")
