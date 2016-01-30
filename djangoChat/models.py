""" djangoChar models"""

from django.db import models
from django.contrib.auth.models import User
import hashlib, binascii

class Message(models.Model):
    """Messeges model """
    
    user_ID = models.CharField(max_length=200)

    # messege maxlength only for textarea default formatting not database
    message = models.TextField(max_length=200) 
    time = models.DateTimeField(auto_now_add=True)
    
    






class ChatUser(models.Model):
    """ chat specific user """
    user = models.OneToOneField(User)
    u_id = models.IntegerField()
    username = models.CharField(max_length=300)
    chat_logged_in = models.BooleanField(default=False)
    gravatar_url = models.CharField(max_length=300)
    last_accessed = models.DateTimeField(auto_now_add=True)


def generate_avatar(email):
    """ generate gravatar by hasing email """
    avatar_link = "http://www.gravatar.com/avatar/"
    avatar_link += hashlib.md5(email.lower()).hexdigest()
    return avatar_link

def hash_username(username):
    """returns the hash of username"""
    hashed_string = binascii.crc32(username)
    return hashed_string
    
User.profile = property(lambda u: ChatUser.objects.get_or_create(user=u,defaults={'gravatar_url':generate_avatar(u.email),'username':u.username,'u_id':hash_username(u.username)})[0])
    