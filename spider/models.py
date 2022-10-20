from django.db import models

# Create your models here.
class Audio(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True,verbose_name="资源名")
    src = models.CharField(max_length=255, blank=True, null=True,verbose_name="资源地址")
    class Meta:
        db_table = 'audio'
        verbose_name = '音频'
        verbose_name_plural = '音频'

class Image(models.Model):
    type=models.CharField(max_length=255,blank=True,null=True,verbose_name="分类")
    name=models.CharField(max_length=255,blank=True,null=True,verbose_name="名称")
    src=models.TextField(blank=True,null=True,verbose_name="资源地址")
    class Meta:
        db_table = 'image'
        verbose_name = '图片'
        verbose_name_plural = '图片'



class Picture(models.Model):
    name=models.CharField(max_length=255,blank=True,null=True,verbose_name="名称")
    src=models.TextField(blank=True,null=True,verbose_name="资源地址")
    class Meta:
        db_table = 'picture'
        verbose_name = '图片'
        verbose_name_plural = '图片'

class New1(models.Model):
    type=models.CharField(max_length=255,blank=True,null=True,verbose_name="分类")
    name=models.CharField(max_length=255,blank=True,null=True,verbose_name="名称")
    src=models.TextField(blank=True,null=True,verbose_name="资源地址")
    class Meta:
        db_table = 'new1'
        verbose_name = '图片1'
        verbose_name_plural = '图片1'

class New2(models.Model):
    type=models.CharField(max_length=255,blank=True,null=True,verbose_name="分类")
    name=models.CharField(max_length=255,blank=True,null=True,verbose_name="名称")
    src=models.TextField(blank=True,null=True,verbose_name="资源地址")
    class Meta:
        db_table = 'new2'
        verbose_name = '图片2'
        verbose_name_plural = '图片2'

class New3(models.Model):
    type=models.CharField(max_length=255,blank=True,null=True,verbose_name="分类")
    name=models.CharField(max_length=255,blank=True,null=True,verbose_name="名称")
    src=models.TextField(blank=True,null=True,verbose_name="资源地址")
    class Meta:
        db_table = 'new3'
        verbose_name = '图片3'
        verbose_name_plural = '图片3'

class New4(models.Model):
    type=models.CharField(max_length=255,blank=True,null=True,verbose_name="分类")
    name=models.CharField(max_length=255,blank=True,null=True,verbose_name="名称")
    src=models.TextField(blank=True,null=True,verbose_name="资源地址")
    class Meta:
        db_table = 'new4'
        verbose_name = '图片4'
        verbose_name_plural = '图片4'

class Audiosrc(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True,verbose_name="资源名")
    src = models.CharField(max_length=255, blank=True, null=True,verbose_name="资源地址")
    class Meta:
        db_table = 'audiosrc'
        verbose_name = '本地音频'
        verbose_name_plural = '本地音频'


class Video(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True,verbose_name="资源名")
    src = models.CharField(max_length=255, blank=True, null=True,verbose_name="资源地址")
    class Meta:
        db_table = 'video'
        verbose_name = '本地视频频'
        verbose_name_plural = '本地视频'



class Vi(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True,verbose_name="资源名")
    visrc = models.CharField(max_length=255, blank=True, null=True,verbose_name="资源地址")
    ausrc = models.CharField(max_length=255, blank=True, null=True,verbose_name="资源地址")
    class Meta:
        db_table = 'vi'
        verbose_name = '本地无声视频频'
        verbose_name_plural = '本地无声视频'




class Gupiao(models.Model):
    lirunfenpei = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    meigushouyi = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    meigujingzichan = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    shujuleixing = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    shujunianfen = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    baobiaokuadu = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    DEDUCT_BASIC_EPS= models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    bianjishijian = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    shifouweixin = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    meigujingyingxianjinliuliang=models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    xiugaishijian = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    ORG_CODE = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    jinglirun = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    nianfen = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    hangye = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    jidu = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    baobiaoshijian = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    daima = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    gupiaodaima = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    gupiaoming = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    gupiaoleixing = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    gupiaoleixingdaima = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    jinglirunhuanbizengzhang = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    jingliruntongbizengzhang = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    yingyezongshouru = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    jiaoyishichang = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    jiaoyishichangdaima = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    jiaoyishichangZJG = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    gengxinriqi = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    jingzichanshouyilv = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    xiaoshoumaolilv = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    zongshourujiduhuanbizengzhang = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")
    zongshourujidutongbizengzhang = models.CharField(max_length=255, blank=True, null=True,verbose_name="每股收益")
    ZGXL = models.CharField(max_length=255, blank=True, null=True,verbose_name="利润分配")

    class Meta:
        db_table = 'gupiao'
        verbose_name = '股票'
        verbose_name_plural = '股票'




