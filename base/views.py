from .models import Room, Topic, Message
from .forms import RoomForm, MessageForm, UserForm
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count

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
        username = request.POST.get('username')
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
            user.username = user.username
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
    #topics = Topic.objects.all()
    # https://stackoverflow.com/questions/23033769/django-order-by-count
    topics = Topic.objects.annotate(
        count=Count('room')).order_by('-count')[0:5]  # [0:5] to get the first five
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )
    print(User.objects.all())

    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):  # pk comes from urls.py
    room = Room.objects.get(id=pk)
    # With message_set.all() we can query child objects of a specific room, and get a set of all the messages. The messages are the children
    # _set.all() works for ONE TO MANY RELATIONSHIPS
    room_messages = room.message_set.all()
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


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        # Fills the form with the data from the POST request
        # i think its .get("topic") because <input name="topic"/>
        topic_name = request.POST.get('topic')
        # Created is a boolean, and its value depends if topic_name was created (True) or if topic_name was found and got (False)
        # topic will always have a value, and it depends on topic_name
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get('description')
        )
        ''' Old way of doing it, no longer valid since we can now create custom topics by just typing them
         form = RoomForm(request.POST)
         if form.is_valid():
             room = form.save(commit=False)
             room.host = request.user
             # Saves the form in the database, based in the Room modal
             room.save()
        '''
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)  # Get the room to edit
    topics = Topic.objects.all()  # Get the list of topics
    # We want to get some data prefilled, to know what Room we are editing.
    # Because of that, we use instance = room
    form = RoomForm(instance=room)  # Get the form with the prefilled values

    # Check if the user editing the room is the owner of the room
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')  # Get the topic from the form
        # Created is a boolean, and its value depends if topic_name was created (True) or if topic_name was found and got (False)
        # topic will always have a value, and it depends on topic_name
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')  # Get the name from the form
        room.topic = topic  # Get the topic from get_or_create
        room.description = request.POST.get(
            'description')  # Get the desc from the form
        room.save()  # Save the room in the db using the values set earlier in the code
        return redirect('home')
    context = {'form': form, 'topics': topics, 'room': room}
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


@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        # I use instance=user so form.save() updates the info. If i didnt use it, form.save() would create a new user
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update-user.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # topics = Topic.objects.filter(name__icontains=q)
    # https://stackoverflow.com/questions/23033769/django-order-by-count
    topics = Topic.objects.annotate(
        count=Count('room')).order_by('-count').filter(name__icontains=q)
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)


def activityPage(request):
    room_messages = Message.objects.all()
    context = {'room_messages': room_messages}
    return render(request, "base/activity.html", context)
