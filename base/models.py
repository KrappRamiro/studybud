from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    # ManyToManyField creates a many to many relationship between the User model and the Room model
    # Normally, we wouldnt need to use related_name, but because we already use the model User in the host declaration, we have to do it
    participants = models.ManyToManyField(
        User, related_name='participants', blank=True)
    # auto_now takes a snapshot every time we save this
    updated = models.DateTimeField(auto_now=True)
    # auto_now_add only saves the value the first time we create this
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # updated meanns ascending, -updated means descending
        ordering = ['-updated', '-created']

    def __str__(self):
        return str(self.name)


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # updated meanns ascending, -updated means descending
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]
