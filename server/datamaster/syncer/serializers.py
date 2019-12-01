from rest_framework import serializers
from syncer.models import ClientDataSet


class ClientDataSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientDataSet
        fields = ['team', 'user', 'metaargs_guid', 'timepath', 'name',
        'project', 'local_path', 'local_machine_name', 'is_active']