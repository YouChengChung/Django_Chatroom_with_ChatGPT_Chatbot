from django.contrib import admin

# Register your models here.
from .models import Room, Topic, Message,gptMessage,UserProfile
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(gptMessage)
admin.site.register(UserProfile)