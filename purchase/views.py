from django.shortcuts import render
import random
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from supply import models
from supply.views import set_copy_message
import re


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
    if (datetime.strptime(date,'%Y-%m-%dT%H:%M') -datetime.now()).days<0:
        request.session["notify"] = [dict(id=0, tittle="错误", context="有效期不应早于当前日期！", type="error", position="top-center")]
        return JsonResponse({"status": False})
    sid = request.POST.get("sid")
    d = models.Caigouxuqiu.objects.filter(demandid=did).first()
    n = 10000000
    if models.Xunjiadan.objects.all().first():
        n = models.Xunjiadan.objects.all().order_by('-inquiryid').first().inquiryid[2:]
    inid = "in" + str(int(n) + 1)  # 编号递增，这样计算避免删除后出现错误
    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id = request.session["info"]['id']
    user = models.Yuangong.objects.filter(id=id).first()
    mid=models.Caigouxuqiu.objects.filter(demandid=did).first().maid_id
    r=models.Gongyingguanxi.objects.filter(materialid_id=mid,supplyid_id=sid)
    if not r:
        request.session["notify"] = [dict(id=0, tittle="错误", context="该供应商不提供此物料",type="error", position="top-center")]
        return JsonResponse({"status": False})
    s=models.Xunjiadan.objects.filter(demandid_id=did,supplyid_id=sid)
    if s:
        request.session["notify"] = [dict(id=0, tittle="错误", context="已经向该供应商发出询价单",type="error", position="top-center")]
        return JsonResponse({"status": False})
    #系统自动发信
    qgd=models.Caigouxuqiu.objects.filter(demandid=did).first()
    gys=models.Gongyingshang.objects.filter(id=sid).first()
    me=models.Yuangong.objects.filter(id=request.session["info"]["id"]).first()
    wl=qgd.maid
    message=[]
    notify=[]
    notify.append(dict(id=0, tittle="提示", context="询价单 {} 创建成功！".format(inid),
                       type="success", position="top-center"))
    message.append("【反馈消息】询价反馈信息")
    message.append("向供应商【{}】<br/>({})发送询价单<br/>请购单号:{}<br/>询价单号:{}"
                   .format(gys.name, gys.id, set_copy_message(qgd.demandid), set_copy_message(inid)))
    message.append("询价物料:{}({})<br/>数量:{} 预期报价:{}元/{}<br/>询价有效期:{}"
                   .format(wl.desc, wl.id, qgd.tcount, qgd.price, wl.calcutype,
                           datetime.strptime(date, '%Y-%m-%dT%H:%M').strftime("%Y{}%m{}%d{} %H:%M").format("年", "月",
                                                                                                           "日")))

    if me.office!="0":
        pur_jl = models.Yuangong.objects.filter(businessid_id=me.businessid_id, office="5").first()
        inv_yg = models.Yuangong.objects.filter(businessid_id=me.businessid_id, office="1").first()
        for m in message:
            models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=pur_jl.id, time=datetime.now(), context=m, read=0)
        message[0]="【系统消息】创建询价单"
        for m in message:
            models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=inv_yg.id, time=datetime.now(), context=m, read=0)
        models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=inv_yg.id, time=datetime.now(),
                                     context='请于询价有效期内获取供应商报价反馈<br/>并填入系统<a class="chat_link" href="/supply/quote/list/">>></a>',
                                     read=0)
        notify.append(dict(id=1, tittle="系统消息", context="已向 【{}】{} 发送反馈信息"
                           .format(pur_jl.get_office_display(), pur_jl.username), type="info", position="top-center"))
        notify.append(dict(id=2, tittle="系统消息", context="已提示 【{}】{} 询价并维护供应商报价单"
                           .format(inv_yg.get_office_display(), inv_yg.username), type="info", position="top-center"))
    else:  #管理员情况
        message[0]="【系统消息】操作历史记录"
        fromid = models.Yuangong.objects.filter(businessid=me.businessid, office="7").first()
        for m in message:
            models.Xiaoxi.objects.create(fromId_id=fromid.id, toId_id=me.id, time=datetime.now(), context=m, read=0)
        models.Xiaoxi.objects.create(fromId_id=fromid.id, toId_id=me.id, time=datetime.now(),
                                     context='于询价有效期内获取供应商报价反馈<br/>并填入系统<a class="chat_link" href="/supply/quote/list/">>></a>',
                                     read=0)
        notify.append(dict(id=1, tittle="系统消息", context="操作历史已更新", type="info", position="top-center"))
    if request.session['produceActive']:
        message = []
        message.append("【系统消息】操作历史记录")
        next = me
        if me.office!="0":
            next = models.Yuangong.objects.filter(businessid=me.businessid, office="1").first()
        message.append("【{}】{}<br/>向供应商【{}】<br/>({})发送询价单<br/>请购单号:{}<br/>询价单号:{}"
                       .format(me.get_office_display(), me.username, gys.name, gys.id, set_copy_message(qgd.demandid), set_copy_message(inid)))
        message.append("询价物料:{}({})<br/>数量:{} 预期报价:{}元/{}<br/>询价有效期:{}"
                       .format(wl.desc, wl.id, qgd.tcount, qgd.price, wl.calcutype,
                               datetime.strptime(date, '%Y-%m-%dT%H:%M').strftime("%Y{}%m{}%d{} %H:%M").format("年", "月",
                                                                                                               "日")))
        message.append('下一步操作人:【{}】{}<br/>'
                       '下一步骤:维护供应商报价单<a class="chat_link" href="/supply/quote/list/">>></a><br/>'
                       .format(next.get_office_display(), next.username))
        fromid = models.Yuangong.objects.filter(businessid=me.businessid, office="7").first()
        toid = models.Yuangong.objects.filter(businessid=me.businessid, office="6").first()
        for m in message:
            models.Xiaoxi.objects.create(fromId_id=fromid.id, toId_id=toid.id, time=datetime.now(), context=m, read=0)
        notify.append(dict(id=len(notify), tittle="系统消息",
                           context="操作历史已抄送至 【{}】{}".format(toid.get_office_display(), toid.username),
                           type="info", position="top-center"))
    request.session["notify"] = notify

    models.Xunjiadan.objects.create(inquiryid=inid, validitytime=date,
                                    createtime=time,  createuserid_id=id,
                                    demandid_id=did, supplyid_id=sid)
    # 将请购单的状态修改为2，即已完成状态，所有的状态含义在supply的models里面找到对应实体类可以查看
    models.Caigouxuqiu.objects.filter(demandid=did).update(status=2)

    # 这里为了展示，需要同时生成报价单,暂时将报价单号等于询价单号，供应商完报价之后，真正形成报价单
    models.Baojiadan.objects.create(inquiryid_id=inid, validitytime=date,
                                    supplyid_id=sid, quoteid=inid)
    return JsonResponse({"status": True, "inid": inid})


