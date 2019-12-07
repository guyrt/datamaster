from django.contrib.auth.models import User
from rest_framework import serializers
from syncer.models import ClientDataSet
from teams.models import Team, Membership
from teams.permissions import has_access


class ClientDataSetSerializer(serializers.ModelSerializer):

    team = serializers.SlugRelatedField(
        queryset=Team.objects.filter(is_active=1),
        slug_field='team_slug'
    )

    user = serializers.SlugRelatedField(
        queryset=User.objects.filter(is_active=1),
        slug_field='username'
    )

    def validate(self, data):
        if not has_access(data['user'], data['team']):
            raise serializers.ValidationError("Invalid team for user.")
        return data

    def create(self, validated_data):
        m, created = ClientDataSet.objects.get_or_create(
            team=validated_data['team'],
            user=validated_data['user'],
            metaargs_guid=validated_data['metaargs_guid'],
            timepath=validated_data['timepath'],
            name=validated_data['name'],
            project=validated_data['project'],
            defaults={
                'local_machine_name': validated_data['local_machine_name'],
                'local_path': validated_data['local_path'],
                'local_machine_time': validated_data['local_machine_time']
            })

        if created:
            return m
        else:
            return self.update(m, validated_data)

    class Meta:
        model = ClientDataSet
        fields = ['team', 'user', 'metaargs_guid', 'timepath', 'name',
        'project', 'local_path', 'local_machine_name', 'local_machine_time']
