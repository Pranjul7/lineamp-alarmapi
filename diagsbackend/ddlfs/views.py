from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from . import serializers
from .models import Alarm, Node, Acknowledgement


class AlarmViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AlarmSerializer

    def get_queryset(self):
        current = Alarm.objects.filter(resolved__isnull=True)
        return current


class AlarmHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AlarmSerializer

    def get_queryset(self):
        history = Alarm.objects.filter(resolved__isnull=False)
        return history


class NodeViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.NodeSerializer

    def get_queryset(self):pip
        nodes = Node.objects.all()
        return nodes


class AckViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.NodeSerializer

    def get_queryset(self):
        ack = Acknowledgement.objects.all()
        return ack