# 评估报价单页面
def quote_evaluate(request):
    m=models.Baojiadan.objects.filter(isreceived=0).filter(validitytime__gte=datetime.now())
    q = models.Baojiadan.objects.filter(isdelete=0).filter(isreceived__gte=1)
    # 返回有效期内的待评估报价单和已完成被拒绝的报价单
    result = {
        "queryset": q.union(m)
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
    bjd = models.Baojiadan.objects.filter(quoteid=quid).first()
    did = bjd.inquiryid.demandid_id
    c = models.Baojiadan.objects.filter(inquiryid__demandid_id=did).exclude(quoteid=quid)
    if isall == "1":
        c.update(isreceived=2)
        # 查询出同一个请购单下的其他所有报价单，并且将其拒绝
    # 将本个报价单状态进行修改
    bjd = models.Baojiadan.objects.filter(quoteid=quid)
    bjd.update(isreceived=isrece)
    bjd = bjd.first()
    notify=[]
    notify.append(dict(id=0, tittle="提示", context="报价单 {} 评估成功！".format(quid), type="success", position="top-center"))
    if isrece=="1":
        # 系统自动发信
        me = models.Yuangong.objects.filter(id=request.session["info"]["id"]).first()
        buss = me.businessid
        inv_yg = models.Yuangong.objects.filter(businessid=buss, isactive=1, office="1").first()
        pur_yg = models.Yuangong.objects.filter(businessid=buss, isactive=1, office="2").first()
        qgd = models.Caigouxuqiu.objects.filter(demandid=did).first()
        wl = qgd.maid
        message = []
        message.append("【反馈消息】报价评估反馈信息")
        message.append("询价单 {}<br/>询价物料:{}({})<br/>询价数量:{}  预期报价:{}元/{}"
                       .format(set_copy_message(bjd.inquiryid_id), wl.desc, wl.id, qgd.tcount, qgd.price, wl.calcutype))
        situation = "报价评估情况:"
        for bj in c:
            situation += '<br/>{}{}{}元/{} <a class="chat_status_{}">{}</a>'\
                .format(bj.supplyid.name, set_copy_message(bj.supplyid_id), bj.quote, wl.calcutype,bj.isreceived,bj.get_isreceived_display())
        situation += '<hr>{}{}{}元/{} <a class="chat_status_{}">{}</a>'\
            .format(bjd.supplyid.name, set_copy_message(bjd.supplyid_id), bjd.quote,wl.calcutype,bjd.isreceived, bjd.get_isreceived_display())
        situation+='<br/>接受报价单号{}'.format(set_copy_message(bjd.quoteid))
        message.append(situation)
        if me.office!="0":
            for m in message:
                models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=inv_yg.id, time=datetime.now(), context=m, read=0)
            message[0]="【系统消息】收到新报价评估"
            for m in message:
                models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=pur_yg.id, time=datetime.now(), context=m, read=0)
            models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=pur_yg.id, time=datetime.now(),
                                         context='请在报价有效期({}) 内创建采购订单<a class="chat_link" href="/purchase/list/">>></a>'
                                         .format(
                                             bjd.inquiryid.validitytime.strftime("%Y{}%m{}%d{} %H:%M").format("年", "月",
                                                                                                              "日")),
                                         read=0)
            notify.append(dict(id=1, context="向 【{}】{} 发信反馈报价评估情况".format(inv_yg.get_office_display(), inv_yg.username)
                               , tittle="系统消息", type="info", position="top-center"))
            notify.append(
                dict(id=2, context="向 【{}】{} 发信报价评估情况，并提示创建采购订单".format(pur_yg.get_office_display(), pur_yg.username)
                     , tittle="系统消息", type="info", position="top-center"))
        else:
            message[0]="【系统消息】操作历史记录"
            next=me
            fromid = models.Yuangong.objects.filter(businessid=me.businessid, office="7").first()
            for m in message:
                models.Xiaoxi.objects.create(fromId_id=fromid.id, toId_id=me.id, time=datetime.now(), context=m, read=0)
            models.Xiaoxi.objects.create(fromId_id=fromid.id, toId_id=me.id, time=datetime.now(),context=
            '请在报价有效期({}) 内创建采购订单<a class="chat_link" href="/purchase/list/">>></a>'
                                         .format(bjd.inquiryid.validitytime.strftime("%Y{}%m{}%d{} %H:%M").format("年", "月", "日")))
            notify=notify[:1]
            notify.append(dict(id=1, tittle="系统消息", context="操作历史已更新", type="info", position="top-center"))
        if request.session['produceActive']:
            message[1] = '【{}】{}<br/>'.format(me.get_office_display(), me.username) + message[1]
            next = me
            if me.office!="0":
                next = models.Yuangong.objects.filter(businessid=me.businessid, office="4").first()
            message.append('下一步操作人:【{}】{}<br/>'
                           '下一步骤:引用报价单，创建采购订单<a class="chat_link" href="/purchase/list/">>></a><br/>'
                           .format(next.get_office_display(), next.username))
            fromid = models.Yuangong.objects.filter(businessid=me.businessid, office="7").first()
            toid = models.Yuangong.objects.filter(businessid=me.businessid, office="6").first()
            for m in message:
                models.Xiaoxi.objects.create(fromId_id=fromid.id, toId_id=toid.id, time=datetime.now(), context=m,
                                             read=0)
            notify.append(dict(id=len(notify), tittle="系统消息",
                               context="操作历史已抄送至 【{}】{}".format(toid.get_office_display(), toid.username),
                               type="info", position="top-center"))
    request.session["notify"] = notify
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
    q = models.Baojiadan.objects.filter(validitytime__gte=datetime.now())
    # 只返回有效期内的报价单
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
    if not deadline:
        return JsonResponse({"status": False, "error": "请填写截止日期"})
    if (datetime.strptime(deadline,"%Y-%m-%d")-datetime.now()).days<0:
        return JsonResponse({"status": False, "error": "截止日期不能早于今天"})

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
    ff = quote.first().inquiryid.demandid.facid
    fid=ff.id
    tcount=quote.first().inquiryid.demandid.tcount
    mid = quote.first().inquiryid.demandid.maid_id
    models.Caigoudan.objects.create(purchaseid=puid,
                                    createtime=createtime, deadline=deadline,
                                    iscomplete=0, createuserid_id=id,
                                   quoteid_id=quid)
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
    models.Zanshoudan.objects.create(temid=puid,
                                     purchaseid_id=puid, qualitycheckinfo=-1,
                                     quantitycheckinfo=-1)
    # 系统自动发信
    me = models.Yuangong.objects.filter(id=request.session["info"]["id"]).first()
    buss = me.businessid
    inv_yg = models.Yuangong.objects.filter(businessid=buss,isactive=1,office="3").first()
    pur_jl = models.Yuangong.objects.filter(businessid=buss,isactive=1,office="4").first()
    message = []
    notify = []
    message.append("【系统消息】新采购订单")
    notify.append(
        dict(id=0, tittle="提示", context="采购订单 {} 创建成功！".format(puid), type="success", position="top-center"))
    message.append("引用报价单 {}<br/>创建采购订单 {}<br/>发往工厂:{}({})<br/>收货截至期限：{}"
                   .format(set_copy_message(quid),set_copy_message(puid),ff.type,ff.address,datetime.strptime(deadline,"%Y-%m-%d").strftime("%Y{}%m{}%d{}").format("年","月","日")))
    message.append('请在追踪供应商送货进度<br/>在截止期限前将货物暂存<a class="chat_link" href="/inventory/temp/">>></a>')
    if me.office!="0" and not me.office=="4":
        for m in message:
            models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=inv_yg.id, time=datetime.now(), context=m, read=0)
        message[0]="【反馈消息】采购订单反馈信息"
        message=message[:-1]
        for m in message:
            models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=pur_jl.id, time=datetime.now(), context=m, read=0)
        notify.append(dict(id=1, context="向 【{}】{} 发信反馈采购订单情况".format(pur_jl.get_office_display(), pur_jl.username)
                           , tittle="系统消息", type="info", position="top-center"))
        notify.append(dict(id=2, context="向 【{}】{} 发信并提追踪送货进度".format(inv_yg.get_office_display(), inv_yg.username)
                           , tittle="系统消息", type="info", position="top-center"))
    else:
        message[0] = "【系统消息】操作历史记录"
        next = me
        fromid = models.Yuangong.objects.filter(businessid=me.businessid, office="7").first()
        for m in message:
            models.Xiaoxi.objects.create(fromId_id=fromid.id, toId_id=me.id, time=datetime.now(), context=m, read=0)
        notify = notify[:1]
        notify.append(dict(id=1, tittle="系统消息", context="操作历史已更新", type="info", position="top-center"))
    if request.session['produceActive']:
        message[0] = "【系统消息】创建采购订单"
        message[1] = '【{}】{}<br/>'.format(me.get_office_display(), me.username) + message[1]
        next = me
        if me.office!="0":
            next = models.Yuangong.objects.filter(businessid=me.businessid, office="3").first()
        message.append('下一步操作人:【{}】{}<br/>'
                       '下一步骤:追踪供货进度，维护暂存单<a class="chat_link" href="/inventory/temp/">>></a><br/>'
                       .format(next.get_office_display(), next.username))
        fromid = models.Yuangong.objects.filter(businessid=me.businessid, office="7").first()
        toid = models.Yuangong.objects.filter(businessid=me.businessid, office="6").first()
        for m in message:
            models.Xiaoxi.objects.create(fromId_id=fromid.id, toId_id=toid.id, time=datetime.now(), context=m,
                                         read=0)
        notify.append(dict(id=len(notify), tittle="系统消息",
                           context="操作历史已抄送至 【{}】{}".format(toid.get_office_display(), toid.username),
                           type="info", position="top-center"))
    request.session["notify"] = notify
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
            fid = p.quoteid.inquiryid.demandid.facid_id
            mid = p.quoteid.inquiryid.demandid.maid_id
            sid = p.quoteid.inquiryid.supplyid_id
            tcount = p.quoteid.inquiryid.demandid.tcount
            price = p.quoteid.quote
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
            m['bid'] = i.demandid.createuserid.businessid_id
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
            if t:
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
                        m["price"] = p.quoteid.quote
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
                    m["totalmoney"]=iv.money+iv.fee
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
        m['bid'] = i.createuserid.businessid.name
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
    ivid=""
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
    if tp == "iv":
        ivid=nid
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
            if qu.isreceived == 2:
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
            if qu.isreceived == 2:
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
    elif ivid:
        iv=models.Fapiao.objects.filter(invoiceid=ivid).first()
        if iv:
            puid=iv.purchaseid_id
            documents(list,puid)
    document_state=""
    for docu in list:
        document_state+=docu['name'][0]
        try:
            document_state+=str(docu["status"])
        except:
            document_state+="X"
    if document_state=="请1":  #区分无报价/未评估报价
        xjd=models.Xunjiadan.objects.filter(demandid=list[0]["id"]).first().inquiryid
        bjd=models.Baojiadan.objects.filter(inquiryid=xjd).first()
        print(xjd,bjd)
        if bjd==None:
            document_state+="报0"
        else:
            bjds=models.Baojiadan.objects.filter(inquiryid=xjd).all()
            flag=False
            for i in bjds:
                if not i.isreceived==2:
                    flag=True
                    break
            if flag:
                document_state+="报1"
            else:
                document_state+="报-1"
    if document_state == "采0请1询X报1暂X":  # 区分三种质检情况
        zsd = models.Zanshoudan.objects.filter(temid=list[0]["id"]).first()
        document_state += "质{}量{}".format(zsd.qualitycheckinfo, zsd.quantitycheckinfo)
    if document_state=="采-1请1询X报1暂-2":  #区分三种质检情况
        print(list)
        zsd=models.Zanshoudan.objects.filter(temid=list[-1]["id"]).first()
        document_state+="质{}量{}".format(zsd.qualitycheckinfo,zsd.quantitycheckinfo)
    document_state_dict={"采1请1询X报1暂1入1发X":[10,0,0],
                         "采1请1询X报1暂0入0":[8,1,0],
                         "采0请1询X报1入-1入-1":[7,1,0],
                         "采0请1询X报1暂X质1量-1":[6,1,0],
                         "采0请1询X报1暂X质-1量1":[6,1,0],
                         "采0请1询X报1暂X质-1量-1":[5,1,0],
                         "采-1请1询X报1暂-2质0量-1":[5,0,1],
                         "采-1请1询X报1暂-2质-1量0":[5,0,1],
                         "采-1请1询X报1暂-2质0量1":[6,0,1],
                         "采-1请1询X报1暂-2质1量0":[6,0,1],
                         "请1询X报-1":[4,1,0],
                         "请1报1":[3,1,0],
                         "请1报0":[2,1,0],
                         "请1报-1": [3, 0, 1],
                         "请0":[1,1,0],
                         "请-1":[-1,1,0],
                         "":[-2,1,0]}
    active="background:#5893df"
    inprogress="background:#f3cb2a"
    danger="background:#ec5e69"
    style=[""]*11
    print(document_state)
    progress=document_state_dict[document_state]
    for i in range(progress[0]+1):
        style[i]=active
    if progress[1]==1:
        style[progress[0]+1] = inprogress
    if progress[2]==1:
        style[progress[0]+1+progress[1]]=danger
    textFirst="货物质检"
    textSecond="货物量检"
    if document_state=="采0请1询X报1暂X质-1量1" \
            or document_state=="采-1请1询X报1暂-2质-1量0" \
            or document_state=="采-1请1询X报1暂-2质0量1":
        textFirst,textSecond=textSecond,textFirst
    progressShow=(len(list)>0)
    result = {
        "list": list,
        "id": nid,
        "title": "查看单据流",
        "progress":progress[0],
        "progress1":progress[1],
        "progress2":progress[2],
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
    notify=[]
    notify.append(dict(id=0, tittle="提示", context="采购订单 {} 删除成功！".format(id), type="success", position="top-center"))
    request.session["notify"] = notify
    return JsonResponse({"status": True})


# 根据id逻辑删除已完成或者已拒绝的报单，已删除的报价单不再显示
def quote_delete(request):
    id = request.GET.get("uid")
    models.Baojiadan.objects.filter(quoteid=id).update(isdelete=1)
    notify=[]
    notify.append(dict(id=0, tittle="提示", context="报价单 {} 删除成功！".format(id), type="success", position="top-center"))
    request.session["notify"] = notify
    return JsonResponse({"status": True})


def to_verify(request, did):
    # 跳转到采购需求管理页面
    return redirect('/inventory/demand/' + did + "/")
