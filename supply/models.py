from django.db import models


# Create your models here.
class Gongsi(models.Model):
    myid = models.CharField(primary_key=True, max_length=40,verbose_name="公司ID")
    name = models.CharField(max_length=40, blank=True, null=True,verbose_name="公司名")
    address = models.CharField(max_length=40, blank=True, null=True,verbose_name="地址")
    postcode = models.CharField(max_length=40, blank=True, null=True,verbose_name="邮编")
    country = models.CharField(max_length=40, blank=True, null=True,verbose_name="国家")
    telephone = models.CharField(max_length=40, blank=True, null=True,verbose_name="电话")

    class Meta:
        db_table = 'gongsi'
        verbose_name = '公司'
        verbose_name_plural = '公司'

    def __str__(self):
        return self.myid+'|'+self.name


class Wuliao(models.Model):
    id = models.CharField(primary_key=True, max_length=40,verbose_name="物料编号")
    type = models.CharField(max_length=40, blank=True, null=True,verbose_name="类型")
    salegroup = models.CharField(max_length=40, blank=True, null=True,verbose_name="销售组")
    saleway = models.CharField(max_length=40, blank=True, null=True,verbose_name="销售渠道")
    calcutype = models.CharField(max_length=10, blank=True, null=True,verbose_name="计量单位")
    desc = models.TextField(blank=True, null=True,verbose_name="物料描述")

    class Meta:
        db_table = 'wuliao'
        verbose_name = '物料'
        verbose_name_plural = '物料'

    def __str__(self):
        return self.id+'|'+self.type+'|'+self.desc


class Securityquestion(models.Model):
    id = models.CharField(primary_key=True, max_length=40,verbose_name="ID")
    question = models.CharField(max_length=255, blank=True, null=True,verbose_name="问题")

    class Meta:
        db_table = 'securityquestion'
        verbose_name = '保密问题'
        verbose_name_plural = '保密问题'

    def __str__(self):
        return self.id+'|'+self.question


class Yuangong(models.Model):
    id = models.CharField(primary_key=True, max_length=40,verbose_name="员工编号")
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
    office = models.CharField(max_length=20, blank=True, null=True, choices=choices,verbose_name="职位")
    password = models.CharField(max_length=40, blank=True, null=True,verbose_name="密码")
    username = models.CharField(max_length=40, blank=True, null=True,verbose_name="姓名")
    choices1 = (
        (1, "启用"),
        (0, "禁用")
    )
    isactive = models.IntegerField(blank=True, null=True, choices=choices1,verbose_name="是否启用")

    email=models.CharField(max_length=40,blank=True,null=True,verbose_name="电子邮箱")
    businessid = models.ForeignKey(to='Gongsi', to_field='myid', on_delete=models.CASCADE,verbose_name="公司")
    questionid = models.ForeignKey(to='Securityquestion',to_field='id',on_delete=models.CASCADE,default="",verbose_name="密保问题")
    verification = models.CharField(max_length=40, blank=True, null=True,verbose_name="问题答案")

    class Meta:
        db_table = 'yuangong'
        verbose_name = '员工'
        verbose_name_plural = '员工'

    def __str__(self):
        return self.id + '|' + self.username


class Xiaoxi(models.Model):
    fromId = models.ForeignKey(to='Yuangong', to_field='id', related_name='from_id', on_delete=models.CASCADE,verbose_name="发送者")
    toId = models.ForeignKey(to='Yuangong', to_field='id', related_name='to_id', on_delete=models.CASCADE,verbose_name="接收者")
    time = models.DateTimeField(blank=True, null=True,verbose_name="时间")
    context = models.TextField(blank=True, null=True,verbose_name="内容")
    choices = (
        (1, "已读"),
        (0, "未读")
    )
    read = models.IntegerField(default=0, choices=choices,verbose_name="是否已读")
    class Meta:
        db_table = 'xiaoxi'
        verbose_name = '消息'
        verbose_name_plural = '消息'

    def __str__(self):
        return self.fromId_id+" 发往 "+self.toId_id + '|' + self.time.strftime("%Y-%m-%d %H:%M:%S")

