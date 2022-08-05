from django import template

register = template.Library()

@register.filter(name="front_add")
def front_add(arg,val):
    return str(val)+str(arg)

@register.filter(name="back_add")
def back_add(arg,val):
    return str(arg)+str(val)

@register.filter(name="message_flow_class")
def message_flow_class(arg):
    return "right-sidebar-toggle chat-item unread"+str(arg)

@register.filter(name="table_status")
def table_status(arg,val):
    #CSS中样式： 0-黄色  1-蓝色  2-绿色  3-红色
    d=dict()
    d['cgxq']={0:0,1:1,2:2} #采购需求对应(0, "未审核"),(1, "已审核"),(2, "已完成")
    d['bjd']={0:0,1:1,2:3,3:2}#报价单对应(0,"待评估"),(1,"接受"),(2,"拒绝"),(3,"已完成")
    d['zsd-jc']={0:3,1:2,-1:0}#暂收单-量检/质检 对应(1,"通过"),(0,"不通过"),(-1,"未检查")
    d['zsd-js']={0:0,1:2,2:2}#暂收单-接受 对应(1,"通过"),(0,"不通过"),(-1,"未检查")
    d['thd']={1:3,2:0,3:1,4:1}#退货单对应(1,"质检不合格"),(2,"运输过程破损"),(3,"额外产品"),(4,"其他")
    #d['']={0:,1:,2:}#单对应
    return "table_status_{}".format(d[val][arg])

from ..models import Gongchang,Gongyingshang,Wuliao

def trans(val,mark):
    if mark==False:
        return val
    if mark=="status":
        if str(val)=="1":
            return "已完成"
        else:
            return "未完成"
    if mark=="mid":
        return Wuliao.objects.filter(id=val).first().desc
    if mark == "fid":
        return Gongchang.objects.filter(id=val).first().address
    if mark=="sid":
        return Gongyingshang.objects.filter(id=val).first().name



@register.filter(name="obj_document")
def obj_document(arg):
    arg=dict(arg)
    names=["请购单","询价单","报价单","采购单","暂收单","入库单","发票"]
    qgd={
        "items":["id","status","fid","fid","mid","mid","tcount","price"],
        "tittles":["请购单号","订单状态","工厂编号","工厂地址","物料编号","物料描述","请购数量","预期单价"],
        # "classes":["full"]*8,
        "classes":["half"]*8,
        "texts":[""]*7+["元"],
        "mark":[False,"status",False,"fid",False,"mid",False,False]
    }
    xjd={
        "items":["id","fid","fid","mid","mid","bid","tcount"],
        "tittles":["询价单号","工厂编号","工厂地址","物料编号","物料描述","请购客户","请购数量"],
        "classes":["full"]+["half"]*6,
        "texts":[""]*7,
        "mark":[False,False,"fid",False,"mid",False,False,False]
    }
    bjd={
        "items":["id","status","sid","sid","mid","mid","tcount","quote"],
        "tittles":["报价单号","订单状态","供应商编号","供应商","物料编号","物料描述","报价数量","报价价格"],
        "classes":["half"]*8,
        "texts":[""]*7+["元"],
        "mark":[False,"status",False,"sid",False,"mid",False,False],
    }
    cgd={
        "items":["id","status","fid","fid","sid","sid","mid","mid","tcount","price"],
        "tittles":["采购单号","订单状态","工厂编号","工厂地址","供应商编号","供应商","物料编号","物料描述","采购数量","采购价格"],
        "classes":["half"]*10,
        "texts":[""]*9+["元"],
        "mark":[False,"status",False,"fid",False,"sid",False,"mid",False,False]
    }
    zsd={
        "items":["id","status","fid","fid","sid","sid","mid","mid","tcount","moreinfo"],
        "tittles":["暂收单号","订单状态","工厂编号","工厂地址","供应商编号","供应商","物料编号","物料描述","暂收数量","备注"],
        "classes":["half"]*9+["full"]*2,
        "texts":[""]*11,
        "mark":[False,"status",False,"fid",False,"sid",False,"mid",False,False]
    }
    fp={
        "items":["id","sid","sid","mid","mid","fee","totalmoney","tcount","moreinfo"],
        "tittles":["发票单号","供应商编号","供应商","物料编号","物料描述","运费","总金额","交易数量","备注"],
        "classes":["full"]+["half"]*6+["full"]*2,
        "texts":[""]*10,
        "mark":[False,False,"sid",False,"mid",False,False,False,False]
    }
    rkd={
        "items":["id","status","fid","fid","sid","sid","mid","mid","tcount","rcount","moreinfo"],
        "tittles":["入库单号","订单状态","工厂编号","工厂地址","供应商编号","供应商","物料编号","物料描述","暂收数量","入库数量","备注"],
        "classes":["half"]*10+["full"]*1,
        "texts":[""]*11,
        "mark":[False,"status",False,"fid",False,"sid",False,"mid",False,False,False]
    }
    patterns=dict(zip(names,[qgd,xjd,bjd,cgd,zsd,rkd,fp]))
    p=patterns[arg["name"]]
    result=[]
    for idx,k in enumerate(p["items"]):
        d={"name":p["tittles"][idx],
           "context":trans(arg[k],p["mark"][idx]),
           "class":"document_flow_"+p["classes"][idx],
           "text":p["texts"][idx]}
        result.append(d)
    return result

@register.filter(name="money_add")
def money_add(arg,val):
    return float(val)+float(arg)