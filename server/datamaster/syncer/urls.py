from django.urls import path
from syncer import views

urlpatterns = [
    path('clientdataset/', views.ClientDataSetList.as_view()),
    path('clientdataset/<int:pk>/', views.ClientDataSetDetails.as_view()),
]