class Gongchang(models.Model):
    id = models.CharField(primary_key=True, max_length=40,verbose_name="工厂编号")
    type = models.CharField(max_length=40, blank=True, null=True,verbose_name="类型")
    address = models.CharField(max_length=255, blank=True, null=True,verbose_name="地址")

    class Meta:
        db_table = 'gongchang'
        verbose_name = '工厂'
        verbose_name_plural = '工厂'

    def __str__(self):
        return self.id + '|' + self.address


class Gongyingshang(models.Model):
    id = models.CharField(primary_key=True, max_length=40,verbose_name="供应商编号")
    address = models.CharField(max_length=255, blank=True, null=True,verbose_name="地址")
    name = models.CharField(max_length=40, blank=True, null=True,verbose_name="名称")
    createtime = models.DateTimeField(blank=True, null=True,verbose_name="创建时间")
    updatetime = models.DateTimeField(blank=True, null=True,verbose_name="修改时间")
    createnumberid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE,
                                       related_name='updatenumberid',verbose_name="创建者")
    updatenumberid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE,
                                       related_name='createnumberid',verbose_name="修改者")

    class Meta:
        db_table = 'gongyingshang'
        verbose_name = '供应商'
        verbose_name_plural = '供应商'

    def __str__(self):
        return self.id + '|' + self.name + '|' + self.address


class Gongyingguanxi(models.Model):
    supplyid = models.ForeignKey(to='Gongyingshang', to_field='id', on_delete=models.CASCADE,verbose_name="供应商")
    materialid = models.ForeignKey(to='Wuliao', to_field='id', on_delete=models.CASCADE,verbose_name="物料")
    createtime = models.DateTimeField(blank=True, null=True,verbose_name="创建时间")
    updatetime = models.DateTimeField(blank=True, null=True,verbose_name="修改时间")
    createid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE, related_name='updateid',verbose_name="创建者")
    updateid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE, related_name='createid',verbose_name="修改者")

    class Meta:
        db_table = 'gongyingguanxi'
        verbose_name = '供应关系'
        verbose_name_plural = '供应关系'

    def __str__(self):
        return self.supplyid_id + '|' + self.materialid_id+ '|' + self.updateid_id


class Gongchangkucun(models.Model):
    facid = models.ForeignKey(to='Gongchang', to_field='id', on_delete=models.CASCADE,verbose_name="工厂")
    maid = models.ForeignKey(to='Wuliao', to_field='id', on_delete=models.CASCADE,verbose_name="物料")
    inventoryonroad = models.FloatField(blank=True, null=True,verbose_name="在途库存")
    inventorytemp = models.FloatField(blank=True, null=True,verbose_name="暂存库存")
    inventoryunrest = models.FloatField(blank=True, null=True,verbose_name="未限制使用库存")
    inventoryfreeze = models.FloatField(blank=True, null=True,verbose_name="冻结库存")
    updatetime = models.DateTimeField(blank=True, null=True,verbose_name="更新时间")

    class Meta:
        db_table = 'gongchangkucun'
        verbose_name = '工厂库存'
        verbose_name_plural = '工厂库存'

    def __str__(self):
        return self.facid_id + '|' + self.maid_id+ '|' + self.updatetime.strftime("%Y-%m-%d %H:%M:%S")


class Caigouxuqiu(models.Model):
    demandid = models.CharField(primary_key=True, max_length=40,verbose_name="请购单号")
    facid = models.ForeignKey(to='Gongchang', to_field='id', on_delete=models.CASCADE,verbose_name="工厂")
    maid = models.ForeignKey(to='Wuliao', to_field='id', on_delete=models.CASCADE,verbose_name="物料")
    price = models.FloatField(blank=True, null=True,verbose_name="价格")
    tcount = models.FloatField(blank=True, null=True,verbose_name="数量")
    choices = (
        (0, "未审核"),
        (1, "已审核"),
        (2, "已完成")
    )
    status = models.IntegerField(blank=True, null=True, choices=choices,verbose_name="状态")
    createuserid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE,
                                     related_name="verifyuserid",verbose_name="创建者")
    createtime = models.DateTimeField(blank=True, null=True,verbose_name="创建时间")
    verifyuserid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE, related_name="createuserid"
                                     , blank=True, null=True,verbose_name="审核者")
    verifytime = models.DateTimeField(blank=True, null=True,verbose_name="审核时间")
    # 1表示删除，当作删除操作时逻辑删除，不进行物理删除
    isdelete = models.IntegerField(default=0,verbose_name="是否删除")

    class Meta:
        db_table = 'caigouxuqiu'
        verbose_name = '采购需求'
        verbose_name_plural = '采购需求'

    def __str__(self):
        return self.demandid + '|' + str(self.facid_id) + '|' + str(self.price)

