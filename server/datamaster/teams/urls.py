from django.urls import path
from teams import views


urlpatterns = [
    path('team/', views.TeamList.as_view(), name='teams'),
    path('team/<int:pk>/', views.TeamDetails.as_view(), name='team'),
    path('membership/', views.MembershipList.as_view(), name='memberships'),
    path('membership/<int:pk>/', views.MembershipDetails.as_view(), name='membership'),
    path('user/', views.UserList.as_view(), name='users'),
    path('user/<int:pk>/', views.UserDetails.as_view(), name='user'),
]