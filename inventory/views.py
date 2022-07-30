from django.shortcuts import render
import random
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from supply import models


# 查看库存
def inventory_display(request):
    a = models.Gongchangkucun.objects.values('facid_id', 'maid_id').distinct()
    q = []
    for i in a:
        q.append(
            models.Gongchangkucun.objects.filter(facid_id=i['facid_id']
                                                 , maid_id=i['maid_id']).order_by('-updatetime').first()
        )
        # 查询展示每个工厂物料对应的最新的库存信息
    # print(q[0].updatetime)
    return render(request, 'inventory_display.html', {"queryset": q, "title": "库存展示"})


def inventory_detail(request, uid):  # 路径传参要写进函数参数中
    m = models.Gongchangkucun.objects.filter(id=uid).first()
    nowdata = []
    nowdata.append(m.inventoryonroad)
    nowdata.append(m.inventorytemp)
    nowdata.append(m.inventoryunrest)
    nowdata.append(m.inventoryfreeze)
    fid = m.facid
    mid = m.maid
    qu = models.Gongchangkucun.objects.filter(facid_id=fid, maid_id=mid).order_by("-updatetime")[:6]

    q = qu[::-1]
    datelist = []
    l1 = []
    l2 = []
    l3 = []
    l4 = []
    for i in q:
        datelist.append(str(i.updatetime.strftime("%Y-%m-%d %H:%M:%S")))
        l1.append(i.inventoryonroad)
        l2.append(i.inventorytemp)
        l3.append(i.inventoryunrest)
        l4.append(i.inventoryfreeze)
    result = {
        "history": q, "now": m, "nowdata": nowdata,
        "datelist": datelist,
        "l1": l1,
        "l2": l2,
        "l3": l3,
        "l4": l4
        , "title": "库存详情"
    }
    print(result)
    return render(request, 'inventory_detail.html', result)


# 采购需求列表
def inventory_demand(request, did):
    """采购需求管理（请购单）"""
    material = models.Wuliao.objects.filter().all()
    factory = models.Gongchang.objects.filter().all()
    caigou = models.Caigouxuqiu.objects.filter(demandid=did)
    if did == "n":
        caigou = models.Caigouxuqiu.objects.filter(isdelete=0).all()
    result = {
        "material": material,
        "factory": factory,
        "caigou": caigou
        , "title": "采购需求管理"
    }
    return render(request, 'inventory_demand.html', result)



""" 表单数据验证+报错信息 """


def form_item_check(context, type="nan"):
    if context.strip() == "":
        if type[:2] == "id":
            return "请设置" + type[2:]
        return "必填字段，内容不能为空"
    need = {"int": "整数", "int+": "正整数", "float": "数字", "float+": "正数"}
    if not type == "nan" and not type[:2] == "id":
        ctx = context
        if context[0] == "-":
            ctx = context[1:]
        if ctx.count(".") > 1 or not ctx[0].isdigit() or not ctx.replace(".", "").isdigit():
            return "输入错误,请输入" + need[type]
        if type[-1] == "+" and float(context) <= 0:
            return "输入错误,请输入" + need[type]
    return True


# 添加采购需求
def demand_add(request):
    print(1)
    """添加采购需求"""
    n = 10000000
    if models.Caigouxuqiu.objects.all().first():
        n = models.Caigouxuqiu.objects.all().order_by('-demandid').first().demandid[2:]
    did = "de" + str(int(n) + 1)  # 编号递增，这样计算避免删除后出现错误
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    r = request.POST
    id = request.session["info"]['id']
    # 设置表单数据校验
    toCheck = [r['facid_id'], r['maid_id'], r['price'], r['tcount']]  # 校验字段
    types = ["id工厂编号", "id物料编号", "float+", "int+"]  # 校验类型
    errors = []  # 校验结果
    returnStatus = True  # 是否通过所有校验
    for idx, (cck, typ) in enumerate(zip(toCheck, types)):
        result = form_item_check(cck, typ)
        errors.append(result)
        if not result == True:
            returnStatus = False
    print(returnStatus)
    if returnStatus:  # 校验成功才执行插入
        models.Caigouxuqiu.objects.create(demandid=did, price=r["price"], tcount=r['tcount']
                                          , status=0, createtime=time, createuserid_id=id,
                                          facid_id=r['facid_id'], maid_id=r['maid_id'])
        # 自动发信功能
        # 1，确认员工身份，是管理员或库存经理则不发信  否则 向本公司的库存经理发信
        me = models.Yuangong.objects.filter(id=id).first()
        message = []
        notify = []
        if me.office != "5" and me.isactive==1 and me.issuper == 0:
            wl=models.Wuliao.objects.filter(id=r['maid_id']).first()
            message.append("【系统自动发信】<br/>申请审核")
            message.append("待审核采购需求：<br/>采购物料：{}({})<br/>采购数量：{}<br/>预期采购价：{}元/{}<br/>请前往审核<a href='/inventory/demand/n/'>>></a>"
                           .format(wl.desc,wl.id,r['tcount'],r['price'],wl.calcutype))
            to = models.Yuangong.objects.filter(businessid=me.businessid, office="5").first()
            for m in message:
                models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=to.id, time=datetime.now(), context=m, read=0)
            notify.append(dict(id=0,tittle="提示", context="采购需求创建成功！", type="success", position="top-center"))
            notify.append(dict(id=1,tittle="系统消息", context="已向{}发送采购需求审核申请".format(to.username), 
                               type="info", position="top-center"))
            request.session["notify"]=notify
    return JsonResponse({"status": returnStatus, "error": errors})


