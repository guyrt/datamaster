from django.shortcuts import render
from rest_framework import generics
from django.auth.models import User
from team.models import Team, Membership
from team.serializers import TeamSerializer, MembershipSerializer


class TeamList(generics.ListCreateAPIView):
    queryset = Team.objects.filter(active=True)
    serializer_class = TeamSerializer


class MembershipList(generics.ListCreateAPIView):
    queryset = Membership.objects.filter(active=True)
    serializer_class = MembershipSerializer


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.filter(active=True)
    serializer_class = UserSerializer


class TeamDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Team.objects.filter(active=True)
    serializer_class = TeamSerializer
