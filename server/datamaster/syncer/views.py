from django.shortcuts import render
from rest_framework import generics

from datamaster.mixins import DeactivateModelMixin
from syncer.models import ClientDataSet
from syncer.serializers import ClientDataSetSerializer


class ClientDataSetList(generics.ListCreateAPIView):
    queryset = ClientDataSet.objects.filter(is_active=True)
    serializer_class = ClientDataSetSerializer


class ClientDataSetDetails(generics.RetrieveUpdateAPIView, DeactivateModelMixin):
    queryset = ClientDataSet.objects.filter(is_active=True)
    serializer_class = ClientDataSetSerializer