@csrf_exempt
def demand_verify(request):
    """审核采购需求"""
    did = request.POST.get("did")
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id = request.session["info"]['id']
    cgd = models.Caigouxuqiu.objects.filter(demandid=did)
    cgd.update(verifytime=time,verifyuserid_id=id, status=1)
    # 自动发信功能
    # 1，确认员工身份，是管理员则不发信 否则 向采购需求对应的员工发信
    me = models.Yuangong.objects.filter(id=id).first()
    message = []
    notify = []
    if me.office != "0" and me.isactive == 1 and me.issuper == 0:
        cgxq = cgd.first()
        wl = models.Wuliao.objects.filter(id=cgxq.maid_id).first()
        message.append("【系统自动发信】")
        message.append("采购需求单{}<br/>采购物料：{}({})<br/>采购数量：{}<br/>预期采购价：{}元/{}<br/>已审核通过"
                       .format(did,wl.desc,wl.id,cgxq.tcount,cgxq.price,wl.calcutype))
        to = models.Yuangong.objects.filter(id=cgxq.createuserid_id).first()
        if me.id!=to.id:
            for m in message:
                models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=to.id, time=datetime.now(), context=m, read=0)
        message[1]="新增已审核采购需求：<br/>采购需求单{}<br/>采购物料：{}({})<br/>采购数量：{}<br/>预期采购价：{}元/{}<br/>已审核通过"\
            .format(did,wl.desc,wl.id,cgxq.tcount,cgxq.price,wl.calcutype)
        message.append("请尽快前往创建询价单<a href='/purchase/inquiry/create/'>>></a>")
        pur_yg = models.Yuangong.objects.filter(businessid=me.businessid,isactive=1,office="2").first()
        for m in message:
            models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=pur_yg.id, time=datetime.now(), context=m, read=0)
        notify.append(dict(id=0, tittle="提示", context="采购需求审核成功！", type="success", position="top-center"))
        notify.append(dict(id=1, tittle="系统消息", context="已向 {}-{} 发送采购需求审核回执"
                           .format(to.get_office_display(), to.username),
                 type="info", position="top-center"))
        notify.append(dict(id=2, tittle="系统消息", context="已向 {}-{} 发送询价单创建提示"
                           .format(pur_yg.get_office_display(), pur_yg.username),
                 type="info", position="top-center"))
        request.session["notify"] = notify
    return JsonResponse({"status": True})


# 进行暂存检查
def inventory_temp(request):
    """暂存检查"""
    # 首先查到所有待暂存的采购订单

    q = models.Zanshoudan.objects.filter(isdelete=0).all()
    print(q)
    return render(request, 'temp_list.html', {"queryset": q, "title": "暂存管理"})


