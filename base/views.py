from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages #login時的error message
from django.contrib.auth.decorators import login_required #用@控制必須login
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm #內建註冊表格
from .models import Room,Topic,Message,gptMessage,UserProfile
from .forms import RoomForm ,UserForm #, MyUserCreationForm

from .chatgpt import chatgpt

# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'Lets learn python!'},
#     {'id': 2, 'name': 'Design with me'},
#     {'id': 3, 'name': 'Frontend developers'},
# ]


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated: #已登入者會直接導向home
        return redirect('home') #在urls.py裡，home page有name，所以這邊不用使用網址，用name作為redirect就行

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        email = request.POST.get('email')
        password = request.POST.get('password')

        try: #確認 user存在
            user = User.objects.get(username=username)

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print(username,'has log in')
                return redirect('home')
            else:
                pass
                messages.error(request, 'Incorrect Password') #Flash message



        except:
            messages.error(request, 'User does not exist') #Flash message
            pass

        



    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user) #註冊完立刻登入
            return redirect('home')
        else:
            print(form.errors)  # 打印表單錯誤信息以便調試
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html',{'form':form})



def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)| #filter parameter符合的topic，icontains使指打部分也能篩選
        Q(name__icontains=q)
        #Q(host__icontains=q)
        )
    topics = Topic.objects.all()[0:5]
    rooms_count  = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains = q))


    context={'rooms': rooms,
             'topics':topics,
             'rooms_count':rooms_count,
             'room_messages':room_messages}
    return render (request, "base/home.html",context)

def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all() # query child object of a specific room:message是Model name(小寫)，跟room有關的message
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body') #在room.html命名input為body
        )
        room.participants.add(request.user)
        return redirect('room', pk= room.id)
    context = {'room': room,
               'room_messages':room_messages,
               'participants':participants
               }
    return render(request, "base/room.html",context)


def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user,
               'rooms':rooms,
               'room_messages':room_messages,
               'topics':topics}
    return render(request,'base/profile.html',context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        print(request.POST)# 查看後端收到REQUSET內容，為dict格式
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name) #決定輸入的topic是否存在
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home') #在urls.py裡，home page有name，所以這邊不用使用網址，用name作為redirect就行
    
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room =  form.save(commit=False)
        #     room.host = request.user
        #     form.save()
        #     return redirect('home') 
        
    context = {'form': form,'topics':topics}
    return render(request, 'base/room_form.html', context)



@login_required(login_url='login')
def updateRoom(request, pk): #pk:what item are we update
    room = Room.objects.get(id=pk) #get the item we are updating
    form = RoomForm(instance=room) #表格將會prefill with room，也就是剛get到的值
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)    
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')#在urls.py裡，home page有name，所以這邊不用使用網址，用name作為redirect就行

    context = {'form': form,'topics':topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form =UserForm(instance=user)

    if request.method=='POST':
        form =UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)

    context = {'form':form}
    return render(request,'base/update-user.html',context)



def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics':topics}
    return render(request,'base/topics.html', context)


def activityPage(request):
    room_messages = Message.objects.all()

    context={'room_messages':room_messages}
    return render(request,'base/activity.html',context)


def update_user_api_key(user, api_key):
    """
    Update the user's API key in UserProfile.
    """
    
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    user_profile.openai_api_key = api_key
    user_profile.save()
    return created  # 返回一个布尔值，指示是否建了新的 UserProfile(更新的話是false，新增是true)

@login_required(login_url='login')
def gpt(request):
    gptmsgobjs=gptMessage.objects.filter(user=request.user)
    gptmsgs=[[eachdata.body,eachdata.gptreply,eachdata] for eachdata in gptmsgobjs]
    
    #print('gptmsgs:',gptmsgs.gptreply)
    reply  = ''
    user_input=""
    warningmsg=""
    if request.method=='POST':
        try:
            user_profile = request.user.userprofile
            api_key = user_profile.openai_api_key
        except UserProfile.DoesNotExist:
            api_key = None
        # 檢查是否設置了API密鑰
        if not api_key:
            print('here')
            messages.error(request, "請先設置您的 OpenAI API key。")
        chatbot = chatgpt(api_key)
        print(f"the openai apikey： {chatbot.api_key}")
        prompt_input = request.POST.get('userInput')
        # 來自prompt的msg(用來更新apikey)
        if prompt_input:  
            # print(f"request.POST.get('userInput')={request.POST.get('userInput')}")
            print(f"Received prompt input: {prompt_input}")
            is_new_api_key = update_user_api_key(request.user, prompt_input)
            messages.success(request, f"API Key has been updated")
        # input box 輸入
        elif 'body' in request.POST and len(request.POST.get('body'))>1:
            user_input = request.POST.get('body')  # 这里可以替换为用户的输入
            print('waiting for chatgpt response...')
            reply = chatbot.get_reply(user_input)
            if reply:
                gptMessage.objects.create(
                    user = request.user,
                    body = request.POST.get('body'),
                    gptreply = reply
                )

            else:
                # js彈出警訊：cant not get gpt's reply
                messages.warning(request, f"Fail to get response from GPT,try to reset the api_key")
                

            print(f'Print the GPT response：{reply}')


            return redirect('chatgpt')

    context={'reply':reply,
             'user_input':user_input,
             'gptmsgs':gptmsgs,
             }
    return render(request,'base/GPTroom.html',context)


@login_required(login_url='login')
def deletegpt(request,pk):
    
    gptmsg = gptMessage.objects.filter(id=pk)
    gptmsg_1 = gptmsg[0].body
    print(gptmsg_1,"will be deleted!")
    if request.method == 'POST':
        gptmsg.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': gptmsg_1})
