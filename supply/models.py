from django.db import models


# Create your models here.
class Gongsi(models.Model):
    myid = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=40, blank=True, null=True)
    address = models.CharField(max_length=40, blank=True, null=True)
    postcode = models.CharField(max_length=40, blank=True, null=True)
    country = models.CharField(max_length=40, blank=True, null=True)
    telephone = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        db_table = 'gongsi'
        verbose_name = '公司'
        verbose_name_plural = '公司'

    def __str__(self):
        return self.myid+'|'+self.name


class Wuliao(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    type = models.CharField(max_length=40, blank=True, null=True)
    salegroup = models.CharField(max_length=40, blank=True, null=True)
    saleway = models.CharField(max_length=40, blank=True, null=True)
    calcutype = models.CharField(max_length=10, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'wuliao'
        verbose_name = '物料'
        verbose_name_plural = '物料'

    def __str__(self):
        return self.id+'|'+self.type+'|'+self.desc


class Securityquestion(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    question = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'securityquestion'
        verbose_name = '保密问题'
        verbose_name_plural = '保密问题'

    def __str__(self):
        return self.id+'|'+self.question


class Yuangong(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    choices = (
        ("0", "系统管理员"),
        ("1", "供应商员工"),
        ("2", "采购员工"),
        ("3", "库存员工"),
        ("4", "采购经理"),
        ("5", "库存经理"),
        ("6", "生产经理"),
        ("7", "操作历史"),
    )
    office = models.CharField(max_length=20, blank=True, null=True, choices=choices)
    password = models.CharField(max_length=40, blank=True, null=True)
    username = models.CharField(max_length=40, blank=True, null=True)
    choices1 = (
        (1, "启用"),
        (0, "禁用")
    )
    isactive = models.IntegerField(blank=True, null=True, choices=choices1)
    choices2 = (
        (1, "是"),
        (0, "否")
    )
    email=models.CharField(max_length=40,blank=True,null=True)
    businessid = models.ForeignKey(to='Gongsi', to_field='myid', on_delete=models.CASCADE)
    questionid = models.ForeignKey(to='Securityquestion',to_field='id',on_delete=models.CASCADE,default="")
    verification = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        db_table = 'yuangong'
        verbose_name = '员工'
        verbose_name_plural = '员工'

    def __str__(self):
        return self.id + '|' + self.username


class Xiaoxi(models.Model):
    fromId = models.ForeignKey(to='Yuangong', to_field='id', related_name='from_id', on_delete=models.CASCADE)
    toId = models.ForeignKey(to='Yuangong', to_field='id', related_name='to_id', on_delete=models.CASCADE)
    time = models.DateTimeField(blank=True, null=True)
    context = models.TextField(blank=True, null=True)
    choices = (
        (1, "已读"),
        (0, "未读")
    )
    read = models.IntegerField(default=0, choices=choices)
    class Meta:
        db_table = 'xiaoxi'
        verbose_name = '消息'
        verbose_name_plural = '消息'

    def __str__(self):
        return self.fromId_id+" 发往 "+self.toId_id + '|' + self.time.strftime("%Y-%m-%d %H:%M:%S")

class Gongchang(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    type = models.CharField(max_length=40, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'gongchang'
        verbose_name = '工厂'
        verbose_name_plural = '工厂'

    def __str__(self):
        return self.id + '|' + self.address


class Gongyingshang(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    address = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=40, blank=True, null=True)
    createtime = models.DateTimeField(blank=True, null=True)
    updatetime = models.DateTimeField(blank=True, null=True)
    createnumberid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE,
                                       related_name='updatenumberid')
    updatenumberid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE,
                                       related_name='createnumberid')

    class Meta:
        db_table = 'gongyingshang'
        verbose_name = '供应商'
        verbose_name_plural = '供应商'

    def __str__(self):
        return self.id + '|' + self.name + '|' + self.address


class Gongyingguanxi(models.Model):
    supplyid = models.ForeignKey(to='Gongyingshang', to_field='id', on_delete=models.CASCADE)
    materialid = models.ForeignKey(to='Wuliao', to_field='id', on_delete=models.CASCADE)
    createtime = models.DateTimeField(blank=True, null=True)
    updatetime = models.DateTimeField(blank=True, null=True)
    createid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE, related_name='updateid')
    updateid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE, related_name='createid')

    class Meta:
        db_table = 'gongyingguanxi'
        verbose_name = '供应关系'
        verbose_name_plural = '供应关系'

    def __str__(self):
        return self.supplyid_id + '|' + self.materialid_id+ '|' + self.updateid_id


class Gongchangkucun(models.Model):
    facid = models.ForeignKey(to='Gongchang', to_field='id', on_delete=models.CASCADE)
    maid = models.ForeignKey(to='Wuliao', to_field='id', on_delete=models.CASCADE)
    inventoryonroad = models.FloatField(blank=True, null=True)
    inventorytemp = models.FloatField(blank=True, null=True)
    inventoryunrest = models.FloatField(blank=True, null=True)
    inventoryfreeze = models.FloatField(blank=True, null=True)
    updatetime = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'gongchangkucun'
        verbose_name = '工厂库存'
        verbose_name_plural = '工厂库存'

    def __str__(self):
        return self.facid_id + '|' + self.maid_id+ '|' + self.updatetime.strftime("%Y-%m-%d %H:%M:%S")


class Caigouxuqiu(models.Model):
    demandid = models.CharField(primary_key=True, max_length=40)
    facid = models.ForeignKey(to='Gongchang', to_field='id', on_delete=models.CASCADE)
    maid = models.ForeignKey(to='Wuliao', to_field='id', on_delete=models.CASCADE)
    price = models.FloatField(blank=True, null=True)
    tcount = models.FloatField(blank=True, null=True)
    choices = (
        (0, "未审核"),
        (1, "已审核"),
        (2, "已完成")
    )
    status = models.IntegerField(blank=True, null=True, choices=choices)
    createuserid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE,
                                     related_name="verifyuserid")
    createtime = models.DateTimeField(blank=True, null=True)
    verifyuserid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE, related_name="createuserid"
                                     , blank=True, null=True)
    verifytime = models.DateTimeField(blank=True, null=True)
    # 1表示删除，当作删除操作时逻辑删除，不进行物理删除
    isdelete = models.IntegerField(default=0)

    class Meta:
        db_table = 'caigouxuqiu'
        verbose_name = '采购需求'
        verbose_name_plural = '采购需求'

    def __str__(self):
        return self.demandid + '|' + str(self.facid_id) + '|' + str(self.price)

