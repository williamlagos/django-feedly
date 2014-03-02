#
# This file is part of Efforia project.
#
# Copyright (C) 2011-2013 William Oliveira de Lagos <william@efforia.com.br>
#
# Efforia is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Efforia is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Efforia. If not, see <http://www.gnu.org/licenses/>.
#

import httplib,urllib2,urllib,json,ast,time,random,mimetypes
from datetime import datetime,timedelta,date
from django.contrib.auth.models import User
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse as response
from django.http import HttpResponseRedirect as redirect
from django.template import Context,Template

from feedly.models import Page,user,superuser
from feedly.feed import Mosaic

class Efforia(Mosaic):
    def __init__(self): pass
    def verify_permissions(self,request):
        perm = 'super'
        if 'permissions' in request.COOKIES:
            perm = request.COOKIES['permissions']
        permissions = True if 'super' in perm else False
        return permissions
    def start(self,request):
        # Painel do usuario
        u = user('efforia'); 
        permissions = self.verify_permissions(request)
        actions = settings.EFFORIA_ACTIONS; apps = []
        for a in settings.EFFORIA_APPS: apps.append(actions[a])
        return render(request,'interface.html',{'static_url':settings.STATIC_URL,
                                            'user':user('efforia'),'perm':permissions,
                                            'name':'%s %s' % (u.first_name,u.last_name),'apps':apps
                                            },content_type='text/html')
        # Pagina inicial
        #p = list(Page.objects.filter(user=superuser()))
        #return render(request,'index.html',{'static_url':settings.STATIC_URL},content_type='text/html')
    def external(self,request):
        u = self.current_user(request)
        sellables = Sellable.objects.filter(user=u)
        for s in sellables: s.paid = True
        return self.redirect('/')
    def profile_view(self,request,name):
        if len(list(User.objects.filter(username=name))) > 0: request.session['user'] = name
        r = redirect('/')
        r.set_cookie('permissions','view_only')
        return r
    def json_decode(self,string):
        j = json.loads(string,'utf-8')
        return ast.literal_eval(j)
    def url_request(self,url,data=None,headers={}):
        request = urllib2.Request(url=url,data=data,headers=headers)
        request_open = urllib2.urlopen(request)
        return request_open.geturl()
    def do_request(self,url,data=None,headers={}):
        response = ''
        request = urllib2.Request(url=url,data=data,headers=headers)
        try:
            request_open = urllib2.urlopen(request)
            response = request_open.read()
            request_open.close()
        except urllib2.HTTPError,e:
            print url
            print data
            print headers
            print e.code
            print e.msg
            print e.hdrs
            print e.fp
        return response
    def oauth_post_request(self,url,tokens,data={},social='twitter',headers={}):
        pass
        #=======================================================================
        # #api = json.load(open('settings.json','r'))['social']
        # posturl ='%s%s'%(api[social]['url'],url)
        # if 'facebook' in social:
        #     socialurl = '%s?%s'%(posturl,urllib.urlencode({'access_token':tokens}))
        #     if 'start_time' in data: data['start_time'] = data['start_time'].date()
        #     return self.do_request(socialurl,urllib.urlencode(data),headers)
        # else:
        #     access_token,access_token_secret = tokens.split(';')
        #     token = oauth.Token(access_token,access_token_secret)
        #     consumer_key = api[social]['client_key']
        #     consumer_secret = api[social]['client_secret']
        #     consumer = oauth.Consumer(consumer_key,consumer_secret)
        #     client = oauth.Client(consumer,token)
        #     try:
        #         return client.request(posturl,'POST',urllib.urlencode(data))
        #     except urllib2.HTTPError,e:
        #         print e.code
        #         print e.msg
        #         print e.hdrs
        #         print e.fp
        #         return 1
        #=======================================================================
    def refresh_google_token(self,token):
        pass
        #=======================================================================
        # api = json.load(open('settings.json','r'))['social']['google']
        # if not token: token = self.own_access()['google_token']
        # data = urllib.urlencode({
        #     'client_id':      api['client_id'],
        #     'client_secret':  api['client_secret'],
        #     'refresh_token':  token,
        #     'grant_type':    'refresh_token' })
        # return json.loads(self.do_request(api['oauth2_token_url'],data))['access_token']
        #=======================================================================
    def object_token(self,token):
        relations = settings.EFFORIA_TOKENS
        typobject = relations[token]
        return typobject
    def object_byid(self,token,ident):
        obj = self.object_token(token)
        return globals()[obj].objects.filter(id=ident)[0]
    def convert_datetime(self,date_value):
        d = time.strptime(date_value,'%d/%m/%Y')
        return datetime.fromtimestamp(time.mktime(d))
    def authenticate(self,username,password):
        exists = User.objects.filter(username=username)
        if exists:
            if exists[0].check_password(password): 
                return exists
        else: return None
    def authenticated(self):
        name = self.get_current_user()
        if not name: 
            #self.redirect('login')
            self.render('templates/enter.html',STATIC_URL=settings.STATIC_URL)
            return False
        else:
            return True
    def accumulate_points(self,points,request=None):
        if request is None: u = self.current_user()
        else: u = self.current_user(request)
        current_profile = Profile.objects.all().filter(user=u)[0]
        current_profile.points += points
        current_profile.save()
    def own_access(self):
        pass
        #=======================================================================
        # objs = json.load(open('settings.json','r'))
        # google_api = objs['social']['google']
        # twitter_api = objs['social']['twitter']
        # facebook_api = objs['social']['facebook']
        # access = {
        #     'google_token': google_api['client_token'],
        #     'twitter_token': '%s;%s' % (twitter_api['client_token'],twitter_api['client_token_secret']),
        #     'facebook_token': facebook_api['client_token']
        # }
        # return access
        #=======================================================================
