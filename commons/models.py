from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Home(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    lat = models.FloatField()
    lon = models.FloatField()

    alarm = models.BooleanField(default=False)
    light = models.BooleanField(default=False)

    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
    	return self.name

class Person(models.Model):
    name = models.CharField(max_length=200)
    photo = models.ImageField()
    card = models.CharField(max_length=20)
    home = models.ForeignKey(Home, on_delete=models.CASCADE)

    def __str__(self):
    	return self.name

class Access(models.Model):
    home = models.ForeignKey(Home, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, blank=True, null=True, on_delete=models.CASCADE)
    accessed_at = models.DateTimeField(auto_now_add=True)
    triggered_alarm = models.BooleanField(default=False)

class Reading(models.Model):
    home = models.ForeignKey(Home, on_delete=models.CASCADE)
    temperature = models.FloatField()
    humidity = models.FloatField()
    gas = models.FloatField()
    illumination = models.FloatField()

    lecture_at = models.DateTimeField(auto_now_add=True)

class Instruction(models.Model):
    home = models.ForeignKey(Home, on_delete=models.CASCADE)
    command = models.CharField(max_length=200)
    theresold = models.FloatField(blank=True, null=True)
    
    executed = models.BooleanField(default=False)
    executed_at = models.DateTimeField()