class Xunjiadan(models.Model):
    inquiryid = models.CharField(primary_key=True, max_length=40)
    demandid = models.ForeignKey(to='Caigouxuqiu', to_field='demandid', on_delete=models.CASCADE)
    supplyid = models.ForeignKey(to='Gongyingshang', to_field='id', on_delete=models.CASCADE)
    # tcount = models.FloatField(blank=True, null=True)
    validitytime = models.DateTimeField(blank=True, null=True)
    createuserid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE)
    createtime = models.DateTimeField(blank=True, null=True)
    # 1表示删除，当作删除操作时逻辑删除，不进行物理删除
    isdelete = models.IntegerField(default=0)

    class Meta:
        db_table = 'xunjiadan'
        verbose_name = '询价单'
        verbose_name_plural = '询价单'

    def __str__(self):
        return self.demandid_id + '|' + self.inquiryid + '|' + self.supplyid_id


class Baojiadan(models.Model):
    quoteid = models.CharField(primary_key=True, max_length=40)
    inquiryid = models.ForeignKey(to='Xunjiadan', to_field='inquiryid', on_delete=models.CASCADE)
    supplyid = models.ForeignKey(to='Gongyingshang', to_field='id', on_delete=models.CASCADE)
    # tcount = models.FloatField(blank=True, null=True)
    quote = models.FloatField(blank=True, null=True)
    validitytime = models.DateTimeField(blank=True, null=True)
    createtime = models.DateTimeField(blank=True, null=True)
    createuserid = models.ForeignKey(blank=True, null=True, to='Yuangong', to_field='id', on_delete=models.CASCADE)
    choices = (
        (0, "待评估"),
        (1, "接受"),
        (2, "拒绝"),
        (3, "已完成")
    )
    isreceived = models.IntegerField(blank=True, null=True, choices=choices)
    # 1表示删除，当作删除操作时逻辑删除，不进行物理删除
    isdelete = models.IntegerField(default=0)

    class Meta:
        db_table = 'baojiadan'
        verbose_name = '报价单'
        verbose_name_plural = '报价单'

    def __str__(self):
        return self.quoteid + '|' + self.inquiryid_id + '|' + self.supplyid_id


