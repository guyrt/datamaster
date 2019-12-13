from django.urls import path
from teams import views


urlpatterns = [
    path('team/', views.TeamList.as_view(), name='teams'),
    path('team/<int:pk>/', views.TeamDetails.as_view(), name='team'),
    path('team/<int:team_pk>/user/', views.UserInTeamList.as_view(), name='users'),
    path('user/<int:pk>/', views.UserDetails.as_view(), name='user'),
]
