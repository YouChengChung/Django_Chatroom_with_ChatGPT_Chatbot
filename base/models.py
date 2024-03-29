from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here. #create db tables

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model): #Room 是 Topic 的child
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True) #Class topic在上面，所以直接用，如果是在下面，要以字串'Topic'呼叫
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(
        User, related_name='participants', blank=True) #前面用過User表格了，這裡要在取用另一個User表格，所以要related_name
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
       ordering = ['-updated', '-created']

    def __str__(self):
        return self.name

class Message(models.Model):                                    #user 是one-to-many:一個使用者對多個留言
    user = models.ForeignKey(User, on_delete=models.CASCADE) #django內建user model，直接import就可以用
    room = models.ForeignKey(Room, on_delete=models.CASCADE)#Room 是parent table，on_delete:當parent table被刪除時，要怎麼做
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]
    

class gptMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    gptreply = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    openai_api_key = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
# 創建 UserProfile 模型的實例，當新的 User 實例被創建時
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()