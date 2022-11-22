from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

rooms = [
    {'id': 1, 'name': 'Lets learn python!'},
    {'id': 2, 'name': 'Design with me'},
    {'id': 3, 'name': 'Frontend developers lounge'},
]


def home(request):
    return render(request, 'base/home.html', {'rooms':rooms})


def room(request, pk): #pk comes from urls.py
    room = None
    for r in rooms:
        if r['id'] == int(pk):
            room = r
    context = {'room': room}
    return render(request, 'base/room.html', context)
