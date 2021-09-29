from django.db import models

# Create your models here.
class Email(models.Model):
   mailID = models.BigIntegerField(primary_key=True)
   sender = models.CharField(max_length=256)
   subject = models.CharField(max_length=1000)
   body = models.TextField()

