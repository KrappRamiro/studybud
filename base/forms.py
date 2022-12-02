from django.forms import ModelForm
from .models import Room, Message
from django.contrib.auth.models import User


class RoomForm(ModelForm):
    class Meta:
        model = Room  # The form is automatically created based on the Room model
        fields = '__all__'  # Gets all the fields from the Room model
        exclude = ['host', 'participants']


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
