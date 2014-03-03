#
# This file is part of Efforia Open Source Initiative.
#
# Copyright (C) 2011-2014 William Oliveira de Lagos <william@efforia.com.br>
#
# Feedly is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Feedly is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Feedly. If not, see <http://www.gnu.org/licenses/>.
#

import json,sys
from django.template import Context,Template
from django.conf import settings
from django.http import HttpResponse as response
from django.shortcuts import render
from django.contrib.sessions.backends.cached_db import SessionStore
from pure_pagination import Paginator,PageNotAnInteger,EmptyPage
from difflib import SequenceMatcher
from models import *

class Activity:
    def __init__(self,user,app):
        config = settings.EFFORIA_OBJS
        self.objects = config[app]
        self.user = user
        self.context = {
                        'apps':settings.EFFORIA_APPS,
                        'static_url':settings.STATIC_URL
                        }
        self.source = """
            <head>
              {% for app in apps %}
                <script type='text/javascript', src='{{STATIC_URL}}js/{{app}}app.js'>   </script>
                <script type='text/javascript', src='{{STATIC_URL}}js/{{app}}events.js'></script>
              {% endfor %}
            </head>
            <body>
              <div class="hidden navigation" href="{{path}}">{{f.render}}</div>
            </body>
        """
    def deadline(self): pass
    def relations(self,feed): pass
    def groupables(self,feed): pass
    def duplicates(self,excludes,obj): pass
    def mosaic(self,request,feed): return ''

class Mosaic:
    def module(self,name): 
        __import__(name)
        return sys.modules[name]
    def class_module(self,module,mclass):
        mod = __import__(module, fromlist=[mclass])
        return getattr(mod,mclass)
    def set_current_user(self,request,name):
        key = request.COOKIES['sessionid']
        s = SessionStore(key)
        s['user'] = name
        s.save()
    def current_user(self,request):
        if 'sessionid' not in request.COOKIES: 
            return User.objects.filter(username='efforia')
        else:
            key = request.COOKIES['sessionid']
            s = SessionStore(key)
            session = s.load()
            if len(session): name = session['user']
            else: name = request.session['user']
            user = User.objects.all().filter(username=name)
            return user[0]
    def view_mosaic(self,request,objlist=None,other=None):
        if 'user' in request.session: u = user(request.session['user'])
        else: u = user('efforia')
        try: page = request.GET.get('page',1)
        except PageNotAnInteger: page = 1
        if objlist is None: f = self.feed(u)
        else: f = objlist
        if other is None: p = u.profile
        else: p = other 
        f.sort(key=lambda item:item.date,reverse=True)
        p = Paginator(f,20,request=request)
        try: objects = p.page(page)
        except EmptyPage: return response('End of feed')
        rendered = self.apps_mosaic(request,objects,u)
        return response(rendered,content_type='text/html')

    def apps_mosaic(self,request,feed,user):
        apps,source = settings.EFFORIA_APPS,''
        for a in apps:
            m = self.module('%s.app'%a)
            app = m.Application(user,a)
            source += app.mosaic(request,feed)
        return source

    def feed(self,userobj,others=None):
        apps = settings.EFFORIA_APPS
        feed = []; exclude = []; people = []
        if others is not None:
            for o in others: people.append(Profile.objects.filter(id=o)[0].user)
        else: 
            people.append(userobj)
            for f in Followed.objects.filter(follower=userobj.id): 
                people.append(Profile.objects.filter(user_id=f.followed)[0].user)
        for u in people:
            feed.append(Profile.objects.filter(user=u)[0])
            for a in apps:
                m = self.module('%s.app'%a)
                app = m.Application(u,a)
                exclude = app.relations(feed)
                app.duplicates(exclude,feed)
                app.groupables(feed) 
        return feed
        
    def deadlines(self,request):
        u = self.current_user(request)
        apps = settings.EFFORIA_APPS
        for a in apps:
            __import__('%s.app'%a)
            m = sys.modules['%s.app'%a]
            app = m.Application(u,a)
            app.deadline()
        return response('Deadlines verified successfully')