def ischeck(request, pid, notify):
    """判断是否检查完成"""
    z = models.Zanshoudan.objects.filter(purchaseid_id=pid)
    flag = False
    # 先判断是否有检查不通过
    if z.first().qualitycheckinfo == 0 or z.first().quantitycheckinfo == 0 :
        n = 10000000
        createtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if models.Zanshoudan.objects.all().first():
            n = models.Zanshoudan.objects.all().order_by('-temid').first().temid[2:]
        zid = "te" + str(int(n) + 1)
        z.update(temid=zid, isreceived=0, createtime=createtime)
        # 更新库存信息,此情况下，库存为冻结库存
        fid = z.first().purchaseid.facid_id
        mid = z.first().maid_id
        tcount = z.first().tcount
        # 更新采购单和暂存单的状态为冻结状态
        models.Zanshoudan.objects.filter(temid=zid).update(isreceived=-1)
        models.Caigoudan.objects.filter(purchaseid=pid).update(iscomplete=-1)

        if z.first().qualitycheckinfo:
            notify.append(dict(id=1, tittle="提示", context="暂存单 {} 量检不通过，转为冻结库存".format(zid), type="error", position="top-center"))
        if not z.first().qualitycheckinfo:
            notify.append(dict(id=1, tittle="提示", context="暂存单 {} 质检不通过，转为冻结库存".format(zid), type="error", position="top-center"))
        w = models.Gongchangkucun.objects.filter(facid_id=fid, maid_id=mid).order_by("-updatetime").first()
        if w:
            models.Gongchangkucun.objects.create(facid_id=fid, maid_id=mid, inventorytemp= w.inventorytemp
                                                 , inventoryonroad=w.inventoryonroad - tcount,
                                                 inventoryfreeze=w.inventoryfreeze+tcount, inventoryunrest=w.inventoryunrest
                                                 , updatetime=createtime)
        else:
            models.Gongchangkucun.objects.create(facid_id=fid, maid_id=mid, inventorytemp=0
                                                 , inventoryonroad=0,
                                                 inventoryfreeze=tcount, inventoryunrest=0
                                                 , updatetime=createtime)
        return notify
    # 质检量检均完成后，才算完成
    if z.first().quantitycheckinfo != -1 and z.first().qualitycheckinfo != -1:
        n = 10000000
        createtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if models.Zanshoudan.objects.all().first():
            n = models.Zanshoudan.objects.all().order_by('-temid').first().temid[2:]
        zid = "te" + str(int(n) + 1)  # 编号递增，这样计算避免删除后出现错误
        z.update(temid=zid, isreceived=0, createtime=createtime)
        # 更新库存信息
        fid = z.first().purchaseid.facid_id
        mid = z.first().maid_id
        tcount = z.first().tcount
        w = models.Gongchangkucun.objects.filter(facid_id=fid, maid_id=mid).order_by("-updatetime").first()
        if w:
            models.Gongchangkucun.objects.create(facid_id=fid, maid_id=mid, inventorytemp=tcount + w.inventorytemp
                                                 , inventoryonroad=w.inventoryonroad - tcount,
                                                 inventoryfreeze=w.inventoryfreeze, inventoryunrest=w.inventoryunrest
                                                 , updatetime=createtime)
        else:
            models.Gongchangkucun.objects.create(facid_id=fid, maid_id=mid, inventorytemp=tcount
                                                 , inventoryonroad=0,
                                                 inventoryfreeze=0, inventoryunrest=0
                                                 , updatetime=createtime)
        # 暂时生成入库单,单号等于暂存单号
        id = request.session["info"]['id']
        models.Rukudan.objects.create(id=zid, purcount=tcount, createusersid_id=id, facid_id=fid,
                                      maid_id=mid, temid_id=zid)
        flag = True
        #系统自动发信
        me=models.Yuangong.objects.filter(id=id).first()
        zcd=z.first()
        cgd=zcd.purchaseid
        yg=cgd.createuserid
        gys=cgd.supplyid
        fac=cgd.facid
        wl=cgd.maid
        jl=models.Yuangong.objects.filter(businessid=me.businessid,isactive=1,office="5").first()
        notify.append(dict(id=1, tittle="提示", context="暂存单 {} 通过【质检】及【量检】".format(zcd.temid), type="success", position="top-center"))
        notify.append(dict(id=2, tittle="系统消息", context="向 {}-{} 发信反馈暂存单检查完成".format(yg.get_office_display(), yg.username),
                           type="info", position="top-center"))
        notify.append(dict(id=3, tittle="系统消息", context="已提示 {}-{} 前往创建入库单".format(jl.get_office_display(), jl.username),type="info", position="top-center"))
        message = []
        message.append("【系统消息】<br/>暂存单通过检查")
        message.append("供应商:{}({})<br/>收货工厂:{}({})<br/>采购订单:{}<br/>采购物料:{}({})<br/>采购数量:{}{}<br/>采购价格:{}元/{}"
                       .format(gys.name,gys.id,fac.type,fac.address,cgd.purchaseid,wl.desc,wl.id,cgd.tcount,wl.calcutype,cgd.price,wl.calcutype))
        message.append("入库前物料检查情况：<br/>量检通过-质检通过<br/>备注：<br/>{}".format(zcd.moreinfo))
        for m in message:
            models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=yg.id, time=datetime.now(), context=m, read=0)
        message.append("请核验物料入库数量并创建入库单<a href='/inventory/receive/'>>></a>".format())
        for m in message:
            models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=jl.id, time=datetime.now(), context=m, read=0)
    return notify



