from django.shortcuts import render
import random
import re
from datetime import datetime
from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from supply import models
# Create your views here.

import json

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


def form_check(toCheck, types):
    # 设置表单数据校验
    errors = []  # 校验结果
    returnStatus = True  # 是否通过所有校验
    for idx, (cck, typ) in enumerate(zip(toCheck, types)):
        result = form_item_check(cck, typ)
        errors.append(result)
        if not result == True:
            returnStatus = False
    res_dict = {"status": returnStatus, "error": errors}
    return res_dict


def check_message(request):
    me = request.GET.get("yid")
    cou = models.Xiaoxi.objects.filter(toId=me, read=0).count()
    return JsonResponse({"status": True, "count": cou})


def ambu_time(time):
    now = int(datetime.now().strftime("%Y%m%d%H"))
    com = int(time.strftime("%Y%m%d%H"))
    if now - com > 18:
        return time.strftime("%m{m}%d{d}").format(m="月", d="日")
    return time.strftime("%H:%M")

#返回登录用户的消息列表，按已读未读分组
#消息列表：所有聊天对象的最后一条消息+人名+格式化时间
def all_message_by_user(request, me="e0002"):
    relevant = models.Xiaoxi.objects.filter(Q(fromId=me) | Q(toId=me)).all().order_by('time')
    read = {}
    unread = {}
    for i in relevant:
        other = i.toId_id
        if other == me:
            other = i.fromId_id
        info = {"id": other, "time": ambu_time(i.time), "text": i.context}
        if (i.read == 0 and i.toId_id==me):
            try:
                read.pop(other)
            except:
                None
            unread[other] = info
        else:
            read[other] = info
    for k, v in read.items():
        read[k]["name"] = models.Yuangong.objects.filter(id=k).first().username
    for k, v in unread.items():
        unread[k]["name"] = models.Yuangong.objects.filter(id=k).first().username
    return {"read": read, "unread": unread, "me": me}

# 找到一对聊天对象的所有消息流
def all_message(them='e0003', me='e0002'):
    print(them, me)
    who = models.Yuangong.objects.filter(id=them).first().username
    froms = models.Xiaoxi.objects.filter(fromId=them, toId=me).all()
    tos = models.Xiaoxi.objects.filter(fromId=me, toId=them).all()
    message_flow = []
    for i in froms:
        message_flow.append(
            {"isThem": True, "time": i.time.strftime("%m{m}%d{d} %H:%M:%S").format(m="月", d="日"), "text": i.context,
             "compare": int(i.time.strftime("%Y%m%d%H%M"))})
    for i in tos:
        message_flow.append(
            {"isThem": False, "time": i.time.strftime("%m{m}%d{d} %H:%M:%S").format(m="月", d="日"), "text": i.context,
             "compare": int(i.time.strftime("%Y%m%d%H%M"))})
    message_flow = sorted(message_flow, key=lambda a: a["compare"])
    flow = {"who": who, "flow": message_flow}
    return flow

#生成页面中一条消息的html
def add_message(line):
    html_class = "me"
    icon = ""
    if line["isThem"]:
        html_class = "them"
        icon = '<div class="chat-bubble-img-container"><img src="http://via.placeholder.com/38x38" alt=""></div>'
    html_template = ' <div class="chat-bubble {}">{}<div class="chat-bubble-text-container"><span class="chat-bubble-text">{}</span></div></div>'
    html = html_template.format(html_class, icon, line["text"])
    return html

#按时间对消息分组，一段时间内的消息归进一组，显示一个时间戳
def group_by_time(f):
    flow = f["flow"]
    start = int(flow[0]["compare"])
    interval = 3 #同一时间组发送时间差上限  分钟
    group = 0
    groups = {0: []}
    for i in flow:
        print(int(i["compare"])-start)
        if int(i["compare"]) - start >= interval:
            start = int(i["compare"])
            group += 1
            groups[group] = []
        groups[group].append(i)
    return groups


