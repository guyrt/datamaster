from django.shortcuts import render
from rest_framework import generics, permissions
from django.contrib.auth.models import User

from datamaster.mixins import DeactivateModelMixin
from teams.models import Team, Membership
from teams.serializers import TeamSerializer, MembershipSerializer, UserSerializer


class TeamList(generics.ListCreateAPIView):
    queryset = Team.objects.filter(is_active=True)
    serializer_class = TeamSerializer


class MembershipList(generics.ListCreateAPIView):
    queryset = Membership.objects.filter(is_active=True)
    serializer_class = MembershipSerializer


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer


class TeamDetails(generics.RetrieveUpdateAPIView, DeactivateModelMixin):
    queryset = Team.objects.filter(is_active=True)
    serializer_class = TeamSerializer


class MembershipDetails(generics.RetrieveUpdateAPIView, DeactivateModelMixin):
    queryset = Membership.objects.filter(is_active=True)
    serializer_class = MembershipSerializer


class UserDetails(generics.RetrieveUpdateAPIView, DeactivateModelMixin):
    queryset = User.objects.filter(is_active=True)
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = UserSerializer