class Xunjiadan(models.Model):
    inquiryid = models.CharField(primary_key=True, max_length=40,verbose_name="询价单号")
    demandid = models.ForeignKey(to='Caigouxuqiu', to_field='demandid', on_delete=models.CASCADE,verbose_name="请购单号")
    supplyid = models.ForeignKey(to='Gongyingshang', to_field='id', on_delete=models.CASCADE,verbose_name="供应商")
    # tcount = models.FloatField(blank=True, null=True)
    validitytime = models.DateTimeField(blank=True, null=True,verbose_name="有效期")
    createuserid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE,verbose_name="创建者")
    createtime = models.DateTimeField(blank=True, null=True,verbose_name="创建时间")
    # 1表示删除，当作删除操作时逻辑删除，不进行物理删除
    isdelete = models.IntegerField(default=0,verbose_name="是否删除")

    class Meta:
        db_table = 'xunjiadan'
        verbose_name = '询价单'
        verbose_name_plural = '询价单'

    def __str__(self):
        return self.demandid_id + '|' + self.inquiryid + '|' + self.supplyid_id


class Baojiadan(models.Model):
    quoteid = models.CharField(primary_key=True, max_length=40,verbose_name="报价单号")
    inquiryid = models.ForeignKey(to='Xunjiadan', to_field='inquiryid', on_delete=models.CASCADE,verbose_name="询价单号")
    supplyid = models.ForeignKey(to='Gongyingshang', to_field='id', on_delete=models.CASCADE,verbose_name="供应商")
    # tcount = models.FloatField(blank=True, null=True)
    quote = models.FloatField(blank=True, null=True,verbose_name="报价")
    validitytime = models.DateTimeField(blank=True, null=True,verbose_name="有效期")
    createtime = models.DateTimeField(blank=True, null=True,verbose_name="创建时间")
    createuserid = models.ForeignKey(blank=True, null=True, to='Yuangong',
                                     to_field='id', on_delete=models.CASCADE,verbose_name="创建者")
    choices = (
        (0, "待评估"),
        (1, "接受"),
        (2, "拒绝"),
        (3, "已完成")
    )
    isreceived = models.IntegerField(blank=True, null=True, choices=choices,verbose_name="状态")
    # 1表示删除，当作删除操作时逻辑删除，不进行物理删除
    isdelete = models.IntegerField(default=0,verbose_name="是否删除")

    class Meta:
        db_table = 'baojiadan'
        verbose_name = '报价单'
        verbose_name_plural = '报价单'

    def __str__(self):
        return self.quoteid + '|' + self.inquiryid_id + '|' + self.supplyid_id


class Caigoudan(models.Model):
    purchaseid = models.CharField(primary_key=True, max_length=40,verbose_name="采购单号")
    quoteid = models.ForeignKey(to='Baojiadan', to_field='quoteid', on_delete=models.CASCADE,verbose_name="报价单号")
    # price = models.FloatField(blank=True, null=True)
    # tcount = models.FloatField(blank=True, null=True)
    createuserid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE,verbose_name="创建者")
    createtime = models.DateTimeField(blank=True, null=True,verbose_name="创建时间")
    deadline = models.DateTimeField(blank=True, null=True,verbose_name="截止日期")
    choices = (
        (1, "是"),
        (-1,"库存冻结"),
        (0, "否")
    )
    iscomplete = models.IntegerField(blank=True, choices=choices, null=True,verbose_name="状态")
    # 1表示删除，当作删除操作时逻辑删除，不进行物理删除
    isdelete = models.IntegerField(default=0,verbose_name="是否删除")

    class Meta:
        db_table = 'caigoudan'
        verbose_name = '采购单'
        verbose_name_plural = '采购单'

    def __str__(self):
        return self.quoteid_id + '|' + self.purchaseid + '|' + self.createuserid_id