def add_group(group):
    time_template = '<div class="chat-start-date">{}</div>'
    time = time_template.format(group[0]["time"])
    for line in group:
        time += add_message(line)
    return time


def add_chart_item(k, v, unread):
    template = '<a href="javascript:void(0);" class="{}"' \
               'data-sidebar-id="chat-right-sidebar" yid="{}">' \
               '<div class="user-avatar"><img src="http://via.placeholder.com/40x40" alt=""></div>' \
               '<div class="chat-info"><span class="chat-author">{}</span><span class="chat-text">{}</span><span class="chat-time">{}</span></div></a>'
    clas = "right-sidebar-toggle chat-item"
    if unread:
        clas = "right-sidebar-toggle chat-item unread active-user"
    return template.format(clas, k, v['name'], re.sub(r"<a.*?</a>",'',v['text']), v['time'])


def add_chart_group(which, d):
    template = '<div class="chat-list"><span class="chat-title">{}</span>{}</div>'
    if which == "暂无消息":
        return template.format(which, "")
    if len(d) == 0:
        return ""
    out = ""
    unread = False
    if which == "新消息":
        unread = True
    for k, v in d.items():
        out += add_chart_item(k, v, unread)
    return template.format(which, out)


def set_chart_group(flow):
    out = ""
    out += add_chart_group("新消息", flow["unread"])
    out += add_chart_group("已读消息", flow["read"])
    if len(flow["unread"]) == 0 and len(flow['read']) == 0:
        out += add_chart_group("暂无消息",None)
    cou = 0
    me = flow["me"]
    for i in flow["unread"].keys():
        cou += models.Xiaoxi.objects.filter(fromId=i, toId=me, read=0).count()
    return {"out": out, "count": cou}


def url_set_message_list(request):
    me = request.GET.get("meid")
    sett = set_chart_group(all_message_by_user(None, me))
    return JsonResponse({"status": True, "setList": sett["out"], "count": sett["count"]})


def set_message_detail(request):
    yid = request.GET.get("yid")
    me = request.GET.get("meid")
    who = models.Yuangong.objects.filter(id=yid).first().username
    unread = models.Xiaoxi.objects.filter(toId=me, fromId=yid, read=0).all().count()
    models.Xiaoxi.objects.filter(toId=me, fromId=yid).update(read=1)
    sett = set_chart_group(all_message_by_user(None, me))
    set_list = sett["out"]
    cou = sett["count"]
    state = "已读"
    if unread > 0:
        state = "{}条未读消息".format(unread)
    flow = all_message(me=me, them=yid)
    groups = group_by_time(flow)
    out = ""
    for g in groups.values():
        out += add_group(g)
    return JsonResponse({"status": True, "message": out, "who": who, "when": state, "setList": set_list, "count": cou})


def send_test_message(request):
    me = request.GET.get("meid")
    gjr = models.Yuangong.objects.filter().exclude(id=me).first().id
    models.Xiaoxi.objects.create(fromId_id=gjr, toId_id=me, context="骚扰" + str(random.randint(1, 20)),
                                 time=datetime.now(), read=0)
    return JsonResponse({"status": True})

def send_message(request):
    me = request.GET.get("meid")
    them = request.GET.get("yid")
    text = request.GET.get("text")
    models.Xiaoxi.objects.create(fromId_id=me, toId_id=them, context=text, time=datetime.now(), read=0)
    return JsonResponse({"status": True})

def delete_notify(request):
    try:
        request.session.pop("notify")
    except:
        None
    return JsonResponse({"status": True})

#询价单系列数据
def xjd_info(xjd,retu):
    wl = xjd.maid
    gs = xjd.bussid
    gc = xjd.demandid.facid
    retu["gs"] = {'id': gs.myid, 'name': gs.name}
    retu['gc'] = {'type': gc.type, 'id': gc.id, 'add': gc.address}
    retu['wl'] = {"id": wl.id, "desc": wl.desc, "cal": wl.calcutype, "type": wl.type}
    retu['tcount'] = xjd.tcount
    return

