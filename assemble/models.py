from django.db import models
from django.conf import settings
import uuid as uuid_lib

# Create your models here.

""" 登録 """
class URL(models.Model):
    id = models.UUIDField(primary_key=True,verbose_name='id',default=uuid_lib.uuid4,editable=False)
    url = models.URLField(verbose_name='url',max_length=512,null=False,unique=True)
    title = models.CharField(verbose_name='title',max_length=128,blank=True)

    def __str__(self):
        return f'{self.title}'

class Regist(models.Model):
    url = models.ForeignKey(
        to=URL,
        verbose_name='url',
        on_delete=models.CASCADE,
        null=True
        )
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='投稿者',
        on_delete=models.SET_NULL,
        null=True
        )
    
    def __str__(self):
        return f'{self.url}-{self.registered_by}'

""" 検索 """

class BigTag(models.Model):
    id = models.UUIDField(primary_key=True,verbose_name='id',default=uuid_lib.uuid4,editable=False)
    tag = models.CharField(verbose_name='tag',max_length=64,null=False)
    
    def __str__(self):
        return f'{self.tag}'

class FineTag(models.Model):
    id = models.UUIDField(primary_key=True,verbose_name='id',default=uuid_lib.uuid4,editable=False)
    tag = models.CharField(verbose_name='tag',max_length=128,null=False)
    parent = models.ForeignKey(
        to=BigTag,
        verbose_name='親タグ',
        on_delete=models.CASCADE,
        null=False
    )

    def __str__(self):
        return f'{self.tag}-{self.parent}'

class URL_BigTag(models.Model):
    tag = models.ForeignKey(
        to=BigTag,
        verbose_name='カテゴリタグ',
        on_delete=models.CASCADE,
    )
    url = models.ForeignKey(
        to=URL,
        verbose_name='url',
        on_delete=models.CASCADE
    )
    def __str__(self):
        return f'{self.tag}->{self.url}'

class URL_FineTag(models.Model):
    tag = models.ForeignKey(
        to=FineTag,
        verbose_name='詳細タグ',
        on_delete=models.CASCADE,
    )
    url = models.ForeignKey(
        to=URL,
        verbose_name='url',
        on_delete=models.CASCADE
    )
    def __str__(self):
        return f'{self.tag}->{self.url}'



""" 報告系 """

class Report(models.Model):
    url = models.ForeignKey(to=URL,verbose_name='url',on_delete=models.CASCADE)
    
    ReportPattern=(
        (1,'incorrect'),
        (2,'spam'),
        (3,'violence'),
        (4,'harassment'),
        (5,'old'),
        (6,'note_need'),
    )

    report = models.IntegerField(verbose_name='報告',choices=ReportPattern)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='報告者',
        related_name='reported_by',
        on_delete=models.SET_NULL,
        null=True
    )
    text = models.TextField(verbose_name='報告文',blank=True)

    def __str__(self):
        return f'{self.report}->{self.url}'

class ReportThread(models.Model):
    to_report = models.ForeignKey(to=Report,verbose_name='レポート',related_name='to_report',on_delete=models.CASCADE)
    send_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        verbose_name='投稿者',
        related_name='send_by',
        on_delete=models.SET_NULL,
        null=True
    )
    text = models.TextField(verbose_name='コメント',help_text='賛同もしくは反論をコメント')

    def __str__(self):
        return f'{self.send_by}->{self.to_report}'