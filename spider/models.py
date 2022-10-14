from django.db import models

# Create your models here.
class Audio(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True,verbose_name="资源名")
    src = models.CharField(max_length=255, blank=True, null=True,verbose_name="资源地址")
    class Meta:
        db_table = 'audio'
        verbose_name = '音频'
        verbose_name_plural = '音频'

