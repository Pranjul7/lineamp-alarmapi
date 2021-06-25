from rest_framework import serializers
from ddlfs.models import Device, Alarm, Acknowledgement, Node


class NodeRefSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Node
        fields = ['id', 'url']


class NodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Node
        fields = '__all__'


class AckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acknowledgement
        fields = '__all__'


class AlarmSerializer(serializers.ModelSerializer):
    node = NodeRefSerializer(read_only=True)
    ack = AckSerializer(read_only=True)

    class Meta:
        model = Alarm
        fields = '__all__'
