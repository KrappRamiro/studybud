from django.db import models

# Create your models here.

class Room(models.Model):
    #host = 
    #topic = 
    name = models.CharField(max_length=200)
    description = models.TextField(null = True, blank="True")
    #participants = 
    updated = models.DateTimeField(auto_now=True) #auto_now takes a snapshot every time we save this
    created = models.DateTimeField(auto_now_add=True) #auto_now_add only saves the value the first time we create this


    def __str__(self):
        return str(self.name)
    