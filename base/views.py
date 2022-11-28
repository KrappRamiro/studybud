from .models import Room, Topic, Message
from .forms import RoomForm, MessageForm
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'Lets learn python!'},
#     {'id': 2, 'name': 'Design with me'},
#     {'id': 3, 'name': 'Frontend developers lounge'},
# ]


def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Incorrect Password")

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # We use commit=False, so it doesnt automatically adds the user to the database
            # Instead, it saves the data from the form in the user variable
            # We do that because we want to modify the data
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.info(request, f"Created user {user.username}")
            # We can login the user with the data from the form because we used UserCreationForm, i guess ?
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occurred during registration")

    context = {'form': form}
    return render(request, 'base/login_register.html', context)


def home(request):
    # q means query
    # Gets the query (?q="my_topic_name_here") from the url.
    # If there is no "q" in the url, the variable q gets the value ''
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # Look for all the rooms that contains the characters in the topic name
    # This uses the Q db model from Django
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()
    room_count = rooms.count()
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/home.html', context)


def room(request, pk):  # pk comes from urls.py
    room = Room.objects.get(id=pk)
    # With message_set.all() we can query child objects of a specific room, and get a set of all the messages. The messages are the children
    # _set.all() works for ONE TO MANY RELATIONSHIPS
    # -created for desc order, created for asc order
    room_messages = room.message_set.all().order_by('-created')
    # For many to many, we just use .all()
    participants = room.participants.all()

    if request.method == 'POST':
        # Create the message if the user commented
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        # Add the user as a room participant
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
    }
    return render(request, 'base/room.html', context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        # Fills the form with the data from the POST request
        form = RoomForm(request.POST)
        if form.is_valid():
            print("Form for createRoom is valid")
            form.save()  # Saves the form in the database, based in the Room modal
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    # We want to get some data prefilled, to know what Room we are editing.
    # Because of that, we use instance = room
    form = RoomForm(instance=room)

    # Check if the user editing the room is the owner of the room
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        # We use instance=room to tell it which room to update. If we dont do that, it will just create another room
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    # Check if the user editing the room is the owner of the room
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    # Check if the user editing the message is the owner of the message
    if request.user != message.user:
        return HttpResponse('You are not allowed here!')

    if request.method == "POST":
        message.delete()
        # TODO: This should send you back to the Room, not the home page
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url="login")
def updateMessage(request, pk):
    message = Message.objects.get(id=pk)
    # We want to get some data prefilled, to know what message we are editing.
    # Because of that, we use instance = message
    form = MessageForm(instance=message)

    # Check if the user editing the message is the owner of the message
    if request.user != message.user:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        # We use instance=message to tell it which message to update. If we dont do that, it will just create another message
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            # TODO: This should send you back to the Room, not the home page
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)
