'''
objebts get from a model ( such as Room.objects.all() )cannot be converted into serialized automatically.
this file will be classes that take a certain objects that we want to serialized, turn it into json data
Basically, take the python object to json.
'''

from rest_framework.serializers import ModelSerializer
from base.models import Room


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'