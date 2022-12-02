from django.urls import path
from . import views


# name = "" is used in {%url 'name-here' %} in html
urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('room/<str:pk>/', views.room, name="room"),  # pk means primary key
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),

    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),
    path('update-message/<str:pk>/', views.updateMessage, name="update-message"),
    path('update-user/', views.updateUser, name="update-user"),
    path('topics', views.topicsPage, name="topics"),
    path('activity', views.activityPage, name="activity"),
]