def quality_check(request):
    """质检"""
    puid = request.GET.get("puid")
    q = request.POST.get("check")
    info = request.POST.get("moreinfo")
    state_dict = {"0": "不通过", "1": "通过"}
    z = models.Zanshoudan.objects.filter(purchaseid_id=puid)
    if z.first().moreinfo:
        info = info + z.first().moreinfo
    z.update(qualitycheckinfo=q, moreinfo=info)
    notify = [dict(id=0, tittle="系统消息", type="success", position="top-center",
                   context="暂存单质检成功，质检状态【{}】".format(state_dict[q]))]
    request.session["notify"] = ischeck(request, puid, notify)
    return JsonResponse({"status": True})

def quantity_check(request):
    """量检"""
    puid = request.GET.get("puid")
    q = request.POST.get("check")
    info = request.POST.get("moreinfo")
    state_dict={"0":"不通过","1":"通过"}
    z = models.Zanshoudan.objects.filter(purchaseid_id=puid)
    if z.first().moreinfo:
        info = info + z.first().moreinfo
    z.update(quantitycheckinfo=q, moreinfo=info)
    notify = [dict(id=0, tittle="系统消息", type="success", position="top-center",
                   context="暂存单量检成功，量检状态【{}】".format(state_dict[q]))]
    request.session["notify"] = ischeck(request, puid, notify)
    return JsonResponse({"status": True})


# 展示入库单
def inventory_receive(request):
    """入库管理"""
    q = models.Rukudan.objects.filter(isdelete=0).all()

    return render(request, 'inventory_receive.html', {"queryset": q, "title": "入库管理"})


# 添加入库
def receive_add(request):
    """添加入库"""
    tid = request.GET.get("tid")
    t = models.Rukudan.objects.filter(temid_id=tid)
    fid = t.first().facid_id
    mid = t.first().maid_id
    pid = t.first().temid.purchaseid_id
    receivecount = request.POST.get("receivecount")
    if not receivecount:
        return JsonResponse({"status": False,"error":"实际入库数量不能为空"})
    if float(receivecount) < 0:
        return JsonResponse({"status": False,"error":"实际入库数量不能为负数"})
    pcount = t.first().purcount
    moreinfo = request.POST.get("moreinfo")
    id = request.session["info"]['id']
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 生成入库单
    n = 10000000
    if models.Rukudan.objects.all().first():
        n = models.Rukudan.objects.all().order_by('-id').first().id[2:]
    wid = "wa" + str(int(n) + 1)  # 编号递增，这样计算避免删除后出现错误
    t.update(id=wid, createtime=time, receivecount=receivecount,
             moreinfo=moreinfo, createusersid_id=id)

    # 库存状态更新
    w = models.Gongchangkucun.objects.filter(facid_id=fid, maid_id=mid).order_by("-updatetime").first()
    if w:
        models.Gongchangkucun.objects.create(facid_id=fid, maid_id=mid, inventorytemp=w.inventorytemp - pcount
                                             , inventoryonroad=w.inventoryonroad,
                                             inventoryfreeze=w.inventoryfreeze,
                                             inventoryunrest=w.inventoryunrest + float(receivecount)
                                             , updatetime=time)
    else:
        models.Gongchangkucun.objects.create(facid_id=fid, maid_id=mid, inventorytemp=0
                                             , inventoryonroad=0,
                                             inventoryfreeze=0, inventoryunrest=receivecount
                                             , updatetime=time)

    # 暂存单，采购单收货状态更新

    models.Zanshoudan.objects.filter(temid=tid).update(isreceived=1)
    models.Caigoudan.objects.filter(purchaseid=pid).update(iscomplete=1)

    notify, message = [], []
    me = models.Yuangong.objects.filter(id=request.session["info"]["id"]).first()
    yg = models.Yuangong.objects.filter(isactive=1, businessid_id=me.businessid_id, office="3").first()
    jl = models.Yuangong.objects.filter(isactive=1, businessid_id=me.businessid_id, office="6").first()
    zcd = models.Zanshoudan.objects.filter(temid=tid).first()
    cgd = zcd.purchaseid
    gys = cgd.supplyid
    fac = cgd.facid
    wl = cgd.maid
    notify.append(dict(id=0, tittle="提示", context="入库单 {} 创建成功".format(zcd.temid), type="success", position="top-center"))
    notify.append(dict(id=1, tittle="系统消息", context="向 {}-{} 发信反馈入库完成".format(yg.get_office_display(), yg.username),
                       type="info", position="top-center"))
    notify.append(dict(id=2, tittle="系统消息", context="向 {}-{} 发信反馈物料需求入库完成".format(jl.get_office_display(), jl.username),
                       type="info",position="top-center"))
    message = []
    message.append("【系统消息】<br/>物料需求成功入库")
    message.append("供应商:{}({})<br/>收货工厂:{}({})<br/>采购物料:{}({})<br/>采购数量:{}{}<br/>采购价格:{}元/{}"
                   .format(gys.name, gys.id, fac.type, fac.address, wl.desc, wl.id, cgd.tcount,wl.calcutype, cgd.price, wl.calcutype))
    message.append("物料检查情况：<br/>量检通过-质检通过<br/>备注：<br/>{}".format(zcd.moreinfo))
    message.append("物料入库情况：<br/>入库数量:{}{}<br/>备注：<br/>{}".format(receivecount,wl.calcutype,moreinfo))
    message.append("查看订单单据流<a href='/purchase/documents/?id={}'>>></a>".format(cgd.purchaseid))
    for m in message:
        models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=yg.id, time=datetime.now(), context=m, read=0)
        models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=jl.id, time=datetime.now(), context=m, read=0)
    request.session["notify"]=notify
    return JsonResponse({"status": True})