#表单信息展示函数
def form_set_byId(request):
    type=request.GET.get("type").split(",")
    print(type)
    retu={"status": True}
    if "gc" in type:
        id = request.GET.get("facid")
        gc = models.Gongchang.objects.filter(id=id).first()
        if gc==None:
            retu["gc"] = {"add": "工厂地址", "type": "工厂类型"}
        else:
            retu["gc"] = {"add": gc.address, "type": gc.type}
    if "wl" in type:
        id = request.GET.get("maid")
        wl = models.Wuliao.objects.filter(id=id).first()
        if wl==None:
            retu["wl"] = {"desc": "物料描述", "cal": "计量单位","type": "物料类型"}
        else:
            retu["wl"] = {"desc": wl.desc, "cal": wl.calcutype,"type":wl.type}
    if "gckc" in type:
        facid = request.GET.get("facid")
        maid=request.GET.get("maid")
        kc = models.Gongchangkucun.objects.filter(facid=facid, maid=maid).order_by('-updatetime').first()
        if not kc==None:
            retu["gckc"] = {"unres":kc.inventoryunrest}
        else:
            retu["gckc"] = {"unres":0}
    if "xjd" in type:
        xid=request.GET.get("xjd")
        xjd=models.Xunjiadan.objects.filter(inquiryid=xid).first()
        xjd_info(xjd,retu)
        retu['xjyxq']=xjd.validitytime.strftime("%Y{}%m{}%d{} %H:%M").format("年","月","日")
    if "bjd" in type:
        xid=request.GET.get("xjd")
        print(xid)
        bjd=models.Baojiadan.objects.filter(quoteid=xid).first()
        xjd=bjd.inquiryid
        xjd_info(xjd,retu)
        retu['xjyxq']=xjd.validitytime.strftime("%Y{}%m{}%d{} %H:%M").format("年","月","日")
        retu['bjyxq'] =bjd.validitytime.strftime("%Y{}%m{}%d{} %H:%M").format("年", "月", "日")
    if 'gys' in type:
        bid=request.GET.get('xjd')
        bjd=models.Baojiadan.objects.filter(quoteid=bid).first()
        gys=bjd.supplyid
        retu['gys']={"id":gys.id,"name":gys.name,"price":bjd.quote}
    if 'cgd' in type:
        pid = request.GET.get("cgd")
        cgd = models.Caigoudan.objects.filter(purchaseid=pid).first()
        xjd = cgd.quoteid.inquiryid
        xjd_info(xjd, retu)
    if 'rkd' in type:
        rid=request.GET.get("rkd")
        rkd=models.Rukudan.objects.filter(id=rid).first()
        zsd=rkd.temid
        cgd=rkd.temid.purchaseid
        bjd=cgd.quoteid
        xjd=bjd.inquiryid
        gys=cgd.supplyid
        xjd_info(xjd,retu)
        facid=xjd.demandid.facid_id
        maid=xjd.demandid.maid_id
        kc=models.Gongchangkucun.objects.filter(facid=facid, maid=maid).order_by('-updatetime').first()
        if not kc==None:
            retu["gckc"] = kc.inventoryunrest
        else:
            retu["gckc"] = 0
        retu['gys']={"id":gys.id,"name":gys.name,"price":bjd.quote}
        retu['cgd']={"time":cgd.createtime.strftime("%Y{}%m{}%d{} %H:%M:%S").format("年","月","日")}
        retu['zsd']={'time':zsd.createtime.strftime("%Y{}%m{}%d{} %H:%M:%S").format("年","月","日"),'info':zsd.moreinfo}
    print(retu)
    return JsonResponse(retu)

