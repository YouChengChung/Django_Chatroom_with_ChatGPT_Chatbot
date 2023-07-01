from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer 

@api_view(['GET']) #what http methods are allowed to access the view
def getRoutes(request):
    # show all routes in api
    routes=[
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]
    return Response(routes)

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    #print("**************",type(rooms)) #this type cant covert to serial
    serializer = RoomSerializer(rooms,many=True) #many=True: one or mutiple objects to be convert
    print('An api request to get all rooms, method=',request.method)
    print('request from ip :',request.META.get('REMOTE_ADDR'))

    return Response(serializer.data)

@api_view(['GET'])
def getRoom(request,pk):
    room = Room.objects.get(id=pk)
    #print("**************",type(rooms)) #this type cant covert to serial
    serializer = RoomSerializer(room,many=False) #many=True: one or mutiple objects to be convert
    return Response(serializer.data)