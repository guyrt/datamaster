from django.contrib.auth.models import User
from rest_framework import serializers
from syncer.models import ClientDataSet, ClientBranch
from teams.models import Team, Membership
from teams.permissions import has_access


class ClientBranchSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientBranch
        fields = ['name', 'team']



class ClientBranchInDataSetField(serializers.RelatedField):

    queryset = ClientBranch.objects.filter(is_active=1)

    def to_representation(self, value):
        return value.name

    def get_object(self, view_name, view_args, view_kwargs):
        # TODO - fix
        lookup_kwargs = {
           'organization__slug': view_kwargs['organization_slug'],
           'pk': view_kwargs['customer_pk']
        }
        return self.get_queryset().get(**lookup_kwargs)

    def to_internal_value(self, data):
        return data


class ClientDataSetSerializer(serializers.ModelSerializer):

    team = serializers.SlugRelatedField(
        queryset=Team.objects.filter(is_active=1),
        slug_field='team_slug'
    )

    user = serializers.SlugRelatedField(
        queryset=User.objects.filter(is_active=1),
        slug_field='username'
    )

    branch = ClientBranchInDataSetField()

    local_machine_guid = serializers.CharField()

    def validate(self, data):
        if not has_access(data['user'], data['team']):
            raise serializers.ValidationError("Invalid team for user.")
        
        branch_name = data['branch']
        branch, created = ClientBranch.objects.get_or_create(
            team=data['team'], 
            name=branch_name,
            defaults={
                'created_by': data['user']
            }
        )
        if not created:
            branch.is_active = True
            branch.save()
        data['branch'] = branch

        return data

    def create(self, validated_data):
        m, created = ClientDataSet.objects.get_or_create(
            team=validated_data['team'],
            user=validated_data['user'],
            metaargs_guid=validated_data['metaargs_guid'],
            timepath=validated_data['timepath'],
            name=validated_data['name'],
            project=validated_data['project'],
            branch=validated_data['branch'],
            defaults={
                'local_machine_name': validated_data['local_machine_name'],
                'local_path': validated_data['local_path'],
                'local_machine_time': validated_data['local_machine_time'],
                'local_machine_guid': validated_data['local_machine_guid']
            })

        if created:
            return m
        else:
            return self.update(m, validated_data)

    class Meta:
        model = ClientDataSet
        fields = ['team', 'user', 'metaargs_guid', 'timepath', 'name',
        'project', 'local_path', 'local_machine_name', 'local_machine_time',
        'branch', 'local_machine_guid']