# 登录功能
def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    username = request.POST.get("username")
    password = request.POST.get("password")
    ins = models.Yuangong.objects.filter(id=username).first()
    err = ["", ""]
    if not str(username).strip():
        err[0] = "员工编号不能为空"
    if not str(password).strip():
        err[1] = "密码不能为空"
    if err[0] or err[1]:
        return JsonResponse({"status": False, "errors": err})
    if not err[0] and not err[1] and not ins:
        err[0] = "员工不存在"
        return JsonResponse({"status": False, "errors": err})
    if password != ins.password:
        err[0] = "密码错误"
        return JsonResponse({"status": False, "errors": err})
    if not ins.isactive:
        err[0] = "该账户已禁用"
        return JsonResponse({"status": False, "errors": err})
    # 记录登录信息
    request.session["info"] = {"name": ins.username, "id": ins.id, "issuper": ins.issuper
        , "office": ins.office, "business": ins.businessid.name, "officename": ins.get_office_display()}
    request.session["messageFlow"] = all_message_by_user(None, ins.id)
    request.session['produceActive']=True #控制是否向生产经理抄送操作记录
    return JsonResponse({"status": True})
from django.contrib import messages
# 找回密码-跳转
def forgot(request):
    question = models.Securityquestion.objects.filter().all()
    sq = []
    for i in question:
        sq.append(i.question)
    return render(request, 'forgot.html',locals())

# 修改密码
def r_password(request):
    username = request.POST.get("username")
    sq = request.POST.get("sq")
    sq_verification = request.POST.get("sq_verification")
    new_password = request.POST.get("new_password")
    ins = models.Yuangong.objects.filter(id=username).first()
    if ins is None:
        messages.success(request, "员工号输入错误！", locals())
        return redirect('/forgot')
    if ins.question == sq:
        if ins.verification == sq_verification:
            models.Yuangong.objects.filter(id=username).update(password=new_password)
            return redirect('/login')
        else:
            messages.success(request, "密保答案错误！", locals())
            return redirect('/forgot')
    else:
        messages.success(request, "密保问题选择错误！", locals())
        return redirect('/forgot')

# 登出功能
def logout(request):
    request.session.clear()
    return redirect('/login')

# 展示供应商列表
def supply_list(request):
    qu = models.Gongyingshang.objects.order_by('createtime')
    yu = models.Yuangong.objects.all()
    id = []
    n = []
    for i in yu:
        id.append(i.id)
        n.append(i.username)
    yuan = dict(zip(id, n))
    return render(request, 'supply_list.html', {"queryset": qu, "yuangong": yuan, "title": "供应商列表"})

# 添加供应商
def supply_add(request):
    n = 10000000
    if models.Gongyingshang.objects.first():
        n = models.Gongyingshang.objects.all().order_by('-id').first().id[1:]
    sid = "s" + str(int(n) + 1)  # 编号递增，这样计算避免删除后出现错误
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    o = request.POST
    id = request.session["info"]['id']
    toCheck = [o['name'], o['address']]
    types = ['nan', 'nan']
    res = form_check(toCheck, types)
    l1=len(o['name'])
    l2=len(o['address'])
    print(res)
    if l1>20:
        res['error'][0]='供应商名称不能超过20个字符'
        res['status']=False
    if l2>20:
        res['error'][0]='供应商地址不能超过20个字符'
        res['status']=False
    if res['status']:
        models.Gongyingshang.objects.create(name=o['name'], address=o['address'], createtime=time
                                            , id=sid, updatetime=time, createnumberid_id=id, updatenumberid_id=id)
    return JsonResponse(res)

# 编辑供应商时返回供应商原始数据
def supply_detail(request):
    sid = request.GET.get("uid")
    su = models.Gongyingshang.objects.filter(id=sid).values("name", "address").first()
    if not su:
        return JsonResponse({"status": False, "error": "数据不存在"})
    return JsonResponse({"supply": su, "status": True})