# 展示发票
def inventory_invoice(request):
    q = models.Fapiao.objects.all()

    return render(request, 'inventory_invoice.html', {"queryset": q, "title": "发票管理"})


# 添加发票
def invoice_add(request):
    tid = request.GET.get("tid")
    t = models.Rukudan.objects.filter(temid_id=tid)
    pid = t.first().temid.purchaseid_id
    sid = t.first().temid.purchaseid.supplyid_id
    fee = request.POST.get("receivecount")
    if not fee:
        return JsonResponse({"status": False,"error":"运费不能为空"})
    if float(fee)<0:
        return JsonResponse({"status": False,"error":"运费不能为负数"})
    pcount = t.first().purcount
    price = t.first().temid.purchaseid.price
    id = request.session["info"]['id']
    bid = t.first().temid.purchaseid.quoteid.bussid
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    totalcount = pcount
    money = round(float(totalcount) * float(price),2)
    totalmoney = money + float(fee)
    totalmoney=round(totalmoney,2)
    moreinfo = request.POST.get("moreinfo")

    n = 10000000
    if models.Fapiao.objects.all().first():
        n = models.Fapiao.objects.all().order_by('-invoiceid').first().invoiceid[2:]
    ivid = "iv" + str(int(n) + 1)  # 编号递增，
    models.Fapiao.objects.create(invoiceid=ivid, totalmoney=totalmoney, totalcount=totalcount
                                 , fee=fee, createtime=time, supplyid_id=sid,
                                 createuserid_id=id, purchaseid_id=pid, money=money, moreinfo=moreinfo
                                 )
    # 更新暂收单状态
    models.Zanshoudan.objects.filter(temid=tid).update(isreceived=2)
    return JsonResponse({"status": True, "id": ivid})


def invoice_display(request, ivid):
    """展示发票详情"""
    invoice = models.Fapiao.objects.filter(invoiceid=ivid).first()
    return render(request, 'invoice_display.html', {"invoice": invoice, "title": "发票展示"})


def demand_delete(request):
    """删除已完成的采购需求"""
    id = request.GET.get("uid")
    models.Caigouxuqiu.objects.filter(demandid=id).update(isdelete=1)
    notify = []
    notify.append(dict(id=0, tittle="提示", context="采购需求删除成功！", type="success", position="top-center"))
    request.session["notify"] = notify
    return JsonResponse({"status": True})


def inventory_delete(request):
    """删除已完成的暂存单"""
    id = request.GET.get("uid")
    models.Zanshoudan.objects.filter(purchaseid_id=id).update(isdelete=1)
    notify=[dict(id=0,tittle="系统消息", type="success", position="top-center",
                 context="暂存单删除成功")]
    request.session["notify"]=notify
    return JsonResponse({"status": True})

def receive_delete(request):
    """删除已完成的入库单"""
    id = request.GET.get("uid")
    models.Rukudan.objects.filter(temid_id=id).update(isdelete=1)
    notify=[dict(id=0,tittle="系统消息", type="success", position="top-center",
                 context="入库单删除成功")]
    request.session["notify"]=notify
    return JsonResponse({"status": True})
