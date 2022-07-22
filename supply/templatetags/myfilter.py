from django import template
register = template.Library()

@register.filter(name="front_add")
def front_add(arg,val):
    return str(val)+str(arg)

@register.filter(name="table_status")
def table_status(arg,val):
    choices = (
        (0, "未审核"),
        (1, "已审核"),
        (2, "已完成")
    )
    #CSS中样式： 0-黄色  1-蓝色  2-绿色  3-红色
    cgxq={0:0,1:1,2:2} #采购需求对应(0, "未审核"),(1, "已审核"),(2, "已完成")

    return "table_status_{}".format(arg)