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
        "items":[],"tittles":[],
        "classes":[],
        "texts":[],
        "foreign":[],
    }
    xjd={
        "items":[],"tittles":[],
        "classes":[],
        "texts":[],
        "foreign":[],
    }
    bjd={
        "items":[],
        "tittles":[],
        "classes":[],
        "texts":[],
        "foreign":[],
    }
    cgd={
        "items":["id","status","fid","sid","mid","tcount","price"],
        "tittles":["采购单号","订单状态","工厂编号","供应商编号","物料编号","采购数量","采购价格"],
        "classes":["full","full","full","full","full","full","full"],
        "texts":[""]*6+["元"],
        "foreign":[False]*7,
    }
    zsd={
        "items":[],"tittles":[],
        "classes":[],
        "texts":[],
        "foreign":[],
    }
    rkd={
        "items":[],"tittles":[],
        "classes":[],
        "texts":[],
        "foreign":[],
    }
    patterns=dict(zip(names,[qgd,xjd,bjd,cgd,zsd,rkd]))
    p=patterns[arg["name"]]
    result=[]
    for idx,k in enumerate(p["items"]):
        d={"name":p["tittles"][idx],"context":arg[k],
           "class":"document_flow_"+p["classes"][idx],
           "text":p["texts"][idx]}
        print(d)
        result.append(d)
    print(result)
    return result

"""
{'name': 'date', 'context': datetime.datetime(2022, 7, 22, 13, 47, 26), 'class': 'try', 'text': '占位'},
 {'name': 'status', 'context': 1, 'class': 'try', 'text': '占位'}, 
 {'name': 'id', 'context': 'pu10000001', 'class': 'try', 'text': '占位'}, 
 {'name': 'fid', 'context': 'f1003', 'class': 'try', 'text': '占位'},
 {'name': 'tcount', 'context': 12.0, 'class': 'try', 'text': '占位'}, 
 {'name': 'price', 'context': 12.0, 'class': 'try', 'text': '占位'}, 
 {'name': 'mid', 'context':'m1002', 'class': 'try', 'text': '占位'}, 
 {'name': 'sid', 'context': 's10000001', 'class': 'try', 'text': '占位'}, 
 {'name': 'name', 'context': '采购单', 'class': 'try', 'text': '占位'}
"""

"""
{% if obj.status %}
<p>
    状态：
    {% if obj.status == 1%}
        已完成
    {% else %}
        未完成
    {% endif %}
</p>
{% endif %}
<p>{{ obj.name }}号：{{ obj.id }}</p>
<p>物料编号：{{ obj.mid }}</p>
{% if obj.fid %}
<p>工厂编号：{{ obj.fid }}</p>
{% endif %}
{% if obj.price %}
<p>价格：{{ obj.price }}</p>
{% endif %}
{% if obj.quote %}
<p>报价：{{ obj.quote }}</p>
{% endif %}
{% if obj.tcount %}
<p>数量：{{ obj.tcount }}</p>
{% endif %}
{% if obj.rcount %}
<p>实际入库数量：{{ obj.rcount }}</p>
{% endif %}
{% if obj.moreinfo %}
<p>备注信息：{{ obj.moreinfo }}</p>
{% endif %}
{% if obj.bid %}
<p>询价公司名：{{ obj.bid }}</p>
{% endif %}
{% if obj.sid %}
<p>供应商编号：{{ obj.sid }}</p>
{% endif %}
"""