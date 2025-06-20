from django.db import models


class Lesson(models.Model):
    title = models.CharField(max_length=100, blank=True)
    text = models.CharField(max_length=5000)
    audio = models.FileField(upload_to="uploads/audio/%Y/%m/", null=True)
    english_audio = models.FileField(upload_to="uploads/audio/%Y/%m/", null=True)
    image = models.ImageField(upload_to="uploads/image/%Y/%m/", null=True)


class Character(models.Model):
    character = models.CharField(max_length=10)
    timestamp = models.TimeField(auto_now_add=True)
    right_count = models.IntegerField()