class Zanshoudan(models.Model):
    temid = models.CharField(primary_key=True, max_length=40,verbose_name="暂收但号")
    purchaseid = models.ForeignKey(to='Caigoudan', to_field='purchaseid', on_delete=models.CASCADE,verbose_name="采购单号")
    # tcount = models.FloatField(blank=True, null=True)
    choices1 = (
        (1, "通过"),
        (0, "不通过"),
        (-1, "未检查")
    )
    qualitycheckinfo = models.IntegerField(blank=True, null=True, choices=choices1,verbose_name="质检信息")
    choices2 = (
        (1, "通过"),
        (0, "不通过"),
        (-1, "未检查")
    )
    quantitycheckinfo = models.IntegerField(blank=True, null=True, choices=choices2,verbose_name="量检信息")
    choices3 = (
        (-1, "已冻结"),
        (1, "已入库"),
        (0, "未入库"),
        (2, "已入库")
    )
    isreceived = models.IntegerField(blank=True, null=True, choices=choices3,verbose_name="是否收货")
    moreinfo = models.TextField(blank=True, null=True,verbose_name="备注")
    createtime = models.DateTimeField(blank=True, null=True,verbose_name="创建时间")
    # 1表示删除，当作删除操作时逻辑删除，不进行物理删除
    isdelete = models.IntegerField(default=0,verbose_name="是否删除")

    # 给暂收单加个创建时间
    class Meta:
        db_table = 'zanshoudan'
        verbose_name = '暂收单'
        verbose_name_plural = '暂收单'

    def __str__(self):
        return self.temid + '|' + self.purchaseid_id



class Rukudan(models.Model):
    id = models.CharField(primary_key=True, max_length=40,verbose_name="入库单号")
    temid = models.ForeignKey(to='Zanshoudan', to_field='temid', on_delete=models.CASCADE,verbose_name="暂存单号")
    receivecount = models.FloatField(blank=True, null=True,verbose_name="实际入库数")
    # purcount = models.FloatField(blank=True, null=True)
    createtime = models.DateTimeField(blank=True, null=True,verbose_name="创建时间")
    createusersid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE,
                                      related_name="updateusersid",verbose_name="创建者")
    moreinfo = models.TextField(blank=True, null=True,verbose_name="备注")
    # 1表示删除，当作删除操作时逻辑删除，不进行物理删除
    isdelete = models.IntegerField(default=0,verbose_name="是否删除")

    class Meta:
        db_table = 'rukudan'
        verbose_name = '入库单'
        verbose_name_plural = '入库单'

    def __str__(self):
        return self.id + '|' + self.temid_id


class Fapiao(models.Model):
    invoiceid = models.CharField(max_length=40, primary_key=True,verbose_name="发票单号")
    purchaseid = models.ForeignKey(to='Caigoudan', to_field='purchaseid', on_delete=models.CASCADE,verbose_name="采购单号")
    money = models.FloatField(blank=True, null=True,verbose_name="订单额")
    # totalcount = models.FloatField(blank=True, null=True)
    fee = models.FloatField(blank=True, null=True,verbose_name="运费")
    # 税款改成运费
    createtime = models.DateTimeField(blank=True, null=True,verbose_name="开票时间")
    createuserid = models.ForeignKey(to='Yuangong', to_field='id', on_delete=models.CASCADE,verbose_name="开票人")
    moreinfo = models.CharField(max_length=255, blank=True, null=True,verbose_name="备注")
    # 1表示删除，当作删除操作时逻辑删除，不进行物理删除
    isdelete = models.IntegerField(default=0,verbose_name="是否删除")

    class Meta:
        db_table = 'fapiao'
        verbose_name = '发票'
        verbose_name_plural = '发票'

    def __str__(self):
        return self.invoiceid + '|' + self.purchaseid_id+ '|' + self.createtime.strftime("%Y-%m-%d %H:%M:%S")
