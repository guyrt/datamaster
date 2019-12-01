from django.contrib.auth.models import User
from rest_framework import serializers
from teams.models import Team, Membership


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['pk', 'is_active', 'team_name', 'team_slug']


class MembershipSerializer(serializers.ModelSerializer):

    class Meta:
        model = Membership
        fields = ['pk', 'is_active', 'user', 'team']


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):

        user = User.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = User
        fields = ['username', 'pk', 'password', 'email']

