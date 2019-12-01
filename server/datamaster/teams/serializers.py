from django.auth.models import User
from rest_framework import serializers
from teams.models import Team, Membership


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['pk', 'active', 'team_name', 'team_slug']


class MembershipSerializer(serializers.ModelSerializer):

    class Meta:
        model = Membership
        fields = ['pk', 'active', 'user', 'team']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'pk']

