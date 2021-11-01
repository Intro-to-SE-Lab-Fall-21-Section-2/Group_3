from django.db import models

#Store email attachments
class FeedFile(models.Model):
   file = models.FileField(upload_to='files/')

   # Create your models here.
class Email(models.Model):
   mailNum = models.BigIntegerField()
   sender = models.CharField(max_length=256)
   recipient = models.CharField(max_length=256)
   subject = models.CharField(max_length=1000)
   body = models.TextField()
   files=models.ManyToManyField(FeedFile)
   fileCount = models.SmallIntegerField(default=0)
   trashFolder = models.BooleanField(default=False)


