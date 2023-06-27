from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User





# class MyUserCreationForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ['name', 'username', 'email', 'password1', 'password2']


class RoomForm(ModelForm):
    class Meta: #create a form based on values in models.Room
        model = Room
        fields = '__all__' #give me all those field，也能用['name','body']格式選擇
        #exclude = ['host', 'participants']


# class UserForm(ModelForm):
#     class Meta:
#         model = User
#         fields = ['avatar', 'name', 'username', 'email', 'bio']
