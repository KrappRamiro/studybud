from django.forms import ModelForm
from .models import Room, Message


class RoomForm(ModelForm):
    class Meta:
        model = Room  # The form is automatically created based on the Room model
        fields = '__all__'  # Gets all the fields from the Room model


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body']
