from django import template
register = template.Library()

@register.filter(name="front_add")
def front_add(arg,val):
    return str(val)+str(arg)

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

@register.filter(name="obj_document")
def obj_document(arg):
    arg=dict(arg)
    names=["请购单","询价单","报价单","采购单","暂收单","入库单"]
    qgd={
        "items":["id","status","fid","mid","tcount","price"],
        "tittles":["请购单号","订单状态","工厂编号","物料编号","请购数量","预期单价"],
        "classes":["full","full","full","full","full","full"],
        "texts":[""]*5+["元"],
        "foreign":[False]*6,
    }
    xjd={
        "items":["id","fid","mid","bid","tcount"],
        "tittles":["询价单号","工厂编号","物料编号","请购客户","请购数量"],
        "classes":["full","full","full","full","full"],
        "texts":[""]*5,
        "foreign":[False]*5,
    }
    bjd={
        "items":["id","status","sid","mid","tcount","quote"],
        "tittles":["报价单号","订单状态","供应商编号","物料编号","报价数量","报价价格"],
        "classes":["full","full","full","full","full","full"],
        "texts":[""]*5+["元"],
        "foreign":[False]*6,
    }
    cgd={
        "items":["id","status","fid","sid","mid","tcount","price"],
        "tittles":["采购单号","订单状态","工厂编号","供应商编号","物料编号","采购数量","采购价格"],
        "classes":["full","full","full","full","full","full","full"],
        "texts":[""]*6+["元"],
        "foreign":[False]*7,
    }
    zsd={
        "items":["id","status","fid","sid","mid","tcount","moreinfo"],
        "tittles":["暂收单号","订单状态","工厂编号","供应商编号","物料编号","暂收数量","备注"],
        "classes":["full","full","full","full","full","full","full"],
        "texts":[""]*7,
        "foreign":[False]*7,
    }
    rkd={
        "items":["id","status","fid","sid","mid","tcount","moreinfo"],
        "tittles":["入库单号","订单状态","工厂编号","供应商编号","物料编号","暂收数量","备注"],
        "classes":["full","full","full","full","full","full","full"],
        "texts":[""]*7,
        "foreign":[False]*7,
    }
    patterns=dict(zip(names,[qgd,xjd,bjd,cgd,zsd,rkd]))
    p=patterns[arg["name"]]
    result=[]
    print("【{}】-{}".format(arg["name"],arg))
    for idx,k in enumerate(p["items"]):
        d={"name":p["tittles"][idx],"context":arg[k],
           "class":"document_flow_"+p["classes"][idx],
           "text":p["texts"][idx]}
        print(d)
        result.append(d)
    return result

"""
【采购单】-{'date': datetime.datetime(2022, 7, 22, 13, 47, 26), 'status': 1, 'id': 'pu10000001', 'fid': 'f1003', 'tcount': 12.0, 'price': 12.0, 'mid': 'm1002',': 's10000001', 'name': '采购单'}
【请购单】-{'date': datetime.datetime(2022, 7, 22, 13, 6, 15), 
'status': 1, 'id': 'de10000003', 'fid': 'f1003', 'tcount': 12.0, 
'price': 1.0, 'mid': 'm1002', ' 's10000001', 'name': '请购单'}
【询价单】-{'date': datetime.datetime(2022, 7, 22, 13, 10, 6), 
'id': 'in10000001', 'fid': 'f1003', 'tcount': 12.0, 'mid': 'm1002', 
'bid': '新世纪', 'name': '询价单'}
【报价单】-{'date': datetime.datetime(2022, 7, 22, 13, 38, 43), 
'status': 1, 'id': 'qu10000002', 'tcount': 12.0, 
'quote': 12.0, 'mid': 'm1002', 'sid': 's10000001', 'name': '报价单'}
【暂收单】-{'status': 1, 'date': datetime.datetime(2022, 7, 22, 13, 52, 52), 
'id': 'te10000003', 'fid': 'f1003', 'tcount': 12.0, 'moreinfo': '',
 'mid': 'm1002'd': 's10000001', 'name': '暂收单'}
【入库单】-{'date': datetime.datetime(2022, 7, 22, 13, 53, 39), 
'status': 1, 'id': 'wa10000006', 'fid': 'f1003', 
'tcount': 12.0, 'price': 12.0, 'mid': 'm1002',
': 's10000001', 'name': '入库单', 'rcount': 12.0, 'moreinfo': '无'}

"""
