from django.shortcuts import render
from rest_framework import viewsets

from datamaster.mixins import DeactivateModelMixin
from syncer.models import ClientDataSet
from syncer.serializers import ClientDataSetSerializer


class ClientDataSetQuerySet(object):

    def get_queryset(self):
        return ClientDataSet.objects.filter(team__team_slug=self.kwargs['team_slug']).filter(is_active=True)


class ClientDataSetViewSet(ClientDataSetQuerySet, viewsets.ModelViewSet):
    
    serializer_class = ClientDataSetSerializer