# 保存编辑供应商的最新数据
def supply_edit(request):
    id = request.GET.get("uid")
    uid = request.session["info"]['id']
    # 用户ID
    s = request.POST
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    toCheck = [s['name'], s['address']]
    types = ['nan', 'nan']
    res = form_check(toCheck, types)
    l1=len(s['name'])
    l2=len(s['address'])
    if l1>20:
        res['error'][0]='供应商名称不能超过20个字符'
        res['status']=False
    if l2>20:
        res['error'][0]='供应商地址不能超过20个字符'
        res['status']=False
    if res['status']:
        models.Gongyingshang.objects.filter(id=id).update(name=s['name'],
                                                          address=s['address'], updatetime=time, updatenumberid_id=uid)

    return JsonResponse(res)

# 删除供应商
def supply_delete(request):
    id = request.GET.get("uid")
    s = models.Gongyingguanxi.objects.filter(supplyid_id=id).first()
    # 先判断是否有关联的供应关系，如果有则不能删除
    if s:
        return JsonResponse({"status": False})
    models.Gongyingshang.objects.filter(id=id).delete()
    return JsonResponse({"status": True})

# 展示供应商与材料的供应关系
def material_list(request):
    qu = models.Gongyingguanxi.objects.all()
    material = models.Wuliao.objects.all()
    supply = models.Gongyingshang.objects.all()
    result = {
        "queryset": qu,
        "material": material,
        "supply": supply
        , "title": "物料供应关系"
    }

    return render(request, 'material_list.html', result)
# 添加供应商与物料的供应关系
def material_add(request):
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    r = request.POST
    sid = r["supplyid"]
    mid = r["materialid"]
    id = request.session["info"]['id']
    # 判断是否已经存在此供应关系，如果已存在则提示不能重复添加
    isexist = models.Gongyingguanxi.objects.filter(supplyid_id=sid, materialid_id=mid)
    if isexist:
        request.session['notify'] = [dict(id=0, tittle="提示", context="供应关系已存在，不能重复创建", type="error", position="top-center")]
        return JsonResponse({"status": True, "isexist": True})
    toCheck = [sid, mid]
    types = ['id供应商编号', 'id物料编号']
    res = form_check(toCheck, types)
    res["isexist"] = False
    print(res)
    if res['status']:
        models.Gongyingguanxi.objects.create(createtime=time, updatetime=time,
                                             createid_id=id, updateid_id=id,
                                             supplyid_id=sid, materialid_id=mid)
        request.session['notify'] = [dict(id=0, tittle="提示", context="供应关系创建成功", type="success", position="top-center")]
    return JsonResponse(res)
# 编辑供应关系时展示原始数据
def material_detail(request):
    smid = request.GET.get("uid")
    su = models.Gongyingguanxi.objects.filter(id=smid).values("supplyid_id", "materialid_id").first()
    if not su:
        return JsonResponse({"status": False, "error": "数据不存在"})
    return JsonResponse({"sm": su, "status": True})
# 保存编辑过后的供应关系
def material_edit(request):
    id = request.GET.get("uid")
    uid = request.session["info"]['id']
    # 用户ID
    s = request.POST
    mid = s["materialid"]
    sid = s["supplyid"]
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    isexist = models.Gongyingguanxi.objects.filter(supplyid_id=sid, materialid_id=mid)
    i = models.Gongyingguanxi.objects.filter(id=id)
    # 如果未作改动依旧显示成功
    if isexist and (i.first().materialid_id != mid or i.first().supplyid_id != sid):
        return JsonResponse({"status": True, "isexist": True})
    toCheck = [sid, mid]
    types = ['id供应商编号', 'id物料编号']
    res = form_check(toCheck, types)
    res["isexist"] = False
    if res["status"]:
        i.update(supplyid_id=sid, materialid_id=mid, updatetime=time, updateid_id=uid)
    return JsonResponse(res)

