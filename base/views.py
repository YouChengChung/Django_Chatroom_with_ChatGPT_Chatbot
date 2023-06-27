from django.shortcuts import render, redirect
#from django.http import HttpResponse
from django.contrib import messages #login時的error message
#from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Room,Topic
from .forms import RoomForm #, UserForm, MyUserCreationForm
# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'Lets learn python!'},
#     {'id': 2, 'name': 'Design with me'},
#     {'id': 3, 'name': 'Frontend developers'},
# ]


def loginPage(request):
    page = 'login'
    # if request.user.is_authenticated:
    #     return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try: #確認 user存在
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist') #Flash message

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exit') #Flash message

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)| #filter parameter符合的topic，icontains使指打部分也能篩選
        Q(name__icontains=q)
        #Q(host__icontains=q)
        )
    topics = Topic.objects.all()
    rooms_count  = rooms.count()

    context={'rooms': rooms,'topics':topics,'rooms_count':rooms_count}
    return render (request, "base/home.html",context)

def room(request,pk):
    room = Room.objects.get(id=pk)

    context = {'room': room,
               
               }
    return render(request, "base/room.html",context)


#@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    #topics = Topic.objects.all()
    if request.method == 'POST':
        print(request.POST)# 查看後端收到REQUSET內容，為dict格式
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home') #在urls.py裡，home page有name，所以這邊不用使用網址，用name作為redirect就行
    #     topic_name = request.POST.get('topic')
    #     topic, created = Topic.objects.get_or_create(name=topic_name)

    #     Room.objects.create(
    #         host=request.user,
    #         topic=topic,
    #         name=request.POST.get('name'),
    #         description=request.POST.get('description'),
    #     )
    #     return redirect('home')

    context = {'form': form}

    return render(request, 'base/room_form.html', context)



#@login_required(login_url='login')
def updateRoom(request, pk): #pk:what item are we update
    room = Room.objects.get(id=pk) #get the item we are updating
    form = RoomForm(instance=room) #表格將會prefill with room，也就是剛get到的值
    # topics = Topic.objects.all()
    # if request.user != room.host:
    #     return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        form = RoomForm(request.POST,instance=room)#instance = ? :Which room to update
        if form.is_valid():
            form.save()
            return redirect('home')
    #     topic_name = request.POST.get('topic')
    #     topic, created = Topic.objects.get_or_create(name=topic_name)
    #     room.name = request.POST.get('name')
    #     room.topic = topic
    #     room.description = request.POST.get('description')
    #     room.save()
    #     return redirect('home')

    context = {'form': form, 'room': room}
    return render(request, 'base/room_form.html', context)



def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    # if request.user != room.host:
    #     return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})
