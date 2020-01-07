from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.utils import model_meta
from syncer.models import ClientDataSet, ClientBranch, ClientDataSetFact
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


class ClientDataSetFactSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientDataSetFact
        fields = ['key', 'value']


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

    facts = ClientDataSetFactSerializer(many=True, source='get_active_facts')

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

    def update(self, instance, validated_data):
        """ Custom updater required to handle the 'facts' field.
        """
        # Update base
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr == 'facts':
                # Ignore facts, which are handled later.
                pass
            elif attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)
        
        # Set facts for the ClientDataSet. Anything not contained on the instance gets set to deactivated.
        ClientDataSetFact.objects.filter(clientdataset=instance).update(is_active=False)
        for fact in validated_data['facts']:
            k = fact['key']
            v = fact['value']
            fact, created = ClientDataSetFact.objects.get_or_create(key=k, value=v, clientdataset=instance)
            if not created and not fact.is_active:
                fact.is_active = True
                fact.save()
        return instance

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
                'local_machine_guid': validated_data['local_machine_guid']
            })

        if created:
            return m
        else:
            return self.update(m, validated_data)

    class Meta:
        model = ClientDataSet
        fields = ['team', 'user', 'metaargs_guid', 'timepath', 'name',
        'project', 'branch', 'local_machine_guid', 'facts']    
