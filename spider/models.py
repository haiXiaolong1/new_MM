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


class Audiosrc(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True,verbose_name="资源名")
    src = models.CharField(max_length=255, blank=True, null=True,verbose_name="资源地址")
    class Meta:
        db_table = 'audiosrc'
        verbose_name = '本地音频'
        verbose_name_plural = '本地音频'


