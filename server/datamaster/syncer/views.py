from django.shortcuts import render
from rest_framework import generics
from syncer.models import ClientDataSet
from syncer.serializers import ClientDataSetSerializer


class ClientDataSetList(generics.ListCreateAPIView):
    queryset = ClientDataSet.objects.filter(active=True)
    serializer_class = ClientDataSetSerializer


class ClientDataSetDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClientDataSet.objects.filter(active=True)
    serializer_class = ClientDataSetSerializer
