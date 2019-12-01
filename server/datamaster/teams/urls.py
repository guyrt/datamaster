from django.urls import path
from teams import views


urlpatterns = [
    path('team/', views.TeamList.as_view()),
    path('team/<int:pk>/', views.TeamDetails.as_view()),
]