def quote_list(request):
    """进行报价"""
    time = datetime.now()
    m=models.Baojiadan.objects.filter(quote=None).filter(validitytime__gte=time)
    q = models.Baojiadan.objects.filter(isdelete=0).filter(quote__isnull=False)
    print(m.union(q))
    # 仅显示有效期内的报价单
    return render(request, 'quote_list.html', {"queryset": m.union(q), "title": "报价单管理"})

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
    toCheck = [quote]
    types = ["float+"]
    res = form_check(toCheck, types)
    if res['status']:
        models.Baojiadan.objects.filter(inquiryid_id=inid).update(quote=quote,
                                                                  quoteid=qid,
                                                                  createtime=time,
                                                                  createuserid_id=id,
                                                                  isreceived=0)
        notify,message=[],[]
        me = models.Yuangong.objects.filter(id=request.session["info"]["id"]).first()
        yg = models.Yuangong.objects.filter(isactive=1,businessid_id=me.businessid_id,office="2").first()
        jl = models.Yuangong.objects.filter(isactive=1,businessid_id=me.businessid_id,office="4").first()
        xjd = models.Xunjiadan.objects.filter(inquiryid=inid).first()
        qgd = models.Caigouxuqiu.objects.filter(demandid=xjd.demandid_id).first()
        wl = models.Wuliao.objects.filter(id=qgd.maid_id).first()
        gys = models.Gongyingshang.objects.filter(id=xjd.supplyid_id).first()
        notify.append(dict(id=0, tittle="提示", context="报价单 {} 创建成功".format(qid), type="success", position="top-center"))
        notify.append(dict(id=1, tittle="系统消息", context="向 {}-{} 发信反馈已报价".format(yg.get_office_display(),yg.username), type="info", position="top-center"))
        notify.append(dict(id=2, tittle="系统消息", context="已提示 {}-{} 前往评估报价单".format(jl.get_office_display(),jl.username), type="info", position="top-center"))
        message.append("【系统消息】收到新报价单")
        message.append("询价单-{} 已收到报价<br/>报价单号-{}".format(xjd.inquiryid, qid))
        if me.issuper==0:
            for m in message:
                models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=yg.id, time=datetime.now(), context=m, read=0)
            message[1] = '供应商:{}<br/>({})已报价<br/>询价单号:{}<br/>报价单号:{}<br/>预期报价:{}元/{}<br/>供应商报价:{}元/{}<br/>请评估报价<a class="chat_link" href="/purchase/quote/evaluate/">>></a>'\
                .format(gys.name,gys.id,xjd.inquiryid,qid,qgd.price,wl.calcutype,quote,wl.calcutype)
            for m in message:
                models.Xiaoxi.objects.create(fromId_id=me.id, toId_id=jl.id, time=datetime.now(), context=m, read=0)
        else:
            message[0]="【系统消息】操作历史记录"
            fromid = models.Yuangong.objects.filter(businessid=me.businessid, office="7").first()
            for m in message:
                models.Xiaoxi.objects.create(fromId_id=fromid.id, toId_id=me.id, time=datetime.now(), context=m, read=0)
            models.Xiaoxi.objects.create(fromId_id=fromid.id, toId_id=me.id, time=datetime.now(),
                                         context='于询价有效期内获取供应商报价反馈<br/>并填入系统<a class="chat_link" href="/supply/quote/list/">>></a>',
                                         read=0)
            notify=notify[:1]
            notify.append(dict(id=1, tittle="系统消息", context="操作历史已更新", type="info", position="top-center"))
        if request.session['produceActive']:
            message[1]='下一步操作人:【{}】{}<br/>'.format(me.get_office_display(),me.username)+message[1]
            next=me
            if me.issuper==0:
                next = models.Yuangong.objects.filter(businessid=me.businessid, office="4").first()
            message.append('下一步操作人:【{}】{}<br/>'
                           '下一步骤:维护供应商报价单<a class="chat_link" href="/supply/quote/list/">>></a><br/>'
                           .format(next.get_office_display(), next.username))
            fromid = models.Yuangong.objects.filter(businessid=me.businessid, office="7").first()
            toid = models.Yuangong.objects.filter(businessid=me.businessid, office="6").first()
            for m in message:
                models.Xiaoxi.objects.create(fromId_id=fromid.id, toId_id=toid.id, time=datetime.now(), context=m,
                                             read=0)
            notify.append(dict(id=len(notify), tittle="系统消息",
                               context="操作历史已抄送至 {}-{}".format(toid.get_office_display(), toid.username),
                               type="info", position="top-center"))
    request.session["notify"] = notify
    return JsonResponse(res)