class Pages:
    def __init__(self): pass
    def view_page(self,request):
        return render(request,'page.jade',{},content_type='text/html')
    def create_page(self,request):
        print request.POST
        c = request.POST['content']
        t = request.POST['title']
        u = self.current_user(request)
        p = Page(content=c,user=u,name='!#%s' % t)
        p.save()
        return render(request,'pageview.jade',{'content':c},content_type='text/html')
    def edit_page(self,request):
        page_id = int(request.GET['id'])
        p = Page.objects.filter(id=page_id)[0]
        return render(request,'pagedit.jade',{
                       'title':p.name,
                       'content':p.content.encode('utf-8'),
                       'pageid':page_id},content_type='text/html')
    def save_page(self,request):
        page_id = request.POST['id']
        p = Page.objects.filter(id=page_id)[0]
        for k,v in request.POST.items():
            if 'content' in k:
                if len(v) > 0: p.content = v
            elif 'title' in k:
                if len(v) > 0: p.name = v
        p.save()
        return response('Page saved successfully')

    def page_view(self,request):
        n = request.GET['title']
        c = Page.objects.filter(name=n)[0].content
        return render(request,'pageview.jade',{'content':c},content_type='text/html')

    def view_mosaic(self,request,objlist=None,other=None):
        if 'user' in request.session: u = user(request.session['user'])
        else: u = user('efforia')
        try: page = request.GET.get('page',1)
        except PageNotAnInteger: page = 1
        if objlist is None: f = self.feed(u)
        else: f = objlist
        if other is None: p = u.profile
        else: p = other 
        f.sort(key=lambda item:item.date,reverse=True)
        p = Paginator(f,20,request=request)
        try: objects = p.page(page)
        except EmptyPage: return response('End of feed')
        apps = settings.EFFORIA_APPS
        return render(request,'grid.jade',{'f':objects,'p':p,'path':request.path,'apps':apps,
                                           'static_url':settings.STATIC_URL},content_type='text/html')
    def feed(self,userobj):
        apps = settings.EFFORIA_APPS
        feed = []; exclude = []; people = [userobj]
        for f in Followed.objects.filter(follower=userobj.id): people.append(Profile.objects.filter(id=f.followed)[0].user)
        for u in people:
            for a in apps:
                m = self.module('%s.app'%a)
                app = m.Application(u,a)
                exclude = app.relations(feed)
                app.duplicates(exclude,feed)
                app.groupables(feed) 
        return feed

    def deadlines(self,request):
        u = self.current_user(request)
        apps = settings.EFFORIA_APPS
        for a in apps:
            __import__('%s.app'%a)
            m = sys.modules['%s.app'%a]
            app = m.Application(u,a)
            app.deadline()
        return response('Deadlines verified successfully')

class Pages:
    def __init__(self): pass
    def view_page(self,request):
        return render(request,'page.jade',{},content_type='text/html')
    def create_page(self,request):
        print request.POST
        c = request.POST['content']
        t = request.POST['title']
        u = self.current_user(request)
        p = Page(content=c,user=u,name='!#%s' % t)
        p.save()
        return render(request,'pageview.jade',{'content':c},content_type='text/html')
    def edit_page(self,request):
        page_id = int(request.GET['id'])
        p = Page.objects.filter(id=page_id)[0]
        return render(request,'pagedit.jade',{
                       'title':p.name,
                       'content':p.content.encode('utf-8'),
                       'pageid':page_id},content_type='text/html')
    def save_page(self,request):
        page_id = request.POST['id']
        p = Page.objects.filter(id=page_id)[0]
        for k,v in request.POST.items():
            if 'content' in k:
                if len(v) > 0: p.content = v
            elif 'title' in k:
                if len(v) > 0: p.name = v
        p.save()
        return response('Page saved successfully')
    def page_view(self,request):
        n = request.GET['title']
        c = Page.objects.filter(name=n)[0].content
        return render(request,'pageview.jade',{'content':c},content_type='text/html')

