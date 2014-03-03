import re,difflib
from unicodedata import normalize
from datetime import datetime,timedelta
from django.shortcuts import render
from django.http import HttpResponse as response
from django.http import HttpResponseRedirect as redirect
from django.conf import settings

from demo.models import Spreadable,Image,Playable,Spreaded,Product
from feedly.feed import Activity
from feedly.models import Profile,Sellable
from demo.models import Event,Project,Interest,Movement,Promoted

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


def sp(x): return '!!' in x[1]
def pl(x): return '>!' in x[1]
def im(x): return '%!' in x[1]

class Application(Activity):
    def __init__(self,user,app): 
        Activity.__init__(self,user,app)
    def deadline(self):
        playables = Playable.objects.filter(user=self.user)
        for play in playables:
            if not play.token and not play.visual: play.delete() 
    def relations(self,feed):
        excludes = []; rels = Spreaded.objects.filter(user=self.user)
        excludes.extend([(r.spreaded,'!!') for r in rels])
        excludes.extend([(r.spread,r.token()) for r in rels]) 
        for v in rels.values('spread').distinct():
            t = rels.filter(spread=v['spread'],user=self.user)
            if len(t) > 0: feed.append(t[len(t)-1])
        return excludes
    def duplicates(self,exclude,feed):
        for o in self.objects:
            objects = globals()[o].objects.filter(user=self.user)
            if 'Spreadable' in o: e = filter(sp,exclude)
            elif 'Playable' in o: e = filter(pl,exclude)
            elif 'Image' in o: e = filter(im,exclude)
            excludes = [x[0] for x in e]
            feed.extend(objects.exclude(id__in=excludes))

def ca(x): return '@#' in x[1]
def ev(x): return '@!' in x[1]

class PromoteApplication(Activity):
    def __init__(self,user,app):
        Activity.__init__(self,user,app)
    def verify_minimum(self,event,tickets):
        tickets_len = len(tickets)
        if event.min >= tickets_len: 
            event.occurred = True
            event.save()
    def increase(self,event,rate):
        if event.increased: return
        increase = event.value
        increase *= rate
        event.value += int(increase)
        event.increased = True
        event.save()
    def deadline(self):
        events = Event.objects.filter(user=self.user)
        for e in events:
            delta = e.remaining()
            if delta < 0:
                tickets = Sellable.objects.filter(sellid=e.id)
                if len(tickets): self.verify_minimum(e,tickets)
                if not e.occurred:
                    if e.postponed: self.return_funding(e,tickets)
                    e.deadline += timedelta(days=(-delta)/2)
                    e.postponed = True
                    e.save()
            elif delta < 5: self.increase(e,0.2)
            elif delta < 10: self.increase(e,0.1)
            else: pass
        projects = Project.objects.filter(user=self.user)
        for p in projects:
            if p.funded: continue 
            delta = p.remaining()
            # Projeto concluido, entrando para fila de movimentos
            if delta < 0:
                pledges = Sellable.objects.filter(sellid=p.id)
                move = Movement.objects.filter(cause=p)
                if len(pledges) > 0: self.verify_funding(p,pledges)
                if not p.funded:
                    p.date += timedelta(days=(-delta)/2)
                    if len(move) is 0: self.create_movement(p,self.user)
                    elif len(move) > 0: self.verify_movement(p,pledges)
            # Projeto ainda em andamento
            else: pass
    def relations(self,feed):
        excludes = []; rels = Promoted.objects.filter(user=self.user)
        excludes.extend([(r.prom,r.name) for r in rels]) 
        for v in rels.values('prom').distinct():
            t = rels.filter(prom=v['prom'],user=self.user)
            if len(t) > 0: feed.append(t[len(t)-1])
        return excludes
    def groupables(self,feed):
        movement = Movement.objects.filter(user=self.user)
        for v in movement.values('name').distinct():
            ts = movement.filter(name=v['name'],user=self.user)
            if len(ts): feed.append(ts[0])
    def duplicates(self,exclude,feed):
        for o in self.objects:
            objects = globals()[o].objects.filter(user=self.user)
            if 'Project' in o: e = filter(ca,exclude)
            elif 'Event' in o: e = filter(ev,exclude)
            excludes = [x[0] for x in e]
            feed.extend(objects.exclude(id__in=excludes))
    def verify_funding(self,project,pledges):
        pledge_sum = 0
        for p in pledges: pledge_sum += p.value
        if project.credit < pledge_sum:
            p = Profile.objects.filter(user_id=project.user_id)[0]
            p.coins += pledge_sum
            p.save()
            project.funded = True
            project.save()
    def verify_movement(self,project,pledges):
        elapsed = project.elapsed()
        final_d = project.deadline()+project.deadline()/2
        if elapsed > final_d:
            self.verify_funding(project,pledges)
            # Projeto nao financiado
            if not project.funded: self.return_funding(project,pledges)
    def create_movement(self,project,user):
        interests = Interest.objects.exclude(project=project).values()
        interest = Interest.objects.filter(project=project).values('key')[0]['key']
        m = Movement(name='##%s'%interest,user=user,cause=project)
        m.save()
        for k in interests:
            s = difflib.SequenceMatcher(None,interest,k['key'])
            if s.ratio() > 0.6:
                c = Project.objects.filter(id=k['project_id'])[0]
                m = Movement(name='##%s'%interest,user=user,cause=c)
                m.save()
    def return_funding(self,funding,pledges):
        funding.delete()
        for p in pledges: p.returnable = True; p.save()
    def return_pledges(self,project,pledges):
        for p in pledges:
            pro = Profile.objects.filter(user_id=p.backer_id)
            pro.coins += p.value
            pro.save()
            p.delete()
        project.delete()

