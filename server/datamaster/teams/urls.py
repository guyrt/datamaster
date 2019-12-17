from django.urls import path
from teams import views


urlpatterns = [
    path('team/<int:team_pk>/user/', views.UserInTeamList.as_view(), name='users'),
    path('user/<str:pk>/', views.UserDetails.as_view(), name='user'),
]
