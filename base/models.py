from django.db import models

# Create your models here.


class Room(models.Model):
    # host =
    # topic =
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank="True")
    # participants =
    # auto_now takes a snapshot every time we save this
    updated = models.DateTimeField(auto_now=True)
    # auto_now_add only saves the value the first time we create this
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)


class Message(models.Model):
    # user =
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50]
