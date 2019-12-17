from django.contrib.auth.models import User
from rest_framework import serializers
from teams.models import Team, Membership, get_urls_for_team


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['pk', 'is_active', 'team_name', 'team_slug']


class TeamWithUrlSerializer(serializers.ModelSerializer):

    urls = serializers.SerializerMethodField('get_urls')
    
    def get_urls(self, team):
            return get_urls_for_team(team)
    
    class Meta:
        model = Team
        fields = ['team_name', 'team_slug', 'urls']


            

class MembershipSerializer(serializers.ModelSerializer):

    class Meta:
        model = Membership
        fields = ['pk', 'is_active', 'user', 'team']


class TeamInUserField(serializers.RelatedField):

    def to_representation(self, value):
        qs = Team.objects.for_user(value.instance)
        teams = [TeamWithUrlSerializer(t).data for t in qs]
        return teams


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    membership_set = TeamInUserField(read_only=True)

    def create(self, validated_data):

        user = User.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = User
        fields = ['username', 'pk', 'password', 'email', 'membership_set']

