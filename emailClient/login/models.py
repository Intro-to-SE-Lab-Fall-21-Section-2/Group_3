from django.db import models

# Create your models here.
class Email(models.Model):
   mailNum = models.BigIntegerField()
   sender = models.CharField(max_length=256)
   recipient = models.CharField(max_length=256)
   subject = models.CharField(max_length=1000)
   body = models.TextField()


