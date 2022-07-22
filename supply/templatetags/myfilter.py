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