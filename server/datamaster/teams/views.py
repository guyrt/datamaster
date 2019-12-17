from django.shortcuts import render
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import NotFound
from django.contrib.auth.models import User

from datamaster.mixins import DeactivateModelMixin
from teams.models import Team, Membership
from teams.permissions import grant_access
from teams.serializers import TeamSerializer, MembershipSerializer, UserSerializer


class TeamViewSet(viewsets.ModelViewSet):

    serializer_class = TeamSerializer
    lookup_field = 'slug'
    lookup_value_regex = '[\w_-]+'

    def get_queryset(self):
        return Team.objects.filter(is_active=True).filter(membership__user=self.request.user)


class MembershipList(generics.ListCreateAPIView):
    serializer_class = MembershipSerializer

    def get_queryset(self):
        return Membership.objects.filter(is_active=True).filter(user=self.request.user)

class UserInTeamList(generics.ListCreateAPIView):
    
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        """Overrides create to also set team"""
        team_id = self.kwargs['team_pk']
        try:
            # Ensure that the authenticated user can create a user in this team.
            team = Team.objects.for_user(self.request.user).get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound()
        
        user = serializer.save()
        grant_access(user, team)

    def get_queryset(self):
        # Show users that share your team.
        team_id = self.kwargs['team_pk']
        try:
            team = Team.objects.for_user(self.request.user).get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound()
        return User.objects.filter(is_active=True).filter(membership__is_active=1, membership__team=team)


class MembershipDetails(generics.RetrieveUpdateAPIView, DeactivateModelMixin):
    queryset = Membership.objects.filter(is_active=True)
    serializer_class = MembershipSerializer


class UserDetails(generics.RetrieveUpdateAPIView, DeactivateModelMixin):
    queryset = User.objects.filter(is_active=True)
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = UserSerializer
    lookup_field = 'username'