class Caigoudan(models.Model):
    purchaseid = models.CharField(primary_key=True, max_length=40)
    quoteid = models.ForeignKey(to='Baojiadan', to_field='quoteid', on_delete=models.CASCADE)
    # price = models.FloatField(blank=True, null=True)
    # tcount = models.FloatField(blank=True, null=True)
    createuserid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE)
    createtime = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    choices = (
        (1, "是"),
        (-1,"库存冻结"),
        (0, "否")
    )
    iscomplete = models.IntegerField(blank=True, choices=choices, null=True)
    # 1表示删除，当作删除操作时逻辑删除，不进行物理删除
    isdelete = models.IntegerField(default=0)

    class Meta:
        db_table = 'caigoudan'
        verbose_name = '采购单'
        verbose_name_plural = '采购单'

    def __str__(self):
        return self.quoteid_id + '|' + self.purchaseid + '|' + self.createuserid_id


class Zanshoudan(models.Model):
    temid = models.CharField(primary_key=True, max_length=40)
    purchaseid = models.ForeignKey(to='Caigoudan', to_field='purchaseid', on_delete=models.CASCADE)
    # tcount = models.FloatField(blank=True, null=True)
    choices1 = (
        (1, "通过"),
        (0, "不通过"),
        (-1, "未检查")
    )
    qualitycheckinfo = models.IntegerField(blank=True, null=True, choices=choices1)
    choices2 = (
        (1, "通过"),
        (0, "不通过"),
        (-1, "未检查")
    )
    quantitycheckinfo = models.IntegerField(blank=True, null=True, choices=choices2)
    choices3 = (
        (-1, "已冻结"),
        (1, "已入库"),
        (0, "未入库"),
        (2, "已入库")
    )
    isreceived = models.IntegerField(blank=True, null=True, choices=choices3)
    moreinfo = models.TextField(blank=True, null=True)
    createtime = models.DateTimeField(blank=True, null=True)
    # 1表示删除，当作删除操作时逻辑删除，不进行物理删除
    isdelete = models.IntegerField(default=0)

    # 给暂收单加个创建时间
    class Meta:
        db_table = 'zanshoudan'
        verbose_name = '暂收单'
        verbose_name_plural = '暂收单'

    def __str__(self):
        return self.temid + '|' + self.purchaseid_id



class Rukudan(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    temid = models.ForeignKey(to='Zanshoudan', to_field='temid', on_delete=models.CASCADE)
    receivecount = models.FloatField(blank=True, null=True)
    # purcount = models.FloatField(blank=True, null=True)
    createtime = models.DateTimeField(blank=True, null=True)
    createusersid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE,
                                      related_name="updateusersid")
    moreinfo = models.TextField(blank=True, null=True)
    # 1表示删除，当作删除操作时逻辑删除，不进行物理删除
    isdelete = models.IntegerField(default=0)

    class Meta:
        db_table = 'rukudan'
        verbose_name = '入库单'
        verbose_name_plural = '入库单'

    def __str__(self):
        return self.id + '|' + self.temid_id


class Fapiao(models.Model):
    invoiceid = models.CharField(max_length=40, primary_key=True)
    purchaseid = models.ForeignKey(to='Caigoudan', to_field='purchaseid', on_delete=models.CASCADE)
    money = models.FloatField(blank=True, null=True)
    # totalcount = models.FloatField(blank=True, null=True)
    fee = models.FloatField(blank=True, null=True)
    # 税款改成运费
    createtime = models.DateTimeField(blank=True, null=True)
    createuserid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE)
    moreinfo = models.CharField(max_length=255, blank=True, null=True)
    # 1表示删除，当作删除操作时逻辑删除，不进行物理删除
    isdelete = models.IntegerField(default=0)

    class Meta:
        db_table = 'fapiao'
        verbose_name = '发票'
        verbose_name_plural = '发票'

    def __str__(self):
        return self.invoiceid + '|' + self.purchaseid_id+ '|' + self.createtime.strftime("%Y-%m-%d %H:%M:%S")
