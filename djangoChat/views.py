""" djangoChat views """
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib import auth
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
import json
from djangoChat.models import Message, ChatUser

from django.shortcuts import render

import datetime
from django.utils.timezone import now as utcnow
from django.utils.safestring import mark_safe
from django.utils.html import escape


def index(request):
    """ index method  """

    if request.user.username and request.user.profile.chat_logged_in:
        # intial chat json data

        latest_msgs = Message.objects.order_by('-time')[:20]
        msgs_array = []
        for msg in reversed(latest_msgs):

            chat_user = ChatUser.objects.get(u_id=msg.user_ID)
            msg_dict = {
                'id':msg.id,
                'user':chat_user.username,
                'msg':msg.message,
                'time':msg.time.strftime('%I:%M:%S %p').lstrip('0'),
                'gravatar':chat_user.gravatar_url
            }
            msgs_array.append(msg_dict)
    
        data = json.dumps(msgs_array)
        # end json
        context = {'data':mark_safe(data)}
        return render(request, 'djangoChat/index.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))

def login(request):
    """ performs login """

    context = {'error':''}

    # if user is already logged into chat
    if request.user.username and request.user.profile.chat_logged_in:
        return HttpResponseRedirect(reverse('index'))
        

    if request.method == 'POST':
        username = request.POST.get('username', '') #return '' if no username
        password = request.POST.get('password', '')

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            chat_user = request.user.profile
            chat_user.chat_logged_in = True
            chat_user.last_accessed = utcnow()
            chat_user.save()
            


            return HttpResponseRedirect(reverse('index'))
        else:
            context['error'] = ' wrong credentials try again'
            return render(request, 'djangoChat/login.html', context)


    context.update(csrf(request))        
    return render(request, 'djangoChat/login.html', context)


def logout(request):
    """ performs logout """
    chat_user = request.user.profile
    chat_user.chat_logged_in = False
    chat_user.save()
    return HttpResponse('succesfully logged out of chat')


@csrf_exempt
def post_messages(request):
    """ post messege """
    if request.method == 'POST':
        msg_json = json.loads(request.body)
        msg = msg_json.get('msg')
        userID = request.user.profile.u_id
        message = Message(user_ID=userID, message=msg)
        message.save()


        res = {
            'id':message.id,
            'msg':message.message,
            'user':request.user.profile.username,
            'time':message.time.strftime('%I:%M:%S %p').lstrip('0'),
            'gravatar':request.user.profile.gravatar_url
        }
        data = json.dumps(res)
        return HttpResponse(data,content_type="application/json")

@csrf_exempt
def chat_api(request):
    """ chat api """
    if request.method == 'POST':


        msg_json = json.loads(request.body)
        msg = escape(msg_json.get('msg'))  #escape html
        userID = request.user.profile.u_id
        message = Message(user_ID=userID, message=msg)
        message.save()


        res = {
            'id':message.id,
            'msg':message.message,
            'user':request.user.profile.username,
            'time':message.time.strftime('%I:%M:%S %p').lstrip('0'),
            'gravatar':request.user.profile.gravatar_url
        }
        data = json.dumps(res)
        return HttpResponse(data, content_type="application/json")



    # get request
    r = Message.objects.order_by('-time')[:20]
    res = []
    for msgs in reversed(r) :

        chat_user = ChatUser.objects.get(u_id=msgs.user_ID)

        res.append({
            'id':msgs.id,
            'user':chat_user.username,
            'msg':msgs.message,
            'time':msgs.time.strftime('%I:%M:%S %p').lstrip('0'),
            'gravatar':chat_user.gravatar_url
        })
    
    data = json.dumps(res)

    
    return HttpResponse(data, content_type="application/json")


def get_logged_chat_users(request):
    """ get logged chat users """

    logged_chat_users = ChatUser.objects.filter(chat_logged_in=True)

    # check if user has left chat room and log him out (45 seconds)
    for user in logged_chat_users:
        elapsed = utcnow() - user.last_accessed
        if elapsed > datetime.timedelta(seconds=45):
            user.chat_logged_in = False
            user.save()
    # check logged users again
    logged_chat_users = ChatUser.objects.filter(chat_logged_in=True)
    print "after check time and update"
   
    users_list = []
    for i in logged_chat_users:
        users_list.append({
            'username': i.username,
            'gravatar':i.gravatar_url,
            'id':i.u_id
        })
    data = json.dumps(users_list)
     

    return HttpResponse(data, content_type="application/json")


def update_time(request):
    """ update last accessed time of user """
    if request.user.username:
        user = request.user.profile
        user.last_accessed = utcnow()
        user.chat_logged_in = True
        user.save()
        return HttpResponse('updated')
    return HttpResponse('who are you?')
