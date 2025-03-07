from django.db import models


class Lesson(models.Model):
    title = models.CharField(max_length=100, blank=True)
    text = models.CharField(max_length=5000)
    audio = models.FileField(upload_to="uploads/audio/%Y/%m/", null=True)
    english_audio = models.FileField(upload_to="uploads/audio/%Y/%m/", null=True)
    image = models.ImageField(upload_to="uploads/image/%Y/%m/", null=True)