def quote_detail(request):
    """修改报价单时返回相应数据"""
    id = request.GET.get("uid")
    quote = models.Baojiadan.objects.filter(quoteid=id).first().quote
    return JsonResponse({"status": True, "quote": quote})

def quote_edit(request):
    """根据报价单号修改报价"""
    quid = request.GET.get("quid")
    quote = request.POST.get("quote")
    toCheck = [quote]
    types = ["float+"]
    res = form_check(toCheck, types)
    if res['status']:
        models.Baojiadan.objects.filter(quoteid=quid).update(quote=quote)
        request.session['notify']=[dict(id=0, tittle="提示", context="报价单 {} 报价修改成功".format(quid), type="success", position="top-center")]
    return JsonResponse(json.dumps(res, ensure_ascii=False), safe=False)
# 展示物料列表
def mm_list(request):
    qu = models.Wuliao.objects.all()
    yu = models.Yuangong.objects.all()
    id = []
    n = []
    for i in yu:
        id.append(i.id)
        n.append(i.username)
    yuan = dict(zip(id, n))
    return render(request, 'create_material.html', {"queryset": qu, "yuangong": yuan, "title": "物料列表"})
# 添加供应商
def mm_add(request):
    n = 1000
    if models.Wuliao.objects.first():
        n = models.Wuliao.objects.all().order_by('-id').first().id[1:]
    sid = "m" + str(int(n) + 1)  # 编号递增，这样计算避免删除后出现错误
    # time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    o = request.POST
    id = request.session["info"]['id']
    models.Wuliao.objects.create(type=o['type'], salegroup=o['salegroup'], saleway=o['saleway']
                                 , id=sid, calcutype=o['calcutype'], desc=o['desc'])

    return JsonResponse({"status": True})


# 编辑供应商时返回供应商原始数据
def mm_detail(request):
    sid = request.GET.get("uid")
    su = models.Wuliao.objects.filter(id=sid).values("type", 'salegroup', 'saleway', "calcutype", "desc").first()
    if not su:
        return JsonResponse({"status": False, "error": "数据不存在"})
    return JsonResponse({"supply": su, "status": True})


# 保存编辑供应商的最新数据
def mm_edit(request):
    id = request.GET.get("uid")
    uid = request.session["info"]['id']
    # 用户ID
    o = request.POST
    # time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    models.Wuliao.objects.filter(id=id).update(type=o['type'], salegroup=o['salegroup'], saleway=o['saleway']
                                               , calcutype=o['calcutype'], desc=o['desc'])

    return JsonResponse({"status": True})

@csrf_exempt
# 删除物料
def mm_delete(request):
    id = request.POST.get("uid")
    '''
    s=models.Wuliao.objects.filter(supplyid_id=id).first()
    # 先判断是否有关联关系，如果有则不能删除，目前没有
    if s:
        return JsonResponse({"status":False})
    '''
    print(id)
    models.Wuliao.objects.filter(id=id).delete()
    return JsonResponse({"status": True})

import django_excel as excel
import json

def supply_excel(request):
    if request.method == "GET":
        return render(request, 'supplyexcel.html')